---
name: jira-cli
description: View and read Jira issues from the command line. Use when the user asks to view, list, or search Jira issues/tickets, check sprint progress, or browse project information. READ-ONLY - no modifications allowed.
license: MIT
compatibility: Requires jira-cli installed (https://github.com/ankitpokhrel/jira-cli) and configured with `jira init`. Requires JIRA_API_TOKEN environment variable.
metadata:
  author: Colby Timm
  version: "1.0"
---

# Jira CLI (Read-Only)

View and browse Atlassian Jira from the command line using [jira-cli](https://github.com/ankitpokhrel/jira-cli). This skill is **READ-ONLY** - it only supports viewing and listing operations.

## When to Use

- User asks to view or search Jira issues/tickets
- User wants to list issues, sprints, epics, or boards
- User asks about their current tasks or sprint progress
- User needs to browse project information
- READ-ONLY operations only - no creating, editing, or modifying

## Prerequisites

1. Install jira-cli: `brew install ankitpokhrel/jira-cli/jira-cli` (macOS) or download from [releases](https://github.com/ankitpokhrel/jira-cli/releases)
2. Set API token: `export JIRA_API_TOKEN="your-token"`
3. Initialize: `jira init` and follow prompts

## Issue Commands (Read-Only)

### List Issues

```bash
# List issues in current project
jira issue list

# List my assigned issues
jira issue list -a$(jira me)

# List issues by status
jira issue list -s"In Progress"

# List high priority issues
jira issue list -yHigh

# List issues with multiple filters
jira issue list -a$(jira me) -s"To Do" -yHigh --created week

# List issues with raw JQL
jira issue list -q "project = PROJ AND status = 'In Progress'"

# Plain text output for scripting
jira issue list --plain --columns key,summary,status --no-headers

# JSON output for parsing
jira issue list --raw

# CSV output for export
jira issue list --csv
```

### View Issues

```bash
# View issue details
jira issue view ISSUE-123

# View with comments
jira issue view ISSUE-123 --comments 10

# View in plain text
jira issue view ISSUE-123 --plain

# View in JSON format
jira issue view ISSUE-123 --raw

# Open issue in browser
jira open ISSUE-123
```

## Epic Commands (Read-Only)

```bash
# List epics
jira epic list

# List epics in table format
jira epic list --table

# List epics in plain text
jira epic list --plain
```

## Sprint Commands (Read-Only)

```bash
# List sprints
jira sprint list

# List current/active sprint
jira sprint list --current

# List my issues in current sprint
jira sprint list --current -a$(jira me)
```

## Project & Board Commands (Read-Only)

```bash
# List projects
jira project list

# List projects in plain text
jira project list --plain

# List boards
jira board list

# List boards in plain text
jira board list --plain

# List releases/versions
jira release list

# Open project in browser
jira open
```

## Utility Commands

```bash
# Get current username
jira me

# Show help
jira --help
jira issue --help
jira epic --help
jira sprint --help
jira project --help
jira board --help

# Setup shell completion
jira completion bash  # or zsh, fish, powershell
```

## Common Flags

| Flag | Description |
| ---- | ----------- |
| `--plain` | Plain text output (no interactive UI) |
| `--raw` | Raw JSON output |
| `--csv` | CSV output |
| `-s, --summary` | Issue summary/title filter |
| `-y, --priority` | Priority filter (Highest, High, Medium, Low, Lowest) |
| `-l, --label` | Label filter (repeatable) |
| `-a, --assignee` | Assignee username filter |
| `-r, --reporter` | Reporter username filter |
| `-C, --component` | Component name filter |
| `-q, --jql` | Raw JQL query |
| `--created` | Filter by creation date (-7d, week, month) |
| `--order-by` | Sort field |
| `--reverse` | Reverse sort order |
| `--columns` | Select specific columns to display |
| `--no-headers` | Hide table headers |

## Common Read-Only Workflows

### Daily Standup Review

```bash
# View my current sprint tasks
jira sprint list --current -a$(jira me)
```

### Search for Issues

```bash
# Search by keyword in summary
jira issue list -q "text ~ 'bug'"

# Search by multiple criteria
jira issue list -a$(jira me) -s"In Progress" -yHigh

# Recent issues created this week
jira issue list --created week
```

### Export Issue Data

```bash
# Export to CSV
jira issue list --csv > issues.csv

# Export specific fields
jira issue list --plain --columns key,summary,status,assignee --no-headers > issues.txt
```

## Output Examples

| Command | Use Case |
| ------- | -------- |
| `jira issue list --plain` | Script-friendly output |
| `jira issue list --raw` | JSON for parsing |
| `jira issue list --csv` | Export to spreadsheet |
| `jira issue view ISSUE-123 --raw` | Full issue details in JSON |

## Limitations

- Requires prior `jira init` configuration
- Some features may vary between Jira Cloud and Server
- Complex custom fields may require `--custom` flag with field IDs
- Rate limits apply based on Jira instance configuration
- **READ-ONLY**: This skill only supports viewing/listing operations
- For creating, editing, or modifying issues, use the full jira-cli directly
