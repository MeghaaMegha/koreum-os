import { useEffect, useState } from "react";
import { api, Document } from "../api/client";

export default function Vault() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showUpload, setShowUpload] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<{ document_title: string; content: string; document_id: string }[]>([]);
  const [searching, setSearching] = useState(false);

  const loadDocs = () => {
    setLoading(true);
    api
      .listDocuments()
      .then((res) => setDocuments(res.data))
      .catch((e) => setError(e.response?.data?.detail || "Failed to load documents"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    setUploadError("");
    setUploading(true);
    api
      .uploadDocument(uploadFile, uploadTitle || uploadFile.name)
      .then(() => {
        setShowUpload(false);
        setUploadFile(null);
        setUploadTitle("");
        loadDocs();
      })
      .catch((err) => setUploadError(err.response?.data?.detail || "Failed to upload"))
      .finally(() => setUploading(false));
  };

  const handleDelete = (doc: Document) => {
    if (!confirm(`Delete "${doc.title}"?`)) return;
    api
      .deleteDocument(doc.id)
      .then(() => loadDocs())
      .catch((err) => alert(err.response?.data?.detail || "Failed to delete"));
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    api
      .searchDocuments(searchQuery)
      .then((res) => setSearchResults(res.data.hits))
      .catch(() => setSearchResults([]))
      .finally(() => setSearching(false));
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800 mb-1">Vault</h1>
          <p className="text-sm text-slate-500">Knowledge base documents</p>
        </div>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="px-4 py-2 bg-koreum-500 text-white text-sm font-medium rounded-lg hover:bg-koreum-600 transition"
        >
          {showUpload ? "Cancel" : "+ Upload Document"}
        </button>
      </div>

      {showUpload && (
        <form onSubmit={handleUpload} className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Upload Document</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Title</label>
              <input
                type="text"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-koreum-500"
                placeholder="Document title (optional)"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">File</label>
              <input
                type="file"
                required
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                className="w-full text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-koreum-50 file:text-koreum-700 hover:file:bg-koreum-100"
                accept=".txt,.md,.csv,.pdf,.docx"
              />
              <p className="text-xs text-slate-400 mt-1">Supported: TXT, MD, CSV, PDF, DOCX (max 25MB)</p>
            </div>
          </div>
          {uploadError && <p className="text-red-500 text-sm mt-3">{uploadError}</p>}
          <button
            type="submit"
            disabled={uploading || !uploadFile}
            className="mt-4 px-5 py-2 bg-koreum-500 text-white text-sm font-medium rounded-lg hover:bg-koreum-600 disabled:opacity-50 transition"
          >
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </form>
      )}

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-6">
        <form onSubmit={handleSearch}>
          <div className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-koreum-500"
              placeholder="Search documents..."
            />
            <button
              type="submit"
              disabled={searching}
              className="px-4 py-2 bg-slate-100 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-200 disabled:opacity-50 transition"
            >
              {searching ? "Searching..." : "Search"}
            </button>
          </div>
        </form>
        {searchResults.length > 0 && (
          <div className="mt-4 space-y-3">
            {searchResults.map((hit, i) => (
              <div key={i} className="border border-slate-200 rounded-lg p-3">
                <p className="text-sm font-medium text-slate-800">{hit.document_title}</p>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2">{hit.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Title</th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Filename</th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Type</th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Size</th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Status</th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading && (
              <tr>
                <td colSpan={6} className="px-5 py-8 text-center text-slate-400">Loading…</td>
              </tr>
            )}
            {error && (
              <tr>
                <td colSpan={6} className="px-5 py-8 text-center text-red-500">{error}</td>
              </tr>
            )}
            {!loading && documents.length === 0 && (
              <tr>
                <td colSpan={6} className="px-5 py-8 text-center text-slate-400">No documents uploaded yet</td>
              </tr>
            )}
            {!loading &&
              documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3 text-slate-800">{doc.title}</td>
                  <td className="px-5 py-3 text-slate-600">{doc.filename}</td>
                  <td className="px-5 py-3 text-slate-600">{doc.content_type}</td>
                  <td className="px-5 py-3 text-slate-600">{formatSize(doc.file_size)}</td>
                  <td className="px-5 py-3">
                    <span className="text-xs px-2 py-0.5 rounded bg-koreum-50 text-koreum-700">{doc.status}</span>
                  </td>
                  <td className="px-5 py-3">
                    <button
                      onClick={() => handleDelete(doc)}
                      className="text-xs px-3 py-1 text-red-500 border border-red-200 rounded hover:bg-red-50 transition"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
