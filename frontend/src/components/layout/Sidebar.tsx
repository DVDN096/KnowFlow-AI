
import {
  LayoutDashboard,
  MessageSquare,
  Files,
  BrainCircuit,
} from "lucide-react";

import { NavLink } from "react-router-dom";

const navigation = [
  { name: "Overview", path: "/", icon: LayoutDashboard },
  { name: "AI Assistant", path: "/assistant", icon: MessageSquare },
  { name: "Knowledge Base", path: "/documents", icon: Files },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-[260px] flex-col border-r border-slate-200 bg-white">

      {/* Brand */}
      <div className="flex h-[76px] items-center border-b border-slate-100 px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-lg shadow-indigo-200">
            <BrainCircuit size={21} />
          </div>

          <div>
            <h1 className="text-[17px] font-bold tracking-tight text-slate-900">
              KnowFlow<span className="text-indigo-600"> AI</span>
            </h1>
            <p className="text-[10px] font-medium uppercase tracking-[1.5px] text-slate-400">
              Knowledge Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 px-4 pt-8">
        <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[1.5px] text-slate-400">
          Workspace
        </p>

        <nav className="space-y-1">
          {navigation.map(({ name, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-3 text-[13px] font-medium transition-all ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                }`
              }
            >
              <Icon size={18} strokeWidth={1.8} />
              {name}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Administrator */}
      <div className="border-t border-slate-100 p-4">
        <div className="flex items-center gap-3 rounded-lg p-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white">
            DD
          </div>

          <div className="flex-1">
            <p className="text-xs font-semibold text-slate-800">
              Administrator
            </p>
            <p className="text-[11px] text-slate-400">
              KnowFlow AI
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
