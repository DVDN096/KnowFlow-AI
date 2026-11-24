
import { useEffect, useState } from "react";
import {
  FileText,
  Database,
  CheckCircle2,
  AlertCircle,
  Upload,
  ArrowUpRight,
  Clock3,
  RefreshCw,
  BrainCircuit,
  Files,
} from "lucide-react";

import { getDocuments, type Document } from "../lib/api";

export default function Dashboard() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard() {
    try {
      setError("");
      setLoading(true);

      const data = await getDocuments();

      setDocuments(data.documents);
      setTotal(data.total);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load dashboard data."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const totalChunks = documents.reduce(
    (sum, document) => sum + document.chunk_count,
    0
  );

  const completed = documents.filter(
    (document) => document.status === "completed"
  ).length;

  const failed = documents.filter(
    (document) => document.status === "failed"
  ).length;

  const processing = documents.filter(
    (document) =>
      document.status === "processing" ||
      document.status === "pending"
  ).length;

  const stats = [
    {
      label: "Total Documents",
      value: total,
      icon: Files,
      description: "Documents in your workspace",
      iconStyle: "bg-violet-50 text-violet-600",
    },
    {
      label: "Total Chunks",
      value: totalChunks,
      icon: Database,
      description: "Knowledge units indexed",
      iconStyle: "bg-blue-50 text-blue-600",
    },
    {
      label: "Successfully Processed",
      value: completed,
      icon: CheckCircle2,
      description: "Documents ready for retrieval",
      iconStyle: "bg-emerald-50 text-emerald-600",
    },
    {
      label: "Failed Documents",
      value: failed,
      icon: AlertCircle,
      description: "Documents requiring attention",
      iconStyle: "bg-rose-50 text-rose-600",
    },
  ];

  function formatDate(date: string) {
    return new Date(date).toLocaleString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

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

  return (
    <div className="space-y-8">

      {/* Page heading */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm text-slate-500">
            <span>Workspace</span>
            <span>/</span>
            <span className="font-medium text-violet-600">Overview</span>
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Dashboard
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Monitor your engineering knowledge and ingestion activity.
          </p>
        </div>

        <button
          onClick={loadDashboard}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
        >
          <RefreshCw
            size={16}
            className={loading ? "animate-spin" : ""}
          />
          Refresh
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4">
          <AlertCircle className="mt-0.5 text-rose-600" size={20} />
          <div className="flex-1">
            <p className="font-semibold text-rose-800">
              Unable to load dashboard
            </p>
            <p className="mt-1 text-sm text-rose-700">{error}</p>
            <button
              onClick={loadDashboard}
              className="mt-2 text-sm font-semibold text-rose-800 underline"
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;

          return (
            <div
              key={stat.label}
              className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="flex items-center justify-between">
                <div className={`rounded-xl p-3 ${stat.iconStyle}`}>
                  <Icon size={21} />
                </div>

                <ArrowUpRight size={17} className="text-slate-300" />
              </div>

              <p className="mt-5 text-sm font-medium text-slate-500">
                {stat.label}
              </p>

              <div className="mt-1">
                {loading ? (
                  <div className="h-9 w-16 animate-pulse rounded-lg bg-slate-100" />
                ) : (
                  <p className="text-3xl font-bold tracking-tight text-slate-900">
                    {error ? "—" : stat.value.toLocaleString("en-IN")}
                  </p>
                )}
              </div>

              <p className="mt-2 text-xs text-slate-400">
                {stat.description}
              </p>
            </div>
          );
        })}
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">

        {/* Documents table */}
        <div className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm xl:col-span-2">
          <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5">
            <div>
              <h2 className="font-semibold text-slate-900">
                Recent Documents
              </h2>
              <p className="mt-1 text-xs text-slate-500">
                Your recently ingested engineering documents
              </p>
            </div>

            <div className="rounded-lg bg-violet-50 p-2 text-violet-600">
              <FileText size={19} />
            </div>
          </div>

          {loading ? (
            <div className="space-y-4 p-6">
              {[1, 2, 3].map((item) => (
                <div
                  key={item}
                  className="h-12 animate-pulse rounded-lg bg-slate-100"
                />
              ))}
            </div>
          ) : error ? (
            <div className="p-8 text-center text-sm text-slate-500">
              Document information is currently unavailable.
            </div>
          ) : documents.length === 0 ? (
            <div className="p-12 text-center">
              <Files className="mx-auto text-slate-300" size={36} />
              <p className="mt-3 font-medium text-slate-700">
                No documents yet
              </p>
              <p className="mt-1 text-sm text-slate-500">
                Upload your first engineering PDF to get started.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-slate-50/80 text-xs uppercase tracking-wider text-slate-400">
                    <th className="px-6 py-3 font-semibold">Document</th>
                    <th className="px-6 py-3 font-semibold">Chunks</th>
                    <th className="px-6 py-3 font-semibold">Status</th>
                    <th className="px-6 py-3 font-semibold">Added</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {documents.map((document) => (
                    <tr
                      key={document.id}
                      className="transition hover:bg-slate-50/70"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="rounded-lg bg-violet-50 p-2 text-violet-600">
                            <FileText size={18} />
                          </div>
                          <div>
                            <p className="max-w-[190px] truncate text-sm font-semibold text-slate-800">
                              {document.filename}
                            </p>
                            <p className="mt-0.5 text-xs text-slate-400">
                              {document.file_type.toUpperCase().replace(".", "")}
                            </p>
                          </div>
                        </div>
                      </td>

                      <td className="px-6 py-4 text-sm font-medium text-slate-700">
                        {document.chunk_count}
                      </td>

                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${statusStyle(document.status)}`}
                        >
                          {document.status}
                        </span>
                      </td>

                      <td className="whitespace-nowrap px-6 py-4 text-xs text-slate-500">
                        {formatDate(document.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="flex items-center justify-between border-t border-slate-100 px-6 py-4">
            <span className="text-xs text-slate-500">
              Showing {loading || error ? "—" : documents.length} of {loading || error ? "—" : total} documents
            </span>

            <span className="text-xs font-medium text-violet-600">
              Live API data
            </span>
          </div>
        </div>

        {/* Knowledge base summary */}
        <div className="space-y-6">

          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-violet-50 p-3 text-violet-600">
                <BrainCircuit size={22} />
              </div>
              <div>
                <h2 className="font-semibold text-slate-900">
                  Knowledge Base
                </h2>
                <p className="text-xs text-slate-500">
                  Workspace health
                </p>
              </div>
            </div>

            <div className="mt-7">
              <div className="mb-2 flex justify-between text-sm">
                <span className="text-slate-500">Processing success</span>
                <span className="font-semibold text-slate-800">
                  {loading || error || total === 0
                    ? "—"
                    : `${Math.round((completed / total) * 100)}%`}
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-violet-600 transition-all"
                  style={{
                    width: `${total > 0 ? (completed / total) * 100 : 0}%`,
                  }}
                />
              </div>
            </div>

            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <CheckCircle2 size={16} className="text-emerald-500" />
                  Completed
                </div>
                <span className="text-sm font-semibold text-slate-800">
                  {loading || error ? "—" : completed}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <Clock3 size={16} className="text-amber-500" />
                  Pending / Processing
                </div>
                <span className="text-sm font-semibold text-slate-800">
                  {loading || error ? "—" : processing}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <AlertCircle size={16} className="text-rose-500" />
                  Failed
                </div>
                <span className="text-sm font-semibold text-slate-800">
                  {loading || error ? "—" : failed}
                </span>
              </div>
            </div>
          </div>

          {/* Upload callout */}
          <div className="overflow-hidden rounded-2xl bg-gradient-to-br from-violet-700 to-indigo-800 p-6 text-white shadow-lg shadow-violet-200/50">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/15">
              <Upload size={22} />
            </div>

            <h2 className="mt-5 text-lg font-semibold">
              Expand your knowledge
            </h2>

            <p className="mt-2 text-sm leading-6 text-violet-100">
              Add engineering documents to build a searchable knowledge base for your team.
            </p>

            <p className="mt-5 flex items-center gap-2 text-sm font-semibold text-white">
              Open Knowledge Base
              <ArrowUpRight size={16} />
            </p>
          </div>
        </div>
      </div>

      <p className="text-center text-xs text-slate-400">
        KnowFlow AI · Engineering Knowledge Intelligence Platform
      </p>
    </div>
  );
}
