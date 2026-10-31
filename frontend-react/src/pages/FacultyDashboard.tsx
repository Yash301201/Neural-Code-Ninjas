import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  BookMarked,
  FileCheck2,
  CheckSquare,
  Wand2,
  FilePlus2,
  CalendarCheck,
  AlertTriangle,
  ArrowRight,
  Send,
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
} from 'recharts';
import { useApp } from '../context/AppContext';
import { AT_RISK_STUDENTS, UPCOMING_TESTS } from '../data/mockData';
import { AtRiskStudent } from '../types';
import { StatCard } from '../components/StatCard';
import { ChartCard } from '../components/ChartCard';
import { DataTable, ColumnDef } from '../components/DataTable';
import { Button } from '../components/Button';

const FACULTY_SUBJECT_STATS = [
  { code: 'CS302 (Sec A)', avgMarks: 74, passRate: 91, highest: 96 },
  { code: 'CS302 (Sec B)', avgMarks: 69, passRate: 86, highest: 94 },
  { code: 'CS412 (Adv DB)', avgMarks: 82, passRate: 97, highest: 98 },
  { code: 'CS302 Lab', avgMarks: 86, passRate: 98, highest: 100 },
];

const RECENT_EXAM_ACTIVITY = [
  {
    id: 'fa-1',
    title: 'CS302 Mid-Term II Evaluation Progress',
    detail: '106 of 124 answer scripts graded · 18 pending descriptive reviews',
    time: '35 mins ago',
  },
  {
    id: 'fa-2',
    title: 'Adaptive SQL Diagnostic Published for Section B',
    detail: 'Scheduled Nov 2, 10:30 AM · 8 Bloom-calibrated MCQs',
    time: '3 hours ago',
  },
  {
    id: 'fa-3',
    title: 'Question Bank Expanded (+12 BCNF & ARIES Items)',
    detail: 'Generated and verified via AI Question Generator',
    time: 'Yesterday',
  },
];

export const FacultyDashboard: React.FC = () => {
  const { currentUser, questionBank, addToast } = useApp();
  const navigate = useNavigate();

  const cseAttentionStudents = AT_RISK_STUDENTS;

  const columns: ColumnDef<AtRiskStudent>[] = [
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
      key: 'avgMarks',
      header: 'Avg. Score',
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
      render: (r) => (
        <span className="font-mono text-slate-700">{r.attendance}%</span>
      ),
    },
    {
      key: 'weakSubjects',
      header: 'Diagnostic Weak Areas',
      render: (r) => (
        <span className="text-xs text-slate-600">{r.weakSubjects.join(' · ')}</span>
      ),
    },
    {
      key: 'action',
      header: 'Intervention',
      align: 'right',
      render: (r) => (
        <Button
          size="sm"
          variant="outline"
          leftIcon={<Send className="w-3.5 h-3.5 text-[#7C3AED]" />}
          onClick={() =>
            addToast(
              'Remediation Assigned',
              `Dispatched 5-day personalized DBMS & OS practice pack to ${r.name} (${r.rollNo}).`,
              'success'
            )
          }
        >
          Assign Remedial Pack
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header + Quick Action Buttons */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs font-medium text-slate-500">
            {currentUser?.department || 'Computer Science & Engineering'} ·{' '}
            {currentUser?.designation || 'Associate Professor'} · ID{' '}
            <span className="font-mono">{currentUser?.rollOrEmpId || 'FAC-CS-209'}</span>
          </p>
          <h1 className="text-2xl font-bold font-display text-slate-900 tracking-tight">
            Faculty Teaching & Assessment Console
          </h1>
          <p className="text-sm text-slate-600">
            Manage {questionBank.length} curated Question Bank items, monitor cohort
            comprehension, and author adaptive tests.
          </p>
        </div>

        {/* Quick Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <Button
            variant="outline"
            leftIcon={<CalendarCheck className="w-4 h-4 text-slate-600" />}
            onClick={() => navigate('/faculty/attendance')}
          >
            Mark Attendance
          </Button>
          <Button
            variant="outline"
            leftIcon={<FilePlus2 className="w-4 h-4 text-[#2563EB]" />}
            onClick={() => navigate('/faculty/create-test')}
          >
            Create Test
          </Button>
          <Button
            variant="ai"
            leftIcon={<Wand2 className="w-4 h-4" />}
            onClick={() => navigate('/faculty/question-generator')}
          >
            AI Question Generator
          </Button>
        </div>
      </div>

      {/* 4 KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="Total Enrolled Students"
          value={248}
          subtext="Across 4 active sections"
          icon={<Users className="w-5 h-5" />}
          accentTone="blue"
          onClick={() => navigate('/faculty/performance')}
        />
        <StatCard
          label="Assigned Subjects"
          value={4}
          subtext="CS302 (A/B), CS412 & DBMS Lab"
          icon={<BookMarked className="w-5 h-5" />}
          accentTone="purple"
          onClick={() => navigate('/faculty/subjects')}
        />
        <StatCard
          label="Active Online Tests"
          value={3}
          trend={{ value: '94% participation', direction: 'up', sentiment: 'positive' }}
          subtext="Live & upcoming windows"
          icon={<FileCheck2 className="w-5 h-5" />}
          accentTone="emerald"
          onClick={() => navigate('/faculty/create-test')}
        />
        <StatCard
          label="Pending Answer Evaluations"
          value={18}
          trend={{ value: 'Due in 48h', direction: 'neutral', sentiment: 'warning' }}
          subtext="CS302 Mid-Term II scripts"
          icon={<CheckSquare className="w-5 h-5" />}
          accentTone="amber"
          onClick={() => navigate('/faculty/evaluation')}
        />
      </div>

      {/* Subject-Wise Performance Chart + Recent Activity & Upcoming Exams */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <ChartCard
          title="Subject-Wise Cohort Performance"
          subtitle="Mean score (%) and pass percentage across your assigned B.Tech sections"
          className="lg:col-span-7"
          action={
            <Button
              size="sm"
              variant="ghost"
              onClick={() => navigate('/faculty/performance')}
              rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
            >
              Detailed Cohort View
            </Button>
          }
        >
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={FACULTY_SUBJECT_STATS}
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
                  dataKey="avgMarks"
                  name="Mean Score (%)"
                  fill="#2563EB"
                  radius={[6, 6, 0, 0]}
                  barSize={26}
                />
                <Bar
                  dataKey="passRate"
                  name="Pass Percentage (%)"
                  fill="#7C3AED"
                  radius={[6, 6, 0, 0]}
                  barSize={26}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <div className="lg:col-span-5 flex flex-col gap-6">
          {/* Recent Examination Activity */}
          <section className="bg-white border border-slate-200 rounded-xl p-5">
            <h3 className="text-base font-semibold font-display text-slate-900">
              Recent Examination Activity
            </h3>
            <p className="text-xs text-slate-500 mb-3.5">
              Automated grading logs and question authoring updates
            </p>
            <div className="divide-y divide-slate-100">
              {RECENT_EXAM_ACTIVITY.map((item) => (
                <div key={item.id} className="py-3 first:pt-0 last:pb-0 space-y-0.5">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-slate-900 truncate">
                      {item.title}
                    </p>
                    <span className="text-[11px] text-slate-400 shrink-0">
                      {item.time}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600">{item.detail}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Upcoming Examinations */}
          <section className="bg-white border border-slate-200 rounded-xl p-5 flex-1">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-base font-semibold font-display text-slate-900">
                Upcoming Examinations
              </h3>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => navigate('/faculty/create-test')}
              >
                + Schedule
              </Button>
            </div>
            <div className="divide-y divide-slate-100">
              {UPCOMING_TESTS.slice(0, 2).map((t) => (
                <div key={t.id} className="py-2.5 first:pt-0 last:pb-0">
                  <p className="text-sm font-medium text-slate-900">{t.title}</p>
                  <p className="text-xs text-slate-500 tabular-nums mt-0.5">
                    {t.date} · {t.time} · {t.durationMinutes}m · {t.totalQuestions} Qs
                  </p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

      {/* Students Needing Attention Table */}
      <DataTable
        title="Students Needing Academic Attention"
        subtitle="Flagged automatically based on < 65% assessment average or < 75% attendance"
        data={cseAttentionStudents}
        columns={columns}
        rowKey={(r) => r.id}
        searchPlaceholder="Search by student name or roll number..."
        searchMatcher={(r, q) =>
          r.name.toLowerCase().includes(q) ||
          r.rollNo.toLowerCase().includes(q) ||
          r.weakSubjects.join(' ').toLowerCase().includes(q)
        }
        filterOptions={[
          { label: 'Critical Risk', value: 'Critical' },
          { label: 'Moderate Risk', value: 'Moderate' },
        ]}
        filterMatcher={(r, f) => r.riskLevel === f}
        headerActions={
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-amber-700">
            <AlertTriangle className="w-4 h-4" />
            <span>{cseAttentionStudents.length} students flagged</span>
          </span>
        }
      />
    </div>
  );
};
