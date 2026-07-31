import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'

const TYPING_LABELS = [
  'Connecting neurons...',
  'Searching memory...',
  'Cooking...',
  'Almost there...',
]

export default function TypingIndicator({ label: _label }: { label?: string }) {
  const [index, setIndex] = useState(0)
  const [show, setShow] = useState(true)

  useEffect(() => {
    const interval = setInterval(() => {
      setShow(false)
      setTimeout(() => {
        setIndex((prev) => (prev + 1) % TYPING_LABELS.length)
        setShow(true)
      }, 200)
    }, 2500)

    return () => clearInterval(interval)
  }, [])

  const currentLabel = TYPING_LABELS[index]

  return (
    <div className="flex w-full items-center gap-3" aria-label={currentLabel}>
      <div className="flex items-center gap-2.5 rounded-2xl border border-white/[0.06] bg-white/[0.03] px-4 py-3">
        <AnimatePresence mode="wait">
          <motion.span
            key={currentLabel}
            className="text-xs font-medium text-slate-400"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.2 }}
          >
            {currentLabel}
          </motion.span>
        </AnimatePresence>
        <div className="flex items-end gap-1" aria-hidden="true">
          {Array.from({ length: 3 }).map((_, i) => (
            <motion.span
              key={i}
              className="h-1.5 w-1.5 rounded-full"
              style={{
                background: i === 0
                  ? 'linear-gradient(135deg, #22d3ee, #818cf8)'
                  : i === 1
                    ? 'linear-gradient(135deg, #818cf8, #a78bfa)'
                    : 'linear-gradient(135deg, #a78bfa, #f472b6)'
              }}
              initial={{ y: 0, opacity: 0.4 }}
              animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }}
              transition={{
                duration: 1.2,
                repeat: Infinity,
                delay: i * 0.2,
                ease: 'easeInOut'
              }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

