import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'

const BOOT_LINES = [
  { label: 'Memory Engine', done: true },
  { label: 'Retriever', done: true },
  { label: 'Reasoning', done: true },
]

export default function BootScreen({ onComplete }: { onComplete: () => void }) {
  const [progress, setProgress] = useState(0)
  const [visibleLines, setVisibleLines] = useState<number[]>([])
  const [showReady, setShowReady] = useState(false)

  useEffect(() => {
    // Animate progress bar
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        const next = Math.min(prev + Math.random() * 15, 100)
        return next
      })
    }, 180)

    // Show boot lines one by one
    const lineTimer1 = setTimeout(() => setVisibleLines([0]), 400)
    const lineTimer2 = setTimeout(() => setVisibleLines([0, 1]), 800)
    const lineTimer3 = setTimeout(() => setVisibleLines([0, 1, 2]), 1200)

    // Show "Ready." and complete
    const readyTimer = setTimeout(() => {
      setProgress(100)
      setShowReady(true)
    }, 1600)

    const completeTimer = setTimeout(() => {
      onComplete()
    }, 2400)

    return () => {
      clearInterval(progressInterval)
      clearTimeout(lineTimer1)
      clearTimeout(lineTimer2)
      clearTimeout(lineTimer3)
      clearTimeout(readyTimer)
      clearTimeout(completeTimer)
    }
  }, [onComplete])

  return (
    <motion.div
      className="fixed inset-0 z-[200] flex flex-col items-center justify-center bg-[#0a0a14]"
      exit={{ opacity: 0 }}
      transition={{ duration: 0.6, ease: 'easeInOut' }}
    >
      {/* Animated background glow */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-1/3 h-[400px] w-[400px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-radial from-cyan-500/10 via-purple-500/5 to-transparent blur-3xl" />
      </div>

      <div className="relative z-10 flex flex-col items-center">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8 text-center"
        >
          <h1 className="bg-gradient-to-r from-cyan-300 via-purple-300 to-pink-300 bg-clip-text text-4xl font-black tracking-tighter text-transparent">
            SYNAPSE AI
          </h1>
          <p className="mt-2 text-xs font-mono tracking-[0.3em] text-slate-600">
            INITIALIZING...
          </p>
        </motion.div>

        {/* Progress bar */}
        <div className="mb-8 w-72">
          <div className="h-[3px] overflow-hidden rounded-full bg-white/5">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400"
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
            />
          </div>
          <div className="mt-2 text-right font-mono text-[10px] text-slate-600">
            {Math.floor(progress)}%
          </div>
        </div>

        {/* Boot lines */}
        <div className="space-y-3">
          {BOOT_LINES.map((line, i) => (
            <AnimatePresence key={line.label}>
              {visibleLines.includes(i) && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="flex items-center gap-3 font-mono text-sm"
                >
                  <span className="text-cyan-400">✓</span>
                  <span className="text-slate-400">{line.label}</span>
                  <span className="text-[10px] text-slate-600">online</span>
                </motion.div>
              )}
            </AnimatePresence>
          ))}
        </div>

        {/* Ready state */}
        <AnimatePresence>
          {showReady && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, type: 'spring' }}
              className="mt-8"
            >
              <div className="flex items-center gap-2 rounded-full border border-cyan-500/20 bg-cyan-500/5 px-5 py-2">
                <div className="h-2 w-2 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.5)]" />
                <span className="text-sm font-semibold text-cyan-300">Ready.</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
