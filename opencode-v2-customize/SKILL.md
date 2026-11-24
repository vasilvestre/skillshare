---
name: OpenCode V2 Customize
description: Customize OpenCode V2 configuration. Use when the user asks to change opencode settings, themes, keybinds, agents, plugins, MCP servers, permissions, skills, providers, or to migrate config from V1. Covers opencode.jsonc (server config) and cli.json (terminal config).
license: MIT
---

# OpenCode V2 Customize

OpenCode V2 splits configuration into two files that never share keys. Pick the
right file before you edit anything.

| File | Scope | Schema |
| --- | --- | --- |
| `opencode.json(c)` | Server, agents, tools, providers | `https://opencode.ai/config.json` |
| `cli.json` | Terminal client only, global only | `https://opencode.ai/v2/cli.json` |

`tui.json` is V1. OpenCode migrates it to `cli.json` once. Do not create it.

## Rule 1: fetch the docs, do not guess

The V2 docs are the source of truth. Fetch the page for the topic before you
edit. Do not use `opencode.ai/docs/*`, which documents V1.

| Topic | URL |
| --- | --- |
| Config reference | `https://opencode.ai/v2/docs/config` |
| CLI settings (`cli.json`) | `https://opencode.ai/v2/docs/cli/config` |
| Keybinds | `https://opencode.ai/v2/docs/cli/keybinds` |
| Themes | `https://opencode.ai/v2/docs/cli/theme` |
| Agents | `https://opencode.ai/v2/docs/agents` |
| Skills | `https://opencode.ai/v2/docs/skills` |
| Plugins | `https://opencode.ai/v2/docs/build/plugins` |
| MCP servers | `https://opencode.ai/v2/docs/mcp-servers` |
| Permissions | `https://opencode.ai/v2/docs/permissions` |
| Policies | `https://opencode.ai/v2/docs/policies` |
| Migration V1 to V2 | `https://opencode.ai/v2/docs/migrate-v1` |
| Doc index | `https://opencode.ai/v2/llms.txt` |

Never guess a keybind command ID or a default binding. Fetch the keybind page.

## Rule 2: pick the file by the setting

Ask: does this setting change the terminal interface, or the agent runtime?

- Theme, keybinds, tabs, diffs, scroll, cursor, animations, mini, alerts,
  terminal title: `cli.json`.
- Model, agents, permissions, MCP, providers, skills, instructions, compaction,
  plugins, worktree: `opencode.jsonc`.

Putting a CLI setting in `opencode.jsonc` does nothing. OpenCode ignores unknown
keys without an error.

## Rule 3: edit in place, preserve the rest

Read the file first. Change only the keys the user asked for. Keep `$schema`.
Keep unrelated settings and comments.

Config reloads on save. Do not tell the user to restart OpenCode. Use `/reload`
only to force a full reload.

## `cli.json` reference

Location: `~/.config/opencode/cli.json`, or `$XDG_CONFIG_HOME/opencode/cli.json`.
There is no project-local CLI file. `OPENCODE_CLI_CONFIG_CONTENT` merges inline
JSON over it.

Top-level keys: `$schema`, `theme`, `keybinds`, `plugins`, `leader`, `scroll`,
`session`, `tabs`, `diffs`, `attention`, `terminal`, `mini`, `prompt`, `mouse`,
`cursor`, `animations`, `highlights`, `debug`, `experimental`.

```jsonc
{
  "$schema": "https://opencode.ai/v2/cli.json",
  "theme": { "name": "tokyonight", "mode": "system" },
  "animations": true,
  "cursor": { "style": "block", "blinking": true },
  "mouse": true,
  "scroll": { "speed": 3, "acceleration": false },
  "prompt": { "editor": true, "paste": "compact", "image_preview": false },
  "session": {
    "sidebar": "auto",
    "scrollbar": false,
    "thinking": "hide",
    "grouping": "auto",
    "tps": true,
    "markdown": "rendered",
    "new_location": "launch",
    "permissions": "prompt"
  },
  "tabs": { "mode": "auto", "scope": "cwd", "layout": "horizontal", "indicators": "status" },
  "diffs": { "source": "branch", "wrap": "word", "tree": true, "single": false, "view": "auto" },
  "attention": { "notifications": true, "sound": true, "volume": 0.4 },
  "terminal": { "title": true, "copy": "select" },
  "keybinds": { "leader": "ctrl+x", "app.exit": ["ctrl+c", "ctrl+d", "<leader>q"] },
  "leader": { "timeout": 2000 },
  "plugins": ["-opencode.notifications", { "package": "./plugins/status", "options": { "compact": true } }],
  "debug": { "devtools": false, "timing": false, "turn_tokens": "verbose" }
}
```

Accepted values:

- `theme.mode`: `system`, `dark`, `light`.
- `cursor.style`: `block`, `underline`, `line`, `default`.
- `scroll.speed`: number, at least 0.001.
- `prompt.paste`: `compact`, `full`.
- `session.sidebar`: `auto`, `hide`. `session.thinking`: `show`, `hide`.
  `session.grouping`: `auto`, `none`. `session.markdown`: `source`, `rendered`.
  `session.new_location`: `launch`, `inherit`. `session.permissions`: `prompt`,
  `autoaccept`.
- `tabs.mode`: `auto`, `on`, `off`. `tabs.scope`: `cwd`, `global`.
  `tabs.layout`: `horizontal`, `vertical`. `tabs.indicators`: `status`, `numbers`.
  Legacy boolean `tabs.enabled` still reads.
- `diffs.source`: `branch`, `committed`, `working`, `turn`. `diffs.wrap`: `word`,
  `none`. `diffs.view`: `auto`, `split`, `unified`.
- `attention.volume`: 0 to 1. `attention.sounds` keys: `default`, `question`,
  `permission`, `error`, `done`, `subagent_done`.
- `terminal.copy`: `manual`, `select`.
- `mini.*`: `show` or `hide` for `thinking`, `tools`, `shell_output`,
  `turn_summary`, `footer`, `splash`. `mini.replay_limit` defaults to 200.
- `keybinds.<command>`: a string, an array of alternatives, or an object
  `{ key, event, preventDefault, fallthrough }`. `"none"` or `false` disables.
- `plugins`: prefix `-` disables a match. Wildcards allowed.
- `debug.turn_tokens`: boolean or `"verbose"`.

## `opencode.jsonc` reference

Locations, lowest to highest precedence:

1. `~/.config/opencode/opencode.json(c)`
2. `<project>/opencode.json(c)`, merged from the farthest ancestor down
3. `<project>/.opencode/opencode.json(c)`, merged the same way
4. `/etc/opencode/opencode.json(c)` (system, highest)

Every discovered `.opencode` config overrides every direct config. Files merge;
they do not replace.

Top-level keys: `$schema`, `shell`, `model`, `default_agent`, `update`, `share`,
`enterprise`, `username`, `timezone`, `permissions`, `policies`, `agents`,
`snapshots`, `watcher`, `formatter`, `lsp`, `media`, `tool_output`, `mcp`,
`compaction`, `skills`, `commands`, `instructions`, `references`, `websearch`,
`plugins`, `worktree`, `warming`, `providers`, `experimental`.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-5-5",
  "default_agent": "build",
  "update": "notify",
  "share": "manual",
  "permissions": [
    { "action": "shell", "resource": "git push *", "effect": "ask" }
  ],
  "agents": {
    "reviewer": {
      "description": "Review changes without editing files",
      "mode": "subagent",
      "system": "Focus on correctness, security, and missing tests.",
      "permissions": [{ "action": "edit", "resource": "*", "effect": "deny" }]
    }
  },
  "mcp": {
    "servers": {
      "playwright": { "type": "local", "command": ["bunx", "@playwright/mcp"] }
    }
  },
  "compaction": { "auto": true, "keep": { "tokens": 15000 }, "buffer": "15%" },
  "skills": ["./team-skills"],
  "references": {
    "docs": { "path": "../product-docs", "description": "Product behavior" }
  },
  "worktree": { "directory": "../worktrees" },
  "plugins": ["opencode-example-plugin", { "package": "./plugins/local", "options": { "enabled": true } }]
}
```

Key shapes:

- `model`: `"provider/model"` or `"provider/model#variant"`.
- `update`: `disable`, `notify`, `auto`. Replaces `autoupdate`.
- `share`: `manual`, `auto`, `disabled`. Replaces `autoshare`.
- `permissions`: ordered array of `{ action, resource, effect }`. Effect is
  `allow`, `ask`, or `deny`. The last match wins.
- `policies`: ordered array of `{ action, resource, effect }`. Effect is `allow`
  or `deny`. Actions: `provider.use`, `tool.use`, `integration.connect`,
  `integration.use`, `mcp.use`, `skill.use`, `plugin.use`.
- `agents.<id>`: `model`, `request`, `system`, `description`, `mode`, `hidden`,
  `color`, `steps`, `disabled`, `permissions`.
- `mcp.servers.<id>`: local (`command`) or remote (`url`, `headers`, `oauth`).
  Use `disabled: true` to turn one off.
- `compaction.buffer`: an integer or a percentage string such as `"15%"`.
- `references.<alias>`: a path string, `{ path, description, hidden }`, or
  `{ repository, branch, description, hidden }`.
- `providers.<id>`: `package`, `settings`, `headers`, `body`, `models`,
  `compatibility`.

## Variables

Use `{env:NAME}` for environment variables and `{file:path}` for file contents.
Both go inside JSON strings. A missing variable or file becomes an empty string.

```jsonc
{ "providers": { "anthropic": { "settings": { "apiKey": "{env:ANTHROPIC_API_KEY}" } } } }
```

Prefer `{env:...}` over writing a secret into the config.

## Migration from V1

Read `https://opencode.ai/v2/docs/migrate-v1` before converting anything. The
three intentional breaking changes are the plugin API, the server API, and
`tui.json` becoming `cli.json`.

Common renames:

| V1 | V2 |
| --- | --- |
| `agent` | `agents` |
| `command` | `commands` |
| `provider` | `providers` |
| `plugin` | `plugins` |
| `reference` | `references` |
| `snapshot` | `snapshots` |
| `attachment` | `media` |
| `permission` (map) | `permissions` (ordered array) |
| `autoupdate` | `update` |
| `autoshare` | `share` |
| `small_model` | `agents.title.model` |
| `mcp.<id>` | `mcp.servers.<id>` |
| `mcp.<id>.enabled` | `mcp.servers.<id>.disabled` (inverted) |
| agent `prompt` | `system` |
| agent `maxSteps` | `steps` |
| permission action `bash` | `shell` |
| permission action `task` | `subagent` |
| permission action `write` / `patch` | `edit` |
| provider `npm` | `package` with `aisdk:` prefix |
| provider `api` | `settings.baseURL` |
| model `id` | `modelID` |

Behavior changes to warn about:

- Todos are off by default. Enable with `experimental.todo: true`.
- `external_directory` is allowed by default in V2. Add
  `{ "action": "external_directory", "resource": "*", "effect": "ask" }` to keep
  V1 behavior.
- `lsp` is accepted but V2 does not run language servers.
- `logLevel` is ignored. Use `OPENCODE_LOG_LEVEL`.
- `CLAUDE.md` is no longer discovered. Only `AGENTS.md`.

## Verify the change

Run these after editing. They read the live config, so they catch a typo that
the editor missed.

```bash
opencode debug config
opencode debug paths
opencode plugin list
opencode mcp list
```

`opencode debug config` prints every config source and the merged result. If a
key you added is missing from the output, OpenCode rejected it.

## Do not

- Do not create `tui.json`. It is V1.
- Do not put CLI settings in `opencode.jsonc`.
- Do not guess a keybind command ID. Fetch the keybind page.
- Do not write a secret into a config file. Use `{env:NAME}`.
- Do not tell the user to restart OpenCode after a config edit.
- Do not cite `opencode.ai/docs/*` for V2 behavior.
