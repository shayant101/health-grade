# PageSpeed API Quick Start Guide

## Setup

### 1. Add API Key to Environment

Edit `backend/.env`:
```bash
PAGESPEED_API_KEY=your_actual_api_key_here
```

### 2. Restart the Server

The server will automatically reload and pick up the new API key.

## Testing

### Test the API Key

```bash
cd backend
python3 test_pagespeed_api.py
```

Expected output:
```
✅ PageSpeed API Test SUCCESSFUL!
------------------------------------------------------------
Performance Score: 71.0/100
Accessibility Score: 89.0/100
Best Practices Score: 96.0/100
SEO Score: 100.0/100
Loading Time: 6511ms
```

### Test the Full Integration

```bash
curl -X POST http://localhost:8000/api/website/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-restaurant-website.com"}' | python3 -m json.tool
```

## What's Included

### PageSpeed Metrics
- ✅ Performance Score (0-100)
- ✅ Accessibility Score (0-100)
- ✅ Best Practices Score (0-100)
- ✅ SEO Score (0-100)
- ✅ Loading Time (milliseconds)

### Enhanced Scoring
- Website scores now incorporate all PageSpeed metrics
- Intelligent weighting: Performance (40%), Accessibility (25%), SEO (20%), Best Practices (15%)
- Combined with mobile-friendliness, HTTPS, and online ordering checks

### Smart Recommendations
- Performance optimization suggestions
- Loading time improvements
- Accessibility enhancements
- SEO recommendations
- Best practices guidance

## Response Format

```json
{
  "scan_id": "...",
  "url": "https://example.com",
  "website_score": 55.36,
  "status": "completed",
  "analysis_data": {
    "performance_score": 64.0,
    "accessibility_score": 86.0,
    "best_practices_score": 92.0,
    "seo_score": 100.0,
    "loading_time_ms": 5461.0,
    "https_enabled": true,
    "mobile_friendly": true,
    "online_ordering_links_count": 9,
    ...
  },
  "recommendations": [...]
}
```

## Troubleshooting

### API Key Not Working
1. Verify the key in `.env` file
2. Restart the server
3. Check logs for error messages

### Timeout Errors
- Normal for very slow websites
- API timeout is set to 90 seconds
- System will gracefully degrade to Playwright-only analysis

### Rate Limits
- Free tier: 25,000 queries/day
- Consider caching results for 24 hours
- Upgrade to paid tier if needed

## Files Modified

- `backend/app/services/website_analyzer.py` - API integration
- `backend/app/core/scoring.py` - Enhanced scoring algorithm
- `backend/app/routes/website.py` - Recommendation generation
- `backend/.env` - API key configuration

## Documentation

See `docs/PAGESPEED_INTEGRATION.md` for complete documentation.
