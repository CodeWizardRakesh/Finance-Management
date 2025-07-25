export interface Message {
  id: string;
  type: 'user' | 'advisor';
  content: string;
  timestamp: Date;
}

export interface ApiResponse {
  advisor_response: string;
  web_links: string;
  manager_response: any;
}

export interface ApiRequest {
  query: string;
}