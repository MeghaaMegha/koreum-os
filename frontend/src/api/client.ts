import axios from "axios";

const API_BASE = "/api/v1";

const client = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT to every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("koreum_access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401, clear tokens and redirect to login
client.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("koreum_access_token");
      localStorage.removeItem("koreum_refresh_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export interface MeResponse {
  id: string;
  email: string;
  full_name: string;
  tenant_id: string;
  roles: string[];
  permissions: string[];
  is_active: boolean;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  roles: { id: string; name: string; permissions: string[] }[];
  created_at: string;
}

export interface AuditEvent {
  id: string;
  action: string;
  details: Record<string, unknown> | null;
  created_at: string;
  actor_user_id: string | null;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
}

export interface Document {
  id: string;
  tenant_id: string;
  uploaded_by: string | null;
  title: string;
  filename: string;
  content_type: string;
  file_size: number;
  status: string;
  created_at: string;
  metadata_: Record<string, unknown> | null;
}

export interface SearchHit {
  chunk_id: string;
  document_id: string;
  document_title: string;
  content: string;
  chunk_index: number;
  score: number;
}

export interface SearchResponse {
  query: string;
  total: number;
  hits: SearchHit[];
}

export const api = {
  login: (email: string, password: string) =>
    client.post("/auth/login", "email=" + encodeURIComponent(email) + "&password=" + encodeURIComponent(password), {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    }),
  me: () => client.get<MeResponse>("/auth/me"),
  listUsers: () => client.get<User[]>("/users"),
  createUser: (data: { email: string; full_name: string; password: string; role_names: string[] }) =>
    client.post<User>("/users", data),
  updateUser: (userId: string, data: { email?: string; full_name?: string; is_active?: boolean; role_names?: string[] }) =>
    client.patch<User>(`/users/${userId}`, data),
  deactivateUser: (userId: string) => client.delete(`/users/${userId}`),
  listAudit: () => client.get<{ items: AuditEvent[]; total: number }>("/audit?limit=100"),
  listTenants: () => client.get<Tenant[]>("/tenants"),
  health: () => client.get("/health"),

  // Vault
  listDocuments: () => client.get<Document[]>("/vault/documents"),
  uploadDocument: (file: File, title: string) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    return client.post<Document>("/vault/documents", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  deleteDocument: (id: string) => client.delete(`/vault/documents/${id}`),
  searchDocuments: (query: string) =>
    client.post<SearchResponse>("/vault/documents/search", null, { params: { query } }),
};

export default client;
