---
name: google-workspace-cli
description: >
  Integrates the Google Workspace CLI (`gws`) into .pop — one command-line tool for Drive, Gmail, Calendar, Sheets, Docs, Chat, Admin, and every other Workspace API. Dynamically built from the Google Discovery Service. Use whenever the user wants to read, write, search, or manage any Google Workspace resource from the terminal or from an AI agent pipeline. Includes guidance on auth setup, command construction, JSON output parsing, pagination, and 40+ built-in agent skills.
---

# Google Workspace CLI (`gws`) Skill

**One CLI for all of Google Workspace — built for humans and AI agents.**
Drive, Gmail, Calendar, Sheets, Docs, Chat, Admin, and every Workspace API. Zero boilerplate. Structured JSON output. 40+ agent skills included.

> Source: https://github.com/googleworkspace/cli
> ⚠️ This is NOT an officially supported Google product. It is under active development; expect breaking changes before v1.0.

---

## Overview

`gws` does **not** ship a static list of commands. It reads Google's own [Discovery Service](https://developers.google.com/discovery) at runtime and dynamically builds its entire command surface. When Google Workspace adds an API endpoint, `gws` picks it up automatically.

**For humans** — stop writing `curl` calls against REST docs. `gws` gives you `--help` on every resource, `--dry-run` to preview requests, and auto‑pagination.

**For AI agents** — every response is structured JSON. Pair it with the included agent skills and your LLM can manage Workspace without custom tooling.

---

## Installation

### Option A — npm (recommended for agents)
```bash
npm install -g @googleworkspace/cli
```

### Option B — Pre-built binary
Download the latest release for your OS from:
https://github.com/googleworkspace/cli/releases

### Option C — Homebrew (macOS/Linux)
```bash
brew install googleworkspace-cli
```

### Option D — Cargo (build from source)
```bash
cargo install --git https://github.com/googleworkspace/cli --locked
```

---

## Authentication Setup

### Which auth flow should I use?

| Situation | Use |
|---|---|
| `gcloud` installed & authenticated | `gws auth setup` (fastest) |
| GCP project but no `gcloud` | Manual OAuth via Cloud Console |
| Pre-obtained access token | `GOOGLE_WORKSPACE_CLI_TOKEN` env var |
| Existing credentials file | `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` env var |

### Interactive (local desktop)
```bash
gws auth setup    # one-time: creates Cloud project, enables APIs, logs you in
gws auth login    # subsequent scope selection and login
```

> `gws auth setup` requires the `gcloud` CLI. Without it, use manual setup.

### Scope note
If your OAuth app is in testing mode (unverified), Google limits consent to ~25 scopes. Use individual service scopes to avoid failures:
```bash
gws auth login -s drive,gmail,sheets
```

### Manual OAuth (Google Cloud Console)
1. Go to Cloud Console → APIs & Services → Credentials
2. Configure OAuth consent (External, testing mode)
3. Add yourself as a **Test User**
4. Create a **Desktop app** OAuth client
5. Download the JSON and save as `~/.config/gws/client_secret.json`
6. Run `gws auth login`

### Headless / CI
```bash
# On a machine with a browser:
gws auth export --unmasked > credentials.json

# On the headless machine:
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/path/to/credentials.json
gws drive files list   # works
```

---

## Quick Start Examples

```bash
# Setup auth
gws auth setup
gws auth login

# Drive
gws drive files list --params '{"pageSize": 10}'
gws drive files get --params '{"fileId": "FILE_ID"}'

# Sheets
gws sheets spreadsheets create --json '{"properties": {"title": "Q1 Budget"}}'

# Gmail
gws gmail users messages list --params '{"userId": "me", "maxResults": 5}'

# Chat
gws chat spaces messages create \
  --params '{"parent": "spaces/xyz"}' \
  --json '{"text": "Deploy complete."}' \
  --dry-run

# Paginate all results as NDJSON
gws drive files list --params '{"pageSize": 100}' --page-all | jq -r '.files[].name'

# Introspect any method's request/response schema
gws schema drive.files.list
```

---

## Command Structure

All `gws` commands follow a consistent pattern:

```
gws <service> <resource> <method> [flags]
```

### Common Flags

| Flag | Purpose |
|---|---|
| `--params '{"key": "val"}'` | URL/query parameters (JSON) |
| `--json '{"key": "val"}'` | Request body (JSON) |
| `--dry-run` | Preview the request without sending |
| `--page-all` | Auto-paginate and stream all pages as NDJSON |
| `--output json` | Force JSON output (default) |
| `--help` | Show method docs, params, and schema |

### Discover Available Commands
```bash
gws --help                  # list all services
gws drive --help            # list Drive resources
gws drive files --help      # list files methods
gws drive files list --help # show params for files.list
```

---

## AI Agent Skills

`gws` ships with 40+ agent skills that pair directly with LLM tool-calling:

- **Drive**: list, search, upload, download, share files
- **Gmail**: search, read, send, label messages
- **Calendar**: create, update, list events
- **Sheets**: read/write cell ranges, create spreadsheets
- **Docs**: create/update documents
- **Chat**: send messages to spaces
- **Admin**: manage users, groups, org units
- **Meet**: create and manage meetings

Each skill outputs structured JSON, making it trivial to pipe results into further agent steps.

---

## Agent Usage Patterns (for .pop pipelines)

### Pattern 1 — Read and summarize
```bash
gws gmail users messages list --params '{"userId":"me","q":"is:unread","maxResults":5}' \
  | jq '[.messages[] | {id, threadId}]'
```
Then pass the message IDs to a follow-up `gws gmail users messages get` call and summarize with the LLM.

### Pattern 2 — Write with dry-run validation
```bash
# Validate before sending
gws gmail users messages send --params '{"userId":"me"}' \
  --json '{"raw": "<base64-encoded-email>"}' \
  --dry-run

# Execute after approval
gws gmail users messages send --params '{"userId":"me"}' \
  --json '{"raw": "<base64-encoded-email>"}'
```

### Pattern 3 — Paginate large datasets
```bash
gws drive files list \
  --params '{"pageSize": 100, "fields": "files(id,name,mimeType,modifiedTime)"}' \
  --page-all \
  | jq -s '[.[] | .files[]]'
```

### Pattern 4 — Schema introspection before tool use
```bash
gws schema gmail.users.messages.send
# Returns full JSON Schema for the request body — no docs needed
```

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `GOOGLE_WORKSPACE_CLI_TOKEN` | Pre-obtained OAuth access token |
| `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` | Path to a credentials JSON file |
| `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND` | Set to `file` to store encryption key in `~/.config/gws/` instead of OS keyring |
| `GWS_LOG` | Logging verbosity (`error`, `warn`, `info`, `debug`, `trace`) |

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | General error |
| `2` | Auth error |
| `3` | API error |
| `4` | User / usage error |

---

## Operational Rules for .pop Agent

When the user asks to interact with any Google Workspace service, follow these steps:

1. **Check auth status first**: Run `gws auth login --status` or attempt a simple read command. If auth fails, guide the user through `gws auth setup` → `gws auth login`.
2. **Introspect before executing**: Use `gws schema <service.resource.method>` or `gws <service> <resource> <method> --help` to confirm params before constructing commands.
3. **Always dry-run writes**: For any mutating operation (create, update, delete, send), run with `--dry-run` first and present the preview to the user before executing.
4. **Parse JSON output**: All responses are JSON. Use `jq` to extract relevant fields before presenting to the user.
5. **Respect scope limits**: If a command fails with a scope/permission error, advise the user to re-run `gws auth login -s <service>` to add the required scope.
6. **Handle pagination**: For list operations that might return many results, use `--page-all` and process with `jq -s` to aggregate pages.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `Access blocked` on OAuth | Add your email under **Test Users** in the OAuth consent screen |
| `Scope not granted` error | Run `gws auth login -s <service>` to add the specific service scope |
| `gws` not found | Ensure the binary is in `$PATH` or re-run `npm install -g @googleworkspace/cli` |
| Credentials expired | Run `gws auth login` to refresh |
| Rate limit errors | Add exponential backoff between requests; use `--page-all` for large lists |

---

## References

- GitHub: https://github.com/googleworkspace/cli
- npm: https://www.npmjs.com/package/@googleworkspace/cli
- Releases: https://github.com/googleworkspace/cli/releases
- Google Discovery Service: https://developers.google.com/discovery
- Google Cloud Console: https://console.cloud.google.com/
