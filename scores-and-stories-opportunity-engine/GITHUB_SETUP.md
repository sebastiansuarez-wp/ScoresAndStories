# Make this branch its own GitHub repository

This folder has already been flattened so the actual project lives at the repository root.
The old wrapper folder and temporary `_downloads-staging` files were removed.

## Option A: easiest, using GitHub Desktop

1. Unzip this folder.
2. Open GitHub Desktop.
3. Choose **File → Add Local Repository**.
4. Select the unzipped `scores-and-stories-opportunity-engine` folder.
5. If GitHub Desktop says it is not a Git repository, choose **Create a Repository**.
6. Repository name: `scores-and-stories-opportunity-engine`.
7. Keep it **Private**.
8. Commit everything with a message like:
   `Initial standalone import from workbench branch`
9. Click **Publish repository**.
10. Make sure **Keep this code private** is checked.

## Option B: command line

From inside this folder:

```bash
git init
git add .
git commit -m "Initial standalone import from workbench branch"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/scores-and-stories-opportunity-engine.git
git push -u origin main
```

Before running the `remote add` line, create an empty private repository on GitHub with the same name.
Do not initialize it with a README, .gitignore, or license, because this folder already has those project files.

## What changed from the branch ZIP

- Promoted `wp-engine/` to the repository root.
- Removed the old outer workbench wrapper.
- Excluded temporary staging/download artifacts.
- Added a basic `.gitignore` for local clutter, Python cache files, virtual environments, env files, and logs.

## What this repository contains

- `.claude/commands/` — Claude Code slash commands.
- `docs/` — dashboard, calendar, feed, digest, exports, drafts, and generated site files.
- `playbook/` — research methodology and source directory.
- `scripts/` — build/run scripts.
- `state/` — engine memory files.
- `README.md`, `HANDOFF.md`, `CLAUDE.md` — operator instructions and project contract.
