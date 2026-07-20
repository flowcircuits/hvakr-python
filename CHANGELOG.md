# Changelog

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-07-20

### Breaking changes

- Project `users` maps returned by `GET /v0/projects`, `GET /v0/projects/{id}`,
  and expanded project responses are now keyed by Firebase UID rather than
  email address.
- Each read-only membership entry now always includes its lowercase `email`.

### Migration

Replace email-keyed access such as `project.users["member@example.com"]` with
iteration over the UID-keyed map and use `member.email` for display or email
matching. Do not add `users` to create or update payloads; it remains a
restricted write field.
