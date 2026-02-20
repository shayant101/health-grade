# PageSpeed API Integration Documentation

## Overview

The PageSpeed API has been successfully integrated into the Restaurant Grader application to provide comprehensive website performance analysis. This integration enhances the website scoring system with real-world performance metrics from Google's Lighthouse.

## Implementation Date
February 20, 2026

## Features

### 1. Comprehensive Performance Metrics

The PageSpeed API provides four key categories of analysis:

- **Performance Score (0-100)**: Measures loading speed, interactivity, and visual stability
- **Accessibility Score (0-100)**: Evaluates how accessible the website is to all users
- **Best Practices Score (0-100)**: Checks adherence to web development best practices
- **SEO Score (0-100)**: Assesses search engine optimization quality

### 2. Enhanced Website Scoring Algorithm

The website score calculation now incorporates all PageSpeed metrics with intelligent weighting:

```python
# Weighted PageSpeed composite score (60% of total)
pagespeed_composite = (
    performance_score * 0.40 +      # 40% - Performance is most important
    accessibility_score * 0.25 +    # 25% - Accessibility matters for all users
    seo_score * 0.20 +              # 20% - SEO helps discoverability
    best_practices_score * 0.15     # 15% - Best practices for quality
)

# Total website score
total_score = (
    pagespeed_composite * 0.60 +    # 60% - PageSpeed metrics
    mobile_friendly_score * 0.15 +  # 15% - Mobile friendliness
    ssl_score * 0.15 +              # 15% - HTTPS security
    online_ordering_score * 0.10    # 10% - Online ordering capability
)
```

### 3. Intelligent Recommendations

The system generates actionable recommendations based on PageSpeed data:

- **Performance Issues**: Identifies slow loading times and suggests optimizations
- **Accessibility Problems**: Highlights accessibility concerns
- **SEO Improvements**: Recommends SEO enhancements
- **Best Practices**: Suggests modern web standards compliance

### 4. Graceful Degradation

If the PageSpeed API fails or times out:
- The system continues with Playwright-based analysis
- Scores are calculated using available data
- Users still receive valuable insights
- Errors are logged but don't break the analysis

## API Configuration

### Environment Variables

```bash
PAGESPEED_API_KEY=your_api_key_here
```

The API key is loaded from the `.env` file via the Pydantic settings system in `backend/app/config.py`.

### API Request Format

The system requests all four categories in a single API call:

```python
params = [
    ('url', url),
    ('key', settings.PAGESPEED_API_KEY),
    ('strategy', 'MOBILE'),  # or 'DESKTOP'
    ('category', 'PERFORMANCE'),
    ('category', 'ACCESSIBILITY'),
    ('category', 'BEST_PRACTICES'),
    ('category', 'SEO')
]
```

### Timeout Configuration

- **API Timeout**: 90 seconds (to handle slow websites)
- **Overall Analysis**: Typically completes in 15-35 seconds

## Response Format

### Website Analysis Response

```json
{
    "scan_id": "6998c6bd50d57ba14f4834f1",
    "url": "https://example-restaurant.com",
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
        "has_contact_form": false,
        "online_ordering_links_count": 9,
        "page_title": "Restaurant Name",
        "meta_description": "Restaurant description..."
    },
    "recommendations": [
        {
            "category": "Performance",
            "priority": "high",
            "title": "Reduce Page Load Time",
            "description": "Your page takes 5.5 seconds to become interactive..."
        }
    ],
    "created_at": "2026-02-20T20:40:29.120954"
}
```

## Testing Results

### Test Cases

Three real restaurant websites were tested successfully:

#### 1. Nizario's Pizza & Grill
- **URL**: https://nizariospizzaandgrill.com
- **Performance**: 64/100
- **Accessibility**: 86/100
- **Best Practices**: 92/100
- **SEO**: 100/100
- **Loading Time**: 5.5 seconds
- **Overall Score**: 55.36/100

#### 2. Burgertown USA
- **URL**: https://www.burgertownusa.net/
- **Performance**: 53/100
- **Accessibility**: 97/100
- **Best Practices**: 100/100
- **SEO**: 100/100
- **Loading Time**: 13.0 seconds
- **Overall Score**: 42.72/100

#### 3. Original Tommy's
- **URL**: https://originaltommys.com/
- **Performance**: 59/100
- **Accessibility**: 85/100
- **Best Practices**: 96/100
- **SEO**: 77/100
- **Loading Time**: 9.1 seconds
- **Overall Score**: 54.16/100

## Performance Considerations

### API Rate Limits

Google PageSpeed API has usage quotas:
- **Free tier**: 25,000 queries per day
- **Paid tier**: Higher limits available

### Optimization Strategies

1. **Caching**: Consider caching PageSpeed results for 24 hours
2. **Async Processing**: PageSpeed analysis runs in parallel with Playwright
3. **Timeout Handling**: 90-second timeout prevents indefinite waits
4. **Error Recovery**: Graceful degradation ensures service continuity

## Code Locations

### Key Files

- **API Integration**: `backend/app/services/website_analyzer.py`
- **Scoring Algorithm**: `backend/app/core/scoring.py`
- **Recommendations**: `backend/app/routes/website.py`
- **Configuration**: `backend/app/config.py`
- **Environment**: `backend/.env`

### Main Functions

```python
# PageSpeed API call
WebsiteAnalyzer._analyze_pagespeed(url, mobile=True)

# Website scoring
RestaurantScorer.calculate_website_score(website_data)

# Recommendation generation
generate_recommendations(analysis_data)
```

## Error Handling

### Common Errors

1. **Timeout**: Website takes too long to analyze
   - **Solution**: Increased timeout to 90 seconds
   - **Fallback**: Continue with Playwright data only

2. **Invalid API Key**: 400 Bad Request
   - **Solution**: Verify API key in `.env` file
   - **Fallback**: Return empty PageSpeed data

3. **Website Unreachable**: FAILED_DOCUMENT_REQUEST
   - **Solution**: Pre-check website availability
   - **Fallback**: Return 422 error to user

4. **Rate Limit Exceeded**: 429 Too Many Requests
   - **Solution**: Implement caching or upgrade API plan
   - **Fallback**: Continue with Playwright data

## Future Enhancements

### Potential Improvements

1. **Result Caching**: Cache PageSpeed results for 24 hours to reduce API calls
2. **Desktop Analysis**: Add option to analyze desktop version
3. **Historical Tracking**: Track performance changes over time
4. **Detailed Audits**: Extract and display specific Lighthouse audit results
5. **Performance Budgets**: Set performance targets and alert on violations
6. **Competitive Analysis**: Compare against industry benchmarks

## API Documentation

For more information about the PageSpeed API:
- **Official Docs**: https://developers.google.com/speed/docs/insights/v5/get-started
- **API Reference**: https://developers.google.com/speed/docs/insights/v5/reference
- **Lighthouse Scoring**: https://web.dev/performance-scoring/

## Support

For issues or questions about the PageSpeed integration:
1. Check the logs in `backend/app/utils/logger.py`
2. Verify API key configuration in `backend/.env`
3. Test API key with `backend/test_pagespeed_api.py`
4. Review error messages in the API response

## Changelog

### Version 1.0 (February 20, 2026)
- ✅ Initial PageSpeed API integration
- ✅ Multi-category analysis (Performance, Accessibility, Best Practices, SEO)
- ✅ Enhanced scoring algorithm with weighted metrics
- ✅ Intelligent recommendation generation
- ✅ Graceful error handling and degradation
- ✅ Comprehensive testing with real restaurant websites
- ✅ 90-second timeout for slow websites
- ✅ Parallel execution with Playwright analysis
