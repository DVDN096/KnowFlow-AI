
export default function Topbar() {
  return (
    <header className="sticky top-0 z-30 flex h-[76px] items-center justify-between border-b border-slate-200 bg-white/90 px-8 backdrop-blur-xl">
      <div>
        <p className="text-xs text-slate-400">
          Knowledge Intelligence Platform
        </p>
        <h2 className="text-sm font-semibold text-slate-800">
          Engineering Workspace
        </h2>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-700">
          DD
        </div>

        <span className="hidden text-xs font-semibold text-slate-700 sm:block">
          Admin
        </span>
      </div>
    </header>
  );
}
