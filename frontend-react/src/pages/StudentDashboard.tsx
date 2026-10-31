import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Award,
  CalendarCheck,
  ClipboardList,
  Compass,
  Play,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  Clock,
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
import {
  STUDENT_COURSES,
  RECENT_EXAM_RESULTS,
  UPCOMING_TESTS,
  STUDENT_WEAK_TOPICS,
} from '../data/mockData';
import { StatCard } from '../components/StatCard';
import { ChartCard } from '../components/ChartCard';
import { Button } from '../components/Button';

const RECENT_ACTIVITIES = [
  {
    id: 'act-1',
    title: 'Completed Day 2 SQL Aggregations & Subqueries Lab',
    meta: 'AI Study Coach · 2 hours ago',
    tone: 'done',
  },
  {
    id: 'act-2',
    title: 'Submitted Wireshark TCP 3-Way Handshake Trace',
    meta: 'CS305 Computer Networks · Yesterday',
    tone: 'done',
  },
  {
    id: 'act-3',
    title: 'Diagnostic flagged BCNF Normalization below 50% threshold',
    meta: 'CS302 DBMS · 3 days ago',
    tone: 'alert',
  },
  {
    id: 'act-4',
    title: 'Scored 44/50 in Graph & Greedy Paradigms Assessment',
    meta: 'CS301 Algorithms · Oct 12',
    tone: 'done',
  },
];

export const StudentDashboard: React.FC = () => {
  const { currentUser, assignments, studyTasks } = useApp();
  const navigate = useNavigate();

  const pendingAssignmentsCount = assignments.filter(
    (a) => a.status === 'Pending' || a.status === 'Overdue'
  ).length;

  const completedPlanCount = studyTasks.filter((t) => t.completed).length;

  const subjectChartData = STUDENT_COURSES.map((c) => ({
    code: c.code,
    subject: c.name,
    studentScore: c.avgScore,
    cohortAvg: Math.min(90, Math.round(c.avgScore * 0.92 + 8)),
  }));

  return (
    <div className="space-y-6">
      {/* Welcome Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs font-medium text-slate-500">
            {currentUser?.department || 'Computer Science & Engineering'} ·{' '}
            {currentUser?.semester || 'Semester 5'} · Roll{' '}
            <span className="font-mono">{currentUser?.rollOrEmpId || '23CS1048'}</span>
          </p>
          <h1 className="text-2xl font-bold font-display text-slate-900 tracking-tight">
            Welcome back, {currentUser?.name || 'Aarav Sharma'}
          </h1>
          <p className="text-sm text-slate-600">
            You have completed{' '}
            <span className="font-semibold text-slate-900 tabular-nums">
              {completedPlanCount} of {studyTasks.length}
            </span>{' '}
            personalized DBMS remediation milestones this week.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <Button
            variant="outline"
            onClick={() => navigate('/student/online-test')}
            leftIcon={<Play className="w-4 h-4 text-[#2563EB]" />}
          >
            Take Practice Exam
          </Button>
          <Button
            variant="ai"
            onClick={() => navigate('/student/study-coach')}
            leftIcon={<Compass className="w-4 h-4" />}
          >
            Open AI Study Coach
          </Button>
        </div>
      </div>

      {/* 4 Key KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="Total Enrolled Subjects"
          value={STUDENT_COURSES.length}
          subtext="21 Total Credits · Sem 5"
          icon={<BookOpen className="w-5 h-5" />}
          accentTone="blue"
          onClick={() => navigate('/student/courses')}
        />
        <StatCard
          label="Average Test Score"
          value="78.5%"
          trend={{ value: '+4.2%', direction: 'up', sentiment: 'positive' }}
          subtext="vs. Mid-Term I"
          icon={<Award className="w-5 h-5" />}
          accentTone="emerald"
          onClick={() => navigate('/student/performance')}
        />
        <StatCard
          label="Attendance Percentage"
          value="86.4%"
          trend={{ value: '+1.4%', direction: 'up', sentiment: 'positive' }}
          subtext="Above 75% mandate"
          icon={<CalendarCheck className="w-5 h-5" />}
          accentTone="purple"
          onClick={() => navigate('/student/attendance')}
        />
        <StatCard
          label="Pending Assignments"
          value={pendingAssignmentsCount}
          trend={{ value: 'Due Nov 4', direction: 'neutral', sentiment: 'warning' }}
          subtext="CS302 & CS304 Labs"
          icon={<ClipboardList className="w-5 h-5" />}
          accentTone="amber"
          onClick={() => navigate('/student/assignments')}
        />
      </div>

      {/* Subject-Wise Performance Chart + AI Learning Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <ChartCard
          title="Subject-Wise Academic Performance"
          subtitle="Comparison of your current subject mastery (%) against Semester 5 cohort average"
          className="lg:col-span-7"
          action={
            <Button
              size="sm"
              variant="ghost"
              onClick={() => navigate('/student/performance')}
              rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
            >
              Full Analytics
            </Button>
          }
        >
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={subjectChartData}
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
                  dataKey="studentScore"
                  name="Your Score (%)"
                  fill="#2563EB"
                  radius={[6, 6, 0, 0]}
                  barSize={24}
                />
                <Bar
                  dataKey="cohortAvg"
                  name="Class Average (%)"
                  fill="#CBD5E1"
                  radius={[6, 6, 0, 0]}
                  barSize={24}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        {/* AI-Generated Learning Recommendations & Weak Topic Identification */}
        <section className="lg:col-span-5 bg-white border border-slate-200 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-start justify-between gap-2 mb-4">
              <div>
                <h3 className="text-base font-semibold font-display text-slate-900">
                  Weak Topic Identification & Coach Plan
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Prioritized from recent CS302 & CS304 diagnostic error patterns
                </p>
              </div>
              <Compass className="w-5 h-5 text-[#7C3AED] shrink-0" />
            </div>

            <div className="divide-y divide-slate-100">
              {STUDENT_WEAK_TOPICS.map((wt) => (
                <div key={wt.id} className="py-3 first:pt-0 last:pb-0 space-y-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-slate-900 truncate">
                      {wt.topic}
                    </p>
                    <span
                      className={`text-xs font-mono font-semibold tabular-nums shrink-0 ${
                        wt.accuracy < 50 ? 'text-red-600' : 'text-amber-600'
                      }`}
                    >
                      {wt.accuracy}% accuracy
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">
                    {wt.subjectCode} · {wt.questionsAttempted} attempts · Next:{' '}
                    <span className="text-slate-700 font-medium">
                      {wt.recommendedAction}
                    </span>
                  </p>
                  <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        wt.accuracy < 50 ? 'bg-red-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${wt.accuracy}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between gap-3">
            <span className="text-xs text-slate-500">
              Adaptive 5-Day DBMS Study Plan Active
            </span>
            <Button
              size="sm"
              variant="ai"
              onClick={() => navigate('/student/study-coach')}
              rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
            >
              Resume Day 3
            </Button>
          </div>
        </section>
      </div>

      {/* Upcoming Tests + Recent Examination Results + Recent Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Upcoming Tests */}
        <section className="lg:col-span-5 bg-white border border-slate-200 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-semibold font-display text-slate-900">
                  Upcoming Examinations
                </h3>
                <p className="text-xs text-slate-500">
                  Scheduled online assessments and diagnostics
                </p>
              </div>
            </div>

            <div className="divide-y divide-slate-100">
              {UPCOMING_TESTS.map((test) => (
                <div
                  key={test.id}
                  className="py-3.5 first:pt-0 last:pb-0 flex items-start justify-between gap-3"
                >
                  <div className="space-y-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-900 leading-snug">
                      {test.title}
                    </p>
                    <p className="text-xs text-slate-500 tabular-nums">
                      {test.subjectCode} · {test.date} at {test.time} ·{' '}
                      {test.durationMinutes} mins · {test.maxMarks} marks
                    </p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigate('/student/online-test')}
                  >
                    Start
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Recent Examination Results */}
        <section className="lg:col-span-4 bg-white border border-slate-200 rounded-xl p-5">
          <div className="mb-4">
            <h3 className="text-base font-semibold font-display text-slate-900">
              Recent Examination Results
            </h3>
            <p className="text-xs text-slate-500">Evaluated scores & cohort percentiles</p>
          </div>

          <div className="divide-y divide-slate-100">
            {RECENT_EXAM_RESULTS.map((res) => {
              const pct = Math.round((res.score / res.maxScore) * 100);
              return (
                <div
                  key={res.id}
                  className="py-3 first:pt-0 last:pb-0 flex items-center justify-between gap-3"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-900 truncate">
                      {res.testTitle}
                    </p>
                    <p className="text-xs text-slate-500 tabular-nums">
                      {res.subjectCode} · {res.date} · {res.percentile}th percentile
                    </p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-sm font-bold font-mono tabular-nums text-slate-900">
                      {res.score}/{res.maxScore}
                    </p>
                    <p
                      className={`text-xs font-medium inline-flex items-center gap-1 ${
                        pct < 60
                          ? 'text-red-600'
                          : pct >= 85
                          ? 'text-emerald-600'
                          : 'text-slate-600'
                      }`}
                    >
                      {pct < 60 ? (
                        <AlertTriangle className="w-3 h-3" />
                      ) : (
                        <CheckCircle2 className="w-3 h-3" />
                      )}
                      <span>{res.status}</span>
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Recent Activities */}
        <section className="lg:col-span-3 bg-white border border-slate-200 rounded-xl p-5">
          <div className="mb-4">
            <h3 className="text-base font-semibold font-display text-slate-900">
              Recent Activity
            </h3>
            <p className="text-xs text-slate-500">Latest learning timeline</p>
          </div>

          <div className="divide-y divide-slate-100">
            {RECENT_ACTIVITIES.map((act) => (
              <div key={act.id} className="py-3 first:pt-0 last:pb-0 flex items-start gap-2.5">
                {act.tone === 'alert' ? (
                  <Clock className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                ) : (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                )}
                <div className="space-y-0.5 min-w-0">
                  <p className="text-xs font-medium text-slate-800 leading-snug">
                    {act.title}
                  </p>
                  <p className="text-[11px] text-slate-500">{act.meta}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};
