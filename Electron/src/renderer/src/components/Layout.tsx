import { Outlet } from 'react-router'
import Sidebar from './Sidebar'

export default function Layout(): React.JSX.Element {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="min-w-0 flex-1 p-6 md:p-8">
        <Outlet />
      </main>
    </div>
  )
}