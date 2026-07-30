import { useEffect, useMemo, useRef, useState } from 'react'
import GlassMessageBubble from './GlassMessageBubble'
import TypingIndicator from './TypingIndicator'

type Role = 'user' | 'assistant'
export type ChatMessage = {
  id: string
  role: Role
  content: string
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
  const listRef = useRef<HTMLDivElement | null>(null)

  const subtitle = useMemo(() => {
    if (selectedDocIds.length === 0) return 'No documents selected'
    return `Using ${selectedDocIds.length} document${selectedDocIds.length > 1 ? 's' : ''}`
  }, [selectedDocIds])

  useEffect(() => {
    if (!listRef.current) return
    listRef.current.scrollTo({
      top: listRef.current.scrollHeight,
      behavior: 'smooth'
    })
  }, [messages])

  const handleSubmit = async () => {
    const trimmed = text.trim()
    if (!trimmed || isSending) return
    setIsSending(true)
    setText('')
    try {
      await onSend(trimmed)
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="flex h-[70vh] min-h-[520px] flex-col">
      <div className="flex items-start justify-between px-2">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">Chat</h2>
          <p className="text-xs text-slate-400">{subtitle}</p>
        </div>
      </div>

      <div
        ref={listRef}
        className="mt-3 flex-1 overflow-y-auto rounded-2xl border border-white/10 bg-slate-950/40 p-4"
      >
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="px-1 py-10 text-center text-sm text-slate-400">No messages yet.</div>
          ) : (
            <>
              {messages.map((m) => (
                <GlassMessageBubble key={m.id} msg={m} />
              ))}
              {isSending ? (
                <div className="mt-3">
                  <TypingIndicator />
                </div>
              ) : null}
            </>
          )}
        </div>
      </div>

      <div className="mt-3 rounded-2xl border border-white/10 bg-slate-950/40 p-2">
        <div className="flex items-end gap-2">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={1}
            placeholder="Ask anything..."
            className="min-h-[44px] w-full resize-none rounded-xl bg-transparent px-3 py-2 text-sm outline-none placeholder:text-slate-500"
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
            className="rounded-xl bg-cyan-500/20 px-4 py-2 text-sm font-medium text-cyan-100 ring-1 ring-cyan-400/30 hover:bg-cyan-500/30 disabled:opacity-50"
          >
            {isSending ? 'Sending...' : 'Send'}
          </button>
        </div>
        <div className="mt-2 px-3 text-[11px] text-slate-500">Tip: Enter to send, Shift+Enter for newline.</div>
      </div>
    </div>
  )
}

