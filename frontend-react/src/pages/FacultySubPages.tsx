import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Plus,
  Wand2,
  Trash2,
  CheckCircle2,
  FilePlus2,
  CheckSquare,
  Save,
} from 'lucide-react';
import { SUBJECT_TOPICS_MAP, STUDENT_COURSES } from '../data/mockData';
import { TestQuestion } from '../types';
import { useApp } from '../context/AppContext';
import { DataTable, ColumnDef } from '../components/DataTable';
import { Button } from '../components/Button';

export const FacultySubjects: React.FC = () => {
  const [courses, setCourses] = useState(STUDENT_COURSES.slice(0, 4));
  const { addToast } = useApp();

  const advanceUnit = (id: string, code: string) => {
    setCourses((prev) =>
      prev.map((c) =>
        c.id === id
          ? { ...c, completionProgress: Math.min(100, c.completionProgress + 5) }
          : c
      )
    );
    addToast('Syllabus Progress Updated', `Logged completed lecture unit for ${code}.`, 'success');
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          My Assigned Subjects & Sections
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Track lecture coverage, cohort strength, and assessment readiness.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {courses.map((c) => (
          <div
            key={c.id}
            className="bg-white border border-slate-200 rounded-xl p-5 space-y-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-mono font-bold text-[#2563EB]">{c.code}</p>
                <h2 className="text-base font-semibold font-display text-slate-900 mt-0.5">
                  {c.name}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Semester {c.semester} · {c.enrolledStudents} Enrolled Students
                </p>
              </div>
              <span className="text-xs font-mono font-semibold text-slate-700 tabular-nums">
                Mean: {c.avgScore}%
              </span>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Syllabus Coverage</span>
                <span className="font-mono font-semibold tabular-nums">
                  {c.completionProgress}%
                </span>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-[#2563EB] rounded-full transition-all"
                  style={{ width: `${c.completionProgress}%` }}
                />
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-100">
              <Button
                size="sm"
                variant="outline"
                onClick={() => advanceUnit(c.id, c.code)}
              >
                + Mark Lecture Unit Completed
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const ManageTopics: React.FC = () => {
  const [topicsBySubject, setTopicsBySubject] =
    useState<Record<string, string[]>>(SUBJECT_TOPICS_MAP);
  const [selectedSubject, setSelectedSubject] = useState(
    Object.keys(SUBJECT_TOPICS_MAP)[0]
  );
  const [newTopic, setNewTopic] = useState('');
  const { addToast } = useApp();

  const handleAddTopic = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTopic.trim()) return;
    setTopicsBySubject((prev) => ({
      ...prev,
      [selectedSubject]: [...(prev[selectedSubject] || []), newTopic.trim()],
    }));
    addToast('Syllabus Topic Added', `Added "${newTopic.trim()}" to ${selectedSubject}.`, 'success');
    setNewTopic('');
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          Manage Curriculum Topics & Outcomes
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Organize granular syllabus modules used by the AI Question Generator and Study Coach.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-5">
        <form onSubmit={handleAddTopic} className="grid grid-cols-1 sm:grid-cols-12 gap-3">
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="sm:col-span-5 px-3.5 py-2 text-sm bg-white border border-slate-200 rounded-lg"
          >
            {Object.keys(topicsBySubject).map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <input
            type="text"
            value={newTopic}
            onChange={(e) => setNewTopic(e.target.value)}
            placeholder="Enter new syllabus topic (e.g., Multiversion Concurrency Control)..."
            className="sm:col-span-5 px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
          />
          <Button
            type="submit"
            variant="primary"
            className="sm:col-span-2"
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Add Topic
          </Button>
        </form>

        <div className="divide-y divide-slate-100 border-t border-slate-200 pt-2">
          {(topicsBySubject[selectedSubject] || []).map((t, i) => (
            <div key={t} className="py-3 flex items-center justify-between text-sm">
              <div className="flex items-center gap-3">
                <span className="font-mono text-xs text-slate-400 tabular-nums">
                  Unit {String(i + 1).padStart(2, '0')}
                </span>
                <span className="font-medium text-slate-900">{t}</span>
              </div>
              <span className="text-xs text-emerald-700 font-medium">CO Mapped</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export const QuestionBankPage: React.FC = () => {
  const { questionBank, deleteBankQuestion, requestConfirm } = useApp();
  const navigate = useNavigate();

  const columns: ColumnDef<TestQuestion>[] = [
    {
      key: 'question',
      header: 'Question & Topic',
      render: (q) => (
        <div className="max-w-xl space-y-1">
          <p className="font-medium text-slate-900 line-clamp-2">{q.questionText}</p>
          <p className="text-xs text-slate-500">
            {q.subject} · {q.topic}
          </p>
        </div>
      ),
    },
    {
      key: 'type',
      header: 'Format',
      render: (q) => <span className="text-xs font-mono font-semibold">{q.type}</span>,
    },
    {
      key: 'difficulty',
      header: 'Difficulty',
      render: (q) => <span className="text-xs font-medium">{q.difficulty}</span>,
    },
    {
      key: 'marks',
      header: 'Marks',
      align: 'right',
      render: (q) => <span className="font-mono tabular-nums">{q.marks}</span>,
    },
    {
      key: 'actions',
      header: 'Manage',
      align: 'right',
      render: (q) => (
        <Button
          size="sm"
          variant="ghost"
          leftIcon={<Trash2 className="w-3.5 h-3.5 text-red-600" />}
          onClick={() =>
            requestConfirm({
              title: 'Delete Question from Repository?',
              message: 'This item will be permanently removed from the department Question Bank.',
              confirmLabel: 'Remove',
              variant: 'danger',
              onConfirm: () => deleteBankQuestion(q.id),
            })
          }
        >
          Remove
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-display text-slate-900">
            Department Question Bank ({questionBank.length})
          </h1>
          <p className="text-sm text-slate-600 mt-0.5">
            Verified MCQ and descriptive questions ready for online examinations.
          </p>
        </div>
        <Button
          variant="ai"
          leftIcon={<Wand2 className="w-4 h-4" />}
          onClick={() => navigate('/faculty/question-generator')}
        >
          Generate New Questions
        </Button>
      </div>

      <DataTable
        data={questionBank}
        columns={columns}
        rowKey={(q) => q.id}
        searchPlaceholder="Search question stem, subject, or topic..."
        searchMatcher={(q, s) =>
          q.questionText.toLowerCase().includes(s) ||
          q.subject.toLowerCase().includes(s) ||
          q.topic.toLowerCase().includes(s)
        }
        filterOptions={[
          { label: 'Easy', value: 'Easy' },
          { label: 'Medium', value: 'Medium' },
          { label: 'Hard', value: 'Hard' },
        ]}
        filterMatcher={(q, f) => q.difficulty === f}
      />
    </div>
  );
};

export const CreateTestPage: React.FC = () => {
  const { questionBank, addToast } = useApp();
  const [title, setTitle] = useState('');
  const [subject, setSubject] = useState('CS302 · Database Management Systems');
  const [duration, setDuration] = useState('45');
  const [date, setDate] = useState('2026-11-14');
  const [publishedTests, setPublishedTests] = useState([
    {
      id: 'pt-1',
      title: 'DBMS Normalization & SQL Joins Adaptive Diagnostic',
      subject: 'CS302 · Database Management Systems',
      duration: 25,
      date: '2026-11-02',
      questions: 8,
    },
  ]);

  const handlePublish = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      addToast('Validation Error', 'Enter a descriptive examination title.', 'error');
      return;
    }
    setPublishedTests((prev) => [
      {
        id: `pt-${Date.now()}`,
        title: title.trim(),
        subject,
        duration: Number(duration) || 45,
        date,
        questions: Math.min(10, questionBank.length),
      },
      ...prev,
    ]);
    setTitle('');
    addToast('Online Examination Scheduled', 'Students notified via Student Portal.', 'success');
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          Create & Schedule Online Examination
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Assemble timed adaptive assessments directly from the Question Bank.
        </p>
      </div>

      <form
        onSubmit={handlePublish}
        className="bg-white border border-slate-200 rounded-xl p-6 space-y-4"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Examination Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Mid-Semester Concurrency & Recovery Assessment"
              className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Target Course
            </label>
            <select
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-3.5 py-2 text-sm bg-white border border-slate-200 rounded-lg"
            >
              <option>CS302 · Database Management Systems</option>
              <option>CS304 · Operating Systems</option>
              <option>CS301 · Design & Analysis of Algorithms</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Duration (Mins)
              </label>
              <input
                type="number"
                min={10}
                max={180}
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="w-full px-3.5 py-2 text-sm font-mono border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Exam Date
              </label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full px-3 py-2 text-sm font-mono border border-slate-200 rounded-lg"
              />
            </div>
          </div>
        </div>
        <div className="flex justify-end">
          <Button
            type="submit"
            variant="primary"
            leftIcon={<FilePlus2 className="w-4 h-4" />}
          >
            Publish Examination
          </Button>
        </div>
      </form>

      <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-3">
        <h2 className="text-base font-semibold font-display text-slate-900">
          Scheduled Assessments ({publishedTests.length})
        </h2>
        <div className="divide-y divide-slate-100">
          {publishedTests.map((t) => (
            <div key={t.id} className="py-3 flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-slate-900">{t.title}</p>
                <p className="text-xs text-slate-500 tabular-nums">
                  {t.subject} · {t.date} · {t.duration} mins · {t.questions} questions
                </p>
              </div>
              <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-700">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Published
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export const FacultyAssignments: React.FC = () => {
  const { assignments, addAssignment } = useApp();
  const [title, setTitle] = useState('');
  const [dueDate, setDueDate] = useState('2026-11-15');

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    addAssignment({
      title: title.trim(),
      subjectCode: 'CS302',
      subjectName: 'Database Management Systems',
      dueDate,
      status: 'Pending',
      maxMarks: 25,
      submissionsCount: 0,
      totalStudents: 124,
    });
    setTitle('');
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          Manage Lab & Coursework Assignments
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Publish lab problem statements and monitor cohort submission rates.
        </p>
      </div>

      <form
        onSubmit={handleCreate}
        className="bg-white border border-slate-200 rounded-xl p-5 flex flex-col sm:flex-row gap-3"
      >
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New lab assignment title (e.g., B+ Tree Split Visualizer in C++)..."
          className="flex-1 px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
        />
        <input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="px-3 py-2 text-sm font-mono border border-slate-200 rounded-lg"
        />
        <Button type="submit" variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
          Assign Lab
        </Button>
      </form>

      <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
        {assignments.map((a) => (
          <div key={a.id} className="p-5 flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-semibold text-slate-900">{a.title}</p>
              <p className="text-xs text-slate-500 tabular-nums">
                {a.subjectCode} · Due {a.dueDate} · Max {a.maxMarks} Marks
              </p>
            </div>
            <span className="text-xs font-mono font-semibold text-slate-700 tabular-nums">
              {a.submissionsCount ?? 0} / {a.totalStudents ?? 124} Submitted
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const AnswerEvaluation: React.FC = () => {
  const { addToast } = useApp();
  const [scripts, setScripts] = useState([
    {
      id: 'scr-1',
      rollNo: '23CS1048',
      student: 'Aarav Sharma',
      question: 'Prove whether R(A,B,C,D) with {AB→C, C→D, D→A} is in 3NF and BCNF.',
      response:
        'Candidate keys are AB, BC, BD. Prime attributes: A, B, C, D. Since all attributes are prime, every FD has a prime RHS, satisfying 3NF. C→D and D→A violate BCNF.',
      maxMarks: 8,
      awarded: '7',
      graded: false,
    },
    {
      id: 'scr-2',
      rollNo: '23CS1087',
      student: 'Rohan Deshmukh',
      question: 'Explain ARIES Analysis, Redo, and Undo recovery phases.',
      response:
        'Analysis scans forward from last checkpoint to reconstruct Dirty Page Table and active transactions. Redo repeats history from smallest recLSN. Undo rolls back loser transactions.',
      maxMarks: 8,
      awarded: '6',
      graded: false,
    },
  ]);

  const handleGrade = (id: string, name: string) => {
    setScripts((prev) => prev.map((s) => (s.id === id ? { ...s, graded: true } : s)));
    addToast('Script Graded', `Published descriptive evaluation for ${name}.`, 'success');
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          Descriptive Answer Script Evaluation
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Review student derivations and finalize marks for CS302 Mid-Term II.
        </p>
      </div>

      <div className="space-y-4">
        {scripts.map((s) => (
          <div
            key={s.id}
            className="bg-white border border-slate-200 rounded-xl p-5 space-y-3"
          >
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-slate-900">
                {s.student} · <span className="font-mono text-xs text-slate-500">{s.rollNo}</span>
              </p>
              <span className="text-xs font-mono text-slate-500">Max: {s.maxMarks} Marks</span>
            </div>
            <p className="text-xs font-semibold text-slate-700">Prompt: {s.question}</p>
            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 leading-relaxed">
              {s.response}
            </div>
            <div className="flex items-center justify-end gap-3 pt-1">
              <label className="text-xs font-medium text-slate-600">Marks:</label>
              <input
                type="number"
                min={0}
                max={s.maxMarks}
                disabled={s.graded}
                value={s.awarded}
                onChange={(e) =>
                  setScripts((prev) =>
                    prev.map((item) =>
                      item.id === s.id ? { ...item, awarded: e.target.value } : item
                    )
                  )
                }
                className="w-16 px-2.5 py-1.5 text-xs font-mono border border-slate-200 rounded-lg text-center"
              />
              <Button
                size="sm"
                variant={s.graded ? 'outline' : 'primary'}
                disabled={s.graded}
                leftIcon={<CheckSquare className="w-3.5 h-3.5" />}
                onClick={() => handleGrade(s.id, s.student)}
              >
                {s.graded ? 'Evaluated' : 'Approve Score'}
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const FacultyAttendance: React.FC = () => {
  const { users, addToast } = useApp();
  const students = users.filter((u) => u.role === 'student');
  const [presentMap, setPresentMap] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(students.map((s) => [s.id, true]))
  );

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-display text-slate-900">
            Roll-Call Attendance Register
          </h1>
          <p className="text-sm text-slate-600 mt-0.5">
            CS302 · Database Management Systems · Section A Morning Slot
          </p>
        </div>
        <Button
          variant="primary"
          leftIcon={<Save className="w-4 h-4" />}
          onClick={() =>
            addToast(
              'Attendance Sheet Committed',
              `Saved lecture attendance for ${students.length} students.`,
              'success'
            )
          }
        >
          Save Attendance
        </Button>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
        {students.map((stu) => {
          const isPresent = presentMap[stu.id] ?? true;
          return (
            <div key={stu.id} className="p-4 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-slate-900">{stu.name}</p>
                <p className="text-xs font-mono text-slate-500">
                  {stu.rollOrEmpId} · {stu.department}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setPresentMap((p) => ({ ...p, [stu.id]: true }))}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg border cursor-pointer ${
                    isPresent
                      ? 'bg-emerald-600 text-white border-emerald-600'
                      : 'bg-white text-slate-600 border-slate-200'
                  }`}
                >
                  Present
                </button>
                <button
                  type="button"
                  onClick={() => setPresentMap((p) => ({ ...p, [stu.id]: false }))}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg border cursor-pointer ${
                    !isPresent
                      ? 'bg-red-600 text-white border-red-600'
                      : 'bg-white text-slate-600 border-slate-200'
                  }`}
                >
                  Absent
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
