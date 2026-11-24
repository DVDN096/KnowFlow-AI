
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <Sidebar />

      <div className="min-h-screen pl-[260px]">
        <Topbar />

        <main className="mx-auto max-w-[1600px] px-8 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
