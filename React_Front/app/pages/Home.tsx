import {
  ArrowRight,
  Box,
  Database,
  Gauge,
  LayoutDashboard,
  MonitorSmartphone,
  Route as RouteIcon,
  ScanSearch,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
import { Link } from "react-router";

export function meta() {
  return [{ title: "InspectVision | Tissue Defect Detection" }];
}

const FEATURES = [
  {
    icon: ScanSearch,
    title: "Real-time Detection",
    text: "A YOLO model inspects every package on the conveyor and flags damaged ones instantly.",
  },
  {
    icon: RouteIcon,
    title: "Object Tracking",
    text: "Each package gets a unique ID so it is counted once, even across many frames.",
  },
  {
    icon: Gauge,
    title: "Line-crossing Counter",
    text: "Packages are counted exactly when they cross the inspection line, with an adjustable tolerance.",
  },
  {
    icon: Database,
    title: "Automatic Logging",
    text: "Every defect is stored in MySQL with its track ID and timestamp for later review.",
  },
  {
    icon: LayoutDashboard,
    title: "Live Dashboard",
    text: "Watch the camera feed, live counters and inspection logs in a single clean screen.",
  },
  {
    icon: MonitorSmartphone,
    title: "Desktop Ready",
    text: "Runs in the browser or as a standalone desktop application built with Electron.",
  },
];

const STEPS = [
  { title: "Capture", text: "The camera streams the production line frame by frame." },
  { title: "Detect & Track", text: "YOLO finds each package and assigns it a persistent ID." },
  { title: "Classify", text: "When a package crosses the line it is counted and checked for damage." },
  { title: "Log & Display", text: "Defects are saved to the database and shown live on the dashboard." },
];

const TECH = ["YOLO (Ultralytics)", "OpenCV", "FastAPI", "MySQL", "React Router", "Tailwind CSS", "Electron"];

export default function Home() {
  return (
    <>
      {/* Hero */}
      <section className="mx-auto grid max-w-6xl items-center gap-12 px-6 py-16 lg:grid-cols-2 lg:py-24">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-600">
            <span className="size-2 rounded-full bg-blue-500" />
            FINE GRADUATION PROJECT
          </span>
          <h1 className="mt-5 text-4xl font-bold leading-tight text-slate-900 sm:text-5xl">
            Catch tissue packaging defects <span className="text-blue-600">in real time</span>
          </h1>
          <p className="mt-5 max-w-xl text-lg text-slate-600">
            InspectVision uses computer vision to watch the production line, count every package and
            log each damaged one automatically.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/monitor"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700"
            >
              Open Live Monitor
              <ArrowRight className="size-4" />
            </Link>
            <a
              href="#how"
              className="rounded-lg border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm transition-colors hover:bg-slate-50"
            >
              How it works
            </a>
          </div>
        </div>

        {/* Dashboard preview (sample values) */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-600">
              <span className="size-2 rounded-full bg-emerald-500" />
              SYSTEM ACTIVE
            </span>
            <span className="text-[10px] font-semibold uppercase text-slate-400">Sample preview</span>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-3">
            <div className="rounded-lg border border-slate-200 p-3">
              <Box className="size-4 text-blue-600" />
              <p className="mt-2 text-2xl font-bold text-slate-900">128</p>
              <p className="text-[10px] text-slate-500">Tracked</p>
            </div>
            <div className="rounded-lg border border-slate-200 p-3">
              <TriangleAlert className="size-4 text-red-500" />
              <p className="mt-2 text-2xl font-bold text-red-600">7</p>
              <p className="text-[10px] text-slate-500">Defective</p>
            </div>
            <div className="rounded-lg border border-slate-200 p-3">
              <ShieldCheck className="size-4 text-emerald-500" />
              <p className="mt-2 text-sm font-semibold text-emerald-600">Active Mode</p>
              <p className="text-[10px] text-slate-500">Status</p>
            </div>
          </div>

          <div className="relative mt-4 aspect-[1020/500] overflow-hidden rounded-lg bg-[#020617]">
            <div className="absolute left-0 right-0 top-[72%] h-0.5 bg-yellow-300" />
            <div className="absolute left-[18%] top-[30%] h-[28%] w-[16%] rounded border-2 border-emerald-500" />
            <div className="absolute left-[46%] top-[45%] h-[28%] w-[16%] rounded border-2 border-red-500" />
            <span className="absolute left-[46%] top-[39%] text-[10px] font-semibold text-red-500">
              ID: 42 [DAMAGED]
            </span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="scroll-mt-20 border-y border-slate-200 bg-white py-16">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-3xl font-bold text-slate-900">Everything you need to inspect</h2>
          <p className="mx-auto mt-3 max-w-2xl text-center text-slate-500">
            From the camera to the database, one pipeline handles detection, counting and reporting.
          </p>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(({ icon: Icon, title, text }) => (
              <div key={title} className="rounded-xl border border-slate-200 bg-slate-50 p-6">
                <div className="flex size-10 items-center justify-center rounded-lg bg-blue-50">
                  <Icon className="size-5 text-blue-600" />
                </div>
                <h3 className="mt-4 font-semibold text-slate-900">{title}</h3>
                <p className="mt-2 text-sm text-slate-600">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="mx-auto max-w-6xl scroll-mt-20 px-6 py-16">
        <h2 className="text-center text-3xl font-bold text-slate-900">How it works</h2>
        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((s, i) => (
            <div key={s.title} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <span className="flex size-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
                {i + 1}
              </span>
              <h3 className="mt-4 font-semibold text-slate-900">{s.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{s.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Tech stack */}
      <section id="tech" className="scroll-mt-20 border-y border-slate-200 bg-white py-14">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <h2 className="text-3xl font-bold text-slate-900">Built with</h2>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            {TECH.map((t) => (
              <span
                key={t}
                className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-700"
              >
                {t}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="rounded-2xl bg-blue-600 px-8 py-12 text-center shadow-lg">
          <h2 className="text-3xl font-bold text-white">Ready to see it in action?</h2>
          <p className="mx-auto mt-3 max-w-xl text-blue-100">
            Open the live monitor, press Start and watch defects get detected on the production line.
          </p>
          <Link
            to="/monitor"
            className="mt-7 inline-flex items-center gap-2 rounded-lg bg-white px-6 py-3 text-sm font-semibold text-blue-600 transition-colors hover:bg-blue-50"
          >
            Open Live Monitor
            <ArrowRight className="size-4" />
          </Link>
        </div>
      </section>
    </>
  );
}