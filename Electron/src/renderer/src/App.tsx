import { HashRouter, Route, Routes } from 'react-router'
import Layout from '~/components/Layout'
import PublicLayout from '~/components/PublicLayout'
import Home from '~/pages/Home'
import LiveMonitor from '~/pages/LiveMonitor'

export default function App(): React.JSX.Element {
  return (
    <HashRouter>
      <Routes>
        <Route element={<PublicLayout />}>
          <Route index element={<Home />} />
        </Route>
        <Route element={<Layout />}>
          <Route path="monitor" element={<LiveMonitor />} />
        </Route>
      </Routes>
    </HashRouter>
  )
}