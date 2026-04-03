/** Shared TypeScript types matching backend schemas. */

export interface Citation {
  source: string;
  text: string;
  url?: string;
}

export interface EmergencyAlert {
  alert_id: string;
  title: string;
  description: string;
  severity: "extreme" | "severe" | "moderate" | "minor";
  emergency_type: string;
  affected_areas: string[];
  issued_at?: string;
  expires_at?: string;
  instructions: string;
  source: string;
}

export interface ShelterInfo {
  shelter_id: string;
  name: string;
  address: string;
  city: string;
  county: string;
  capacity: number;
  current_occupancy: number;
  accepts_pets: boolean;
  ada_accessible: boolean;
  status: string;
  distance_miles?: number;
}

export interface ChatRequest {
  message: string;
  language: string;
  session_id?: string;
  location?: string;
}

export interface ChatResponse {
  response: string;
  translated_response?: string;
  language: string;
  confidence: number;
  citations: Citation[];
  alerts?: EmergencyAlert[];
  shelters?: ShelterInfo[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  data?: ChatResponse;
  timestamp: Date;
}
