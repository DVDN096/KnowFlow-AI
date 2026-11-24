
import { useEffect, useRef, useState } from "react";
import {
  Upload,
  FileText,
  Search,
  Trash2,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Database,
  X,
  Files,
  Loader2,
} from "lucide-react";

import {
  getDocuments,
  uploadDocument,
  deleteDocument,
  type Document,
} from "../lib/api";

export default function KnowledgeBase() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  async function loadDocuments() {
    try {
      setError("");
      setLoading(true);

      const data = await getDocuments();
      setDocuments(data.documents);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to retrieve documents."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function handleUpload(file?: File) {
    if (!file) return;

    setError("");
    setSuccess("");

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.");
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setError("File exceeds the 20 MB upload limit.");
      return;
    }

    if (file.size === 0) {
      setError("The selected file is empty.");
      return;
    }

    try {
      setUploading(true);

      const result = await uploadDocument(file);

      setSuccess(
        `${result.filename} uploaded successfully. ${result.chunks_saved} chunks indexed.`
      );

      await loadDocuments();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Document upload failed."
      );
    } finally {
      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  async function handleDelete(document: Document) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${document.filename}"? This will also delete its associated chunks.`
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");

    try {
      setDeletingId(document.id);

      await deleteDocument(document.id);

      setDocuments((current) =>
        current.filter((item) => item.id !== document.id)
      );

      setSuccess(`${document.filename} was deleted successfully.`);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete document."
      );
    } finally {
      setDeletingId(null);
    }
  }

  const filteredDocuments = documents.filter((document) =>
    document.filename
      .toLowerCase()
      .includes(search.trim().toLowerCase())
  );

  const totalChunks = documents.reduce(
    (sum, document) => sum + document.chunk_count,
    0
  );

  const completed = documents.filter(
    (document) => document.status === "completed"
  ).length;

  function statusStyle(status: string) {
    switch (status) {
      case "completed":
        return "bg-emerald-50 text-emerald-700";
      case "processing":
        return "bg-blue-50 text-blue-700";
      case "pending":
        return "bg-amber-50 text-amber-700";
      case "failed":
        return "bg-rose-50 text-rose-700";
      default:
        return "bg-slate-100 text-slate-600";
    }
  }

  function formatDate(date: string) {
    return new Date(date).toLocaleString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  return (
    <div className="space-y-8">

      {/* Header */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm text-slate-500">
            <span>Workspace</span>
            <span>/</span>
            <span className="font-medium text-violet-600">
              Knowledge Base
            </span>
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Knowledge Base
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Upload, organize and manage your engineering knowledge.
          </p>
        </div>

        <button
          onClick={loadDocuments}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-50"
        >
          <RefreshCw
            size={16}
            className={loading ? "animate-spin" : ""}
          />
          Refresh
        </button>
      </div>

      {/* Alerts */}
      {error && (
        <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4">
          <AlertCircle size={19} className="mt-0.5 text-rose-600" />
          <p className="flex-1 text-sm text-rose-800">{error}</p>
          <button onClick={() => setError("")}>
            <X size={17} className="text-rose-500" />
          </button>
        </div>
      )}

      {success && (
        <div className="flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <CheckCircle2 size={19} className="mt-0.5 text-emerald-600" />
          <p className="flex-1 text-sm text-emerald-800">{success}</p>
          <button onClick={() => setSuccess("")}>
            <X size={17} className="text-emerald-500" />
          </button>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        {[
          {
            label: "Total Documents",
            value: documents.length,
            icon: Files,
            color: "bg-violet-50 text-violet-600",
          },
          {
            label: "Indexed Chunks",
            value: totalChunks,
            icon: Database,
            color: "bg-blue-50 text-blue-600",
          },
          {
            label: "Completed",
            value: completed,
            icon: CheckCircle2,
            color: "bg-emerald-50 text-emerald-600",
          },
        ].map((stat) => {
          const Icon = stat.icon;

          return (
            <div
              key={stat.label}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="flex items-center gap-3">
                <div className={`rounded-xl p-3 ${stat.color}`}>
                  <Icon size={21} />
                </div>
                <div>
                  <p className="text-sm text-slate-500">{stat.label}</p>
                  <p className="mt-1 text-2xl font-bold text-slate-900">
                    {loading ? "—" : stat.value.toLocaleString("en-IN")}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Upload area */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-5">
          <h2 className="font-semibold text-slate-900">
            Upload documents
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Add engineering PDFs to your knowledge base.
          </p>
        </div>

        <div
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={(event) => {
            event.preventDefault();
            setDragging(false);
          }}
          onDrop={(event) => {
            event.preventDefault();
            setDragging(false);

            if (!uploading) {
              handleUpload(event.dataTransfer.files[0]);
            }
          }}
          className={`rounded-xl border-2 border-dashed p-10 text-center transition ${
            dragging
              ? "border-violet-500 bg-violet-50"
              : "border-slate-200 bg-slate-50/70 hover:border-violet-300"
          }`}
        >
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-100 text-violet-600">
            <Upload size={26} />
          </div>

          <h3 className="mt-4 font-semibold text-slate-800">
            {dragging
              ? "Drop your PDF here"
              : "Drag and drop your PDF here"}
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            or select a file from your computer
          </p>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            className="hidden"
            onChange={(event) =>
              handleUpload(event.target.files?.[0])
            }
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="mt-5 inline-flex items-center gap-2 rounded-xl bg-violet-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-violet-700 disabled:opacity-50"
          >
            {uploading ? (
              <>
                <Loader2 size={17} className="animate-spin" />
                Processing document...
              </>
            ) : (
              <>
                <Upload size={17} />
                Browse files
              </>
            )}
          </button>

          <p className="mt-4 text-xs text-slate-400">
            PDF format only · Maximum file size 20 MB
          </p>
        </div>

        {uploading && (
          <div className="mt-4 flex items-center gap-3 rounded-xl bg-violet-50 p-4">
            <Loader2
              size={19}
              className="animate-spin text-violet-600"
            />
            <div>
              <p className="text-sm font-semibold text-violet-800">
                Processing your document
              </p>
              <p className="mt-1 text-xs text-violet-600">
                Extracting text, generating embeddings and indexing chunks.
                This may take a while.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Document list */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col justify-between gap-4 border-b border-slate-100 px-6 py-5 sm:flex-row sm:items-center">
          <div>
            <h2 className="font-semibold text-slate-900">
              All Documents
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Manage your uploaded engineering documents.
            </p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search
              size={17}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            />
            <input
              type="text"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search documents..."
              className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-100"
            />
          </div>
        </div>

        {loading ? (
          <div className="space-y-4 p-6">
            {[1, 2, 3].map((item) => (
              <div
                key={item}
                className="h-14 animate-pulse rounded-lg bg-slate-100"
              />
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center">
            <Files size={38} className="mx-auto text-slate-300" />
            <h3 className="mt-3 font-semibold text-slate-700">
              No documents found
            </h3>
            <p className="mt-1 text-sm text-slate-500">
              Upload your first engineering PDF to get started.
            </p>
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="p-10 text-center text-sm text-slate-500">
            No documents match "{search}".
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50 text-xs uppercase tracking-wider text-slate-400">
                  <th className="px-6 py-4 font-semibold">Document</th>
                  <th className="px-6 py-4 font-semibold">Chunks</th>
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold">Uploaded</th>
                  <th className="px-6 py-4 text-right font-semibold">
                    Actions
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100">
                {filteredDocuments.map((document) => (
                  <tr
                    key={document.id}
                    className="transition hover:bg-slate-50/70"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="rounded-lg bg-violet-50 p-2 text-violet-600">
                          <FileText size={19} />
                        </div>
                        <div>
                          <p className="max-w-[230px] truncate text-sm font-semibold text-slate-800">
                            {document.filename}
                          </p>
                          <p className="mt-1 text-xs text-slate-400">
                            Document ID: {document.id}
                          </p>
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4 text-sm font-medium text-slate-700">
                      {document.chunk_count}
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${statusStyle(document.status)}`}
                      >
                        {document.status}
                      </span>
                    </td>

                    <td className="whitespace-nowrap px-6 py-4 text-xs text-slate-500">
                      {formatDate(document.created_at)}
                    </td>

                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDelete(document)}
                        disabled={deletingId === document.id}
                        title="Delete document"
                        className="rounded-lg p-2 text-slate-400 transition hover:bg-rose-50 hover:text-rose-600 disabled:opacity-50"
                      >
                        {deletingId === document.id ? (
                          <Loader2 size={17} className="animate-spin" />
                        ) : (
                          <Trash2 size={17} />
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="border-t border-slate-100 px-6 py-4">
          <p className="text-xs text-slate-500">
            Showing {filteredDocuments.length} of {documents.length} documents
          </p>
        </div>
      </div>

      <p className="text-center text-xs text-slate-400">
        KnowFlow AI · Engineering Knowledge Intelligence Platform
      </p>
    </div>
  );
}
