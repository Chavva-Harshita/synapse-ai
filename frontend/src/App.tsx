import { useEffect, useMemo, useState } from 'react'
import Sidebar from './components/Sidebar'
import UploadArea from './components/UploadArea'
import ChatPanel, { type ChatMessage } from './components/ChatPanel'
import { apiRagChat } from './api/client'

export type UploadedDoc = {
  id: string

  name: string
  size: number
  uploadedAt: number
}

export default function App() {
  const [docs, setDocs] = useState<UploadedDoc[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: crypto.randomUUID(),
      role: 'assistant',
      content:
        'Welcome to Synapse AI. Upload a PDF to see it appear in your sidebar, then start chatting.'
    }
  ])

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
      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Error: ${String(e?.message ?? e)}`
      }
      setMessages((prev) => [...prev, assistantMsg])
    }
  }


  const selectedDocIds = useMemo(() => docs.slice(0, 1).map((d) => d.id), [docs])


  return (
    <div className="min-h-screen w-full bg-slate-950">
      <div className="mx-auto max-w-7xl px-4 py-6">
        <header className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl glass">
              <span className="font-black tracking-tight">S</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold">Synapse AI</h1>
              <p className="text-sm text-slate-400">Modern full-stack foundation</p>
            </div>
          </div>
          <div className="hidden text-sm text-slate-400 sm:block">Dark • Glass • Responsive</div>
        </header>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-[320px_1fr]">
          <aside className="glass rounded-2xl p-3">
            <UploadArea onUploaded={onUploaded} />
            <div className="mt-4 h-px bg-white/10" />
            <Sidebar docs={docs} />
          </aside>

          <main className="glass rounded-2xl p-3 md:p-4">
            <ChatPanel messages={messages} onSend={onSendMessage} selectedDocIds={selectedDocIds} />
          </main>
        </div>
      </div>
    </div>
  )
}

