import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GraduationCap,
  Users,
  BookOpen,
  Award,
  CalendarCheck,
  AlertTriangle,
  Download,
  TrendingUp,
  TrendingDown,
  Mail,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  AreaChart,
  Area,
} from 'recharts';
import { useApp } from '../context/AppContext';
import { AT_RISK_STUDENTS, STUDENT_COURSES } from '../data/mockData';
import { AtRiskStudent } from '../types';
import { StatCard } from '../components/StatCard';
import { ChartCard } from '../components/ChartCard';
import { DataTable, ColumnDef } from '../components/DataTable';
import { Button } from '../components/Button';

export const HODDashboard: React.FC = () => {
  const { departments, addToast } = useApp();
  const navigate = useNavigate();

  const totalStudents = departments.reduce((acc, d) => acc + d.totalStudents, 0);
  const totalFaculty = departments.reduce((acc, d) => acc + d.totalFaculty, 0);
  const totalCourses = departments.reduce((acc, d) => acc + d.totalCourses, 0);
  const totalAtRisk = departments.reduce((acc, d) => acc + d.atRiskCount, 0);
  const avgDeptPerformance = (
    departments.reduce((acc, d) => acc + d.avgPerformance, 0) / departments.length
  ).toFixed(1);
  const overallAttendance = (
    departments.reduce((acc, d) => acc + d.attendanceRate, 0) / departments.length
  ).toFixed(1);

  const sortedSubjects = [...STUDENT_COURSES].sort((a, b) => b.avgScore - a.avgScore);
  const topSubjects = sortedSubjects.slice(0, 3);
  const weakSubjects = [...sortedSubjects].reverse().slice(0, 3);

  const handleDownloadReport = () => {
    const headers = [
      'Department Code',
      'Department Name',
      'HOD',
      'Students',
      'Faculty',
      'Courses',
      'Avg Performance (%)',
      'Attendance (%)',
      'At-Risk Students',
    ];
    const rows = departments.map((d) => [
      d.code,
      `"${d.name}"`,
      `"${d.hodName}"`,
      d.totalStudents,
      d.totalFaculty,
      d.totalCourses,
      d.avgPerformance,
      d.attendanceRate,
      d.atRiskCount,
    ]);
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'LearnPath_HOD_Department_Analytics_2026.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    addToast(
      'Department Report Exported',
      'Downloaded LearnPath_HOD_Department_Analytics_2026.csv',
      'success'
    );
  };

  const supportColumns: ColumnDef<AtRiskStudent>[] = [
    {
      key: 'student',
      header: 'Student & Roll No.',
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
      sortable: true,
      sortValue: (r) => r.department,
      render: (r) => <span className="text-xs text-slate-700">{r.department}</span>,
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
      key: 'mentorAssigned',
      header: 'Faculty Advisor',
      render: (r) => <span className="text-xs text-slate-700">{r.mentorAssigned}</span>,
    },
    {
      key: 'notify',
      header: 'Counseling',
      align: 'right',
      render: (r) => (
        <Button
          size="sm"
          variant="outline"
          leftIcon={<Mail className="w-3.5 h-3.5 text-[#2563EB]" />}
          onClick={() =>
            addToast(
              'Faculty Mentor Escalated',
              `Scheduled academic review between ${r.name} and ${r.mentorAssigned}.`,
              'info'
            )
          }
        >
          Schedule Review
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs font-medium text-slate-500">
            Head of Department Governance · Odd Semester 2026–27
          </p>
          <h1 className="text-2xl font-bold font-display text-slate-900 tracking-tight">
            Department & Curriculum Outcome Overview
          </h1>
          <p className="text-sm text-slate-600">
            Cross-sectional performance benchmarking, NBA outcome attainment, and proactive
            at-risk student tracking.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <Button
            variant="outline"
            onClick={() => navigate('/hod/analytics')}
          >
            Subject Analytics
          </Button>
          <Button
            variant="primary"
            leftIcon={<Download className="w-4 h-4" />}
            onClick={handleDownloadReport}
          >
            Download Reports (CSV)
          </Button>
        </div>
      </div>

      {/* 6 KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          label="Total Students"
          value={totalStudents.toLocaleString()}
          subtext="UG & PG cohorts"
          icon={<GraduationCap className="w-5 h-5" />}
          accentTone="blue"
          onClick={() => navigate('/hod/students')}
        />
        <StatCard
          label="Total Faculty"
          value={totalFaculty}
          subtext="5 Engineering Depts"
          icon={<Users className="w-5 h-5" />}
          accentTone="purple"
          onClick={() => navigate('/hod/faculty')}
        />
        <StatCard
          label="Total Courses"
          value={totalCourses}
          subtext="Core & Electives"
          icon={<BookOpen className="w-5 h-5" />}
          accentTone="blue"
          onClick={() => navigate('/hod/courses')}
        />
        <StatCard
          label="Dept Avg Performance"
          value={`${avgDeptPerformance}%`}
          trend={{ value: '+2.8%', direction: 'up', sentiment: 'positive' }}
          icon={<Award className="w-5 h-5" />}
          accentTone="emerald"
          onClick={() => navigate('/hod/analytics')}
        />
        <StatCard
          label="Overall Attendance"
          value={`${overallAttendance}%`}
          trend={{ value: '+1.1%', direction: 'up', sentiment: 'positive' }}
          icon={<CalendarCheck className="w-5 h-5" />}
          accentTone="emerald"
          onClick={() => navigate('/hod/attendance-analytics')}
        />
        <StatCard
          label="At-Risk Students"
          value={totalAtRisk}
          trend={{ value: '-6 vs Sep', direction: 'down', sentiment: 'positive' }}
          icon={<AlertTriangle className="w-5 h-5" />}
          accentTone="red"
          onClick={() => navigate('/hod/at-risk')}
        />
      </div>

      {/* Department-Wise & Subject-Wise Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <ChartCard
          title="Department-Wise Performance & Attendance"
          subtitle="Mean academic score (%) vs. average lecture attendance (%) across engineering branches"
          className="lg:col-span-7"
        >
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={departments}
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
                  dataKey="avgPerformance"
                  name="Avg Performance (%)"
                  fill="#2563EB"
                  radius={[6, 6, 0, 0]}
                  barSize={24}
                />
                <Bar
                  dataKey="attendanceRate"
                  name="Attendance (%)"
                  fill="#7C3AED"
                  radius={[6, 6, 0, 0]}
                  barSize={24}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard
          title="Subject-Wise Score Trajectory"
          subtitle="Average score & syllabus completion (%) across core Semester 5 subjects"
          className="lg:col-span-5"
        >
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={STUDENT_COURSES}
                margin={{ top: 8, right: 12, left: -16, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="hodBlueGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563EB" stopOpacity={0.22} />
                    <stop offset="95%" stopColor="#2563EB" stopOpacity={0.01} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis
                  dataKey="code"
                  tick={{ fill: '#475569', fontSize: 12 }}
                  axisLine={{ stroke: '#E2E8F0' }}
                  tickLine={false}
                />
                <YAxis
                  domain={[40, 100]}
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
                <Area
                  type="monotone"
                  dataKey="avgScore"
                  name="Subject Mean Score (%)"
                  stroke="#2563EB"
                  strokeWidth={2.5}
                  fill="url(#hodBlueGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Top-Performing Subjects vs Weak-Performing Subjects */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="bg-white border border-slate-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold font-display text-slate-900">
                Top-Performing Subjects
              </h3>
              <p className="text-xs text-slate-500">
                Courses exceeding 78% cohort mean mastery
              </p>
            </div>
            <TrendingUp className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="divide-y divide-slate-100">
            {topSubjects.map((sub) => (
              <div
                key={sub.id}
                className="py-3 first:pt-0 last:pb-0 flex items-center justify-between gap-3"
              >
                <div>
                  <p className="text-sm font-semibold text-slate-900">
                    {sub.code} · {sub.name}
                  </p>
                  <p className="text-xs text-slate-500">
                    Faculty: {sub.faculty} · {sub.enrolledStudents} students
                  </p>
                </div>
                <span className="text-sm font-bold font-mono tabular-nums text-emerald-600">
                  {sub.avgScore}%
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-white border border-slate-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold font-display text-slate-900">
                Weak-Performing Subjects Requiring Focus
              </h3>
              <p className="text-xs text-slate-500">
                Courses prioritized for adaptive diagnostic intervention
              </p>
            </div>
            <TrendingDown className="w-5 h-5 text-amber-600" />
          </div>
          <div className="divide-y divide-slate-100">
            {weakSubjects.map((sub) => (
              <div
                key={sub.id}
                className="py-3 first:pt-0 last:pb-0 flex items-center justify-between gap-3"
              >
                <div>
                  <p className="text-sm font-semibold text-slate-900">
                    {sub.code} · {sub.name}
                  </p>
                  <p className="text-xs text-slate-500">
                    Faculty: {sub.faculty} · Attendance {sub.attendanceRate}%
                  </p>
                </div>
                <span
                  className={`text-sm font-bold font-mono tabular-nums ${
                    sub.avgScore < 65 ? 'text-red-600' : 'text-amber-600'
                  }`}
                >
                  {sub.avgScore}%
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Students Requiring Additional Support */}
      <DataTable
        title="Students Requiring Additional Academic Support"
        subtitle="Cross-departmental watchlist with direct faculty advisor escalation"
        data={AT_RISK_STUDENTS}
        columns={supportColumns}
        rowKey={(r) => r.id}
        searchPlaceholder="Search student, roll number, or advisor..."
        searchMatcher={(r, q) =>
          r.name.toLowerCase().includes(q) ||
          r.rollNo.toLowerCase().includes(q) ||
          r.department.toLowerCase().includes(q) ||
          r.mentorAssigned.toLowerCase().includes(q)
        }
        filterOptions={[
          { label: 'Critical', value: 'Critical' },
          { label: 'Moderate', value: 'Moderate' },
        ]}
        filterMatcher={(r, f) => r.riskLevel === f}
      />
    </div>
  );
};
