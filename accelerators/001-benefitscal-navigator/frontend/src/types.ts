export interface Citation {
  source: string;
  text: string;
  policy_ref?: string;
  url?: string;
}

export interface ProgramInfo {
  program_id: string;
  name: string;
  description: string;
  agency: string;
  requirements: string[];
  documents_needed: string[];
}

export interface EligibilityResult {
  program: string;
  likely_eligible: boolean;
  confidence: number;
  factors: string[];
  next_steps: string[];
}

export interface ChatRequest {
  message: string;
  language?: string;
  session_id?: string;
  county?: string;
}

export interface ChatResponse {
  response: string;
  confidence: number;
  citations: Citation[];
  programs?: ProgramInfo[];
  eligibility?: EligibilityResult;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  citations?: Citation[];
  programs?: ProgramInfo[];
  eligibility?: EligibilityResult;
  confidence?: number;
}
