---
name: context-mode
description: >
  Context window optimization for AI coding sessions. Sandboxes tool output
  (98% size reduction), persists session memory in SQLite with FTS5 search,
  and enforces code-first analysis routing. Use when working on large codebases,
  long sessions, or any time context window pressure is a concern. Trigger
  phrases: "enable context mode", "optimize context", "ctx stats", "ctx doctor",
  "ctx search", "ctx index", "why is context filling up".
---

# Context Mode Skill

You are operating with **Context Mode** active — the context window optimization
layer for the `.pop` Agent Operating System.

Context Mode solves four sides of the context problem:

1. **Context Saving** — Sandbox tools keep raw data out of context. 315 KB → 5.4 KB (98% reduction).
2. **Session Continuity** — Every file edit, git op, task, error, and decision is tracked in SQLite
   with FTS5 full-text search. On compact/restart, only BM25-ranked relevant events are retrieved —
   not a full dump.
3. **Think in Code** — Use `ctx_execute` to write a script that does the analysis and logs only the
   result. One script replaces ten tool calls and saves 100× context.
4. **No prose enforcement** — Context Mode controls *where data goes*, not *how you respond*.

---

## Setup (First-Time Only)

### Step 1 — Install globally

```bash
npm install -g context-mode
```

Verify:
```bash
context-mode --version
```

### Step 2 — Register MCP + hooks in `~/.gemini/settings.json`

Add the following block (merge with any existing `mcpServers` / `hooks` keys):

```json
{
  "mcpServers": {
    "context-mode": {
      "command": "context-mode"
    }
  },
  "hooks": {
    "BeforeTool": [
      {
        "matcher": "run_shell_command|read_file|read_many_files|grep_search|search_file_content|web_fetch|activate_skill|mcp__plugin_context-mode|mcp__context-mode|mcp__(?!.*context-mode)",
        "hooks": [{ "type": "command", "command": "context-mode hook gemini-cli beforetool" }]
      }
    ],
    "AfterTool": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "context-mode hook gemini-cli aftertool" }]
      }
    ],
    "PreCompress": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "context-mode hook gemini-cli precompress" }]
      }
    ],
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "context-mode hook gemini-cli sessionstart" }]
      }
    ]
  }
}
```

### Step 3 — (Optional) Copy routing instructions

```bash
cp $(npm root -g)/context-mode/configs/gemini-cli/GEMINI.md ~/.gemini/GEMINI.md
```

### Step 4 — Verify

Restart Gemini CLI, then run:
```
/mcp list
```
You should see `context-mode: ... - Connected`.

---

## The 11 MCP Tools

### Sandbox Tools (keep raw data out of context)

| Tool | What it does |
|---|---|
| `ctx_execute(lang, code)` | Run a script; only `console.log()` output enters context |
| `ctx_execute_file(path)` | Execute a file; only stdout enters context |
| `ctx_batch_execute(tasks[])` | Run multiple scripts in parallel; aggregated stdout only |
| `ctx_fetch_and_index(url)` | Fetch a URL and index it; returns summary, not full content |
| `ctx_index(path)` | Index a local file/dir into the FTS5 knowledge base |
| `ctx_search(query)` | BM25 search over indexed content |

### Meta Tools

| Tool | What it does |
|---|---|
| `ctx_stats` | Context savings — per-tool breakdown, tokens consumed, savings ratio |
| `ctx_doctor` | Diagnostics — runtimes, hooks, FTS5, plugin registration, versions |
| `ctx_upgrade` | Pull latest, rebuild, migrate cache, fix hooks |
| `ctx_purge` | Permanently delete all indexed content |
| `ctx_insight` | Open the hosted Insight dashboard in browser |

---

## Slash Commands (type in chat)

| Command | Action |
|---|---|
| `ctx stats` | Show context savings this session |
| `ctx doctor` | Run diagnostics — verify everything is wired correctly |
| `ctx index <path>` | Index a file or directory into persistent knowledge base |
| `ctx search <query>` | Search previously indexed content |
| `ctx upgrade` | Upgrade context-mode to latest version |
| `ctx purge` | Clear the knowledge base |
| `ctx insight` | Open analytics dashboard |

---

## Think in Code — Core Paradigm

**Before context-mode** (50 file reads = 700 KB of context burned):
```js
// Tool call: read_file("src/auth.ts")
// Tool call: read_file("src/db.ts")
// ... × 47 more files
```

**After context-mode** (1 script = 3.6 KB):
```js
ctx_execute("javascript", `
  const files = fs.readdirSync('src').filter(f => f.endsWith('.ts'));
  files.forEach(f => console.log(f + ': ' + fs.readFileSync('src/'+f,'utf8').split('\n').length + ' lines'));
`);
```

### Rules for Code-First Analysis

1. **Never read 3+ files into context sequentially** — write a script that extracts only what you need.
2. **Never run `grep` on 10+ files** — use `ctx_execute` with a targeted regex script instead.
3. **Never fetch a full web page into context** — use `ctx_fetch_and_index(url)` then `ctx_search(query)`.
4. **Always log only the result** — the model reads `console.log()` output, not full file contents.
5. **Batch parallel work** — use `ctx_batch_execute` when multiple independent scripts are needed.

---

## Session Continuity Protocol

Context Mode tracks every meaningful event in SQLite. On session start:
1. The `SessionStart` hook fires automatically, injecting a routing block.
2. Previous session snapshots are retrieved via BM25 search — only relevant facts, not a full dump.
3. The agent picks up exactly where it left off.

To start fresh (no prior session data), start a new session without `--continue`.

---

## Operational Rules Within `.pop`

1. **Enable proactively** — if a request involves reading many files, large tool outputs, or long
   sessions, route through `ctx_execute` / `ctx_batch_execute` by default.
2. **Never dump raw tool output** — all large outputs (>5 KB) must be sandboxed via context-mode tools.
3. **Index knowledge aggressively** — use `ctx_index` on any docs, large files, or reference material
   before starting work. Use `ctx_search` to retrieve instead of re-reading.
4. **Check stats periodically** — run `ctx stats` after intensive tool use to monitor savings.
5. **Fail open** — if context-mode is unreachable, continue normally without it. Warn once:
   `"⚠️ context-mode unavailable — operating without context sandboxing this session."`

---

## Integration with Orchestrator

The Orchestrator Agent should route to this skill for:
- Any request that will involve reading 5+ files
- Any long-running research or multi-step coding session
- Explicit commands: `ctx stats`, `ctx doctor`, `ctx index`, `ctx search`, `ctx upgrade`
- Any time the user mentions "context", "context window", "token limit", or "compaction"
