/**
 * Wire transfer type definitions
 */

export enum WireStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface Wire {
  id: number;
  sender_name: string;
  recipient_name: string;
  amount: number;
  currency: string;
  status: WireStatus;
  reference_number: string;
  created_by: number;
  created_at: string;
  updated_at: string | null;
}

export interface WireCreate {
  sender_name: string;
  recipient_name: string;
  amount: number;
  currency: string;
}

export interface WireUpdate {
  sender_name?: string;
  recipient_name?: string;
  amount?: number;
  currency?: string;
  status?: WireStatus;
}

export interface WireListResponse {
  wires: Wire[];
  total: number;
  page: number;
  page_size: number;
  cached: boolean;
}

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
