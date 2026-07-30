import { motion } from 'framer-motion'
import { Sparkles, Brain, Upload, MessageCircle } from 'lucide-react'

export default function ChatEmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center px-6 text-center">
      {/* Robot Avatar */}
      <motion.div
        className="relative mb-6"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 15 }}
      >
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500/20 via-purple-500/20 to-pink-500/20 ring-1 ring-white/10 shadow-[0_0_30px_rgba(0,240,255,0.15)]">
          <span className="text-4xl" role="img" aria-label="robot">🤖</span>
        </div>
        <div className="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 shadow-lg">
          <Sparkles className="h-3.5 w-3.5 text-white" />
        </div>
      </motion.div>

      {/* Hey Bestie */}
      <h2 className="text-2xl font-extrabold tracking-tight text-slate-100">
        Hey Bestie.
      </h2>
      <h3 className="mt-1 bg-gradient-to-r from-cyan-300 via-purple-300 to-pink-300 bg-clip-text text-xl font-bold text-transparent">
        I'm Synapse.
      </h3>

      {/* Feature list */}
      <div className="mt-6 space-y-3">
        {[
          { icon: Upload, text: 'Upload your notes.', color: 'text-cyan-300' },
          { icon: Brain, text: "I'll remember everything.", color: 'text-purple-300' },
          { icon: MessageCircle, text: 'Ask me anything.', color: 'text-pink-300' },
        ].map((item, i) => (
          <motion.div
            key={i}
            className="flex items-center gap-2.5 rounded-xl px-4 py-2"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 + i * 0.15, duration: 0.4 }}
          >
            <item.icon className={`h-4 w-4 ${item.color}`} />
            <span className="text-sm font-medium text-slate-300">{item.text}</span>
          </motion.div>
        ))}
      </div>

      {/* Tagline */}
      <motion.div
        className="mt-6 rounded-2xl border border-cyan-500/10 bg-cyan-500/5 px-5 py-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9, duration: 0.4 }}
      >
        <p className="text-xs leading-relaxed text-slate-400">
          <span className="text-cyan-300">No hallucinations.</span>{' '}
          <span className="text-purple-300">Only receipts.</span>
        </p>
        <p className="mt-1 text-sm font-semibold text-slate-300">
          Let's cook. 🔥
        </p>
      </motion.div>
    </div>
  )
}

