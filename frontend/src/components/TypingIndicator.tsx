import { motion, AnimatePresence } from 'framer-motion'

export default function TypingIndicator({ label = 'Synapse is typing…' }: { label?: string }) {
  return (
    <div className="flex w-full items-center gap-3" aria-label={label}>
      <div className="flex items-center gap-1 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
        <span className="text-xs text-slate-400">{label}</span>
        <AnimatePresence mode="wait">
          <motion.span
            className="sr-only"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
        </AnimatePresence>
        <div className="flex items-end gap-1" aria-hidden="true">
          {Array.from({ length: 3 }).map((_, i) => (
            <motion.span
              key={i}
              className="h-2 w-2 rounded-full bg-cyan-300/70"
              initial={{ y: 0, opacity: 0.5 }}
              animate={{ y: [0, -4, 0], opacity: [0.5, 1, 0.5] }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: i * 0.15,
                ease: 'easeInOut'
              }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

