# Viral Growth & Engagement Scripts

Automated community engagement, viral growth, and traffic generation system for Evez666.

## Overview

This directory contains scripts for automating:
- Social media posting (Twitter, Reddit, Hacker News, YouTube)
- Community engagement (star appreciation, milestone celebrations)
- Analytics & metrics tracking
- A/B testing for messaging
- Referral tracking

## Scripts

### Social Media Automation

#### `post_to_social.py`
Auto-posts to Twitter/X for milestones, PRs, and updates.

```bash
# Post milestone celebration
python scripts/engagement/post_to_social.py --milestone

# Announce new PR
python scripts/engagement/post_to_social.py --pr

# Thank new sponsor
python scripts/engagement/post_to_social.py --sponsor

# Custom message
python scripts/engagement/post_to_social.py --message "Your message here"
```

**Environment Variables:**
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_SECRET`

#### `post_to_reddit.py`
Cross-posts major updates to relevant subreddits.

```bash
# Post major milestone
python scripts/engagement/post_to_reddit.py --major

# Post progress update
python scripts/engagement/post_to_reddit.py --progress --title "Update Title" --description "Description"
```

**Environment Variables:**
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USERNAME`
- `REDDIT_PASSWORD`

#### `post_to_hn.py`
Submits to Hacker News for major milestones.

```bash
# Submit launch milestone
python scripts/engagement/post_to_hn.py --milestone launch

# Submit stars milestone
python scripts/engagement/post_to_hn.py --milestone stars --count 100

# Custom Show HN
python scripts/engagement/post_to_hn.py --title "Show HN: ..." --url "..." --text "..."
```

**Environment Variables:**
- `HN_USERNAME`
- `HN_PASSWORD`

### Content Generation

#### `generate_content.py`
Generates scheduled content for content calendar.

```bash
# Generate Monday architecture post
python scripts/engagement/generate_content.py --day monday

# Generate Wednesday progress update
python scripts/engagement/generate_content.py --day wednesday

# Generate Friday weekend project
python scripts/engagement/generate_content.py --day friday
```

#### `generate_youtube_content.py`
Creates YouTube video scripts and metadata.

```bash
# Generate full video script
python scripts/engagement/generate_youtube_content.py --script

# Generate short-form script
python scripts/engagement/generate_youtube_content.py --short --hook "Your hook"

# Generate title ideas
python scripts/engagement/generate_youtube_content.py --titles

# Generate video description
python scripts/engagement/generate_youtube_content.py --description
```

### Analytics & Tracking

#### `check_milestones.py`
Checks for repository milestones (stars, forks, sponsors).

```bash
python scripts/engagement/check_milestones.py
```

Sets GitHub Actions outputs:
- `milestone_reached` (true/false)
- `milestone_type` (stars/forks/sponsors)
- `milestone_count` (number)

#### `generate_engagement_report.py`
Generates comprehensive weekly engagement report.

```bash
python scripts/engagement/generate_engagement_report.py
```

Outputs:
- `engagement_report_YYYYMMDD.json` - Full data
- `engagement_summary_YYYYMMDD.md` - Markdown summary

#### `update_metrics.py`
Updates engagement metrics and stores historical data.

```bash
python scripts/engagement/update_metrics.py
```

Stores data in: `data/metrics_history.json`

#### `referral_tracker.py`
Tracks traffic sources and top referrers.

```bash
python scripts/engagement/referral_tracker.py
```

Outputs: `referral_report.md`

### Community Engagement

#### `thank_stars.py`
Thanks recent stargazers (complementary to GitHub Action).

```bash
python scripts/engagement/thank_stars.py
```

### A/B Testing

#### `message_tester.py`
A/B testing framework for messaging variants.

```bash
# Get test variant
python scripts/engagement/message_tester.py --get-variant --platform twitter

# Record test results
python scripts/engagement/message_tester.py --record TEST_ID --engagement 150

# Show winning variant
python scripts/engagement/message_tester.py --winner

# Generate full report
python scripts/engagement/message_tester.py --report
```

## GitHub Actions Integration

The scripts are integrated with GitHub Actions workflows:

### `.github/workflows/thank-new-stars.yml`
Triggers on `watch` event to thank new stargazers.

### `.github/workflows/content-calendar.yml`
Scheduled posts:
- Monday 2pm UTC: Architecture deep-dive
- Wednesday 2pm UTC: Progress update
- Friday 2pm UTC: Weekend project idea

### `.github/workflows/viral-growth-engine.yml`
Runs every 6 hours to:
- Thank new stars
- Check milestones
- Post to social media if milestone reached
- Update engagement metrics
- Generate weekly report (Mondays)

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**

Create `.env` or set in GitHub Secrets:

```bash
# Twitter/X
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_token_secret

# Reddit
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password

# Hacker News
HN_USERNAME=your_username
HN_PASSWORD=your_password

# GitHub (usually provided by Actions)
GH_TOKEN=your_github_token
GITHUB_REPOSITORY=EvezArt/Evez666
```

3. **Create data directory:**
```bash
mkdir -p data
```

## Messaging Variants

The system A/B tests four messaging approaches:

1. **Technical**: "Built a self-aware GitHub repo using LORD × EKF × Copilot"
2. **Revenue**: "This GitHub repo generates $2.8K/month autonomously"
3. **Speed**: "From zero to monetized repo in 24 hours using AI"
4. **Mystery**: "I taught a GitHub repo to evolve itself. Here's how."

Use `message_tester.py` to track which performs best.

## Target Metrics (Month 1)

**Traffic Goals:**
- GitHub profile views: 1,000
- Repo visits: 500
- Stars: 50
- Forks: 10

**Social Goals:**
- Twitter followers: 200
- Reddit posts: 5 (avg 50 upvotes)
- HN frontpage: 1 time
- YouTube views: 1,000

**Conversion Goals:**
- Newsletter signups: 100
- Sponsor conversions: 10 (1% of traffic)
- Product sales: 20

## Architecture

```
┌─────────────────────────────────────────┐
│        GitHub Actions Workflows          │
│  (thank-new-stars, content-calendar,    │
│   viral-growth-engine)                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Engagement Scripts (Python)         │
│  - Social media posting                  │
│  - Content generation                    │
│  - Milestone checking                    │
│  - Metrics tracking                      │
│  - A/B testing                           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      External Services & APIs            │
│  - Twitter/X API                         │
│  - Reddit API (praw)                     │
│  - Hacker News                           │
│  - GitHub API                            │
└─────────────────────────────────────────┘
```

## Notes

- All scripts handle missing API credentials gracefully (dry-run mode)
- Historical data is stored in `data/` directory
- Reports are generated in markdown format
- Scripts output GitHub Actions-compatible variables
- Rate limiting is respected for all APIs

## Contributing

When adding new engagement scripts:
1. Follow the existing pattern
2. Handle missing credentials gracefully
3. Add to this README
4. Update requirements.txt if needed
5. Test with GitHub Actions

## License

Part of the Evez666 cognitive engine project.
