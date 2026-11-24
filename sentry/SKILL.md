---
name: sentry
description: "Sentry error monitoring via an on-demand MCP (starts only when first invoked). Use for: production errors, grouped issues, stack traces, root cause analysis, Seer autofix analysis, error/event/log/span/metric search, session replays, traces, releases, monitors, cron monitors, DSNs, project/org lookup, issue status updates (resolve/assign/ignore). Triggers: sentry, production error, bug report from users, why is this crashing, investigate exception, search logs, trace this request, resolve issue, assign issue. NOT for setting up the Sentry SDK in code (use sentry-php-sdk or Sentry docs)."
---

# Sentry

Sentry MCP on demand. The connection opens lazily on the first `skill_mcp` call — nothing is paid until a real Sentry task appears.

**First call triggers a one-time OAuth flow**: a local callback server starts (127.0.0.1) and an authorization URL is produced — the user opens it in a browser, approves, and the token is cached in the plugin's `mcp-oauth` storage. Subsequent sessions reuse it.

## How to invoke

All operations go through `skill_mcp` with `mcp_name="sentry"` (in Hermes the same tools are exposed as `mcp__sentry__*` and called via `tool_call` after `tool_describe`):

```
skill_mcp(mcp_name="sentry", tool_name="search_issues", arguments={"organizationSlug": "my-org", "query": "is:unresolved"})
skill_mcp(mcp_name="sentry", tool_name="get_sentry_resource", arguments={"url": "https://my-org.sentry.io/issues/PROJ-123/"})
```

## Core tools (direct)

| Tool | Use |
|---|---|
| `find_organizations` | List orgs the user can access |
| `find_projects` | List/find projects in an org |
| `search_issues` | Grouped issue list (is:unresolved, level:error…) — NOT counts |
| `search_events` | Events/aggregations: errors, logs, spans, metrics, profiles, replays |
| `get_sentry_resource` | Fetch issue/event/trace/replay by URL or type+id |
| `analyze_issue_with_seer` | AI root-cause analysis + fix recommendations (~2–5 min) |
| `update_issue` | Resolve/ignore/assign — **confirm with the user first** |
| `search_sentry_tools` | Meta-search the full catalog for long-tail ops (DSNs, releases, teams, monitors, attachments) |
| `execute_sentry_tool` | Run a tool found via `search_sentry_tools` |

## Workflow rules

- **URL given?** Pass it straight to `get_sentry_resource` — type is auto-detected.
- **Counts/aggregations** → `search_events` with fields like `count()`. **Grouped problems** → `search_issues`. **One specific issue** → `get_sentry_resource`.
- `name/otherName` params = `organizationSlug/projectSlug` — parse directly, don't look up first.
- Long-tail Sentry features (releases, DSNs, teams, alerts): `search_sentry_tools` first, then `execute_sentry_tool` — don't guess tool names.
- `update_issue` mutates state: show the user exactly what will change and get approval before calling.

## Pitfalls

- **Region is per org.** `find_organizations` returns a `regionUrl` for each org (one org may be on `us.sentry.io`, another on `de.sentry.io`). Pass that `regionUrl` on every search for the org; omitting it against a non-default region returns empty results with no error.
- **Thematic searches fail silently.** `search_issues` matches issue titles/messages, so a natural-language query like "json-ld structured data availability" returns "No issues found" rather than a bad-query error. Start from `is:unresolved` (plus `period`/`sort`), read the candidates with `get_sentry_resource`, and filter them yourself.
- **Sentry records exceptions, not correctness.** JSON-LD/schema.org markup, feed fields, prices, stock/availability flags and template-data bugs raise no event. Say "no Sentry signal" instead of citing a nearby unrelated issue as if it were correlated.
- **Quote the window with counts.** Occurrence and user counts differ per `period`; report them as "26 events / 25 users (24 h)" so the numbers are reproducible and comparable with the UI.
