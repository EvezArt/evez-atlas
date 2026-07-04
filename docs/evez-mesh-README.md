# EVEZ GCP Mesh — GOLDEN SETUP

This mesh is fully automated, reproducible, and self-healing. One command = all nodes, all green.

## Quickstart

```bash
git clone git@github.com:EvezArt/evez-mesh.git
cd evez-mesh
# Sync and status all nodes
bash mesh_status.sh
# Update all nodes
bash mesh_sync.sh
```

## Topology

- **gcp-west**: 34.53.51.34
- **gcp-small**: 34.23.192.213
- **gcp-openclaw**: 35.222.248.151
- **gcp-power**: 136.113.102.152
- **gcp-knot**: 136.118.144.227

## How It Works

- **Config**: openclaw.json, .bak, .last-good all atomically updated on change.
- **Cron**: openclaw jobs validated on every update.
- **Model**: Ollama model (`evez-subagent`), always loaded.
- **Git**: master config and code — never edit nodes directly, always push/pull.

## Restore any Node

```bash
# From any box with SSH key
ssh -i ~/.ssh/openclaw-gcp openclaw@NODE-IP
cd ~/openclaw
git pull origin main
cp openclaw.json openclaw.json.bak
cp openclaw.json openclaw.json.last-good
openclaw config validate && openclaw config apply
sudo systemctl restart openclaw.service # (or user mode on gcp-knot/small/etc)
```

## Healthcheck

- Run `bash mesh_status.sh` — should print all nodes GREEN. If not, read logs below table.

## Secrets

- Tokens and credentials are `.env` only, never in repo.
- Rotate tokens via Makefile: `make rotate-tokens`
- Audit: `make audit-secrets` (scans logs and git for secret leaks)

## Extending

- Add a new node: Add to NODES[] in scripts, push config, run `mesh_sync.sh`
- Add a new skill: `git pull`, then `openclaw skills sync` on all nodes.

## FAQ

- **Node fails self-heal?** Re-run mesh_sync, check logs, run per-node restore.
- **Model not loaded?** Check Ollama service, run `ollama pull evez-subagent`.
- **Git stale?** Nodes must always be clean; push local changes before pulling.
- **Telegram bot down?** Check pgrep, restart service.

---

**This setup: One command, all green. Peter Steinberger would approve.**
