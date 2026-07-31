import { motion } from 'framer-motion'
import type { ChatMessage } from './ChatPanel'

const PLACEHOLDERS = [
  "Ask me literally anything...",
  "Brain.exe is waiting...",
  "Spill your question...",
  "Type. I overthink for you.",
  "Drop some knowledge on me...",
  "Your curiosity called...",
  "Ready when you are...",
  "I don't bite. Much.",
]

export default function GlassMessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user'

  return (
    <motion.div
      className={isUser ? 'flex justify-end' : 'flex justify-start'}
      initial={{ opacity: 0, y: 8, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
    >
      <div
        className={
          'max-w-[86%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed ' +
          (isUser
            ? 'bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-400/20 text-cyan-50 shadow-[0_0_15px_rgba(0,240,255,0.08)]'
            : 'border border-white/[0.06] bg-white/[0.04] text-slate-100')
        }
      >
        {msg.content}
      </div>
    </motion.div>
  )
}

