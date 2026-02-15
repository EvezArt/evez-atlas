# Snapshots Directory

This directory is for **local-only** snapshots of your code for AI interactions. Each snapshot is a markdown file that includes relevant code context and project structure information.

> **Important:** This `.snapshots/` directory is intended for temporary, generated artifacts and **should not be committed to version control**.  
> Add the following entry to your `.gitignore` so these files stay local to your machine:
>
> ```gitignore
> .snapshots/
> ```
## What's included in snapshots?
- Selected code files and their contents
- Project structure (if enabled)
- Your prompt/question for the AI

## Configuration
You can customize snapshot behavior in `config.json`.
