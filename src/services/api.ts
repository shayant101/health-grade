import { CreateScanResponse, ScanResponse, WebsiteAnalysisResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  /**
   * Create a new restaurant scan
   * Returns scan_id immediately, scan runs in background
   */
  async createScan(restaurantName: string, restaurantWebsite: string): Promise<CreateScanResponse> {
    const response = await fetch(`${API_BASE_URL}/api/scans/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        restaurant_name: restaurantName,
        restaurant_website: restaurantWebsite
      })
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create scan' }));
      throw new Error(error.detail || 'Failed to create scan');
    }
    
    return response.json();
  },

  /**
   * Get scan status and results by ID
   * Poll this endpoint to track scan progress
   */
  async getScan(scanId: string): Promise<ScanResponse> {
    const response = await fetch(`${API_BASE_URL}/api/scans/${scanId}`);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch scan' }));
      throw new Error(error.detail || 'Failed to fetch scan');
    }
    
    return response.json();
  },

  /**
   * Analyze website only (fast, 2-5 seconds)
   * Returns immediate results without full restaurant scan
   */
  async analyzeWebsite(url: string): Promise<WebsiteAnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/api/website/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to analyze website' }));
      throw new Error(error.detail || 'Failed to analyze website');
    }
    
    return response.json();
  }
};
