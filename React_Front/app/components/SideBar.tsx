import { Activity, Camera } from "lucide-react";

const SideBar = () => {
    return (
        <>
           <aside className="w-64 bg-white border-r border-slate-200 p-6 hidden md:flex md:flex-col justify-between">
                <div>
                    <div className="flex items-center gap-2">
                        <Activity className="text-blue-500 w-6 h-6" />
                        <h2 className="text-xl font-bold text-slate-900">InspectVision</h2>
                    </div>
                    <p className="text-xs text-slate-500 mt-4">Tissue & Packaging Defect Monitor</p>
                    <nav className="mt-4">
                        <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-blue-50 text-blue-600 font-semibold text-sm cursor-pointer transition-colors">
                        <Camera className="w-4 h-4" />
                        <span>Live Monitor</span>
                        </div>
                    </nav>
                </div>
                <div className="border-t border-slate-100 pt-4">
                    <p className="text-sm font-semibold text-slate-800">InspectVision Core</p>
                    <p className="text-xs text-slate-400">© 2026 Fine Graduation Project Team</p>
                </div>
            </aside>
        </>
    )
}

export default SideBar;