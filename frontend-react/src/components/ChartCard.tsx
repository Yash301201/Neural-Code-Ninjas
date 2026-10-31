import React from 'react';
import { AlertCircle } from 'lucide-react';
import { Button } from './Button';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  isLoading?: boolean;
  isEmpty?: boolean;
  emptyMessage?: string;
  error?: string | null;
  onRetry?: () => void;
  children: React.ReactNode;
  className?: string;
}

export const ChartCard: React.FC<ChartCardProps> = ({
  title,
  subtitle,
  action,
  isLoading = false,
  isEmpty = false,
  emptyMessage = 'No academic records match the selected filters.',
  error = null,
  onRetry,
  children,
  className = '',
}) => {
  return (
    <section
      className={`bg-white border border-slate-200 rounded-xl p-5 flex flex-col ${className}`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3 mb-5">
        <div className="space-y-0.5">
          <h3 className="text-base font-semibold text-slate-900 font-display">{title}</h3>
          {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </div>

      {isLoading ? (
        <div className="h-64 w-full flex flex-col justify-end gap-3 p-4 bg-slate-50/70 rounded-lg animate-pulse">
          <div className="grid grid-cols-6 items-end gap-4 h-44">
            <div className="bg-slate-200 rounded-t h-24" />
            <div className="bg-slate-200 rounded-t h-36" />
            <div className="bg-slate-200 rounded-t h-28" />
            <div className="bg-slate-200 rounded-t h-40" />
            <div className="bg-slate-200 rounded-t h-32" />
            <div className="bg-slate-200 rounded-t h-44" />
          </div>
          <div className="h-3 bg-slate-200 rounded w-1/3" />
        </div>
      ) : error ? (
        <div className="h-64 flex flex-col items-center justify-center text-center px-4 bg-red-50/40 rounded-lg">
          <AlertCircle className="w-7 h-7 text-red-600 mb-2" />
          <p className="text-sm font-medium text-slate-900">{error}</p>
          {onRetry && (
            <div className="mt-3">
              <Button size="sm" variant="outline" onClick={onRetry}>
                Retry Load
              </Button>
            </div>
          )}
        </div>
      ) : isEmpty ? (
        <div className="h-64 flex flex-col items-center justify-center text-center px-4 bg-slate-50 rounded-lg">
          <p className="text-sm font-medium text-slate-700">{emptyMessage}</p>
          <p className="text-xs text-slate-500 mt-1">
            Adjust department or semester filters to view performance data.
          </p>
        </div>
      ) : (
        <div className="w-full flex-1 min-h-[260px]">{children}</div>
      )}
    </section>
  );
};
