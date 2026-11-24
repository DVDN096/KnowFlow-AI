
const API_BASE_URL = "https://knowflow-ai-9exa.onrender.com/api/v1";

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
  chunk_count: number;
}

export interface DocumentsResponse {
  total: number;
  documents: Document[];
}

export interface UploadResponse {
  message: string;
  document_id: number;
  filename: string;
  chunks_saved: number;
  status: string;
}

export interface DeleteResponse {
  message: string;
  document_id: number;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    const detail = errorData?.detail;

    const message =
      typeof detail === "string"
        ? detail
        : detail?.message || `Request failed (${response.status})`;

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

// Fetch all documents
export async function getDocuments(): Promise<DocumentsResponse> {
  const response = await fetch(`${API_BASE_URL}/documents`);
  return handleResponse<DocumentsResponse>(response);
}

// Fetch individual document details
export async function getDocument(id: number) {
  const response = await fetch(`${API_BASE_URL}/documents/${id}`);
  return handleResponse<unknown>(response);
}

// Upload a PDF document
export async function uploadDocument(
  file: File
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<UploadResponse>(response);
}

// Delete a document and its associated chunks
export async function deleteDocument(
  id: number
): Promise<DeleteResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
    method: "DELETE",
  });

  return handleResponse<DeleteResponse>(response);
}


export interface AskRequest {
  question: string;
  top_k: number;
}

export interface AnswerSource {
  source: string;
  page_number: number;
  chunk_index: number;
}

export interface AnswerTimings {
  retrieval_seconds: number;
  generation_seconds: number;
  total_seconds: number;
}

export interface AskResponse {
  answer: string;
  sources: AnswerSource[];
  timings: AnswerTimings;
}

export async function askQuestion(
  question: string,
  top_k: number = 5
): Promise<AskResponse> {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      top_k,
    }),
  });

  return handleResponse<AskResponse>(response);
}
