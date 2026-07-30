import { motion } from 'framer-motion'
import type { ChatMessage } from './ChatPanel'

export default function GlassMessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user'

  return (
    <motion.div
      className={isUser ? 'flex justify-end' : 'flex justify-start'}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      <div
        className={
          'max-w-[86%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed ' +
          (isUser
            ? 'border border-cyan-400/25 bg-cyan-500/15 text-cyan-100'
            : 'border border-white/10 bg-white/5 text-slate-100')
        }
      >
        {msg.content}
      </div>
    </motion.div>
  )
}

