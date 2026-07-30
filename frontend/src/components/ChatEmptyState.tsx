import { Sparkles } from 'lucide-react'

export default function ChatEmptyState() {
  return (
    <div className="mt-8 flex flex-col items-center justify-center px-8 text-center">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
        <Sparkles className="h-6 w-6 text-cyan-300" />
      </div>
      <h3 className="mt-4 text-base font-semibold text-slate-100">Start a conversation</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">
        Upload a PDF on the left and ask questions. This starter UI is ready for the backend integration.
      </p>
    </div>
  )
}

