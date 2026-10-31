import React, { useState, useMemo } from 'react';
import { Search, ArrowUpDown, RotateCcw } from 'lucide-react';
import { Button } from './Button';

export interface ColumnDef<T> {
  key: string;
  header: string;
  align?: 'left' | 'right' | 'center';
  sortable?: boolean;
  sortValue?: (row: T) => string | number;
  render: (row: T) => React.ReactNode;
}

interface FilterOption {
  label: string;
  value: string;
}

interface DataTableProps<T> {
  title?: string;
  subtitle?: string;
  data: T[];
  columns: ColumnDef<T>[];
  rowKey: (row: T) => string;
  searchPlaceholder?: string;
  searchMatcher?: (row: T, query: string) => boolean;
  filterOptions?: FilterOption[];
  filterMatcher?: (row: T, filterValue: string) => boolean;
  headerActions?: React.ReactNode;
  isLoading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
}

export function DataTable<T>({
  title,
  subtitle,
  data,
  columns,
  rowKey,
  searchPlaceholder = 'Search records...',
  searchMatcher,
  filterOptions,
  filterMatcher,
  headerActions,
  isLoading = false,
  emptyTitle = 'No matching records found',
  emptyDescription = 'Try clearing your search query or switching the active filter.',
}: DataTableProps<T>) {
  const [query, setQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortAsc, setSortAsc] = useState<boolean>(true);

  const filteredData = useMemo(() => {
    let list = [...data];
    if (query.trim() && searchMatcher) {
      const q = query.trim().toLowerCase();
      list = list.filter((row) => searchMatcher(row, q));
    }
    if (activeFilter !== 'all' && filterMatcher) {
      list = list.filter((row) => filterMatcher(row, activeFilter));
    }
    if (sortKey) {
      const col = columns.find((c) => c.key === sortKey);
      if (col?.sortValue) {
        list.sort((a, b) => {
          const va = col.sortValue!(a);
          const vb = col.sortValue!(b);
          if (va < vb) return sortAsc ? -1 : 1;
          if (va > vb) return sortAsc ? 1 : -1;
          return 0;
        });
      }
    }
    return list;
  }, [data, query, activeFilter, sortKey, sortAsc, searchMatcher, filterMatcher, columns]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
      {(title || searchMatcher || filterOptions || headerActions) && (
        <div className="p-5 border-b border-slate-200 space-y-4">
          {(title || headerActions) && (
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                {title && (
                  <h3 className="text-base font-semibold text-slate-900 font-display">
                    {title}
                  </h3>
                )}
                {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
              </div>
              {headerActions && <div className="flex items-center gap-2">{headerActions}</div>}
            </div>
          )}

          {(searchMatcher || filterOptions) && (
            <div className="flex flex-wrap items-center justify-between gap-3">
              {searchMatcher && (
                <div className="relative flex-1 min-w-[220px] max-w-sm">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={searchPlaceholder}
                    className="w-full pl-9 pr-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg text-slate-900 placeholder:text-slate-400 focus:outline-none focus:bg-white focus:border-blue-600 transition-colors"
                  />
                </div>
              )}

              {filterOptions && filterOptions.length > 0 && (
                <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg overflow-x-auto max-w-full">
                  <button
                    type="button"
                    onClick={() => setActiveFilter('all')}
                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0 cursor-pointer ${
                      activeFilter === 'all'
                        ? 'bg-white text-slate-900 shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    All
                  </button>
                  {filterOptions.map((opt) => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => setActiveFilter(opt.value)}
                      className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0 cursor-pointer ${
                        activeFilter === opt.value
                          ? 'bg-white text-slate-900 shadow-xs'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/70">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-5 py-3 text-xs font-semibold text-slate-600 whitespace-nowrap ${
                    col.align === 'right'
                      ? 'text-right'
                      : col.align === 'center'
                      ? 'text-center'
                      : 'text-left'
                  }`}
                >
                  {col.sortable ? (
                    <button
                      type="button"
                      onClick={() => handleSort(col.key)}
                      className="inline-flex items-center gap-1 hover:text-slate-900 transition-colors cursor-pointer"
                    >
                      <span>{col.header}</span>
                      <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
                    </button>
                  ) : (
                    col.header
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm">
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <tr key={`skeleton-${i}`} className="animate-pulse">
                  {columns.map((col) => (
                    <td key={col.key} className="px-5 py-3.5">
                      <div className="h-4 bg-slate-200 rounded w-3/4" />
                    </td>
                  ))}
                </tr>
              ))
            ) : filteredData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-5 py-12 text-center">
                  <p className="text-sm font-medium text-slate-800">{emptyTitle}</p>
                  <p className="text-xs text-slate-500 mt-1">{emptyDescription}</p>
                  {(query || activeFilter !== 'all') && (
                    <div className="mt-4">
                      <Button
                        size="sm"
                        variant="outline"
                        leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
                        onClick={() => {
                          setQuery('');
                          setActiveFilter('all');
                        }}
                      >
                        Reset Filters
                      </Button>
                    </div>
                  )}
                </td>
              </tr>
            ) : (
              filteredData.map((row) => (
                <tr
                  key={rowKey(row)}
                  className="hover:bg-slate-50/80 transition-colors duration-100"
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={`px-5 py-3.5 text-slate-700 ${
                        col.align === 'right'
                          ? 'text-right tabular-nums'
                          : col.align === 'center'
                          ? 'text-center'
                          : 'text-left'
                      }`}
                    >
                      {col.render(row)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
