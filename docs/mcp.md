# MCP servers

The scaffold writes `.mcp.json` at the project root (committed) so any agent cloning the repo
gets the same tool surface. Installation is **manual** — the previous "auto-install" approach
silently masked failures and left agents thinking MCP worked when it didn't.

## What each server exposes

### `esp-idf-mcp`

- Read / modify `sdkconfig`.
- List Kconfig options.
- Trigger `idf.py build` / `flash` / `monitor`.
- Parse build-error output into structured diagnostics.

Typical agent use: "tweak `CONFIG_SPIRAM_MODE_OCT` and rebuild" without re-reading the entire
doc tree.

### `serial-mcp-server`

- List serial ports.
- Open / close.
- Read-with-timeout.
- Write-line.

Typical agent use: send REPL commands to the DUT, capture boot logs after a flash, run
interactive smoke probes without writing new Python.

## Installation

These aren't published on standard indexes under canonical names. Pin to specific sources the
user has vetted. Examples (adjust for your actual vendor/version):

```bash
# esp-idf-mcp — example; replace with your vetted source.
uv tool install git+https://github.com/<org>/esp-idf-mcp

# serial-mcp-server — example; replace with your vetted source.
cargo install --git https://github.com/<org>/serial-mcp-server
```

After installing, verify:

```bash
command -v esp-idf-mcp
command -v serial-mcp-server
```

Both should print a path. If either is missing, MCP for that server is disabled — Claude will
continue without it but some tool-driven flows will silently skip steps.

## Security posture

- `.mcp.json` is committed and must contain **no secrets**. No API keys, tokens, or credentials
  in the `env` section.
- User-specific MCP configuration (e.g. cloud services) belongs in
  `~/.claude/settings.json`, not in the committed project file.
