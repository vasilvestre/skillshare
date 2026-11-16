---
name: semantic-search
description: |
  Decide between grep (regex) and grepai (semantic) search tools for codebase queries.
  Use this skill whenever the user asks to search, find, or locate code, files, or patterns
  in a codebase, repository, or project. Also trigger when the user mentions "grep",
  "search", "find", "locate", "semantic search", "code search", or "where is" —
  even if they don't explicitly ask for a comparison. This skill provides a fast decision
  framework and optional benchmarking to pick the right tool for the job.
---

# semantic-search

## Purpose

When a user wants to search a codebase, you have two powerful tools:
- **grep** — fast regex search, exact/pattern matching
- **grepai** — semantic search, natural language understanding

This skill helps you decide which to use, and optionally benchmark both to prove the choice.

## Quick Decision Framework

Follow this decision tree exactly. Do not override with your own judgment.

### Step 1: Check for Exact Match Keywords
Does the query contain any of these?
- Exact class/function/variable names (e.g., "UserRepository", "handleRequest")
- Specific error messages or strings
- File extensions or patterns (e.g., "*.php", "*.tsx")
- Known regex patterns

**If YES → Use grep immediately. Stop here.**

### Step 2: Check for Conceptual Keywords
Does the query contain any of these?
- "how does...work"
- "something that does X"
- "code related to Y concept"
- "find me..." (without exact names)
- Broad exploration questions
- Natural language descriptions of functionality

**If YES → Use grepai immediately. Stop here.**

### Step 3: Check Query Breadth
- **Narrow lookup** ("where is X defined?", "find Y class") → **grep**
- **Broad exploration** ("how does auth work?", "explain the billing flow") → **grepai**

**If still unclear after Step 3 → Benchmark both tools and compare.**

## When to Use grep

- Exact function/class/variable names
- Specific strings, error messages, or log patterns
- File type or extension filtering (`*.php`, `*.tsx`)
- Regex patterns (e.g., `function\s+\w+`)
- Cross-references (find all callers of a function)
- Performance-critical searches (grep is faster)

## When to Use grepai

- Natural language queries ("user authentication flow", "error handling middleware")
- Conceptual searches ("how does the billing system work?")
- When you don't know the exact naming conventions
- Finding semantically related code across different naming schemes
- Exploring unfamiliar codebases
- Searching for patterns described in prose

## Benchmarking Workflow

When the user explicitly asks to "benchmark" or "compare" grep vs grepai, or when you want to validate your choice:

### Step 1: Run Both Tools on the Same Query

```
grep query: "function handleRequest"
grepai query: "function that handles HTTP requests"
```

### Step 2: Compare Results

Evaluate on these dimensions:

| Dimension | grep | grepai |
|-----------|------|--------|
| Speed | Faster (regex) | Slower (semantic) |
| Exact match | Perfect | May miss exact matches |
| Conceptual match | Poor | Excellent |
| False positives | Low | Possible |
| Token cost | Low | Higher |

### Step 3: Report Findings

Use this template:

```markdown
## Search Benchmark: [Query]

### grep Results
- Command: `grep -r "pattern" .`
- Matches: N
- Relevance: High/Medium/Low
- Time: ~Xms

### grepai Results
- Query: "natural language query"
- Matches: N
- Relevance: High/Medium/Low
- Time: ~Xms

### Recommendation
[Which tool won and why]
```

## Examples

**Example 1: Exact identifier lookup**
User: "Where is the UserRepository class defined?"
→ Use **grep**: `grep -r "class UserRepository" src/`

**Example 2: Conceptual search**
User: "How does the payment processing work?"
→ Use **grepai**: `grepai "payment processing workflow"`

**Example 3: Ambiguous case — benchmark both**
User: "Find code that handles user sessions"
→ Run both, compare, report which found the relevant `SessionHandler` faster.

## Anti-Patterns

- **NEVER** use grepai for exact string lookups (wasteful)
- **NEVER** use grep for conceptual queries like "how does X work?" (poor results)
- **NEVER** default to one tool without running the decision framework
- **NEVER** override the framework with your own reasoning — the framework is optimized for accuracy
- Don't benchmark unless asked or the choice is genuinely unclear after Step 3

## Integration with Other Tools

- After grepai finds relevant files, use **grep** to drill into specifics
- Use **ast-grep** for AST-level pattern matching when regex isn't enough
- Combine with **lsp_find_references** for precise symbol navigation
