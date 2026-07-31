import { useEffect, useMemo, useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import Sidebar from './components/Sidebar'
import UploadArea from './components/UploadArea'
import ChatPanel, { type ChatMessage } from './components/ChatPanel'
import { apiRagChat } from './api/client'
import ToastContainer from './components/Toast'
import BootScreen from './components/BootScreen'
import { Brain, Sparkles, Cpu } from 'lucide-react'

export type UploadedDoc = {
  id: string

  name: string
  size: number
  uploadedAt: number
}

const FRIENDLY_ERRORS = [
  "🤖 Oops...\n\nI couldn't answer that.\n\nLooks like my reasoning engine is offline.\n\nPlease check the AI model and try again.",
  "🤖 Brain offline.\n\nPlease check the AI model and try again.",
  "🤖 Hmm. Something went wrong on my end.\n\nMy neural pathways are tangled.\n\nTry again in a bit?",
]

function getRandomFriendlyError(): string {
  return FRIENDLY_ERRORS[Math.floor(Math.random() * FRIENDLY_ERRORS.length)]
}

export default function App() {
  const [bootComplete, setBootComplete] = useState(false)
  const [docs, setDocs] = useState<UploadedDoc[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])

  useEffect(() => {
    document.documentElement.classList.add('dark')
  }, [])

  const onUploaded = (doc: UploadedDoc) => {
    setDocs((prev) => [doc, ...prev])
  }

  const onSendMessage = async (text: string) => {
    if (docs.length === 0) {
      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Upload a PDF first, then ask a question.'
      }
      const userMsg: ChatMessage = { id: crypto.randomUUID(), role: 'user', content: text }
      setMessages((prev) => [...prev, userMsg, assistantMsg])
      return
    }

    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])

    const activeDocId = docs[0].id
    try {
      const res = await apiRagChat({ message: text, document_id: activeDocId })
      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: res.reply
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (e: any) {
      console.error('[Synapse Error]', e?.message || e)
      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: getRandomFriendlyError()
      }
      setMessages((prev) => [...prev, assistantMsg])
    }
  }

  const selectedDocIds = useMemo(() => docs.slice(0, 1).map((d) => d.id), [docs])

  return (
    <>
      <AnimatePresence>
        {!bootComplete && <BootScreen onComplete={() => setBootComplete(true)} />}
      </AnimatePresence>

      {bootComplete && (
        <div className="min-h-screen w-full bg-slate-950">
          <div className="animated-bg" />
          <div className="bg-overlay" />
          <div className="bg-orb bg-orb--1" />
          <div className="bg-orb bg-orb--2" />
          <div className="bg-orb bg-orb--3" />
          <div className="bg-radial-glow bg-radial-glow--1" />
          <div className="bg-radial-glow bg-radial-glow--2" />

          <ToastContainer />

          <div className="relative z-10 mx-auto max-w-7xl px-4 py-6">
            <header className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/20 via-purple-500/20 to-pink-500/20 ring-1 ring-white/10 shadow-[0_0_20px_rgba(0,240,255,0.1)]">
                  <Brain className="h-5 w-5 text-cyan-300" />
                  <div className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-purple-500">
                    <Sparkles className="h-2.5 w-2.5 text-white" />
                  </div>
                </div>
                <div>
                  <h1 className="bg-gradient-to-r from-cyan-200 via-purple-200 to-pink-200 bg-clip-text text-lg font-extrabold tracking-tight text-transparent">
                    Synapse AI
                  </h1>
                  <p className="text-xs font-medium text-slate-500 tracking-wide">
                    Reads. Remembers. Responds.
                  </p>
                </div>
              </div>

              <div className="hidden items-center gap-2 sm:flex">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-cyan-500/10">
                  <div className="h-2 w-2 animate-pulse-glow rounded-full bg-cyan-400" />
                </div>
                <span className="text-xs font-medium text-slate-500">Neural Core Online</span>
              </div>
            </header>

            <div className="grid grid-cols-1 gap-5 md:grid-cols-[340px_1fr] items-stretch">
              <aside className="glass-card rounded-2xl p-4 transition-all duration-300 hover:shadow-[0_10px_40px_rgba(99,102,241,0.1)]">
                <UploadArea onUploaded={onUploaded} />
                <div className="mt-5 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
                <div className="mt-5">
                  <Sidebar docs={docs} />
                </div>
              </aside>

              <main className="glass-card rounded-2xl p-3 md:p-4 transition-all duration-300 hover:shadow-[0_10px_40px_rgba(99,102,241,0.1)]">
                <ChatPanel messages={messages} onSend={onSendMessage} selectedDocIds={selectedDocIds} />
              </main>
            </div>
            <footer className="mt-6 text-center">
              <p className="text-[11px] text-slate-700 flex items-center justify-center gap-1.5">
                <Cpu className="h-3 w-3" />
                Powered by Synapse AI · Memory Bank · RAG Engine
              </p>
            </footer>
          </div>
        </div>
      )}
    </>
  )
}
