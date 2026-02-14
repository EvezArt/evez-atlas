# Autonomous Revenue Farm (Level-1 Safe Implementation)

This directory contains the Level-1 safe implementation of autonomous revenue generation systems for the Evez666 project. All high-risk operations require human approval.

## 🛡️ Safety Features

- **No Auto-Spend**: All financial transactions require manual approval
- **No Live Trading**: Trading features are disabled and documented only
- **Proposal-Only**: All agents generate proposals for human review
- **Data Anonymization**: All exported data is automatically anonymized
- **Audit Logging**: All operations are logged for review

## 📂 Directory Structure

```
revenue_farm/
├── content_farm/          # Autonomous content generation
│   ├── blog_generator.py  # Blog post generation (proposal-only)
│   ├── doc_generator.py   # Documentation generation
│   └── templates/         # Content templates
├── action_marketplace/    # GitHub Action packaging
│   ├── action_packager.py # Action metadata generator
│   └── templates/         # Action templates
├── training_data/         # Training data packaging
│   ├── data_packager.py   # Data extraction and anonymization
│   └── datasets/          # Generated datasets
├── product_wiring/        # Payment platform integration
│   ├── product_meta.py    # Product metadata generator
│   └── configs/           # Platform configs
├── configs/               # Global configurations
│   ├── revenue_config.yml # Revenue stream settings
│   └── safety_config.yml  # Safety guardrails
└── orchestrator.py        # Main orchestration script
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Revenue Streams
Edit `configs/revenue_config.yml` to enable desired revenue streams.

### 3. Run Orchestrator (Proposal Mode)
```bash
python revenue_farm/orchestrator.py --mode=proposal
```

This will generate proposals for:
- Blog posts based on recent commits
- Documentation updates
- GitHub Actions to package
- Training datasets to publish
- Products to list on marketplaces

### 4. Review and Approve
Review generated proposals in `revenue_farm/proposals/` and manually execute approved actions.

## 💰 Revenue Streams (Level-1 Safe)

### 1. Content Farm
- **Status**: Proposal-only
- **Output**: Blog posts, documentation, technical guides
- **Safety**: No auto-publishing, requires manual review

### 2. GitHub Action Marketplace
- **Status**: Semi-automated
- **Output**: Packaged GitHub Actions with marketplace metadata
- **Safety**: Human approves before marketplace listing

### 3. Training Data Marketplace
- **Status**: Automated packaging, manual listing
- **Output**: Anonymized training datasets
- **Safety**: Auto-anonymization, manual pricing/listing

### 4. Sponsor/Ko-fi/Gumroad Products
- **Status**: Metadata generation only
- **Output**: Product descriptions, pricing configs
- **Safety**: Human creates actual listings

## 🔐 Ethical Guardrails

1. **Transparency**: All AI-generated content is clearly labeled
2. **Privacy**: Personal data is automatically anonymized
3. **Quality**: Human review for all public-facing content
4. **Compliance**: GDPR-compliant data handling
5. **Attribution**: Proper citations for all sources

## 📊 Monitoring

View revenue stream status:
```bash
python revenue_farm/orchestrator.py --status
```

Generate revenue report:
```bash
python revenue_farm/orchestrator.py --report
```

## 🛠️ Configuration

### Enable/Disable Streams
Edit `configs/revenue_config.yml`:
```yaml
revenue_streams:
  content_farm: true
  action_marketplace: true
  training_data: true
  product_wiring: true
```

### Adjust Safety Settings
Edit `configs/safety_config.yml`:
```yaml
safety:
  require_human_approval: true
  auto_publish: false
  max_daily_proposals: 10
  anonymize_data: true
```

## 📚 Documentation

- [Content Farm Guide](content_farm/README.md)
- [Action Marketplace Guide](action_marketplace/README.md)
- [Training Data Guide](training_data/README.md)
- [Product Wiring Guide](product_wiring/README.md)

## 🆘 Support

For issues or questions:
- GitHub Issues: https://github.com/EvezArt/Evez666/issues
- Email: [Contact in repo]

---

**Note**: This is a Level-1 safe implementation. No real money is spent automatically. All high-risk actions require explicit human approval.
