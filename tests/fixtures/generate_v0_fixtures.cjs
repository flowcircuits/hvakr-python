// Writes the v0 API payloads that tests/test_v0_shapes.py parses. Each payload
// must pass the @hvakr/client Zod schema unchanged, so the Python tests use
// shapes the API accepts and returns.
//
// Run it from a directory where @hvakr/client is installed:
//   node <hvakr-python>/tests/fixtures/generate_v0_fixtures.cjs
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const { createRequire } = require('node:module')

const requireFromCwd = createRequire(path.join(process.cwd(), 'index.js'))
const client = requireFromCwd('@hvakr/client')
const clientPackageJson = path.join(
    path.dirname(requireFromCwd.resolve('@hvakr/client')),
    '..',
    'package.json'
)
const clientVersion = JSON.parse(fs.readFileSync(clientPackageJson, 'utf8')).version
const outDir = path.join(__dirname, 'v0')

const write = (name, schema, value) => {
    assert.deepStrictEqual(schema.parse(value), value, `${name} changed when parsed`)
    fs.writeFileSync(
        path.join(outDir, name),
        `${JSON.stringify({ clientVersion, value }, null, 4)}\n`
    )
}

const occupiedHours = [
    0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0,
]

const centralUnitConfig = {
    components: [
        { id: 'OA', type: 'OUTSIDE_AIR_INTAKE' },
        { id: 'CC', type: 'COOLING_COIL' },
        { id: 'HC', type: 'HEATING_COIL' },
        { id: 'INEFF', type: 'EQUIPMENT_INEFFICIENCY' },
    ],
    componentConfigsByMode: {
        cooling_mode: {
            OA: {
                enabled: true,
                configuration: {
                    componentType: 'OUTSIDE_AIR_INTAKE',
                    method: 'PERCENT',
                    percentage: 0.2,
                },
            },
            CC: {
                enabled: true,
                configuration: {
                    componentType: 'COOLING_COIL',
                    targetTemperature: 55,
                    type: 0,
                    waterDeltaT: 10,
                },
            },
            HC: {
                enabled: false,
                configuration: { componentType: 'HEATING_COIL', type: 2 },
            },
            INEFF: {
                enabled: true,
                configuration: {
                    componentType: 'EQUIPMENT_INEFFICIENCY',
                    sensibleHeatGain: { type: 'POWER', power: 1500 },
                },
            },
        },
    },
    miscInefficiencies: 0.01,
    pressureLoss: 0.5,
    outlet: { ductHeatGain: 2, ductLeakagePercent: 0.01 },
    energyConfiguration: {
        schedule: { occupiedHours, warmupHours: 2, warmupMultiplier: 1.5 },
        efficiency: {
            heatingType: 'heatPump',
            coolingSEER: 14,
            heatingCOP: 3.2,
            heatingAFUE: 0.8,
        },
    },
}

const terminalUnitConfig = {
    components: [{ id: 'HC', type: 'HEATING_COIL' }],
    componentConfigsByMode: {
        heating_mode: {
            HC: {
                enabled: true,
                configuration: {
                    componentType: 'HEATING_COIL',
                    targetTemperature: 90,
                    type: 3,
                },
            },
        },
    },
    inletData: {
        enabled: true,
        configuration: {
            componentType: 'EQUIPMENT_INLET',
            decoupled: false,
            method: 'CUSTOM',
            flowRate: 250,
        },
    },
}

const centralUnit = {
    id: 'unit-ahu-1',
    nodeType: 'CENTRAL_UNIT',
    systemId: 'system-1',
    level: 1,
    point: { x: 120, y: 48 },
    rotation: 90,
    width: 144,
    height: 72,
    productId: 'product-rtu',
    cost: 42000,
    selections: {
        'heater-1': { productId: 'product-heater', quantity: 1, leavingAirTemp: 95 },
    },
    ...centralUnitConfig,
}

const terminalUnit = {
    id: 'unit-vav-1',
    nodeType: 'TERMINAL_UNIT',
    zoneId: 'zone-1',
    productId: 'product-vav',
    cost: 0,
    ...terminalUnitConfig,
}

const register = {
    id: 'register-1',
    nodeType: 'REGISTER',
    level: 1,
    point: { x: 10, y: 20 },
    flowType: 'SUPPLY',
    placementType: 'CEILING',
    flowRate: 200,
    spaceIds: ['space-1'],
}

write('graph.json', client.GraphSchema_v0, {
    [centralUnit.id]: {
        ...centralUnit,
        adjacencies: [
            { id: register.id, adjacencyType: 'DUCT', ductTypeId: 'duct-type-1' },
        ],
    },
    [terminalUnit.id]: { ...terminalUnit, adjacencies: [] },
    [register.id]: {
        ...register,
        adjacencies: [{ id: centralUnit.id, adjacencyType: 'DUCT' }],
    },
})

const airflows = { supply: 1000, return: 800, outside: 200, relief: 0, exhaust: 0 }

write('calculations.json', client.APIProjectCalculationsSchema_v0, {
    errors: [],
    flags: {},
    graph: {
        [centralUnit.id]: {
            ...centralUnit,
            pressure: 1.2,
            adjacencies: [
                {
                    id: register.id,
                    adjacencyType: 'DUCT',
                    ductSize: { ductSizeType: 'CIRCLE', height: 12 },
                    flowRate: 1000,
                },
            ],
        },
        [terminalUnit.id]: { ...terminalUnit, adjacencies: [] },
    },
    equipment: {
        [centralUnit.id]: {
            scope: { type: 'system', id: 'system-1' },
            airflows: {
                centralUnit: {
                    diversity: 0.9,
                    outdoorIntakeMultiZone: 180,
                    outdoorIntakeSumOfSpaces: 200,
                },
                raw: { cooling_mode: airflows },
            },
            modes: {
                cooling_mode: {
                    pipeline: { componentResults: {} },
                    summary: {
                        airflows: { asConfigured: airflows, withoutLeakage: airflows },
                        systemProcess: {
                            fanMotorHeatGain: 1200,
                            otherInefficiencies: 300,
                            total: 1500,
                        },
                    },
                },
            },
        },
        [terminalUnit.id]: { scope: { type: 'zone', id: 'zone-1' } },
    },
})

write('subcollections.json', client.ProjectSubcollectionsSchema_v0, {
    annotations: {
        'annotation-1': {
            x: 10,
            y: 20,
            arrowX: 30,
            arrowY: 40,
            text: 'Verify duct size',
            width: 120,
            author: 'user-1',
            level: 1,
            color: '#ff0000',
            size: 'medium',
            align: 'center',
            shape: 'cloud',
        },
    },
    exports: {
        'export-1': {
            id: 'export-1',
            name: 'Load Calculation',
            status: 'completed',
            downloadUrl: 'https://example.com/export.pdf',
            date: 1762300800000,
            outputFileType: 'PDF',
            progress: 1,
            studyId: 'study-1',
            studyName: 'Option B',
        },
    },
    sheetFilePages: {
        'page-1': {
            aiProcessing: {
                status: 'COMPLETE',
                results: { scale: { result: 48, confidence: 0.9 } },
            },
            customScaleInfo: { leftScale: 1, leftUnit: 'IN', rightScale: 4, rightUnit: 'FT' },
            defaultCeilingHeight: 108,
            defaultSlabHeight: 144,
            pageNumber: 1,
            pdfUrl: 'https://example.com/page-1.pdf',
            png: {
                standard: {
                    status: 'COMPLETE',
                    height: 1700,
                    width: 2200,
                    resolution: 150,
                    url: 'https://example.com/page-1.png',
                },
                thumbnail: { status: 'PENDING' },
            },
            scale: 48,
            sheetFileId: 'sheet-file-1',
            sheetNumber: 'M-101',
            sourceFileName: 'mechanical.pdf',
            createdAt: 1762300800000,
            title: 'First Floor Mechanical Plan',
        },
    },
    systems: { 'system-1': { name: 'AHU-1', color: '#8a8a8a', configured: true } },
    zones: { 'zone-1': { name: 'VAV-1', systemId: 'system-1' } },
})

fs.writeFileSync(
    path.join(outDir, 'keys.json'),
    `${JSON.stringify(
        {
            clientVersion,
            value: {
                expandKeys: client.PROJECT_SUBCOLLECTION_KEYS_V0,
                calculationSections: client.APICalculationSectionSchema_v0.options,
            },
        },
        null,
        4
    )}\n`
)
