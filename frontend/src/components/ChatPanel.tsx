import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import GlassMessageBubble from './GlassMessageBubble'
import TypingIndicator from './TypingIndicator'
import ChatEmptyState from './ChatEmptyState'
import { Send, ArrowDown, Sparkles } from 'lucide-react'

type Role = 'user' | 'assistant'
export type ChatMessage = {
  id: string
  role: Role
  content: string
}

const PLACEHOLDERS = [
  "Ask me literally anything...",
  "Brain.exe is waiting...",
  "Spill your question...",
  "Type. I overthink for you.",
  "Drop some knowledge on me...",
  "Your curiosity called...",
  "Ready when you are...",
]

function getRandomPlaceholder(): string {
  return PLACEHOLDERS[Math.floor(Math.random() * PLACEHOLDERS.length)]
}

export default function ChatPanel({
  messages,
  onSend,
  selectedDocIds
}: {
  messages: ChatMessage[]
  onSend: (text: string) => Promise<void> | void
  selectedDocIds: string[]
}) {
  const [text, setText] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [placeholder] = useState(getRandomPlaceholder)
  const [showScrollBtn, setShowScrollBtn] = useState(false)
  const listRef = useRef<HTMLDivElement | null>(null)

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    if (!listRef.current) return
    listRef.current.scrollTo({
      top: listRef.current.scrollHeight,
      behavior
    })
  }

  useEffect(() => {
    if (!listRef.current) return
    const el = listRef.current
    const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 100
    if (isAtBottom) {
      scrollToBottom()
    }
  }, [messages])

  const handleScroll = () => {
    if (!listRef.current) return
    const el = listRef.current
    const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 100
    setShowScrollBtn(!isAtBottom)
  }

  const handleSubmit = async () => {
    const trimmed = text.trim()
    if (!trimmed || isSending) return
    setIsSending(true)
    setText('')
    const userMessage = trimmed
    scrollToBottom()
    try {
      await onSend(userMessage)
      scrollToBottom()
    } finally {
      setIsSending(false)
      scrollToBottom()
    }
  }

  return (
    <div className="flex h-[70vh] min-h-[520px] flex-col">
      {/* Robot Identity Header */}
      <div className="flex items-center justify-between px-2 pb-3 border-b border-white/[0.04]">
        <div className="flex items-center gap-3">
          <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/20 via-purple-500/20 to-pink-500/20 ring-1 ring-white/[0.06]">
            <span className="text-lg">🤖</span>
            <motion.div
              className="absolute -right-0.5 -top-0.5 flex h-3 w-3 items-center justify-center"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Sparkles className="h-2.5 w-2.5 text-cyan-300" />
            </motion.div>
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-200">Synapse</h2>
            <div className="flex items-center gap-1.5 mt-0.5">
              <div className="h-1.5 w-1.5 rounded-full bg-cyan-400 shadow-[0_0_6px_rgba(34,211,238,0.6)] animate-status-pulse" />
              <span className="text-[10px] font-medium text-cyan-400/70">Online</span>
            </div>
          </div>
        </div>
        {selectedDocIds.length > 0 && (
          <div className="rounded-full bg-cyan-500/10 px-2.5 py-1 text-[10px] font-medium text-cyan-300">
            {selectedDocIds.length} doc{selectedDocIds.length > 1 ? 's' : ''} active
          </div>
        )}
      </div>

      {/* Messages area */}
      <div className="relative mt-3 flex-1">
        <div
          ref={listRef}
          onScroll={handleScroll}
          className="h-full overflow-y-auto rounded-2xl border border-white/[0.04] bg-slate-950/20 p-4"
        >
          <div className="space-y-5">
            {messages.length === 0 ? (
              <ChatEmptyState />
            ) : (
              <>
                {messages.map((m) => (
                  <GlassMessageBubble key={m.id} msg={m} />
                ))}
                {isSending ? (
                  <div className="mt-4">
                    <TypingIndicator />
                  </div>
                ) : null}
              </>
            )}
          </div>

        {/* Scroll to bottom button */}
        {showScrollBtn && (
          <button
            onClick={() => scrollToBottom()}
            className="absolute bottom-3 left-1/2 -translate-x-1/2 flex items-center gap-1.5 rounded-full border border-white/10 bg-slate-900/80 px-3 py-1.5 text-xs text-slate-400 backdrop-blur-lg hover:bg-slate-800/80 hover:text-slate-200 transition-all duration-200 active:scale-95"
          >
            <ArrowDown className="h-3 w-3" />
            New messages
          </button>
        )}
      </div>
      </div>

      {/* Input area */}
      <div className="mt-3 rounded-2xl border border-white/[0.06] bg-slate-900/40 p-2 transition-all duration-200 focus-within:border-cyan-500/20 focus-within:shadow-[0_0_15px_rgba(0,240,255,0.05)]">
        <div className="flex items-end gap-2">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={1}
            placeholder={placeholder}
            className="min-h-[44px] w-full resize-none rounded-xl bg-transparent px-3 py-2 text-sm outline-none placeholder:text-slate-500 text-slate-100"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                void handleSubmit()
              }
            }}
          />
          <button
            type="button"
            onClick={() => void handleSubmit()}
            disabled={isSending || text.trim().length === 0}
            className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-cyan-500/20 to-purple-500/20 px-4 py-2 text-sm font-medium text-cyan-100 ring-1 ring-cyan-400/20 hover:from-cyan-500/30 hover:to-purple-500/30 hover:ring-cyan-400/30 disabled:opacity-40 transition-all duration-200 active:scale-95"
          >
            {isSending ? (
              <span className="flex items-center gap-1.5">
                <span className="h-3 w-3 animate-spin rounded-full border-2 border-cyan-400/30 border-t-cyan-400" />
                Sending
              </span>
            ) : (
              <span className="flex items-center gap-1.5">
                <Send className="h-3.5 w-3.5" />
                Send
              </span>
            )}
          </button>
        </div>
        <div className="mt-2 px-3 text-[11px] text-slate-600">
          Enter to send &middot; Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}
