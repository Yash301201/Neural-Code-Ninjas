import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Compass,
  RefreshCw,
  CheckCircle2,
  Circle,
  Clock,
  BookOpen,
  Award,
  AlertTriangle,
  Play,
  ArrowRight,
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { useApp } from '../context/AppContext';
import { STUDENT_WEAK_TOPICS, WEEKLY_STUDY_HOURS } from '../data/mockData';
import { StatCard } from '../components/StatCard';
import { ChartCard } from '../components/ChartCard';
import { Button } from '../components/Button';

const RECOMMENDED_ACTIVITIES = [
  {
    id: 'ra-1',
    title: 'Interactive SQL Join Visualizer Sandbox',
    category: 'Hands-on Lab · 20 mins',
    detail:
      'Step through Nested-Loop vs. Hash Join execution plans on a 10,000-row Engineering Enrollment dataset.',
  },
  {
    id: 'ra-2',
    title: 'Attribute Closure & Minimal Cover Worksheet',
    category: 'Guided Problem Set · 25 mins',
    detail:
      'Solve 6 step-by-step BCNF decomposition proofs with automated lossless-join verification.',
  },
  {
    id: 'ra-3',
    title: 'Dr. Meera Krishnan Lecture Notes: ARIES & WAL',
    category: 'Concept Summary · 15 mins',
    detail:
      'Concise 4-page engineering crib sheet covering LSNs, Dirty Page Tables, and Undo/Redo passes.',
  },
];

const PRACTICE_RECOMMENDATIONS = [
  {
    id: 'pr-1',
    topic: 'BCNF Decomposition',
    difficulty: 'Medium',
    questionCount: 10,
    estimatedTime: '15m',
  },
  {
    id: 'pr-2',
    topic: 'Correlated SQL Subqueries',
    difficulty: 'Hard',
    questionCount: 8,
    estimatedTime: '12m',
  },
  {
    id: 'pr-3',
    topic: 'B+ Tree Node Splitting',
    difficulty: 'Hard',
    questionCount: 6,
    estimatedTime: '10m',
  },
];

export const AIStudyPlanner: React.FC = () => {
  const {
    studyTasks,
    activePlanFocus,
    toggleStudyTask,
    regenerateStudyPlan,
    requestConfirm,
    addToast,
  } = useApp();
  const navigate = useNavigate();

  const [taskFilter, setTaskFilter] = useState<'all' | 'pending' | 'completed'>('all');
  const [isRegenerating, setIsRegenerating] = useState(false);

  const completedTasks = studyTasks.filter((t) => t.completed);
  const pendingTasks = studyTasks.filter((t) => !t.completed);
  const completionPct = Math.round(
    (completedTasks.length / Math.max(1, studyTasks.length)) * 100
  );

  const totalProjectedGain = studyTasks
    .filter((t) => t.completed)
    .reduce((acc, t) => acc + t.targetMasteryGain, 0);

  const visibleTasks = studyTasks.filter((t) => {
    if (taskFilter === 'completed') return t.completed;
    if (taskFilter === 'pending') return !t.completed;
    return true;
  });

  const handleRegenerateClick = (targetFocus?: 'DBMS' | 'OS') => {
    requestConfirm({
      title: 'Regenerate Personalized Study Plan?',
      message:
        'The AI Study Coach will recalibrate your 5-day remediation schedule using your latest diagnostic accuracy and upcoming exam dates.',
      confirmLabel: 'Recalibrate Plan',
      variant: 'primary',
      onConfirm: () => {
        setIsRegenerating(true);
        setTimeout(() => {
          regenerateStudyPlan(targetFocus);
          setIsRegenerating(false);
        }, 650);
      },
    });
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs font-medium text-[#7C3AED]">
            <Compass className="w-4 h-4" />
            <span>Adaptive Study Coach · Personalized 5-Day Mastery Roadmap</span>
          </div>
          <h1 className="text-2xl font-bold font-display text-slate-900 tracking-tight">
            {activePlanFocus === 'DBMS'
              ? 'Database Management Systems (CS302) Recovery Plan'
              : 'Operating Systems (CS304) Concurrency & Paging Plan'}
          </h1>
          <p className="text-sm text-slate-600">
            Generated because your Mid-Term II DBMS score (58%) flagged conceptual gaps in
            SQL Joins and BCNF Normalization.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg">
            <button
              type="button"
              onClick={() => {
                if (activePlanFocus !== 'DBMS') handleRegenerateClick('DBMS');
              }}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors cursor-pointer ${
                activePlanFocus === 'DBMS'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              CS302 DBMS
            </button>
            <button
              type="button"
              onClick={() => {
                if (activePlanFocus !== 'OS') handleRegenerateClick('OS');
              }}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors cursor-pointer ${
                activePlanFocus === 'OS'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              CS304 OS
            </button>
          </div>

          <Button
            variant="ai"
            isLoading={isRegenerating}
            leftIcon={<RefreshCw className="w-4 h-4" />}
            onClick={() => handleRegenerateClick()}
          >
            Regenerate Study Plan
          </Button>
        </div>
      </div>

      {/* Student Performance Summary KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="Plan Completion"
          value={`${completionPct}%`}
          subtext={`${completedTasks.length} completed · ${pendingTasks.length} pending`}
          icon={<CheckCircle2 className="w-5 h-5" />}
          accentTone="purple"
        />
        <StatCard
          label="Weak Subjects Flagged"
          value="2 Subjects"
          subtext="CS302 DBMS (61%) · CS304 OS (76%)"
          icon={<AlertTriangle className="w-5 h-5" />}
          accentTone="amber"
        />
        <StatCard
          label="Estimated Mastery Gain"
          value={`+${totalProjectedGain}%`}
          trend={{ value: 'Target: 82%', direction: 'up', sentiment: 'positive' }}
          subtext="From completed milestones"
          icon={<Award className="w-5 h-5" />}
          accentTone="emerald"
        />
        <StatCard
          label="Daily Study Commitment"
          value="50 mins"
          subtext="19.5 hrs logged this week"
          icon={<Clock className="w-5 h-5" />}
          accentTone="blue"
        />
      </div>

      {/* Main Split: 5-Day Study Schedule (7 cols) + Weak Topics & Weekly Progress Chart (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Daily Study Schedule & Tasks */}
        <section className="lg:col-span-7 bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="p-5 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold font-display text-slate-900">
                Daily Personalized Study Schedule
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Sequential 5-day curriculum from fundamentals to timed mastery check
              </p>
            </div>

            {/* Completed / Pending Filter */}
            <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg">
              {(['all', 'pending', 'completed'] as const).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setTaskFilter(mode)}
                  className={`px-3 py-1 text-xs font-medium rounded-md capitalize transition-colors cursor-pointer ${
                    taskFilter === mode
                      ? 'bg-white text-slate-900 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>

          {isRegenerating ? (
            <div className="p-6 space-y-4 animate-pulse">
              {Array.from({ length: 4 }).map((_, idx) => (
                <div key={idx} className="h-24 bg-slate-100 rounded-xl" />
              ))}
            </div>
          ) : visibleTasks.length === 0 ? (
            <div className="p-10 text-center space-y-2">
              <p className="text-sm font-medium text-slate-800">
                No {taskFilter} tasks in this view.
              </p>
              <Button size="sm" variant="outline" onClick={() => setTaskFilter('all')}>
                View All Days
              </Button>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {visibleTasks.map((task) => (
                <div
                  key={task.id}
                  className={`p-5 transition-colors ${
                    task.completed ? 'bg-slate-50/60' : 'bg-white hover:bg-slate-50/40'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                    <div className="flex items-start gap-3.5">
                      <button
                        type="button"
                        onClick={() => toggleStudyTask(task.id)}
                        aria-label={
                          task.completed ? 'Mark task pending' : 'Mark task completed'
                        }
                        className="mt-0.5 text-slate-400 hover:text-[#2563EB] cursor-pointer shrink-0"
                      >
                        {task.completed ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                        ) : (
                          <Circle className="w-5 h-5" />
                        )}
                      </button>

                      <div className="space-y-1.5">
                        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                          <span className="font-mono font-semibold text-[#7C3AED]">
                            {task.day}
                          </span>
                          <span aria-hidden="true">·</span>
                          <span>{task.activityType}</span>
                          <span aria-hidden="true">·</span>
                          <span className="tabular-nums">{task.durationMinutes} mins</span>
                          <span aria-hidden="true">·</span>
                          <span className="text-emerald-700 font-medium tabular-nums">
                            +{task.targetMasteryGain}% Mastery
                          </span>
                        </div>

                        <h3
                          className={`text-sm font-semibold font-display ${
                            task.completed
                              ? 'line-through text-slate-400'
                              : 'text-slate-900'
                          }`}
                        >
                          {task.dayTitle}
                        </h3>
                        <p className="text-xs text-slate-600 leading-relaxed">
                          {task.description}
                        </p>
                        <p className="text-xs text-slate-500">
                          Focus Topic:{' '}
                          <span className="font-medium text-slate-700">{task.topic}</span>
                        </p>
                      </div>
                    </div>

                    <div className="shrink-0 sm:self-center">
                      <Button
                        size="sm"
                        variant={task.completed ? 'outline' : 'primary'}
                        onClick={() => toggleStudyTask(task.id)}
                      >
                        {task.completed ? 'Completed' : 'Mark Completed'}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Right Column: Weekly Progress Chart + Weak Topics */}
        <div className="lg:col-span-5 space-y-6">
          <ChartCard
            title="Weekly Study Hours & Mastery Lift"
            subtitle="Daily study hours logged vs. cumulative DBMS mastery index"
          >
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart
                  data={WEEKLY_STUDY_HOURS}
                  margin={{ top: 8, right: 8, left: -18, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis
                    dataKey="day"
                    tick={{ fill: '#475569', fontSize: 12 }}
                    axisLine={{ stroke: '#E2E8F0' }}
                    tickLine={false}
                  />
                  <YAxis
                    yAxisId="left"
                    tick={{ fill: '#64748B', fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    domain={[50, 100]}
                    tick={{ fill: '#7C3AED', fontSize: 12 }}
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
                    yAxisId="left"
                    dataKey="actual"
                    name="Actual Hours"
                    fill="#2563EB"
                    radius={[5, 5, 0, 0]}
                    barSize={20}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="masteryScore"
                    name="Mastery Index (%)"
                    stroke="#7C3AED"
                    strokeWidth={2.5}
                    dot={{ r: 3.5, fill: '#7C3AED' }}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          {/* Weak Subjects & Weak Topics Card */}
          <section className="bg-white border border-slate-200 rounded-xl p-5 space-y-4">
            <div>
              <h3 className="text-base font-semibold font-display text-slate-900">
                Identified Weak Subjects & Topics
              </h3>
              <p className="text-xs text-slate-500">
                Root-cause breakdown driving your study schedule
              </p>
            </div>

            <div className="divide-y divide-slate-100">
              {STUDENT_WEAK_TOPICS.map((wt) => (
                <div
                  key={wt.id}
                  className="py-3 first:pt-0 last:pb-0 flex items-center justify-between gap-3"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">
                      {wt.topic}
                    </p>
                    <p className="text-xs text-slate-500">
                      {wt.subjectCode} · {wt.subject}
                    </p>
                  </div>
                  <span
                    className={`text-xs font-mono font-semibold tabular-nums shrink-0 ${
                      wt.accuracy < 50 ? 'text-red-600' : 'text-amber-600'
                    }`}
                  >
                    {wt.accuracy}%
                  </span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

      {/* Recommended Learning Activities + Practice Question Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <section className="lg:col-span-7 bg-white border border-slate-200 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold font-display text-slate-900">
                Recommended Learning Activities
              </h3>
              <p className="text-xs text-slate-500">
                Curated interactive labs and faculty notes aligned with Day 3 & Day 4
              </p>
            </div>
            <BookOpen className="w-5 h-5 text-[#2563EB]" />
          </div>

          <div className="divide-y divide-slate-100">
            {RECOMMENDED_ACTIVITIES.map((act) => (
              <div
                key={act.id}
                className="py-3.5 first:pt-0 last:pb-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-slate-900">{act.title}</p>
                  <p className="text-xs text-slate-500">{act.category}</p>
                  <p className="text-xs text-slate-600">{act.detail}</p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                  onClick={() =>
                    addToast(
                      'Learning Module Opened',
                      `Launched "${act.title}" in study workspace.`,
                      'info'
                    )
                  }
                >
                  Launch
                </Button>
              </div>
            ))}
          </div>
        </section>

        <section className="lg:col-span-5 bg-white border border-slate-200 rounded-xl p-5 space-y-4">
          <div>
            <h3 className="text-base font-semibold font-display text-slate-900">
              Practice Question Sets
            </h3>
            <p className="text-xs text-slate-500">
              Targeted micro-assessments to verify concept retention
            </p>
          </div>

          <div className="divide-y divide-slate-100">
            {PRACTICE_RECOMMENDATIONS.map((pr) => (
              <div
                key={pr.id}
                className="py-3.5 first:pt-0 last:pb-0 flex items-center justify-between gap-3"
              >
                <div>
                  <p className="text-sm font-semibold text-slate-900">{pr.topic}</p>
                  <p className="text-xs text-slate-500 tabular-nums">
                    {pr.questionCount} Questions · {pr.difficulty} · {pr.estimatedTime}
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="primary"
                  leftIcon={<Play className="w-3.5 h-3.5" />}
                  onClick={() => navigate('/student/online-test')}
                >
                  Practice
                </Button>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};
