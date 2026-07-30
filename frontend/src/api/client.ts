const BACKEND_URL = (import.meta as any).env?.VITE_BACKEND_URL ?? 'http://127.0.0.1:8000'



export async function apiHealth(): Promise<{ status: string }> {
  const res = await fetch(`${BACKEND_URL}/api/health`)
  if (!res.ok) throw new Error(`Health failed: ${res.status}`)
  return res.json()
}

export async function apiUploadPdfAndIndex(payload: {
  file: File
}): Promise<{
  document: { id: string; name: string; size: number; uploadedAt: number }
  stored: number
  chunk_count: number
  chunk_size: number
  chunk_overlap: number
}> {

  const form = new FormData()
  form.append('file', payload.file)

  const res = await fetch(`${BACKEND_URL}/api/upload-rag`, {
    method: 'POST',
    body: form
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Upload+index failed: ${res.status} ${text}`)
  }

  return res.json()
}


export async function apiRagChat(payload: {
  message: string
  document_id: string
  top_k?: number
}): Promise<{ reply: string; retrieved_chunks: any[]; document_id: string }> {
  const res = await fetch(`${BACKEND_URL}/api/rag-chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`RAG chat failed: ${res.status} ${text}`)
  }

  return res.json()
}


export async function apiChat(payload: {
  message: string
  document_ids?: string[]
}): Promise<{ reply: string; retrieved_chunks?: any[] }> {

  const res = await fetch(`${BACKEND_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Chat failed: ${res.status} ${text}`)
  }

  return res.json()
}

export async function apiUploadPdf(payload: {
  file: File
}): Promise<{ document: { id: string; name: string; size: number; uploadedAt: number } }> {
  const form = new FormData()
  form.append('file', payload.file)

  const res = await fetch(`${BACKEND_URL}/api/upload`, {
    method: 'POST',
    body: form
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Upload failed: ${res.status} ${text}`)
  }

  return res.json()
}

