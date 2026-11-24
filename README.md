# skillshare

Ma collection personnelle de skills pour agents (OpenCode, Claude Code…), gérée avec [skillshare](https://github.com/runkids/skillshare).

Ce repo est la **source globale** de skillshare : `sources.skills` dans `~/.config/skillshare/config.yaml` pointe sur ce dossier, et `skillshare sync -g` lie son contenu dans les cibles de la machine (`~/.config/opencode/skills`, `~/.agents/skills`).

Il est volontairement séparé du repo d'équipe [akawaka/skills](https://github.com/akawaka/skills), qui porte les skills partagés avec l'équipe (`audit__*`, `git__*`, `jira__*`…). Ici, uniquement ce qui m'est utile à moi, partout.

## Contenu

| Skill | Origine | Rôle |
|---|---|---|
| `skillshare` | [runkids/skillshare](https://github.com/runkids/skillshare/tree/main/skills/skillshare) | Piloter skillshare lui-même |
| `opencode-skill-creator` | [antongulin/opencode-skill-creator](https://github.com/antongulin/opencode-skill-creator) | Créer, tester et packager des skills OpenCode |
| `ponytail`, `ponytail-audit`, `ponytail-help`, `ponytail-review` | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Mode « dev paresseux » : la plus petite solution qui marche |
| `opencode-v2-customize` | local | Configurer OpenCode V2 (thèmes, keybinds, agents, MCP) |
| `sentry` | local | Sentry via un MCP lancé à la demande |
| `stateless-php-services` | local | Détecter et corriger les services PHP/Symfony à état |

Les skills « remote » sont suivis par skillshare : leur source est enregistrée dans `.metadata.json`, donc `skillshare check -g` et `skillshare update` fonctionnent. Les skills « local » n'ont pas de source distante.

## Utilisation

```bash
skillshare list -g               # skills et leur source
skillshare check -g              # mises à jour disponibles sur les skills remote
skillshare update --all -g       # les appliquer
skillshare sync -g              # lier la source dans les cibles
```

Installer un skill externe dans cette collection (sans prompt interactif) :

```bash
skillshare install github.com/<user>/<repo>/<chemin> -g --kind skill
skillshare sync -g
```

Retirer un skill : `skillshare uninstall <nom> -g` (corbeille 7 jours, `skillshare trash restore <nom>` pour annuler).

## Ce qui n'est pas ici

- **Skills d'équipe** : dans [akawaka/skills](https://github.com/akawaka/skills). Éviter les doublons de nom entre les deux.
- **Skills privés** (infra perso, GitLab privé, blog…) : dans `~/.claude/skills/`, hors de skillshare, donc jamais poussés ici. Ne pas les déposer dans `~/.agents/skills` ni dans `~/.config/opencode/skills` : `skillshare sync` y supprime ce qu'il ne reconnaît pas.
- **Skills installés avec `npx skills`** (grepai, golang-*, php-pro…) : gérés par `npx skills` dans `~/.agents/skills` (`npx skills check -g`). Rien à voir avec ce repo.
