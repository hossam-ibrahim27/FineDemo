import type { ReactNode } from "react";

interface DashboardCardProps {
  title: string;
  count: ReactNode;
  component: ReactNode;
}

const DashboardCards = ({ title, count, component }: DashboardCardProps) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm transition-all hover:shadow-md">
      <div className="flex justify-between items-center text-slate-500 text-xs font-medium">
        <span>{title}</span>
        {component}
      </div>
      {count}
    </div>
  );
};

export default DashboardCards;