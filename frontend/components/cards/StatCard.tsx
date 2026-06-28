import { cn } from "@/utils";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color?: string;
  subtitle?: string;
}

export default function StatCard({ title, value, icon: Icon, color = "text-primary-600", subtitle }: StatCardProps) {
  return (
    <div className="card flex items-start gap-4">
      <div className={cn("p-3 rounded-xl bg-gray-50", color.replace("text-", "bg-").replace("600", "50"))}>
        <Icon className={cn("w-6 h-6", color)} />
      </div>
      <div>
        <p className="text-sm text-gray-500 font-medium">{title}</p>
        <p className="text-2xl font-bold text-gray-900 mt-0.5">{value}</p>
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
    </div>
  );
}
