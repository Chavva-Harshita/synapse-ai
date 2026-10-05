# RAG upload processing (upload-time indexing)

- [x] Add backend endpoint `/api/upload-rag` to store PDF + extract text + chunk + embed+persist in Chroma
- [x] Add response model for the endpoint
- [x] Add frontend client function `apiUploadPdfAndIndex`

- [x] Update `UploadArea.tsx` to call `/api/upload-rag` and update UI messaging

- [x] Smoke test: upload a PDF then send multiple chat messages (no re-index needed)
