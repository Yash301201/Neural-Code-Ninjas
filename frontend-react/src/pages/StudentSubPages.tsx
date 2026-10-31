import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Upload,
  CheckCircle2,
  Clock,
  CalendarCheck,
  MessageSquareCode,
  Send,
  Compass,
} from 'lucide-react';
import { STUDENT_COURSES } from '../data/mockData';
import { AssignmentRecord } from '../types';
import { useApp } from '../context/AppContext';
import { DataTable, ColumnDef } from '../components/DataTable';
import { Button } from '../components/Button';

export const StudentCourses: React.FC = () => {
  const { addToast } = useApp();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-display text-slate-900">
            My Enrolled B.Tech Courses
          </h1>
          <p className="text-sm text-slate-600 mt-0.5">
            Semester 5 · 6 Core & Elective Courses · 21 Total Credits
          </p>
        </div>
        <Button
          variant="ai"
          leftIcon={<Compass className="w-4 h-4" />}
          onClick={() => navigate('/student/study-coach')}
        >
          AI Study Coach
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {STUDENT_COURSES.map((course) => (
          <div
            key={course.id}
            className="bg-white border border-slate-200 rounded-xl p-5 flex flex-col justify-between space-y-4"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span className="font-mono font-bold text-[#2563EB]">{course.code}</span>
                <span className="tabular-nums">
                  {course.credits} Credits · {course.topicsCount} Units
                </span>
              </div>
              <h2 className="text-base font-semibold font-display text-slate-900">
                {course.name}
              </h2>
              <p className="text-xs text-slate-500">Instructor: {course.faculty}</p>
            </div>

            <div className="space-y-3 pt-2 border-t border-slate-100">
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Syllabus Mastery</span>
                  <span className="font-mono font-semibold text-slate-900 tabular-nums">
                    {course.completionProgress}%
                  </span>
                </div>
                <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#2563EB] rounded-full"
                    style={{ width: `${course.completionProgress}%` }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-600 tabular-nums">
                <span>Avg Score: {course.avgScore}%</span>
                <span>Attendance: {course.attendanceRate}%</span>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1"
                  leftIcon={<BookOpen className="w-3.5 h-3.5" />}
                  onClick={() =>
                    addToast(
                      `${course.code} Lecture Repository`,
                      `Opened ${course.topicsCount} syllabus modules for ${course.name}.`,
                      'info'
                    )
                  }
                >
                  Syllabus
                </Button>
                <Button
                  size="sm"
                  variant="primary"
                  className="flex-1"
                  onClick={() => navigate('/student/online-test')}
                >
                  Practice Quiz
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const StudentAssignments: React.FC = () => {
  const { assignments, submitAssignment } = useApp();

  const columns: ColumnDef<AssignmentRecord>[] = [
    {
      key: 'title',
      header: 'Assignment & Lab',
      sortable: true,
      sortValue: (a) => a.title,
      render: (a) => (
        <div>
          <p className="font-semibold text-slate-900">{a.title}</p>
          <p className="text-xs text-slate-500">
            {a.subjectCode} · {a.subjectName}
          </p>
        </div>
      ),
    },
    {
      key: 'dueDate',
      header: 'Due Date',
      sortable: true,
      sortValue: (a) => a.dueDate,
      render: (a) => <span className="font-mono text-xs tabular-nums">{a.dueDate}</span>,
    },
    {
      key: 'marks',
      header: 'Score / Max',
      align: 'right',
      render: (a) => (
        <span className="font-mono text-xs font-semibold tabular-nums">
          {a.marksObtained !== undefined ? `${a.marksObtained}/${a.maxMarks}` : `— / ${a.maxMarks}`}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (a) => (
        <span
          className={`inline-flex items-center gap-1.5 text-xs font-medium ${
            a.status === 'Evaluated' || a.status === 'Submitted'
              ? 'text-emerald-700'
              : 'text-amber-700'
          }`}
        >
          {a.status === 'Evaluated' || a.status === 'Submitted' ? (
            <CheckCircle2 className="w-3.5 h-3.5" />
          ) : (
            <Clock className="w-3.5 h-3.5" />
          )}
          <span>{a.status}</span>
        </span>
      ),
    },
    {
      key: 'action',
      header: 'Submission',
      align: 'right',
      render: (a) =>
        a.status === 'Pending' ? (
          <Button
            size="sm"
            variant="primary"
            leftIcon={<Upload className="w-3.5 h-3.5" />}
            onClick={() => submitAssignment(a.id)}
          >
            Submit Lab
          </Button>
        ) : (
          <span className="text-xs text-slate-400">Recorded</span>
        ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          Coursework & Lab Assignments
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Upload lab deliverables and inspect graded rubrics across Semester 5 subjects.
        </p>
      </div>

      <DataTable
        title="Semester 5 Assignment Ledger"
        data={assignments}
        columns={columns}
        rowKey={(a) => a.id}
        searchPlaceholder="Search assignment title or subject..."
        searchMatcher={(a, q) =>
          a.title.toLowerCase().includes(q) || a.subjectName.toLowerCase().includes(q)
        }
        filterOptions={[
          { label: 'Pending', value: 'Pending' },
          { label: 'Submitted', value: 'Submitted' },
          { label: 'Evaluated', value: 'Evaluated' },
        ]}
        filterMatcher={(a, f) => a.status === f}
      />
    </div>
  );
};

export const StudentAttendance: React.FC = () => {
  const attendanceRows = STUDENT_COURSES.map((c) => {
    const totalClasses = 42;
    const attended = Math.round((c.attendanceRate / 100) * totalClasses);
    const minRequired = Math.ceil(totalClasses * 0.75);
    const buffer = attended - minRequired;
    return {
      ...c,
      totalClasses,
      attended,
      buffer,
    };
  });

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-display text-slate-900">
            Lecture & Lab Attendance Tracker
          </h1>
          <p className="text-sm text-slate-600 mt-0.5">
            University minimum eligibility requirement: 75.0% per course
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm font-semibold text-emerald-700">
          <CalendarCheck className="w-5 h-5" />
          <span className="tabular-nums">Overall: 86.4% Eligible</span>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/70 text-xs font-semibold text-slate-600">
                <th className="px-5 py-3">Course</th>
                <th className="px-5 py-3">Faculty</th>
                <th className="px-5 py-3 text-right">Attended / Held</th>
                <th className="px-5 py-3 text-right">Percentage</th>
                <th className="px-5 py-3 text-right">75% Margin</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {attendanceRows.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50/70">
                  <td className="px-5 py-3.5">
                    <p className="font-semibold text-slate-900">
                      {r.code} · {r.name}
                    </p>
                  </td>
                  <td className="px-5 py-3.5 text-xs text-slate-600">{r.faculty}</td>
                  <td className="px-5 py-3.5 text-right font-mono tabular-nums">
                    {r.attended} / {r.totalClasses}
                  </td>
                  <td className="px-5 py-3.5 text-right font-mono font-semibold text-slate-900 tabular-nums">
                    {r.attendanceRate}%
                  </td>
                  <td className="px-5 py-3.5 text-right text-xs font-medium text-emerald-700 tabular-nums">
                    +{r.buffer} classes above 75%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

interface DoubtTurn {
  id: string;
  sender: 'student' | 'coach';
  subject: string;
  text: string;
}

const PRESET_DOUBTS = [
  {
    subject: 'CS302 DBMS',
    prompt: 'Why can BCNF decomposition fail to be dependency-preserving unlike 3NF?',
    answer:
      'In R(A, B, C) with F = { AB → C, C → B }, candidate keys are AB and AC. C → B violates BCNF because C is not a superkey. Decomposing on C → B yields R1(C, B) and R2(A, C). Notice AB → C spans attributes across both R1 and R2 and cannot be enforced without a join, proving BCNF is always lossless-join but not always dependency-preserving.',
  },
  {
    subject: 'CS304 OS',
    prompt: 'What is the exact time complexity of Banker’s safety algorithm?',
    answer:
      'For n processes and m resource types, the safety algorithm scans up to n processes in each pass, comparing m-element Need[i] ≤ Work vectors. In the worst case it performs n passes of n × m comparisons, yielding O(m · n²) time complexity.',
  },
  {
    subject: 'CS301 Algorithms',
    prompt: 'When does Dijkstra’s shortest path algorithm fail on negative edge weights?',
    answer:
      'Dijkstra greedily finalizes the vertex u with minimum tentative distance d[u], assuming future paths via unvisited vertices only add non-negative weights. If a negative weight edge (v, u) exists later, d[v] + w(v, u) could be smaller than the already-locked d[u]; Bellman-Ford handles negative edges in O(V·E).',
  },
];

export const AIDoubtAssistant: React.FC = () => {
  const [subjectTag, setSubjectTag] = useState('CS302 DBMS');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<DoubtTurn[]>([
    {
      id: 'd-init',
      sender: 'coach',
      subject: 'CS302 DBMS',
      text: 'Ask any engineering concept doubt across DBMS, Operating Systems, Algorithms, or Computer Networks. Select a quick prompt below or enter your own question for a step-by-step derivation.',
    },
  ]);

  const handleSend = (customPrompt?: string, customSubject?: string, presetReply?: string) => {
    const questionText = (customPrompt ?? input).trim();
    if (!questionText) return;
    const activeSubj = customSubject ?? subjectTag;

    const userMsg: DoubtTurn = {
      id: `u-${Date.now()}`,
      sender: 'student',
      subject: activeSubj,
      text: questionText,
    };

    const synthesizedReply =
      presetReply ||
      `Step-by-step resolution (${activeSubj}): 1) Identify core invariants in "${questionText}". 2) Formulate boundary conditions and verify asymptotic / relational constraints. 3) Cross-check with your Semester 5 lecture rubric — practice 3 related problems in the AI Study Coach to lock in retention.`;

    const coachMsg: DoubtTurn = {
      id: `c-${Date.now() + 1}`,
      sender: 'coach',
      subject: activeSubj,
      text: synthesizedReply,
    };

    setMessages((prev) => [...prev, userMsg, coachMsg]);
    if (!customPrompt) setInput('');
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-2">
        <div className="flex items-center gap-2 text-xs font-medium text-[#7C3AED]">
          <MessageSquareCode className="w-4 h-4" />
          <span>24×7 Engineering Concept Tutor</span>
        </div>
        <h1 className="text-2xl font-bold font-display text-slate-900">
          AI Doubt Assistant
        </h1>
        <p className="text-sm text-slate-600">
          Resolve derivations, SQL queries, synchronization traces, and algorithmic proofs.
        </p>
      </div>

      {/* Quick Prompts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {PRESET_DOUBTS.map((p) => (
          <button
            key={p.prompt}
            type="button"
            onClick={() => handleSend(p.prompt, p.subject, p.answer)}
            className="text-left p-4 bg-white border border-slate-200 hover:border-[#7C3AED] rounded-xl transition-colors cursor-pointer space-y-1.5"
          >
            <p className="text-xs font-mono font-semibold text-[#7C3AED]">{p.subject}</p>
            <p className="text-xs font-medium text-slate-800 leading-snug">{p.prompt}</p>
          </button>
        ))}
      </div>

      {/* Conversation Thread */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden flex flex-col min-h-[400px]">
        <div className="flex-1 p-5 space-y-4 overflow-y-auto max-h-[420px]">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex ${m.sender === 'student' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-2xl rounded-xl p-4 text-sm leading-relaxed space-y-1 ${
                  m.sender === 'student'
                    ? 'bg-[#2563EB] text-white'
                    : 'bg-slate-50 border border-slate-200 text-slate-800'
                }`}
              >
                <p
                  className={`text-[11px] font-mono ${
                    m.sender === 'student' ? 'text-blue-100' : 'text-[#7C3AED] font-semibold'
                  }`}
                >
                  {m.sender === 'student' ? 'You' : 'Study Coach'} · {m.subject}
                </p>
                <p>{m.text}</p>
              </div>
            </div>
          ))}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="p-4 border-t border-slate-200 bg-slate-50/60 flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5"
        >
          <select
            value={subjectTag}
            onChange={(e) => setSubjectTag(e.target.value)}
            className="px-3 py-2 text-xs font-medium bg-white border border-slate-200 rounded-lg text-slate-700"
          >
            <option>CS302 DBMS</option>
            <option>CS304 OS</option>
            <option>CS301 Algorithms</option>
            <option>CS305 Networks</option>
          </select>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type an engineering concept, SQL query, or theorem question..."
            className="flex-1 px-3.5 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
          />
          <Button
            type="submit"
            variant="ai"
            leftIcon={<Send className="w-4 h-4" />}
          >
            Ask Tutor
          </Button>
        </form>
      </div>
    </div>
  );
};
