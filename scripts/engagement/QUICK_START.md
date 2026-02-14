# Viral Growth Engine - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Without Credentials (Dry-Run Mode)
```bash
# Generate Monday content
python scripts/engagement/generate_content.py --day monday

# Check milestones
python scripts/engagement/check_milestones.py

# Update metrics
python scripts/engagement/update_metrics.py
```

### 3. Configure Social Media (Optional)

Add to GitHub Secrets (Settings > Secrets > Actions):

**Twitter/X:**
```
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_token_secret
```

**Reddit:**
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

## 📊 What Runs Automatically

### On Every Star ⭐
- Creates thank-you issue
- Links to sponsors & products
- *Workflow: `.github/workflows/thank-new-stars.yml`*

### Mon/Wed/Fri at 2pm UTC 📅
- Generates scheduled content
- Posts to social media
- *Workflow: `.github/workflows/content-calendar.yml`*

### Every 6 Hours ⏰
- Checks for milestones
- Updates metrics
- Celebrates achievements
- *Workflow: `.github/workflows/viral-growth-engine.yml`*

## 🧪 Testing Individual Scripts

```bash
# Content generation
python scripts/engagement/generate_content.py --day monday
python scripts/engagement/generate_content.py --day wednesday
python scripts/engagement/generate_content.py --day friday

# YouTube content
python scripts/engagement/generate_youtube_content.py --titles
python scripts/engagement/generate_youtube_content.py --script

# A/B testing
python scripts/engagement/message_tester.py --get-variant
python scripts/engagement/message_tester.py --winner

# Social media (dry-run without credentials)
python scripts/engagement/post_to_social.py --milestone
python scripts/engagement/post_to_reddit.py --major

# Analytics
python scripts/engagement/check_milestones.py
python scripts/engagement/update_metrics.py
python scripts/engagement/generate_engagement_report.py
python scripts/engagement/referral_tracker.py
```

## 📈 Target Metrics (Month 1)

| Metric | Target |
|--------|--------|
| GitHub Stars | 50 |
| Repository Visits | 500 |
| Profile Views | 1,000 |
| Sponsors | 10 |
| Twitter Followers | 200 |
| Revenue Impact | $3,000/mo |

## 🔄 Viral Loops

1. **Star → Thank → Sponsor**
   - User stars repo
   - Auto thank-you issue created
   - Links to sponsor page
   
2. **Milestone → Tweet → Stars**
   - Hit star milestone
   - Auto-tweet celebration
   - New users discover repo

3. **Content → Reddit → Traffic**
   - Scheduled content posted
   - Reddit engagement
   - Traffic to repo

4. **Fork → Template → Referral**
   - User forks as template
   - Backlink to original
   - Referral traffic

## 🛠️ Manual Triggers

### Trigger Star Appreciation
```bash
gh workflow run thank-new-stars.yml
```

### Trigger Content Post
```bash
gh workflow run content-calendar.yml
```

### Trigger Growth Engine
```bash
gh workflow run viral-growth-engine.yml
```

## 📚 Documentation

- **Full System Docs**: `docs/VIRAL_GROWTH_ENGINE.md`
- **Script Details**: `scripts/engagement/README.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY_VIRAL_GROWTH.md`

## 🎯 A/B Testing Variants

The system tests 4 message variants:

1. **Technical**: "Built a self-aware GitHub repo using LORD × EKF × Copilot"
2. **Revenue**: "This GitHub repo generates $2.8K/month autonomously"
3. **Speed**: "From zero to monetized repo in 24 hours using AI"
4. **Mystery**: "I taught a GitHub repo to evolve itself. Here's how."

Best performer becomes default messaging.

## 💡 Pro Tips

1. **Start without credentials** - All scripts work in dry-run mode
2. **Monitor metrics daily** - Check `data/metrics_history.json`
3. **Review A/B tests weekly** - Optimize messaging
4. **Adjust content calendar** - Based on engagement data
5. **Celebrate milestones** - Manual posts for major wins

## ⚠️ Known Limitations

- **Reddit**: 10-min delays between posts (rate limiting)
- **Hacker News**: Manual submission recommended
- **API Limits**: Requires credentials for live posting

## 🤝 Get Help

- Issues: https://github.com/EvezArt/Evez666/issues
- Discussions: https://github.com/EvezArt/Evez666/discussions
- Sponsor: https://github.com/sponsors/EvezArt

---

**Ready to grow? Start with `python scripts/engagement/check_milestones.py`** 🚀
