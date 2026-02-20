# Website-Only Analysis Feature

## Overview

The Website-Only Analysis feature provides a fast, lightweight alternative to the full restaurant scan. Users can quickly check their website's health without waiting for a comprehensive analysis of Google Business Profile, reviews, and ordering systems.

## Key Benefits

- **Fast Response**: 2-7 seconds vs 10-15 seconds for full scan
- **Lower Barrier to Entry**: Users can test the tool with just a URL
- **Clear Upsell Path**: Easy upgrade to full restaurant scan
- **Data Tracking**: All analyses saved to database for analytics
- **Actionable Insights**: 3-5 prioritized recommendations

## Architecture

### Backend Components

#### 1. API Endpoint
**File**: `backend/app/routes/website.py`

**Endpoint**: `POST /api/website/analyze`

**Request**:
```json
{
  "url": "https://example.com"
}
```

**Response**:
```json
{
  "scan_id": "6998bc978ec046b091a95b22",
  "url": "https://example.com",
  "website_score": 72.5,
  "status": "completed",
  "analysis_data": {
    "https_enabled": true,
    "mobile_friendly": true,
    "online_ordering_links_count": 2,
    "performance_score": 85,
    "seo_score": 78,
    "accessibility_score": 82
  },
  "recommendations": [
    {
      "category": "Performance",
      "priority": "high",
      "title": "Improve Website Speed",
      "description": "Your website performance score is 85/100..."
    }
  ],
  "created_at": "2026-02-20T19:57:11.258735"
}
```

#### 2. Scoring Logic
**File**: `backend/app/core/scoring.py`

Uses existing `RestaurantScorer.calculate_website_score()` method:
- **70%** - PageSpeed performance score
- **10%** - Mobile friendliness
- **10%** - Online ordering presence
- **10%** - SSL/HTTPS enabled

#### 3. Analysis Service
**File**: `backend/app/services/website_analyzer.py`

Reuses existing `WebsiteAnalyzer.analyze_website()` method which performs:
- PageSpeed Insights API call (performance, SEO, accessibility)
- Playwright browser analysis (HTTPS, mobile, ordering buttons)

#### 4. Database Storage
**Collection**: `scans`

**Document Structure**:
```json
{
  "_id": "6998bc978ec046b091a95b22",
  "type": "website_only",
  "url": "https://example.com",
  "status": "completed",
  "website_score": 72.5,
  "analysis_data": {...},
  "recommendations": [...],
  "created_at": "2026-02-20T19:57:11.258735",
  "completed_at": "2026-02-20T19:57:18.653000",
  "upgraded_to_full_scan": false
}
```

### Frontend Components

#### 1. SearchForm Component
**File**: `src/components/SearchForm.tsx`

**Features**:
- Mode toggle: "Full Restaurant Scan" vs "Quick Website Check"
- Separate form inputs for each mode
- Visual distinction with different button colors

#### 2. WebsiteResults Component
**File**: `src/components/WebsiteResults.tsx`

**Displays**:
- Overall website score (0-100) with color coding
- Key metrics: HTTPS, Mobile, Ordering status
- Prioritized recommendations list
- Upgrade CTA to full restaurant scan

#### 3. Index Page Integration
**File**: `src/pages/Index.tsx`

**New States**:
- `website-analyzing`: Loading state during analysis
- `website-results`: Display results

**New Handlers**:
- `handleQuickWebsiteCheck()`: Calls API and manages state
- `handleUpgradeToFullScan()`: Converts website-only to full scan

#### 4. API Service
**File**: `src/services/api.ts`

**New Method**:
```typescript
async analyzeWebsite(url: string): Promise<WebsiteAnalysisResponse>
```

#### 5. TypeScript Types
**File**: `src/types/api.ts`

**New Interfaces**:
- `WebsiteRecommendation`
- `WebsiteAnalysisRequest`
- `WebsiteAnalysisResponse`

## User Flow

### Quick Website Check Flow

1. **Landing Page**
   - User sees two options: "Full Restaurant Scan" or "Quick Website Check"
   - User clicks "Quick Website Check" toggle

2. **URL Entry**
   - User enters website URL (e.g., "yourrestaurant.com")
   - System auto-adds "https://" if missing
   - User clicks "Quick Check" button

3. **Analysis (2-7 seconds)**
   - Loading spinner with message: "Analyzing Your Website..."
   - Backend performs parallel analysis:
     - PageSpeed Insights API call
     - Playwright browser check

4. **Results Display**
   - Overall website score with visual indicator
   - Three key metrics: HTTPS, Mobile, Ordering
   - 3-5 prioritized recommendations
   - Upgrade CTA: "Get Your Full Restaurant Grade"

5. **Upgrade Path**
   - User clicks "Get Your Full Restaurant Grade"
   - System pre-fills restaurant data from website URL
   - Proceeds to confirmation screen for full scan

### Recommendation Generation Logic

**File**: `backend/app/routes/website.py` - `generate_recommendations()`

**Priority Levels**:
- **High**: Critical issues affecting security, mobile, or performance
- **Medium**: Important improvements for SEO and accessibility
- **Low**: Nice-to-have enhancements

**Categories**:
- Security (HTTPS)
- Mobile Experience
- Performance
- Online Ordering
- SEO
- Accessibility
- Customer Engagement

**Example Recommendations**:
```python
# High Priority - No HTTPS
{
  "category": "Security",
  "priority": "high",
  "title": "Enable HTTPS",
  "description": "Your website is not using HTTPS. Enable SSL/TLS..."
}

# Medium Priority - Low SEO Score
{
  "category": "SEO",
  "priority": "medium",
  "title": "Improve SEO",
  "description": "Your SEO score is 65/100. Optimize meta descriptions..."
}
```

## Performance Characteristics

### Response Times
- **Target**: 2-5 seconds
- **Actual**: 5-8 seconds (with test API key)
- **Bottlenecks**:
  - PageSpeed Insights API: 1-2 seconds
  - Playwright browser analysis: 3-5 seconds

### Optimization Opportunities
1. **Cache PageSpeed results** for 24 hours
2. **Parallel execution** (already implemented)
3. **Timeout handling** for slow websites
4. **Fallback to basic checks** if PageSpeed fails

## Database Analytics

### Tracking Metrics
- Total website-only scans
- Conversion rate to full scans (`upgraded_to_full_scan` field)
- Most common recommendations
- Average website scores by industry
- Time to complete analysis

### Sample Queries

**Count website-only scans**:
```javascript
db.scans.countDocuments({ type: "website_only" })
```

**Conversion rate**:
```javascript
db.scans.aggregate([
  { $match: { type: "website_only" } },
  { $group: {
    _id: null,
    total: { $sum: 1 },
    upgraded: { $sum: { $cond: ["$upgraded_to_full_scan", 1, 0] } }
  }}
])
```

**Average website score**:
```javascript
db.scans.aggregate([
  { $match: { type: "website_only", status: "completed" } },
  { $group: { _id: null, avgScore: { $avg: "$website_score" } } }
])
```

## Testing

### Manual Testing
1. Visit http://localhost:5173
2. Click "Quick Website Check" toggle
3. Enter URL: "chipotle.com"
4. Click "Quick Check"
5. Verify results display within 10 seconds
6. Check recommendations are relevant
7. Click "Get Your Full Restaurant Grade"
8. Verify upgrade flow works

### API Testing
```bash
# Test website analysis endpoint
curl -X POST http://localhost:8000/api/website/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.chipotle.com"}'

# Expected: 200 OK with analysis results
```

### Error Handling
- Invalid URL format → 422 Validation Error
- Website unreachable → Returns partial results with recommendations
- PageSpeed API failure → Falls back to Playwright-only analysis
- Timeout → Returns error after 30 seconds

## Future Enhancements

### Phase 2
- [ ] Email results to user
- [ ] Compare with competitors
- [ ] Historical tracking (re-scan same URL)
- [ ] PDF report generation
- [ ] Social sharing of score

### Phase 3
- [ ] Scheduled monitoring
- [ ] Alerts for score drops
- [ ] White-label for agencies
- [ ] API access for integrations

## Configuration

### Environment Variables
```bash
# Required
MONGODB_URL=mongodb://localhost:27017
PAGESPEED_API_KEY=your_api_key_here

# Optional
WEBSITE_ANALYSIS_TIMEOUT=30000  # milliseconds
BROWSER_HEADLESS=true
```

### Feature Flags
Currently no feature flags. To disable:
1. Remove route registration in `backend/app/main.py`
2. Hide "Quick Website Check" toggle in `SearchForm.tsx`

## Troubleshooting

### Issue: PageSpeed API returns 400 error
**Cause**: Invalid or missing API key
**Solution**: Set valid `PAGESPEED_API_KEY` in `.env`

### Issue: Playwright timeout
**Cause**: Website takes too long to load
**Solution**: Increase timeout in `BrowserManager` or skip slow sites

### Issue: Score always 0
**Cause**: Both PageSpeed and Playwright failing
**Solution**: Check logs, verify website is accessible

### Issue: Frontend not showing results
**Cause**: CORS or API connection issue
**Solution**: Verify backend is running on port 8000

## Success Metrics

### KPIs to Track
1. **Adoption Rate**: % of users choosing website-only vs full scan
2. **Conversion Rate**: % upgrading to full scan
3. **Completion Rate**: % of analyses that complete successfully
4. **Average Score**: Benchmark for restaurant websites
5. **Time to Result**: Average response time

### Target Goals
- 30% of users start with website-only check
- 40% conversion rate to full scan
- 95% completion rate
- < 5 second average response time

## Maintenance

### Regular Tasks
- Monitor API error rates
- Review recommendation relevance
- Update scoring weights based on data
- Optimize slow queries
- Clean up old scan records (> 90 days)

### Dependencies
- Playwright (browser automation)
- PageSpeed Insights API
- MongoDB (data storage)
- FastAPI (backend framework)
- React (frontend framework)

## Support

For issues or questions:
- Check logs in `backend/app/routes/website.py`
- Review browser console for frontend errors
- Test API endpoint directly with curl
- Verify MongoDB connection and data

---

**Last Updated**: 2026-02-20
**Version**: 1.0.0
**Status**: ✅ Implemented and Tested
