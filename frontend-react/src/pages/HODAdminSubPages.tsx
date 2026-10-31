import React, { useState } from 'react';
import {
  Building2,
  Download,
  Calendar,
  Plus,
  Save,
  UserCircle,
  CheckCircle2,
} from 'lucide-react';
import { STUDENT_COURSES, AT_RISK_STUDENTS } from '../data/mockData';
import { CourseItem, UserRole } from '../types';
import { useApp } from '../context/AppContext';
import { DataTable, ColumnDef } from '../components/DataTable';
import { Button } from '../components/Button';

export const DepartmentsView: React.FC = () => {
  const { departments } = useApp();

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          Engineering Departments Directory
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Program capacity, faculty leadership, and mean outcome performance across branches.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {departments.map((d) => (
          <div
            key={d.id}
            className="bg-white border border-slate-200 rounded-xl p-5 space-y-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-mono font-bold text-[#2563EB]">{d.code}</p>
                <h2 className="text-base font-semibold font-display text-slate-900 mt-0.5">
                  {d.name}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">HOD: {d.hodName}</p>
              </div>
              <Building2 className="w-5 h-5 text-slate-400" />
            </div>

            <div className="grid grid-cols-3 gap-2 pt-3 border-t border-slate-100 text-xs tabular-nums">
              <div>
                <p className="text-slate-500">Students</p>
                <p className="font-mono font-bold text-slate-900 text-sm">{d.totalStudents}</p>
              </div>
              <div>
                <p className="text-slate-500">Faculty</p>
                <p className="font-mono font-bold text-slate-900 text-sm">{d.totalFaculty}</p>
              </div>
              <div>
                <p className="text-slate-500">Mean Score</p>
                <p className="font-mono font-bold text-emerald-700 text-sm">
                  {d.avgPerformance}%
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const PeopleDirectory: React.FC<{ filterRole: UserRole }> = ({ filterRole }) => {
  const { users } = useApp();
  const list = users.filter((u) => u.role === filterRole);

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900 capitalize">
          {filterRole === UserRole.FACULTY ? 'Faculty Members Roster' : 'Enrolled Students Roster'}
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Institutional academic directory with roll numbers, employee IDs, and departments.
        </p>
      </div>

      <DataTable
        data={list}
        rowKey={(u) => u.id}
        searchPlaceholder="Search name, ID, or department..."
        searchMatcher={(u, q) =>
          u.name.toLowerCase().includes(q) ||
          u.rollOrEmpId.toLowerCase().includes(q) ||
          u.department.toLowerCase().includes(q)
        }
        columns={[
          {
            key: 'name',
            header: 'Full Name',
            sortable: true,
            sortValue: (u) => u.name,
            render: (u) => (
              <div>
                <p className="font-semibold text-slate-900">{u.name}</p>
                <p className="text-xs text-slate-500">{u.email}</p>
              </div>
            ),
          },
          {
            key: 'id',
            header: filterRole === UserRole.STUDENT ? 'Roll No.' : 'Employee ID',
            render: (u) => <span className="font-mono text-xs">{u.rollOrEmpId}</span>,
          },
          {
            key: 'dept',
            header: 'Department',
            render: (u) => <span className="text-xs text-slate-700">{u.department}</span>,
          },
          {
            key: 'meta',
            header: filterRole === UserRole.STUDENT ? 'Attendance' : 'Designation',
            align: filterRole === UserRole.STUDENT ? 'right' : 'left',
            render: (u) =>
              filterRole === UserRole.STUDENT ? (
                <span className="font-mono text-xs">{u.attendance ?? 85}%</span>
              ) : (
                <span className="text-xs text-slate-600">
                  {u.designation || 'Assistant Professor'}
                </span>
              ),
          },
        ]}
      />
    </div>
  );
};

export const CoursesCatalog: React.FC = () => {
  const cols: ColumnDef<CourseItem>[] = [
    {
      key: 'code',
      header: 'Code',
      render: (c) => <span className="font-mono font-bold text-[#2563EB] text-xs">{c.code}</span>,
    },
    {
      key: 'name',
      header: 'Course Title',
      sortable: true,
      sortValue: (c) => c.name,
      render: (c) => <span className="font-semibold text-slate-900">{c.name}</span>,
    },
    {
      key: 'faculty',
      header: 'Course Coordinator',
      render: (c) => <span className="text-xs text-slate-600">{c.faculty}</span>,
    },
    {
      key: 'credits',
      header: 'Credits',
      align: 'right',
      render: (c) => <span className="font-mono">{c.credits}</span>,
    },
    {
      key: 'avgScore',
      header: 'Mean Score',
      align: 'right',
      sortable: true,
      sortValue: (c) => c.avgScore,
      render: (c) => <span className="font-mono font-semibold">{c.avgScore}%</span>,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          CBCS Engineering Curriculum & Subjects
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Credit allocation, faculty coordinators, and outcome averages across subjects.
        </p>
      </div>

      <DataTable
        data={STUDENT_COURSES}
        columns={cols}
        rowKey={(c) => c.id}
        searchPlaceholder="Search course code, title, or coordinator..."
        searchMatcher={(c, q) =>
          c.code.toLowerCase().includes(q) ||
          c.name.toLowerCase().includes(q) ||
          c.faculty.toLowerCase().includes(q)
        }
      />
    </div>
  );
};

export const AtRiskStudentsPage: React.FC = () => {
  const { addToast } = useApp();

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          At-Risk Student Early Warning & Remediation
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Students below 62% academic average or 75% mandatory attendance threshold.
        </p>
      </div>

      <DataTable
        data={AT_RISK_STUDENTS}
        rowKey={(r) => r.id}
        searchPlaceholder="Search student, roll number, or department..."
        searchMatcher={(r, q) =>
          r.name.toLowerCase().includes(q) ||
          r.rollNo.toLowerCase().includes(q) ||
          r.department.toLowerCase().includes(q)
        }
        filterOptions={[
          { label: 'Critical', value: 'Critical' },
          { label: 'Moderate', value: 'Moderate' },
        ]}
        filterMatcher={(r, f) => r.riskLevel === f}
        columns={[
          {
            key: 'name',
            header: 'Student',
            render: (r) => (
              <div>
                <p className="font-semibold text-slate-900">{r.name}</p>
                <p className="text-xs font-mono text-slate-500">{r.rollNo}</p>
              </div>
            ),
          },
          {
            key: 'dept',
            header: 'Department',
            render: (r) => <span className="text-xs">{r.department}</span>,
          },
          {
            key: 'marks',
            header: 'Avg Marks',
            align: 'right',
            render: (r) => (
              <span className="font-mono font-semibold text-red-600">{r.avgMarks}%</span>
            ),
          },
          {
            key: 'att',
            header: 'Attendance',
            align: 'right',
            render: (r) => <span className="font-mono">{r.attendance}%</span>,
          },
          {
            key: 'act',
            header: 'Action',
            align: 'right',
            render: (r) => (
              <Button
                size="sm"
                variant="outline"
                onClick={() =>
                  addToast(
                    'Study Coach Triggered',
                    `Activated mandatory 5-day remediation plan for ${r.name}.`,
                    'success'
                  )
                }
              >
                Trigger Coach Plan
              </Button>
            ),
          },
        ]}
      />
    </div>
  );
};

export const ReportsCenter: React.FC = () => {
  const { addToast } = useApp();
  const reports = [
    {
      id: 'rep-1',
      title: 'NBA Course Outcome (CO-PO) Attainment Matrix — Odd Sem 2026',
      scope: 'All B.Tech Semesters 3, 5, 7',
      updated: '2026-10-29',
    },
    {
      id: 'rep-2',
      title: 'Monthly Attendance Shortage & Detainment Risk Ledger',
      scope: '5 Engineering Departments',
      updated: '2026-10-28',
    },
    {
      id: 'rep-3',
      title: 'Adaptive AI Study Coach Efficacy & Score Lift Audit',
      scope: 'CS302 & CS304 Remediation Cohorts',
      updated: '2026-10-25',
    },
  ];

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          Institutional Reports & Accreditation Exports
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Download NAAC / NBA ready analytical summaries and semester grade sheets.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
        {reports.map((rep) => (
          <div
            key={rep.id}
            className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
          >
            <div>
              <p className="text-sm font-semibold text-slate-900">{rep.title}</p>
              <p className="text-xs text-slate-500 tabular-nums mt-0.5">
                {rep.scope} · Generated {rep.updated}
              </p>
            </div>
            <Button
              size="sm"
              variant="outline"
              leftIcon={<Download className="w-3.5 h-3.5 text-[#2563EB]" />}
              onClick={() =>
                addToast('Report Downloaded', `Exported "${rep.title}" as CSV.`, 'success')
              }
            >
              Download CSV
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
};

export const SectionsPage: React.FC = () => {
  const sections = [
    { code: 'CSE-5A', dept: 'Computer Science & Engg', strength: 62, advisor: 'Dr. Meera Krishnan', room: 'LH-201' },
    { code: 'CSE-5B', dept: 'Computer Science & Engg', strength: 62, advisor: 'Dr. Siddharth Verma', room: 'LH-202' },
    { code: 'ECE-5A', dept: 'Electronics & Comm.', strength: 58, advisor: 'Prof. Ananya Chatterjee', room: 'EC-104' },
    { code: 'EEE-5A', dept: 'Electrical & Electronics', strength: 54, advisor: 'Dr. Harish Patel', room: 'EE-108' },
  ];

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          Academic Class Sections & Lab Batches
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Section-wise student allocations, lecture halls, and faculty class advisors.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {sections.map((s) => (
          <div key={s.code} className="bg-white border border-slate-200 rounded-xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-mono font-bold text-[#2563EB] text-sm">{s.code}</span>
              <span className="text-xs font-mono text-slate-500">Room {s.room}</span>
            </div>
            <p className="text-sm font-semibold text-slate-900">{s.dept}</p>
            <p className="text-xs text-slate-600 tabular-nums">
              {s.strength} Students · Advisor: {s.advisor}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export const AcademicCalendarPage: React.FC = () => {
  const { addToast } = useApp();
  const [events, setEvents] = useState([
    { id: 'ev-1', date: '2026-11-02', title: 'Adaptive Diagnostic Window — CS302 & CS304', category: 'Assessment' },
    { id: 'ev-2', date: '2026-11-12', title: 'Internal Lab Practical Examinations', category: 'Laboratory' },
    { id: 'ev-3', date: '2026-11-24', title: 'Last Date for Attendance Condonation Review', category: 'Governance' },
    { id: 'ev-4', date: '2026-12-03', title: 'End-Semester Theory Examinations Commence', category: 'University Exam' },
  ]);
  const [title, setTitle] = useState('');
  const [date, setDate] = useState('2026-11-18');

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setEvents((prev) => [
      ...prev,
      { id: `ev-${Date.now()}`, date, title: title.trim(), category: 'Academic' },
    ]);
    setTitle('');
    addToast('Calendar Milestone Added', 'Published to institutional academic calendar.', 'success');
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          Institutional Academic Calendar (Odd Sem 2026–27)
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Key examination windows, lab evaluations, and semester governance milestones.
        </p>
      </div>

      <form
        onSubmit={handleAdd}
        className="bg-white border border-slate-200 rounded-xl p-5 flex flex-col sm:flex-row gap-3"
      >
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="px-3 py-2 text-sm font-mono border border-slate-200 rounded-lg"
        />
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Add academic event or exam milestone..."
          className="flex-1 px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
        />
        <Button type="submit" variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
          Add Event
        </Button>
      </form>

      <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
        {events.map((ev) => (
          <div key={ev.id} className="p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <Calendar className="w-4 h-4 text-[#2563EB] shrink-0" />
              <div>
                <p className="text-sm font-semibold text-slate-900">{ev.title}</p>
                <p className="text-xs text-slate-500">{ev.category}</p>
              </div>
            </div>
            <span className="font-mono text-xs text-slate-700 tabular-nums">{ev.date}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const SystemSettingsPage: React.FC = () => {
  const { addToast } = useApp();
  const [minAttendance, setMinAttendance] = useState(75);
  const [autoRemediation, setAutoRemediation] = useState(true);
  const [nbaMapping, setNbaMapping] = useState(true);

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h1 className="text-2xl font-bold font-display text-slate-900">
          System & Academic Policy Settings
        </h1>
        <p className="text-sm text-slate-600 mt-0.5">
          Configure institution-wide attendance thresholds and adaptive coaching policies.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-5">
        <div>
          <div className="flex justify-between text-sm font-medium text-slate-900 mb-1.5">
            <span>Minimum Mandatory Attendance Threshold</span>
            <span className="font-mono font-bold text-[#2563EB] tabular-nums">
              {minAttendance}%
            </span>
          </div>
          <input
            type="range"
            min={65}
            max={85}
            value={minAttendance}
            onChange={(e) => setMinAttendance(Number(e.target.value))}
            className="w-full accent-[#2563EB]"
          />
        </div>

        <label className="flex items-center justify-between py-3 border-t border-slate-100 cursor-pointer">
          <div>
            <p className="text-sm font-semibold text-slate-900">
              Automatic AI Study Coach Remediation
            </p>
            <p className="text-xs text-slate-500">
              Generate 5-day recovery schedules automatically when test score drops below 60%
            </p>
          </div>
          <input
            type="checkbox"
            checked={autoRemediation}
            onChange={(e) => setAutoRemediation(e.target.checked)}
            className="w-4 h-4 accent-[#2563EB]"
          />
        </label>

        <label className="flex items-center justify-between py-3 border-t border-slate-100 cursor-pointer">
          <div>
            <p className="text-sm font-semibold text-slate-900">
              Enforce NBA CO-PO Tagging on Question Bank
            </p>
            <p className="text-xs text-slate-500">
              Require Course Outcome metadata when approving faculty-generated items
            </p>
          </div>
          <input
            type="checkbox"
            checked={nbaMapping}
            onChange={(e) => setNbaMapping(e.target.checked)}
            className="w-4 h-4 accent-[#2563EB]"
          />
        </label>

        <div className="flex justify-end pt-2">
          <Button
            variant="primary"
            leftIcon={<Save className="w-4 h-4" />}
            onClick={() =>
              addToast(
                'System Policies Updated',
                `Saved ${minAttendance}% attendance rule and adaptive coaching preferences.`,
                'success'
              )
            }
          >
            Save Configuration
          </Button>
        </div>
      </div>
    </div>
  );
};

export const UserProfilePage: React.FC = () => {
  const { currentUser, addToast } = useApp();
  const [phone, setPhone] = useState('+91 98450 22104');
  const [digestEnabled, setDigestEnabled] = useState(true);

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex items-center gap-4">
        <div className="w-14 h-14 rounded-full bg-[#2563EB] text-white flex items-center justify-center font-display font-bold text-xl shrink-0">
          <UserCircle className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-2xl font-bold font-display text-slate-900">
            {currentUser?.name || 'Academic User'}
          </h1>
          <p className="text-sm text-slate-600 capitalize">
            {currentUser?.role} · {currentUser?.department} ·{' '}
            <span className="font-mono">{currentUser?.rollOrEmpId}</span>
          </p>
        </div>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          addToast('Profile Preferences Saved', 'Updated contact and notification settings.', 'success');
        }}
        className="bg-white border border-slate-200 rounded-xl p-6 space-y-4"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Institutional Email
            </label>
            <input
              type="email"
              disabled
              value={currentUser?.email || ''}
              className="w-full px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg text-slate-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Campus Mobile Number
            </label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full px-3.5 py-2 text-sm font-mono border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
            />
          </div>
        </div>

        <label className="flex items-center justify-between py-3 border-t border-slate-100 cursor-pointer">
          <div>
            <p className="text-sm font-semibold text-slate-900">
              Weekly Academic Progress & Exam Alerts
            </p>
            <p className="text-xs text-slate-500">
              Receive email reminders 24 hours prior to scheduled online tests
            </p>
          </div>
          <input
            type="checkbox"
            checked={digestEnabled}
            onChange={(e) => setDigestEnabled(e.target.checked)}
            className="w-4 h-4 accent-[#2563EB]"
          />
        </label>

        <div className="flex items-center justify-between pt-2">
          <span className="inline-flex items-center gap-1.5 text-xs text-emerald-700 font-medium">
            <CheckCircle2 className="w-4 h-4" />
            Verified Campus Identity
          </span>
          <Button type="submit" variant="primary">
            Update Profile
          </Button>
        </div>
      </form>
    </div>
  );
};
