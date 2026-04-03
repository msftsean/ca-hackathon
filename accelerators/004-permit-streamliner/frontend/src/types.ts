export interface Citation {
  source: string;
  text: string;
  policy_ref?: string;
  url?: string;
}

export interface ChatRequest {
  message: string;
  language?: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  confidence: number;
  citations: Citation[];
  data?: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  citations?: Citation[];
  confidence?: number;
  data?: Record<string, unknown>;
}

export interface PermitApplication {
  app_id: string;
  applicant_name: string;
  project_type: string;
  project_description: string;
  address: string;
  status: string;
  submitted_at?: string;
  estimated_completion?: string;
}

export interface ZoningResult {
  address: string;
  zone_code: string;
  zone_name: string;
  permitted_uses: string[];
  conditional_uses: string[];
  setbacks: Record<string, number>;
  max_height_ft: number;
  lot_coverage_pct: number;
  compliant: boolean;
  issues: string[];
}
