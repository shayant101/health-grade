# Priority 1: The Plumbing - Test Guide

## Prerequisites
- ✅ Frontend running on `http://localhost:5173`
- ✅ Backend running on `http://localhost:8000`
- ✅ MongoDB connected

## Test Flow

### Step 1: Navigate to Frontend
1. Open browser to `http://localhost:5173`
2. Open browser DevTools Console (F12 → Console tab)
3. You should see the landing page with "How Healthy is Your Digital Presence?"

### Step 2: Enter Restaurant Information
1. In the search form, enter:
   - **Restaurant name**: `Chipotle`
   - **City**: `San Francisco`
2. Click "Check My Restaurant"
3. You should see the confirmation page

### Step 3: Verify Confirmation Page
1. Check that the page shows:
   - Restaurant name: "Chipotle"
   - Website: `https://www.thegoldenfork.com` (mock data for now)
   - Address and other mock details
2. Click "Yes, scan this restaurant"

### Step 4: Monitor Scan Creation
**Expected Console Output:**
```
✅ Scan created: 67abc123def456...
```

**What to verify:**
- [ ] Console shows "✅ Scan created: [scan_id]"
- [ ] Page transitions to scanning view
- [ ] Debug info box shows:
  - Status: pending
  - Progress: 10%
  - Scan ID: [the scan_id]

### Step 5: Monitor Polling
**Expected Console Output (every 2 seconds):**
```
🔄 Starting polling for scan: 67abc123def456...
📊 Scan status: pending Score: undefined
📊 Scan status: in_progress Score: undefined
📊 Scan status: in_progress Score: undefined
📊 Scan status: completed Score: 68
✅ Scan completed! Overall score: 68
🛑 Stopping polling
🎉 Scan complete callback received: { overall: 68, scanData: {...} }
```

**What to verify:**
- [ ] Console shows "🔄 Starting polling for scan: [id]"
- [ ] Console shows "📊 Scan status: pending"
- [ ] Status changes to "in_progress" (progress bar moves to ~50%)
- [ ] Status changes to "completed" (progress bar reaches 100%)
- [ ] Console shows "✅ Scan completed! Overall score: [number]"
- [ ] Console shows "🛑 Stopping polling"
- [ ] No more polling messages after completion

### Step 6: Verify Results Page
**What to verify:**
- [ ] Page transitions to results dashboard
- [ ] Blue debug banner shows:
  - "✅ Real Data: Overall Score = [number] (from MongoDB)"
  - "⚠️ Category scores still using mock data (Priority 2+)"
- [ ] Large score circle shows the real overall score
- [ ] Category cards show mock data (expected for Priority 1)
- [ ] Restaurant name is "Chipotle"

### Step 7: Verify MongoDB
1. Open MongoDB Compass or Atlas
2. Navigate to `restaurantgrader` database → `scans` collection
3. Find the scan by the scan_id from console
4. Verify:
   - [ ] `status` = "completed"
   - [ ] `overall_score` matches the UI
   - [ ] `restaurant_name` = "Chipotle"
   - [ ] `restaurant_website` = "https://www.thegoldenfork.com"
   - [ ] `created_at` and `completed_at` timestamps exist

### Step 8: Test React Strict Mode (No Duplicates)
1. Check MongoDB - there should be only ONE scan document for this test
2. If you see duplicate scans, the `hasCompletedRef` is not working

## Success Criteria Checklist

### ✅ The Plumbing Works
- [ ] Click "Confirm" creates scan in MongoDB
- [ ] Console shows scan_id
- [ ] Polling starts automatically
- [ ] Status updates: pending → in_progress → completed
- [ ] Polling stops when completed
- [ ] Overall score displays on results page
- [ ] Real score matches MongoDB document
- [ ] No duplicate scans (React Strict Mode handled)
- [ ] Category scores still show mock data (expected)

### ✅ Console Logs Confirm
- [ ] "✅ Scan created: [id]"
- [ ] "🔄 Starting polling for scan: [id]"
- [ ] "📊 Scan status: [status]"
- [ ] "✅ Scan completed! Overall score: [score]"
- [ ] "🛑 Stopping polling"

### ✅ Database Verification
- [ ] Scan document exists in MongoDB
- [ ] Status = "completed"
- [ ] overall_score has value
- [ ] Timestamps are correct

## Troubleshooting

### Issue: "Failed to create scan"
- Check backend is running on port 8000
- Check `.env` has `VITE_API_URL=http://localhost:8000`
- Check browser console for CORS errors

### Issue: Polling never completes
- Check backend logs for errors
- Check MongoDB connection
- Verify Celery worker is running (if using Celery)
- Check scan status in MongoDB manually

### Issue: Score shows as 0 or undefined
- Check MongoDB document has `overall_score` field
- Check backend scoring logic is working
- Verify website analysis completed successfully

### Issue: Duplicate scans in MongoDB
- This is a React Strict Mode issue
- Check `hasCompletedRef` in ScanProgress.tsx
- In production build, this won't happen

## Next Steps After Success

Once all tests pass:
1. Document the console output
2. Take screenshot of results page
3. Export MongoDB scan document
4. Move to Priority 2: Website Slice integration
