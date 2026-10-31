import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  trend?: {
    value: string;
    direction: 'up' | 'down' | 'neutral';
    sentiment?: 'positive' | 'warning' | 'negative' | 'neutral';
  };
  icon: React.ReactNode;
  accentTone?: 'blue' | 'purple' | 'emerald' | 'amber' | 'red';
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subtext,
  trend,
  icon,
  accentTone = 'blue',
  onClick,
}) => {
  const iconToneMap: Record<NonNullable<StatCardProps['accentTone']>, string> = {
    blue: 'bg-blue-50 text-[#2563EB]',
    purple: 'bg-violet-50 text-[#7C3AED]',
    emerald: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
    red: 'bg-red-50 text-red-600',
  };

  const trendSentimentMap = {
    positive: 'text-emerald-700',
    warning: 'text-amber-700',
    negative: 'text-red-700',
    neutral: 'text-slate-500',
  };

  return (
    <div
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
      className={`bg-white border border-slate-200 rounded-xl p-5 transition-colors duration-150 ${
        onClick ? 'cursor-pointer hover:border-blue-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600' : ''
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1.5 min-w-0">
          <p className="text-xs font-medium text-slate-500 truncate">{label}</p>
          <p className="text-2xl font-bold font-display text-slate-900 tabular-nums tracking-tight">
            {value}
          </p>
        </div>
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${iconToneMap[accentTone]}`}
        >
          {icon}
        </div>
      </div>

      {(trend || subtext) && (
        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center gap-2 text-xs">
          {trend && (
            <span
              className={`inline-flex items-center gap-0.5 font-semibold tabular-nums ${
                trendSentimentMap[trend.sentiment || 'neutral']
              }`}
            >
              {trend.direction === 'up' && <ArrowUpRight className="w-3.5 h-3.5" />}
              {trend.direction === 'down' && <ArrowDownRight className="w-3.5 h-3.5" />}
              {trend.direction === 'neutral' && <Minus className="w-3.5 h-3.5" />}
              {trend.value}
            </span>
          )}
          {trend && subtext && <span className="text-slate-300" aria-hidden="true">·</span>}
          {subtext && <span className="text-slate-500 truncate">{subtext}</span>}
        </div>
      )}
    </div>
  );
};
