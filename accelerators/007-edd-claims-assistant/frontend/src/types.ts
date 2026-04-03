export interface Citation {
  source: string;
  text: string;
  policy_ref?: string;
}

export interface ClaimStatus {
  claim_id: string;
  claim_type: string;
  status: string;
  filed_date: string;
  last_certified?: string;
  weekly_benefit_amount: number;
  remaining_balance: number;
  pending_issues: string[];
  next_payment_date?: string;
}

export interface EligibilityAssessment {
  claim_type: string;
  likely_eligible: boolean;
  confidence: number;
  factors: string[];
  requirements: string[];
  next_steps: string[];
}

export interface DocumentItem {
  name: string;
  required: boolean;
  submitted: boolean;
  description: string;
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
  claim_status?: ClaimStatus;
  eligibility?: EligibilityAssessment;
  document_checklist?: DocumentItem[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  citations?: Citation[];
  claim_status?: ClaimStatus;
  eligibility?: EligibilityAssessment;
  document_checklist?: DocumentItem[];
  confidence?: number;
}
