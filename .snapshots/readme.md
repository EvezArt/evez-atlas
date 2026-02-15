# Snapshots Directory

This directory is for **local-only** snapshots of your code for AI interactions. Each snapshot is a markdown file that includes relevant code context and project structure information.

> **Important:** The `.snapshots/` directory is intended for temporary, generated artifacts and **should not be committed to version control**, other than this `readme.md` (or equivalent documentation).
> In your own project, ensure that any generated snapshot files are not tracked by git by adding the following entry to your `.gitignore` so these files stay local to your machine:
>
> ```gitignore
> .snapshots/
> ```
>
> If you find other files under `.snapshots/` checked into this repository, remove them from version control so that only documentation (like this file) remains.
## What's included in snapshots?
- Selected code files and their contents
- Project structure (if enabled)
- Your prompt/question for the AI

## Configuration
You can customize snapshot behavior in `config.json`.
