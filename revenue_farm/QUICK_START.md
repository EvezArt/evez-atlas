# Revenue Farm Quick Start Guide

Get started with the Level-1 autonomous revenue farm in 15 minutes.

## 🎯 What This Does

The revenue farm generates **proposals** for:
- Technical blog posts based on your commits
- Documentation products to sell
- GitHub Actions for the marketplace
- Training datasets from your repo activity
- Payment platform configurations

**Important**: Everything is in **proposal-only mode**. No auto-publishing, no auto-spending. You review and approve everything.

## ⚡ Quick Setup (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Your First Proposals
```bash
python revenue_farm/orchestrator.py --mode=proposal
```

This will create proposals in `revenue_farm/proposals/`.

### 3. Review Proposals
```bash
# Read the human-friendly summary
cat revenue_farm/proposals/summary_*.md

# Or check the JSON for details
cat revenue_farm/proposals/proposals_*.json | jq
```

### 4. Check Status
```bash
python revenue_farm/orchestrator.py --status
```

## 📊 What Gets Generated

### Content Farm
- **Blog posts**: Technical articles based on recent commits
- **Documentation**: API references, tutorials, cookbooks
- **Revenue**: $200-400 per product

### GitHub Action Marketplace
- **Actions**: 5 ready-to-package GitHub Actions
  - LORD consciousness monitor
  - Cognitive health check
  - Autonomous PR review
  - Training data export
  - Revenue report generator
- **Revenue**: $100 per action (free with sponsor links)

### Training Data
- **Datasets**: Anonymized repository evolution data
- **Formats**: JSONL, CSV, Parquet
- **Revenue**: $500-2,000 per dataset

### Product Wiring
- **Platforms**: GitHub Sponsors, Ko-fi, Gumroad
- **Products**: 4 premium guides ($47-497)
- **Revenue**: $1,000-2,000/month potential

## 🔧 Configuration

### Enable/Disable Streams
Edit `revenue_farm/configs/revenue_config.yml`:

```yaml
revenue_streams:
  content_farm: true      # Blog posts and docs
  action_marketplace: true # GitHub Actions
  training_data: true     # Data products
  product_wiring: true    # Payment setup
```

### Safety Settings
Edit `revenue_farm/configs/safety_config.yml`:

```yaml
safety_level: 1  # Always keep at 1 for maximum safety

human_approval:
  required: true  # Always true for Level-1
```

## 🚀 Execution Workflow

### 1. Generate Proposals (Automated)
The GitHub Action runs weekly and generates new proposals automatically.

Or run manually:
```bash
python revenue_farm/orchestrator.py --mode=proposal
```

### 2. Review Proposals
Read the summary markdown file. Each proposal includes:
- Title and description
- Revenue potential
- Risk level
- Step-by-step execution instructions

### 3. Execute Approved Proposals
Follow the execution steps in each proposal. Examples:

**For blog posts:**
1. Review the outline
2. Write the full article
3. Publish to dev.to/Medium
4. Share on social media

**For GitHub Actions:**
1. Create new repo: `evezart/lord-monitor`
2. Copy `action.yml` from proposal
3. Add implementation scripts
4. Publish to marketplace

**For training data:**
1. Review sample data
2. Export full dataset
3. Add licensing terms
4. List on marketplace

### 4. Track Revenue
Update the revenue tracking manually or use the report command:

```bash
python revenue_farm/orchestrator.py --report
```

## 💰 Revenue Projections

Based on generated proposals:

### Month 1 (Conservative)
- 3 blog posts → $150
- 2 documentation products → $400
- 5 GitHub Actions → $500
- 1 training dataset → $500
- **Total: $1,550**

### Month 3 (Optimistic)
- 10 blog posts → $500
- 5 documentation products → $1,000
- 10 GitHub Actions → $1,000
- 3 training datasets → $1,500
- GitHub Sponsors → $500
- **Total: $4,500**

## 🛡️ Safety Features

All safety features are **always enabled** in Level-1:

- ✅ No auto-publishing
- ✅ No auto-spending
- ✅ Data anonymization required
- ✅ Human approval for all actions
- ✅ Emergency kill switch available
- ✅ Audit logging enabled

### Emergency Stop
If something goes wrong:
```bash
python revenue_farm/orchestrator.py --emergency-stop
```

This creates a stop flag. Remove `revenue_farm/.emergency_stop` to resume.

## 📈 Monitoring

### View Dashboard (via logs)
```bash
tail -f revenue_farm/audit.log
```

### Generate Reports
```bash
python revenue_farm/orchestrator.py --report
```

### Check Recent Proposals
```bash
ls -ltr revenue_farm/proposals/
```

## 🎓 Next Steps

### Week 1: Content
1. Generate proposals
2. Write and publish 2 blog posts
3. Create API reference doc
4. Set up GitHub Sponsors

### Week 2: Actions
1. Package 2 GitHub Actions
2. Publish to marketplace
3. Add sponsor links

### Week 3: Data
1. Export training dataset
2. Create licensing terms
3. List on data marketplace

### Week 4: Products
1. Generate product PDFs
2. Set up Gumroad account
3. List products

## 🆘 Troubleshooting

### "Not enough commits for blog post"
**Solution**: Make 5+ commits, then regenerate proposals.

### "No data available"
**Solution**: Some features need existing data. They'll activate as you use the system.

### "Module not found"
**Solution**: Ensure you're running from repo root and requirements are installed.

### Proposals not generating
**Check**:
1. Are streams enabled in config?
2. Is emergency stop flag present?
3. Check audit log for errors

## 📚 Documentation

- [Full README](README.md)
- [Configuration Guide](configs/revenue_config.yml)
- [Safety Guide](configs/safety_config.yml)
- [Gumroad Setup](../docs/gumroad-setup.md)
- [Ko-fi Setup](../docs/kofi-setup.md)

## 🤝 Support

- Issues: https://github.com/EvezArt/Evez666/issues
- Discussions: https://github.com/EvezArt/Evez666/discussions

---

**Remember**: This is Level-1 safe mode. Everything requires your approval. No surprises, no auto-spending, full control.

Start generating income from your repository activity today! 🚀
