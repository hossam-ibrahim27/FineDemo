import type { Route } from "./+types/home";
import Traffic from "~/pages/Traffic";

export function meta({ }: Route.MetaArgs) {
  return [
    { title: "Fine Graduation Project Demo" },
    { name: "description", content: "AI Powered Defect Detection System" },
  ];
}

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <Traffic/>
    </main>
  );
}