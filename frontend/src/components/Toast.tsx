import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, XCircle, X } from 'lucide-react'

export type ToastType = 'success' | 'error'

export type ToastData = {
  id: string
  type: ToastType
  title: string
  message?: string
}

let toastIdCounter = 0
let globalSetToasts: ((updater: (prev: ToastData[]) => ToastData[]) => void) | null = null

export function showToast(type: ToastType, title: string, message?: string) {
  const id = `toast-${++toastIdCounter}`
  const toast: ToastData = { id, type, title, message }
  if (globalSetToasts) {
    globalSetToasts((prev) => [...prev, toast])
    setTimeout(() => {
      globalSetToasts?.((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }
  return id
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState<ToastData[]>([])

  useEffect(() => {
    globalSetToasts = setToasts
    return () => {
      globalSetToasts = null
    }
  }, [])

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }

  return (
    <div className="fixed right-4 top-4 z-[100] flex flex-col gap-3">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            layout
            initial={{ opacity: 0, x: 80, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 80, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            className={
              'glass-strong relative flex w-80 items-start gap-3 overflow-hidden rounded-2xl p-4 ' +
              (toast.type === 'success'
                ? 'border-cyan-500/20 shadow-[0_0_20px_rgba(0,240,255,0.15)]'
                : 'border-pink-500/20 shadow-[0_0_20px_rgba(255,45,149,0.15)]')
            }
          >
            {/* Accent line */}
            <div
              className={
                'absolute left-0 top-0 h-full w-[3px] ' +
                (toast.type === 'success' ? 'bg-gradient-to-b from-cyan-400 to-purple-500' : 'bg-gradient-to-b from-pink-500 to-red-500')
              }
            />

            {toast.type === 'success' ? (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-cyan-500/20">
                <CheckCircle className="h-4 w-4 text-cyan-300" />
              </div>
            ) : (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-pink-500/20">
                <XCircle className="h-4 w-4 text-pink-300" />
              </div>
            )}

            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-100">{toast.title}</p>
              {toast.message && (
                <p className="mt-0.5 text-xs text-slate-400">{toast.message}</p>
              )}
            </div>

            <button
              onClick={() => removeToast(toast.id)}
              className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-slate-500 hover:bg-white/5 hover:text-slate-300 transition-colors"
            >
              <X className="h-3.5 w-3.5" />
            </button>

            {/* Progress bar */}
            <motion.div
              className={
                'absolute bottom-0 left-0 h-[2px] ' +
                (toast.type === 'success' ? 'bg-cyan-400/50' : 'bg-pink-400/50')
              }
              initial={{ width: '100%' }}
              animate={{ width: '0%' }}
              transition={{ duration: 4, ease: 'linear' }}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}

