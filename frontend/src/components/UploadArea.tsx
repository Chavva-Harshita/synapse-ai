import { useRef, useState } from 'react'
import { apiUploadPdfAndIndex } from '../api/client'

import type { UploadedDoc } from '../App'


function isPdf(file: File) {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
}

export default function UploadArea({ onUploaded }: { onUploaded: (doc: UploadedDoc) => void }) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [dragOver, setDragOver] = useState(false)

  const handleFiles = async (files: FileList | null) => {

    if (!files || files.length === 0) return

    const file = files[0]
    if (!isPdf(file)) {
      alert('Please upload a PDF file.')
      return
    }


    try {
      // Upload + build embeddings/index for RAG.
      const result = await apiUploadPdfAndIndex({ file })
      onUploaded(result.document)
    } catch (e: any) {
      const msg = String(e?.message ?? e)
      alert(`Upload failed: ${msg}`)
      // rethrow for devtools/console visibility
      throw e
    }

  }





  return (
    <div>
      <div className="flex items-center justify-between px-1">
        <h2 className="text-sm font-semibold text-slate-200">Upload PDF</h2>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200 hover:bg-white/10"
        >
          Choose
        </button>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      <div
        className={
          'mt-3 rounded-2xl border px-4 py-6 text-center transition ' +
          (dragOver
            ? 'border-cyan-400/60 bg-cyan-400/10'
            : 'border-white/10 bg-slate-900/20 hover:border-white/20')
        }
        onDragEnter={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          void handleFiles(e.dataTransfer.files)
        }}
      >
        <div className="text-sm font-medium">Drop your PDF here</div>
        <div className="mt-1 text-xs text-slate-400">(Upload builds RAG index; then chat.)</div>
        <div className="mt-3 text-xs text-slate-500">Drag & drop or use “Choose”</div>

      </div>
    </div>
  )
}

