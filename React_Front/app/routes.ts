import { type RouteConfig, index, layout, route } from "@react-router/dev/routes";

export default [
  layout("components/PublicLayout.tsx", [index("pages/Home.tsx")]),
  layout("components/Layout.tsx", [route("monitor", "pages/LiveMonitor.tsx")]),
] satisfies RouteConfig;