// Minimal types for Priority 1 - just the plumbing
export interface ScanResponse {
  _id: string;
  restaurant_name: string;
  restaurant_website: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  overall_score?: number;
  error_message?: string;
  created_at?: string;
  completed_at?: string;
}

export interface CreateScanRequest {
  restaurant_name: string;
  restaurant_website: string;
}

export interface CreateScanResponse {
  scan_id: string;
  message: string;
}

// Website-only analysis types
export interface WebsiteRecommendation {
  category: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
}

export interface WebsiteAnalysisRequest {
  url: string;
}

export interface WebsiteAnalysisResponse {
  scan_id: string;
  url: string;
  website_score: number;
  status: string;
  analysis_data: Record<string, any>;
  recommendations: WebsiteRecommendation[];
  created_at: string;
}
