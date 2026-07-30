import { useRef, useState } from 'react'
import { apiUploadPdfAndIndex } from '../api/client'
import type { UploadedDoc } from '../App'
import { showToast } from './Toast'
import { Brain, Upload, Loader2, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

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
      showToast('success', '🧠 Memory Updated', `${file.name}\nKnowledge absorbed.\nReady to chat.`)
    } catch (e: any) {
      console.error(e)
      showToast('error', 'Mission failed 💀', "Let's try again.")
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
          className="rounded-xl border border-white/10 bg-white/5 px-3.5 py-1.5 text-xs font-medium text-slate-200 hover:bg-white/10 hover:border-cyan-400/30 transition-all duration-200 disabled:opacity-50 active:scale-95"
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

      <motion.div
        className={
          'relative mt-3 overflow-hidden rounded-2xl border-2 border-dashed px-4 py-8 text-center transition-all duration-300 animate-border-glow ' +
          (isUploading
            ? 'border-cyan-400/40 bg-cyan-500/5'
            : dragOver
              ? 'border-cyan-400/60 bg-cyan-400/10 shadow-[0_0_40px_rgba(0,240,255,0.15)]'
              : 'border-white/[0.08] bg-slate-900/20 hover:border-white/20 hover:bg-slate-900/30')
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
        whileHover={{ scale: 1.01 }}
        transition={{ duration: 0.2 }}
      >
        {/* Floating brain icon */}
        <div className="mb-4 flex justify-center">
          <motion.div
            className={
              'flex h-14 w-14 items-center justify-center rounded-full transition-all duration-300 ' +
              (dragOver || isUploading
                ? 'bg-cyan-500/20 scale-110'
                : 'bg-white/5')
            }
            animate={{ y: [0, -6, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          >
            {isUploading ? (
              <Loader2 className="h-6 w-6 animate-spin text-cyan-300" />
            ) : (
              <Brain className={
                'h-6 w-6 transition-colors duration-300 ' +
                (dragOver ? 'text-cyan-300' : 'text-slate-400')
              } />
            )}
          </motion.div>
          {/* Sparkle decorations */}
          <motion.div
            className="absolute right-[30%] top-6"
            animate={{ opacity: [0, 1, 0], scale: [0.8, 1.2, 0.8] }}
            transition={{ duration: 2.5, repeat: Infinity, delay: 0.5 }}
          >
            <Sparkles className="h-3 w-3 text-cyan-400/60" />
          </motion.div>
          <motion.div
            className="absolute left-[30%] top-8"
            animate={{ opacity: [0, 1, 0], scale: [0.8, 1.2, 0.8] }}
            transition={{ duration: 3, repeat: Infinity, delay: 1.5 }}
          >
            <Sparkles className="h-2.5 w-2.5 text-purple-400/60" />
          </motion.div>
        </div>

        <div className="text-sm font-medium text-slate-200">
          {isUploading ? 'Knowledge incoming...' : dragOver ? "Drop it like it's hot! 🔥" : 'Drop your notes.'}
        </div>
        <div className="mt-1 text-xs text-slate-500">
          {isUploading ? 'Indexing and building memory...' : "I'll remember them forever."}
        </div>

        {/* Animated progress bar during upload */}
        {isUploading && (
          <div className="mx-auto mt-5 h-1 w-3/4 overflow-hidden rounded-full bg-white/5">
            <motion.div
              className="h-full w-full rounded-full bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400"
              initial={{ scaleX: 0, transformOrigin: 'left' }}
              animate={{ scaleX: 1, transformOrigin: 'left' }}
              transition={{ duration: 2, ease: 'easeInOut' }}
            />
          </div>
        )}
      </motion.div>
    </div>
  )
}
