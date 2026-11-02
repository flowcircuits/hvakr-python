"""Tests for the base URL default and the sheet and file byte downloads."""

from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from hvakr import AsyncHVAKRClient, HVAKRClient, HVAKRClientError

PDF_BYTES = b"%PDF-1.7 sheet page"
PNG_BYTES = b"\x89PNG\r\n\x1a\n sheet image"
FILE_BYTES = b"name,area\nOffice,120\n"


class TestBaseURL:
    def test_default_base_url(self) -> None:
        client = HVAKRClient(access_token="test-token")
        assert client._create_url("/me") == "https://api.hvakr.com/v0/me"

    @pytest.mark.parametrize("client_class", [HVAKRClient, AsyncHVAKRClient])
    def test_env_sets_default_base_url(
        self, monkeypatch: pytest.MonkeyPatch, client_class: type[HVAKRClient]
    ) -> None:
        monkeypatch.setenv("HVAKR_BASE_URL", "https://agent.example.test/agent/")
        client = client_class(access_token="test-token")
        assert client._create_url("/me") == "https://agent.example.test/agent/v0/me"

    @pytest.mark.parametrize("client_class", [HVAKRClient, AsyncHVAKRClient])
    def test_explicit_base_url_wins_over_env(
        self, monkeypatch: pytest.MonkeyPatch, client_class: type[HVAKRClient]
    ) -> None:
        monkeypatch.setenv("HVAKR_BASE_URL", "https://agent.example.test/agent")
        client = client_class(access_token="test-token", base_url="https://api.example.test")
        assert client._create_url("/me") == "https://api.example.test/v0/me"

    def test_empty_env_uses_default_base_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HVAKR_BASE_URL", "")
        client = HVAKRClient(access_token="test-token")
        assert client._create_url("/me") == "https://api.hvakr.com/v0/me"

    def test_env_base_url_is_used_for_requests(
        self, monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock
    ) -> None:
        monkeypatch.setenv("HVAKR_BASE_URL", "https://agent.example.test/agent")
        httpx_mock.add_response(
            url="https://agent.example.test/agent/v0/projects/p1/sheets/M-101/pdf",
            content=PDF_BYTES,
        )

        with HVAKRClient(access_token="test-token") as client:
            assert client.download_sheet("p1", "M-101") == PDF_BYTES


class TestSyncDownloads:
    def test_download_sheet_pdf_returns_bytes(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project%201/sheets/M%2F101/pdf",
            content=PDF_BYTES,
            headers={"Content-Type": "application/pdf"},
        )

        with HVAKRClient(access_token="test-token") as client:
            data = client.download_sheet("project 1", "M/101")

        request = httpx_mock.get_requests()[0]
        assert data == PDF_BYTES
        assert request.method == "GET"
        assert request.headers["Authorization"] == "Bearer test-token"
        assert request.headers["X-HVAKR-Client"] == "hvakr-python/0.6.1"

    def test_download_sheet_png(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/p1/sheets/M-101/png", content=PNG_BYTES
        )

        with HVAKRClient(access_token="test-token") as client:
            assert client.download_sheet("p1", "M-101", format="png") == PNG_BYTES

    def test_download_sheet_writes_to_path(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/p1/sheets/M-101/pdf", content=PDF_BYTES
        )
        target = tmp_path / "M-101.pdf"

        with HVAKRClient(access_token="test-token") as client:
            result = client.download_sheet("p1", "M-101", path=str(target))

        assert result == target
        assert target.read_bytes() == PDF_BYTES
        assert list(tmp_path.iterdir()) == [target]

    def test_download_file_returns_bytes_or_writes_to_path(
        self, httpx_mock: HTTPXMock, tmp_path: Path
    ) -> None:
        url = "https://api.hvakr.com/v0/projects/p1/files/file%201/content"
        httpx_mock.add_response(url=url, content=FILE_BYTES)
        httpx_mock.add_response(url=url, content=FILE_BYTES)
        target = tmp_path / "rooms.csv"

        with HVAKRClient(access_token="test-token") as client:
            data = client.download_file("p1", "file 1")
            result = client.download_file("p1", "file 1", path=target)

        assert data == FILE_BYTES
        assert result == target
        assert target.read_bytes() == FILE_BYTES

    def test_download_error_raises_with_metadata(self, httpx_mock: HTTPXMock) -> None:
        body = {"code": "invalid_request", "message": "The sheet PDF exceeds the size cap."}
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/p1/sheets/M-101/pdf",
            status_code=413,
            json=body,
        )

        with HVAKRClient(access_token="test-token") as client:
            with pytest.raises(HVAKRClientError) as exc_info:
                client.download_sheet("p1", "M-101")

        assert exc_info.value.status_code == 413
        assert exc_info.value.metadata == body

    def test_download_error_does_not_write_path(
        self, httpx_mock: HTTPXMock, tmp_path: Path
    ) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/p1/files/f1/content",
            status_code=404,
            text="Not Found",
        )
        target = tmp_path / "missing.bin"

        with HVAKRClient(access_token="test-token") as client:
            with pytest.raises(HVAKRClientError) as exc_info:
                client.download_file("p1", "f1", path=target)

        assert exc_info.value.status_code == 404
        assert exc_info.value.metadata == {"body": "Not Found"}
        assert list(tmp_path.iterdir()) == []

    def test_download_error_keeps_existing_file(
        self, httpx_mock: HTTPXMock, tmp_path: Path
    ) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/p1/files/f1/content",
            status_code=413,
            json={"code": "invalid_request", "message": "Too large"},
        )
        target = tmp_path / "rooms.csv"
        target.write_bytes(b"old")

        with HVAKRClient(access_token="test-token") as client:
            with pytest.raises(HVAKRClientError):
                client.download_file("p1", "f1", path=target)

        assert target.read_bytes() == b"old"
        assert list(tmp_path.iterdir()) == [target]


class TestAsyncDownloads:
    async def test_download_sheet_returns_bytes_or_writes_to_path(
        self, httpx_mock: HTTPXMock, tmp_path: Path
    ) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/p1/sheets/M-101/pdf", content=PDF_BYTES
        )
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/p1/sheets/M-101/png", content=PNG_BYTES
        )
        target = tmp_path / "M-101.png"

        async with AsyncHVAKRClient(access_token="test-token") as client:
            data = await client.download_sheet("p1", "M-101")
            result = await client.download_sheet("p1", "M-101", format="png", path=target)

        assert data == PDF_BYTES
        assert result == target
        assert target.read_bytes() == PNG_BYTES

    async def test_download_file_returns_bytes_or_writes_to_path(
        self, httpx_mock: HTTPXMock, tmp_path: Path
    ) -> None:
        url = "https://api.hvakr.com/v0/projects/p1/files/f1/content"
        httpx_mock.add_response(url=url, content=FILE_BYTES)
        httpx_mock.add_response(url=url, content=FILE_BYTES)
        target = tmp_path / "rooms.csv"

        async with AsyncHVAKRClient(access_token="test-token") as client:
            data = await client.download_file("p1", "f1")
            result = await client.download_file("p1", "f1", path=str(target))

        assert data == FILE_BYTES
        assert result == target
        assert target.read_bytes() == FILE_BYTES

    async def test_download_error_raises_and_does_not_write_path(
        self, httpx_mock: HTTPXMock, tmp_path: Path
    ) -> None:
        body = {"code": "invalid_request", "message": "Too large"}
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/p1/sheets/M-101/pdf",
            status_code=413,
            json=body,
        )
        target = tmp_path / "M-101.pdf"

        async with AsyncHVAKRClient(access_token="test-token") as client:
            with pytest.raises(HVAKRClientError) as exc_info:
                await client.download_sheet("p1", "M-101", path=target)

        assert exc_info.value.status_code == 413
        assert exc_info.value.metadata == body
        assert list(tmp_path.iterdir()) == []


def test_download_sheet_rejects_unknown_format() -> None:
    client = HVAKRClient(access_token="test-token")
    with pytest.raises(ValueError, match="Unsupported sheet format"):
        client.download_sheet("p1", "M-101", format="svg")  # type: ignore[call-overload]
