export interface Citation {
  source: string;
  text: string;
  agency?: string;
  document_id?: string;
}

export interface DocumentResult {
  doc_id: string;
  title: string;
  agency: string;
  department: string;
  document_type: string;
  summary: string;
  relevance_score: number;
  last_updated: string;
  access_level: string;
}

export interface CrossReference {
  source_doc_id: string;
  target_doc_id: string;
  relationship: string;
  description: string;
}

export interface ExpertInfo {
  expert_id: string;
  name: string;
  agency: string;
  department: string;
  expertise_areas: string[];
  email: string;
  available: boolean;
}

export interface ChatRequest {
  message: string;
  language?: string;
  session_id?: string;
  agency_filter?: string[];
  document_types?: string[];
}

export interface ChatResponse {
  response: string;
  confidence: number;
  citations: Citation[];
  documents?: DocumentResult[];
  experts?: ExpertInfo[];
  cross_references?: CrossReference[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  citations?: Citation[];
  documents?: DocumentResult[];
  experts?: ExpertInfo[];
  cross_references?: CrossReference[];
  confidence?: number;
}
