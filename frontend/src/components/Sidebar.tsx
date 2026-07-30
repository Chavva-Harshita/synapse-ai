import type { UploadedDoc } from '../App'

export default function Sidebar({ docs }: { docs: UploadedDoc[] }) {
  return (
    <div className="min-h-[220px]">
      <div className="flex items-center justify-between px-1">
        <h2 className="text-sm font-semibold text-slate-200">Documents</h2>
        <span className="text-xs text-slate-400">{docs.length}</span>
      </div>
      <div className="mt-3 space-y-2">
        {docs.length === 0 ? (
          <div className="px-1 text-sm text-slate-400">Upload a PDF to populate this list.</div>
        ) : (
          docs.map((d) => (
            <div
              key={d.id}
              className="rounded-xl border border-white/10 bg-slate-900/30 px-3 py-2"
            >
              <div className="truncate text-sm font-medium">{d.name}</div>
              <div className="mt-1 text-xs text-slate-400">{(d.size / 1024).toFixed(1)} KB</div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

