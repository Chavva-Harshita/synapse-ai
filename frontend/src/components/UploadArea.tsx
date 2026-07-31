import { useRef, useState } from 'react'
import { apiUploadPdfAndIndex } from '../api/client'
import type { UploadedDoc } from '../App'
import { showToast } from './Toast'
import { Brain, Upload, Loader2 } from 'lucide-react'

function isPdf(file: File) {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
}

export default function UploadArea({ onUploaded }: { onUploaded: (doc: UploadedDoc) => void }) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return

    const file = files[0]
    if (!isPdf(file)) {
      showToast('error', 'Mission failed 💀', 'Please upload a PDF file.')
      return
    }

    setIsUploading(true)
    try {
      const result = await apiUploadPdfAndIndex({ file })
      onUploaded(result.document)
      showToast('success', '🧠 Memory Updated', `${file.name}\nIndexed successfully. Ready to chat.`)
    } catch (e: any) {
      const msg = String(e?.message ?? e)
      showToast('error', 'Mission failed 💀', 'Let\'s try again.')
      throw e
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between px-1">
        <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Brain className="h-4 w-4 text-cyan-400" />
          Feed My Brain
        </h2>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={isUploading}
          className="rounded-xl border border-white/10 bg-white/5 px-3.5 py-1.5 text-xs font-medium text-slate-200 hover:bg-white/10 hover:border-cyan-400/30 transition-all duration-200 disabled:opacity-50"
        >
          {isUploading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            'Choose'
          )}
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
          'relative mt-3 overflow-hidden rounded-2xl border-2 border-dashed px-4 py-8 text-center transition-all duration-300 ' +
          (isUploading
            ? 'border-cyan-400/40 bg-cyan-500/5'
            : dragOver
              ? 'border-cyan-400/60 bg-cyan-400/10 shadow-[0_0_30px_rgba(0,240,255,0.1)]'
              : 'border-white/10 bg-slate-900/20 hover:border-white/20 hover:bg-slate-900/30')
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
        {/* Upload icon */}
        <div className="mb-3 flex justify-center">
          <div className={
            'flex h-12 w-12 items-center justify-center rounded-full transition-all duration-300 ' +
            (dragOver || isUploading
              ? 'bg-cyan-500/20 scale-110'
              : 'bg-white/5')
          }>
            {isUploading ? (
              <Loader2 className="h-5 w-5 animate-spin text-cyan-300" />
            ) : (
              <Upload className={
                'h-5 w-5 transition-colors duration-300 ' +
                (dragOver ? 'text-cyan-300' : 'text-slate-400')
              } />
            )}
          </div>
        </div>

        <div className="text-sm font-medium text-slate-200">
          {isUploading ? 'Knowledge incoming...' : dragOver ? 'Drop it like it\'s hot! 🔥' : 'Drag your notes here'}
        </div>
        <div className="mt-1 text-xs text-slate-400">
          {isUploading ? 'Indexing and building memory...' : 'or click to upload.'}
        </div>

        {/* Animated progress bar during upload */}
        {isUploading && (
          <div className="mx-auto mt-4 h-1 w-3/4 overflow-hidden rounded-full bg-white/5">
            <div className="h-full w-full origin-left animate-pulse rounded-full bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400" />
          </div>
        )}
      </div>
    </div>
  )
}

