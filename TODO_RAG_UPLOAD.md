# RAG upload processing (upload-time indexing)

- [ ] Add backend endpoint `/api/upload-rag` to store PDF + extract text + chunk + embed+persist in Chroma
- [ ] Add response model for the endpoint
- [x] Add frontend client function `apiUploadPdfAndIndex`

- [x] Update `UploadArea.tsx` to call `/api/upload-rag` and update UI messaging

- [ ] Smoke test: upload a PDF then send a chat message (no re-index needed)

