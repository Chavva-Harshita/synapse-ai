import type { UploadedDoc } from "../App"
import { motion } from "framer-motion"
import { BrainCircuit, FileText, HardDrive } from "lucide-react"

type SidebarProps = {
  docs: UploadedDoc[]
}

function formatSize(bytes: number): string {
  if (bytes >= 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }
  if (bytes >= 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }
  return `${bytes} B`
}

function formatUploadTime(timestamp: number): string {
  return new Date(timestamp).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export default function Sidebar({ docs }: SidebarProps) {
  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between px-1">
        <h2 className="flex items-center gap-2 text-sm font-bold text-slate-200">
          <BrainCircuit className="h-4 w-4 text-cyan-400" />
          Memory Bank
        </h2>
        {docs.length > 0 && (
          <span className="rounded-full border border-cyan-400/20 bg-cyan-500/10 px-2 py-0.5 text-[10px] font-medium text-cyan-300">
            {docs.length} {docs.length === 1 ? "doc" : "docs"}
          </span>
        )}
      </div>

      {/* Document list */}
      <div className="mt-3 space-y-2">
        {docs.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="rounded-2xl border border-white/[0.06] bg-slate-900/30 px-4 py-8 text-center"
          >
            <motion.div
              className="mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-white/5 ring-1 ring-white/[0.06]"
              animate={{ y: [0, -4, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            >
              <BrainCircuit className="h-5 w-5 text-slate-600" />
            </motion.div>
            <p className="text-sm font-medium text-slate-300">
              🧠 Memory Bank is empty
            </p>
            <p className="mt-1 text-xs leading-relaxed text-slate-500">
              Upload a PDF to begin training my neural memory.
            </p>
          </motion.div>
        ) : (
          docs.map((doc, i) => (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.25, delay: i * 0.05 }}
              whileHover={{ scale: 1.02, y: -2 }}
              className="group relative flex items-center gap-3 overflow-hidden rounded-xl border border-white/[0.06] bg-slate-900/40 p-3 transition-all duration-200 hover:border-cyan-400/30 hover:bg-slate-900/60 hover:shadow-[0_0_20px_rgba(0,240,255,0.08)]"
            >
              {/* Accent glow line on hover */}
              <div className="absolute left-0 top-0 h-full w-[2px] bg-gradient-to-b from-cyan-400 to-purple-500 opacity-0 transition-opacity duration-200 group-hover:opacity-100" />

              {/* PDF icon */}
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-pink-500/15 to-red-500/10 ring-1 ring-pink-400/20 transition-all duration-200 group-hover:ring-pink-400/40 group-hover:shadow-[0_0_12px_rgba(255,45,149,0.15)]">
                <FileText className="h-4 w-4 text-pink-400" />
              </div>

              {/* Doc info */}
              <div className="min-w-0 flex-1">
                <p
                  className="truncate text-[13px] font-semibold text-slate-200"
                  title={doc.name}
                >
                  {doc.name}
                </p>
                <div className="mt-1 flex items-center gap-1.5 text-[10px] text-slate-500">
                  <span className="flex items-center gap-1">
                    <HardDrive className="h-3 w-3" />
                    {formatSize(doc.size)}
                  </span>
                  <span className="h-0.5 w-0.5 rounded-full bg-slate-600" />
                  <span>{formatUploadTime(doc.uploadedAt)}</span>
                </div>
              </div>

              {/* Glowing Indexed chip */}
              <span className="shrink-0 rounded-full border border-emerald-400/20 bg-emerald-500/10 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wider text-emerald-300 shadow-[0_0_10px_rgba(52,211,153,0.25)]">
                Indexed
              </span>
            </motion.div>
          ))
        )}
      </div>
    </div>
  )
}

