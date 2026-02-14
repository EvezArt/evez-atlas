# Conversion Tracking Data

This directory contains sponsor conversion funnel analytics.

## Files

- `latest.json` - Most recent conversion snapshot
- `history.jsonl` - Historical conversion data (one JSON object per line)
- `README.md` - Conversion summary and analysis

## Conversion Funnel

```
Profile Views → Repository Stars → Sponsor Clicks → Actual Sponsors
```

## Target Metrics

- Profile views: 1,000/month
- View → Star: 3% conversion
- Star → Sponsor Click: 50% interest
- Click → Sponsor: 33-66% close rate
- **Goal:** 5-10 sponsors

## Updates

Conversion data is tracked automatically every 6 hours by the `track-conversions` GitHub Action.
