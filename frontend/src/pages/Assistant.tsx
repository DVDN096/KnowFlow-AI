
import { useState, type FormEvent } from "react";
import {
  Send,
  Bot,
  User,
  FileText,
  Clock3,
  Database,
  Sparkles,
  Plus,
  Loader2,
  AlertCircle,
  Settings2,
} from "lucide-react";

import {
  askQuestion,
  type AskResponse,
} from "../lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: AskResponse["sources"];
  timings?: AskResponse["timings"];
}

export default function Assistant() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previous) => [...previous, userMessage]);
    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const response = await askQuestion(trimmedQuestion, topK);

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        timings: response.timings,
      };

      setMessages((previous) => [...previous, assistantMessage]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate an answer. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  function startNewChat() {
    if (loading) return;

    setMessages([]);
    setQuestion("");
    setError("");
  }

  function formatSeconds(value: number) {
    return `${value.toFixed(2)}s`;
  }

  return (
    <div className="flex min-h-[calc(100vh-140px)] flex-col">

      {/* Header */}
      <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm text-slate-500">
            <span>Workspace</span>
            <span>/</span>
            <span className="font-medium text-violet-600">
              AI Assistant
            </span>
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            AI Assistant
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Ask questions and discover insights from your engineering documents.
          </p>
        </div>

        <button
          onClick={startNewChat}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
        >
          <Plus size={17} />
          New conversation
        </button>
      </div>

      {/* Chat container */}
      <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

        {/* Chat toolbar */}
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-100 text-violet-700">
              <Bot size={22} />
            </div>

            <div>
              <p className="text-sm font-semibold text-slate-900">
                KnowFlow Intelligence
              </p>
              <p className="flex items-center gap-1.5 text-xs text-emerald-600">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                RAG-powered assistant
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2">
            <Settings2 size={15} className="text-slate-500" />
            <label htmlFor="top-k" className="text-xs text-slate-500">
              Retrieval depth
            </label>

            <select
              id="top-k"
              value={topK}
              onChange={(event) => setTopK(Number(event.target.value))}
              disabled={loading}
              className="bg-transparent text-sm font-semibold text-slate-800 outline-none"
            >
              {[3, 5, 8, 10, 15, 20].map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 space-y-6 overflow-y-auto bg-slate-50/60 p-5 sm:p-8">

          {messages.length === 0 ? (
            <div className="flex min-h-[420px] flex-col items-center justify-center text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-100 text-violet-700">
                <Sparkles size={30} />
              </div>

              <h2 className="mt-6 text-xl font-semibold text-slate-900">
                What would you like to know?
              </h2>

              <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                Ask questions about your uploaded engineering documents.
                KnowFlow retrieves relevant information and generates grounded answers.
              </p>

              <div className="mt-8 grid w-full max-w-2xl grid-cols-1 gap-3 sm:grid-cols-2">
                {[
                  "Where should temperature sensors be placed in a data center?",
                  "What is the purpose of hot-aisle and cold-aisle containment?",
                  "How does object detection work?",
                  "Explain the attention mechanism in Transformers.",
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setQuestion(suggestion)}
                    className="rounded-xl border border-slate-200 bg-white p-4 text-left text-sm text-slate-600 transition hover:border-violet-300 hover:bg-violet-50/50 hover:text-violet-700"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === "user"
                    ? "flex-row-reverse"
                    : "flex-row"
                }`}
              >
                <div
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${
                    message.role === "user"
                      ? "bg-slate-200 text-slate-700"
                      : "bg-violet-100 text-violet-700"
                  }`}
                >
                  {message.role === "user" ? (
                    <User size={18} />
                  ) : (
                    <Bot size={19} />
                  )}
                </div>

                <div
                  className={`min-w-0 max-w-[85%] ${
                    message.role === "user" ? "text-right" : ""
                  }`}
                >
                  <p className="mb-2 text-xs font-semibold text-slate-500">
                    {message.role === "user" ? "You" : "KnowFlow AI"}
                  </p>

                  <div
                    className={`rounded-2xl p-4 text-sm leading-7 ${
                      message.role === "user"
                        ? "bg-violet-600 text-white"
                        : "border border-slate-200 bg-white text-slate-700 shadow-sm"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>

                  {message.role === "assistant" &&
                    message.sources &&
                    message.sources.length > 0 && (
                      <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4 text-left">
                        <div className="mb-3 flex items-center gap-2">
                          <Database size={16} className="text-violet-600" />
                          <p className="text-xs font-semibold text-slate-800">
                            Retrieved sources ({message.sources.length})
                          </p>
                        </div>

                        <div className="space-y-2">
                          {message.sources.map((source, index) => (
                            <div
                              key={`${source.source}-${source.page_number}-${source.chunk_index}-${index}`}
                              className="flex items-start gap-3 rounded-lg bg-slate-50 p-3"
                            >
                              <div className="rounded-lg bg-violet-100 p-2 text-violet-600">
                                <FileText size={16} />
                              </div>

                              <div className="min-w-0 flex-1">
                                <p className="break-all text-xs font-semibold text-slate-700">
                                  {source.source}
                                </p>
                                <p className="mt-1 text-xs text-slate-500">
                                  Page {source.page_number} · Chunk {source.chunk_index}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                  {message.timings && (
                    <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-400">
                      <span className="flex items-center gap-1">
                        <Clock3 size={13} />
                        Retrieval: {formatSeconds(message.timings.retrieval_seconds)}
                      </span>
                      <span>
                        Generation: {formatSeconds(message.timings.generation_seconds)}
                      </span>
                      <span>
                        Total: {formatSeconds(message.timings.total_seconds)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="flex gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-100 text-violet-700">
                <Bot size={19} />
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Loader2 size={17} className="animate-spin text-violet-600" />
                  Searching documents and generating an answer...
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mx-5 mb-3 flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3">
            <AlertCircle size={17} className="mt-0.5 shrink-0 text-rose-600" />
            <p className="text-sm text-rose-700">{error}</p>
          </div>
        )}

        {/* Input */}
        <form
          onSubmit={handleSubmit}
          className="border-t border-slate-100 bg-white p-4 sm:p-5"
        >
          <div className="flex items-end gap-3 rounded-xl border border-slate-200 bg-slate-50 p-2 transition focus-within:border-violet-400 focus-within:ring-2 focus-within:ring-violet-100">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  event.currentTarget.form?.requestSubmit();
                }
              }}
              placeholder="Ask anything about your engineering documents..."
              rows={2}
              disabled={loading}
              className="max-h-36 min-h-12 flex-1 resize-y bg-transparent px-3 py-2 text-sm text-slate-800 outline-none placeholder:text-slate-400 disabled:opacity-50"
            />

            <button
              type="submit"
              disabled={!question.trim() || loading}
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-violet-600 text-white shadow-sm transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-40"
              aria-label="Send message"
            >
              {loading ? (
                <Loader2 size={19} className="animate-spin" />
              ) : (
                <Send size={19} />
              )}
            </button>
          </div>

          <div className="mt-3 flex flex-col justify-between gap-2 px-1 sm:flex-row sm:items-center">
            <p className="text-xs text-slate-400">
              Enter to send · Shift + Enter for a new line
            </p>
            <p className="text-xs text-slate-400">
              Responses are grounded in retrieved document context.
            </p>
          </div>
        </form>
      </div>

      <p className="mt-4 text-center text-xs text-slate-400">
        KnowFlow AI · Engineering Knowledge Intelligence Platform
      </p>
    </div>
  );
}
