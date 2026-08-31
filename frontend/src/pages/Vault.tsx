import { useEffect, useState, useRef } from "react";
import { api } from "../api/client";
import type { Document, SearchHit } from "../api/client";

export default function Vault() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchMode, setSearchMode] = useState("hybrid");
  const [searchResults, setSearchResults] = useState<SearchHit[] | null>(null);
  const [searching, setSearching] = useState(false);
  const [confidence, setConfidence] = useState<number | null>(null);
  const [evidence, setEvidence] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    try {
      const res = await api.listDocuments();
      setDocuments(res.data);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await api.uploadDocument(file, file.name);
      await fetchDocuments();
    } catch (err) {
      console.error("Upload failed", err);
      alert("Upload failed. Check file type (TXT, MD, CSV, PDF, DOCX).");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this document?")) return;
    try {
      await api.deleteDocument(id);
      await fetchDocuments();
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    setSearchResults(null);
    setConfidence(null);
    setEvidence([]);
    try {
      const res = await api.searchDocuments(searchQuery, searchMode);
      setSearchResults(res.data.hits);
      setConfidence(res.data.confidence);
      setEvidence(res.data.evidence || []);
    } catch (err) {
      console.error("Search failed", err);
      alert("Search failed. Try again.");
    } finally {
      setSearching(false);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return { label: "High", color: "text-emerald-600" };
    if (score >= 0.6) return { label: "Medium", color: "text-amber-600" };
    return { label: "Low", color: "text-slate-500" };
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Vault</h1>
          <p className="text-sm text-slate-500 mt-1">Knowledge base documents</p>
        </div>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {uploading ? "Uploading..." : "+ Upload Document"}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleUpload}
          accept=".txt,.md,.csv,.pdf,.docx"
          className="hidden"
        />
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg border border-slate-200 p-4 mb-6">
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Search documents..."
            className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={searchMode}
            onChange={(e) => setSearchMode(e.target.value)}
            className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="hybrid">Hybrid</option>
            <option value="vector">Vector</option>
            <option value="keyword">Keyword</option>
          </select>
          <button
            onClick={handleSearch}
            disabled={searching}
            className="px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {searching ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Confidence + Evidence */}
        {confidence !== null && searchResults && (
          <div className="flex items-center gap-4 text-xs flex-wrap">
            <span className="text-slate-500">
              Results: {searchResults.length}
            </span>
            <span className={`font-medium ${getConfidenceLabel(confidence).color}`}>
              Confidence: {getConfidenceLabel(confidence).label} ({(confidence * 100).toFixed(1)}%)
            </span>
            {evidence.length > 0 && (
              <span className="text-slate-500">
                Sources: {evidence.map((e) => e.document_title).join(", ")}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Search Results */}
      {searchResults && searchResults.length > 0 && (
        <div className="space-y-3 mb-6">
          {searchResults.map((hit) => (
            <div
              key={hit.chunk_id}
              className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-700">
                  {hit.document_title}
                </span>
                <div className="flex items-center gap-3 text-xs">
                  <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded">
                    {hit.search_type}
                  </span>
                  <span className="text-slate-500">
                    Score: {hit.score.toFixed(4)}
                  </span>
                </div>
              </div>
              <p className="text-sm text-slate-600 line-clamp-3">{hit.content}</p>
              <p className="text-xs text-slate-400 mt-2">
                Source: {hit.source_citation}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Document Table */}
      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              <th className="text-left px-4 py-3 font-medium text-slate-600">Title</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Filename</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Type</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Size</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Status</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                  Loading documents...
                </td>
              </tr>
            ) : documents.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                  No documents uploaded yet.
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-700">{doc.title}</td>
                  <td className="px-4 py-3 text-slate-500">{doc.filename}</td>
                  <td className="px-4 py-3 text-slate-500">{doc.content_type}</td>
                  <td className="px-4 py-3 text-slate-500">{formatSize(doc.file_size)}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 text-xs rounded ${
                        doc.status === "indexed"
                          ? "bg-emerald-50 text-emerald-700"
                          : "bg-amber-50 text-amber-700"
                      }`}
                    >
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="text-xs text-red-500 hover:text-red-700 font-medium"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
