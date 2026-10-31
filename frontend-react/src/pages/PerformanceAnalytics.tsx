import React, { useState, useMemo } from 'react';
import {
  Award,
  CalendarCheck,
  ClipboardCheck,
  AlertTriangle,
  Download,
  Filter,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import {
  STUDENT_COURSES,
  MONTHLY_PROGRESS_DATA,
  PERFORMANCE_DISTRIBUTION,
  AT_RISK_STUDENTS,
  STUDENT_WEAK_TOPICS,
} from '../data/mockData';
import { AtRiskStudent } from '../types';
import { useApp } from '../context/AppContext';
import { StatCard } from '../components/StatCard';
import { ChartCard } from '../components/ChartCard';
import { DataTable, ColumnDef } from '../components/DataTable';
import { Button } from '../components/Button';

const TOPIC_MASTERY_DATA = [
  { topic: 'Graph & Greedy Algorithms', mastery: 91, assignmentsScore: 92 },
  { topic: 'TCP Congestion Control', mastery: 84, assignmentsScore: 86 },
  { topic: 'Process Synchronization', mastery: 77, assignmentsScore: 80 },
  { topic: 'SQL Joins & Aggregations', mastery: 56, assignmentsScore: 64 },
  { topic: 'BCNF Normalization', mastery: 48, assignmentsScore: 58 },
];

export const PerformanceAnalytics: React.FC = () => {
  const { departments, addToast } = useApp();

  const [selectedDept, setSelectedDept] = useState<string>('ALL');
  const [dateRange, setDateRange] = useState<'sem' | '30d' | 'year'>('sem');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const handleFilterChange = (nextDept: string, nextRange: 'sem' | '30d' | 'year') => {
    setIsRefreshing(true);
    setSelectedDept(nextDept);
    setDateRange(nextRange);
    setTimeout(() => {
      setIsRefreshing(false);
    }, 280);
  };

  // Adjust numbers slightly based on active filter so filters demonstrably recalculate charts & KPIs
  const deptMultiplier =
    selectedDept === 'ALL'
      ? 1
      : selectedDept === 'Computer Science & Engineering'
      ? 1.03
      : selectedDept === 'Electronics & Communication'
      ? 0.97
      : 0.95;

  const rangeOffset = dateRange === '30d' ? 2 : dateRange === 'year' ? -1.5 : 0;

  const filteredMonthlyData = useMemo(
    () =>
      MONTHLY_PROGRESS_DATA.map((m) => ({
        ...m,
        studentAvg: Math.min(100, Math.round((m.studentAvg + rangeOffset) * deptMultiplier)),
        deptAvg: Math.min(100, Math.round((m.deptAvg + rangeOffset) * deptMultiplier)),
        attendance: Math.min(100, Math.round(m.attendance * deptMultiplier)),
      })),
    [deptMultiplier, rangeOffset]
  );

  const filteredSubjects = useMemo(
    () =>
      STUDENT_COURSES.map((s) => ({
        code: s.code,
        name: s.name,
        avgScore: Math.min(100, Math.round((s.avgScore + rangeOffset) * deptMultiplier)),
        attendanceRate: Math.min(100, Math.round(s.attendanceRate * deptMultiplier)),
        assignmentAvg: Math.min(
          100,
          Math.round((s.avgScore * 0.9 + 10 + rangeOffset) * deptMultiplier)
        ),
      })),
    [deptMultiplier, rangeOffset]
  );

  const filteredAtRisk = useMemo(
    () =>
      selectedDept === 'ALL'
        ? AT_RISK_STUDENTS
        : AT_RISK_STUDENTS.filter((s) => s.department === selectedDept),
    [selectedDept]
  );

  const avgMarksMetric = (78.5 * deptMultiplier + rangeOffset).toFixed(1);
  const attendanceMetric = Math.min(98, 86.4 * deptMultiplier).toFixed(1);
  const assignmentMetric = Math.min(98, 84.2 * deptMultiplier + rangeOffset).toFixed(1);

  const handleExportAnalytics = () => {
    const headers = ['Subject Code', 'Subject Name', 'Avg Marks (%)', 'Attendance (%)', 'Assignment Score (%)'];
    const rows = filteredSubjects.map((s) => [
      s.code,
      `"${s.name}"`,
      s.avgScore,
      s.attendanceRate,
      s.assignmentAvg,
    ]);
    const csv =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csv));
    link.setAttribute('download', `LearnPath_Academic_Analytics_${dateRange}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    addToast(
      'Analytics Report Exported',
      `Saved LearnPath_Academic_Analytics_${dateRange}.csv`,
      'success'
    );
  };

  const atRiskColumns: ColumnDef<AtRiskStudent>[] = [
    {
      key: 'student',
      header: 'Student',
      sortable: true,
      sortValue: (r) => r.name,
      render: (r) => (
        <div>
          <p className="font-semibold text-slate-900">{r.name}</p>
          <p className="text-xs text-slate-500 font-mono">{r.rollNo}</p>
        </div>
      ),
    },
    {
      key: 'department',
      header: 'Department',
      render: (r) => <span className="text-xs text-slate-600">{r.department}</span>,
    },
    {
      key: 'avgMarks',
      header: 'Avg. Marks',
      align: 'right',
      sortable: true,
      sortValue: (r) => r.avgMarks,
      render: (r) => (
        <span className="font-mono font-semibold text-red-600">{r.avgMarks}%</span>
      ),
    },
    {
      key: 'attendance',
      header: 'Attendance',
      align: 'right',
      sortable: true,
      sortValue: (r) => r.attendance,
      render: (r) => <span className="font-mono">{r.attendance}%</span>,
    },
    {
      key: 'weak',
      header: 'Weak Topic Cluster',
      render: (r) => <span className="text-xs text-slate-600">{r.weakSubjects.join(' · ')}</span>,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header + Date & Department Filters + Export Button */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col xl:flex-row xl:items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs font-medium text-slate-500">
            Academic Intelligence & Outcome Telemetry
          </p>
          <h1 className="text-2xl font-bold font-display text-slate-900 tracking-tight">
            Performance, Attendance & Topic Mastery Analytics
          </h1>
          <p className="text-sm text-slate-600">
            Examine longitudinal assessment trends, assignment completion, grade
            distributions, and early-warning risk cohorts.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <div className="relative flex items-center">
            <Filter className="w-3.5 h-3.5 text-slate-400 absolute left-3 pointer-events-none" />
            <select
              aria-label="Filter by department"
              value={selectedDept}
              onChange={(e) => handleFilterChange(e.target.value, dateRange)}
              className="pl-8 pr-4 py-2 text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:border-[#2563EB]"
            >
              <option value="ALL">All Engineering Departments</option>
              {departments.map((d) => (
                <option key={d.id} value={d.name}>
                  {d.code} — {d.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg">
            {(
              [
                { id: '30d', label: 'Last 30 Days' },
                { id: 'sem', label: 'Current Sem' },
                { id: 'year', label: 'AY 2026–27' },
              ] as const
            ).map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => handleFilterChange(selectedDept, opt.id)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors cursor-pointer ${
                  dateRange === opt.id
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          <Button
            variant="primary"
            size="md"
            leftIcon={<Download className="w-4 h-4" />}
            onClick={handleExportAnalytics}
          >
            Export Report
          </Button>
        </div>
      </div>

      {/* 4 Overview KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="Average Assessment Marks"
          value={`${avgMarksMetric}%`}
          trend={{ value: '+3.9%', direction: 'up', sentiment: 'positive' }}
          subtext="Across mid-terms & quizzes"
          icon={<Award className="w-5 h-5" />}
          accentTone="blue"
        />
        <StatCard
          label="Attendance Analysis"
          value={`${attendanceMetric}%`}
          trend={{ value: '+1.6%', direction: 'up', sentiment: 'positive' }}
          subtext="Lecture + Lab sessions"
          icon={<CalendarCheck className="w-5 h-5" />}
          accentTone="emerald"
        />
        <StatCard
          label="Assignment Performance"
          value={`${assignmentMetric}%`}
          subtext="94.2% on-time submission"
          icon={<ClipboardCheck className="w-5 h-5" />}
          accentTone="purple"
        />
        <StatCard
          label="At-Risk Students Identified"
          value={filteredAtRisk.length}
          subtext="Below 62% score or 75% attendance"
          icon={<AlertTriangle className="w-5 h-5" />}
          accentTone="red"
        />
      </div>

      {/* Monthly Progress Chart + Subject-Wise Exam vs Assignment Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <ChartCard
          title="Monthly Academic Progress & Attendance Trend"
          subtitle="Longitudinal progression of student score, department mean, and attendance (%)"
          isLoading={isRefreshing}
          className="lg:col-span-6"
        >
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={filteredMonthlyData}
                margin={{ top: 8, right: 12, left: -16, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis
                  dataKey="month"
                  tick={{ fill: '#475569', fontSize: 12 }}
                  axisLine={{ stroke: '#E2E8F0' }}
                  tickLine={false}
                />
                <YAxis
                  domain={[50, 100]}
                  tick={{ fill: '#64748B', fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E2E8F0',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Line
                  type="monotone"
                  dataKey="studentAvg"
                  name="Assessment Avg (%)"
                  stroke="#2563EB"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="attendance"
                  name="Attendance Rate (%)"
                  stroke="#16A34A"
                  strokeWidth={2}
                  dot={{ r: 3.5 }}
                />
                <Line
                  type="monotone"
                  dataKey="deptAvg"
                  name="Department Benchmark (%)"
                  stroke="#7C3AED"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard
          title="Subject-Wise Exam, Assignment & Attendance Breakdown"
          subtitle="Triangulated comparison per course code"
          isLoading={isRefreshing}
          className="lg:col-span-6"
        >
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={filteredSubjects}
                margin={{ top: 8, right: 12, left: -16, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis
                  dataKey="code"
                  tick={{ fill: '#475569', fontSize: 12 }}
                  axisLine={{ stroke: '#E2E8F0' }}
                  tickLine={false}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fill: '#64748B', fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E2E8F0',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Bar
                  dataKey="avgScore"
                  name="Exam Score (%)"
                  fill="#2563EB"
                  radius={[4, 4, 0, 0]}
                  barSize={16}
                />
                <Bar
                  dataKey="assignmentAvg"
                  name="Assignment (%)"
                  fill="#7C3AED"
                  radius={[4, 4, 0, 0]}
                  barSize={16}
                />
                <Bar
                  dataKey="attendanceRate"
                  name="Attendance (%)"
                  fill="#16A34A"
                  radius={[4, 4, 0, 0]}
                  barSize={16}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Topic-Wise Performance + Performance Distribution Chart + Weak Topic Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Topic-Wise Performance */}
        <section className="lg:col-span-4 bg-white border border-slate-200 rounded-xl p-5 space-y-4">
          <div>
            <h3 className="text-base font-semibold font-display text-slate-900">
              Topic-Wise Mastery Index
            </h3>
            <p className="text-xs text-slate-500">
              Granular syllabus competency across evaluated units
            </p>
          </div>

          <div className="space-y-3.5">
            {TOPIC_MASTERY_DATA.map((item) => (
              <div key={item.topic} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-slate-800">{item.topic}</span>
                  <span className="font-mono font-semibold tabular-nums text-slate-900">
                    {item.mastery}%
                  </span>
                </div>
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      item.mastery >= 80
                        ? 'bg-emerald-600'
                        : item.mastery >= 65
                        ? 'bg-[#2563EB]'
                        : 'bg-amber-500'
                    }`}
                    style={{ width: `${item.mastery}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Performance Distribution Chart */}
        <ChartCard
          title="Cohort Grade & Score Distribution"
          subtitle="Student count across university grade bands"
          isLoading={isRefreshing}
          className="lg:col-span-5"
        >
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={PERFORMANCE_DISTRIBUTION}
                margin={{ top: 8, right: 8, left: -20, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis
                  dataKey="band"
                  tick={{ fill: '#475569', fontSize: 11 }}
                  axisLine={{ stroke: '#E2E8F0' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: '#64748B', fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E2E8F0',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Bar
                  dataKey="count"
                  name="Students"
                  fill="#7C3AED"
                  radius={[6, 6, 0, 0]}
                  barSize={28}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        {/* Weak Topic Diagnostic Summary */}
        <section className="lg:col-span-3 bg-white border border-slate-200 rounded-xl p-5 space-y-3.5">
          <div>
            <h3 className="text-base font-semibold font-display text-slate-900">
              Weak Topic Analysis
            </h3>
            <p className="text-xs text-slate-500">Lowest accuracy syllabus concepts</p>
          </div>

          <div className="divide-y divide-slate-100">
            {STUDENT_WEAK_TOPICS.map((wt) => (
              <div key={wt.id} className="py-2.5 first:pt-0 last:pb-0 space-y-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-semibold text-slate-900 truncate">
                    {wt.topic}
                  </span>
                  <span className="text-xs font-mono font-bold text-red-600 tabular-nums">
                    {wt.accuracy}%
                  </span>
                </div>
                <p className="text-[11px] text-slate-500">
                  {wt.subjectCode} · {wt.recommendedAction}
                </p>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* At-Risk Student Identification Table */}
      <DataTable
        title="At-Risk Student Identification"
        subtitle="Automated academic early-warning table filtered by selected department"
        data={filteredAtRisk}
        columns={atRiskColumns}
        rowKey={(r) => r.id}
        isLoading={isRefreshing}
        searchPlaceholder="Search student name, roll number, or weak subject..."
        searchMatcher={(r, q) =>
          r.name.toLowerCase().includes(q) ||
          r.rollNo.toLowerCase().includes(q) ||
          r.weakSubjects.join(' ').toLowerCase().includes(q)
        }
      />
    </div>
  );
};
