---
name: server-sync-pull
description: Check drift between the local ultracc/ repo and the live seedbox, then pull server files into the repo. Use this whenever the user mentions syncing, drift, "1-1", pulling from the server, file differences with the seedbox, or after any change was made directly on the live server (le4-0-103-188radon.pulsedmedia.com, user nadwey). Also use proactively before pushing or editing compose/.env files in the ultracc project to make sure the local copy is current.
---

# Server sync: status then pull

The live seedbox is `nadwey@le4-0-103-188radon.pulsedmedia.com` (uid 1033,
`185.148.0.188`). It is running truth for `compose.yaml` and `.env`. The local
repo (`/home/vsilvestre/ultracc/`) is source of truth for docs and configs.
Drift happens when someone edits the server directly. This skill detects and
resolves it.

> **Do not confuse this box with `3-229mighty.pulsedmedia.com`.** That is a
> *different* seedbox on the same provider (`185.148.3.239`). An earlier version
> of this skill named it by mistake. All commands must go through `./sync.sh`,
> which pins the correct host and verifies the box's identity before touching
> it — never hand-roll an `ssh`/`scp` to a guessed hostname.

## Steps

1. From `/home/vsilvestre/ultracc/`, run `./sync.sh status`.
   This runs an identity preflight first and aborts if it is not talking to the
   expected seedbox.
2. Read the output. Each line is either `OK` (identical) or `DIFF`.
3. If any line shows `DIFF`, run `./sync.sh pull`.
   - `pull` overwrites local `compose.yaml` and `.env.SECRETS` with the server
     versions. This is correct: the server is live truth for those two.
   - It snapshots any local file it is about to overwrite into
     `backup/pre-pull-<timestamp>/` first, and prints where.
   - Do NOT edit the pulled files afterward to "improve" them without asking.
4. **Diff before discarding.** The server's copies are not always the better
   copy: a server-side edit can silently drop documentation that only existed
   locally. Compare before overwriting, and if the server version looks *older*
   or thinner, say so and ask rather than proceeding.
5. Run `./sync.sh status` again and confirm every line says `OK`.
6. Report what was out of sync and that it is now resolved.

## Rules

- Never run `./sync.sh push` from this skill. Push overwrites the LIVE server.
  Only push when the user explicitly asks.
- `./sync.sh status` **does** compare AGENTS.md, README.md and CREDENTIALS.md,
  so there is no need to hand-roll an `scp` to fetch docs. If you do need an
  out-of-band file, use the `SERVER` value from `sync.sh` and keep the
  `nadwey@le4-0-103-188radon.pulsedmedia.com` hostname.
- All sync.sh commands must run from the repo root `/home/vsilvestre/ultracc/`.
- The repo is a **local-only** git repo with **no remote**. `.env`,
  `.env.SECRETS` and `CREDENTIALS.md` hold live credentials — never add a
  remote, never `git push`.

## Example

```
$ ./sync.sh status
== local (ultracc/) vs live server ==
OK    compose.yaml
DIFF  .env / .env.SECRETS
OK    nginx/seerr-subfolder.conf
```

Line 2 is DIFF, so run `./sync.sh pull`, then re-run status and expect all OK.
