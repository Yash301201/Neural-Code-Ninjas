import React, { useState } from 'react';
import {
  Users,
  GraduationCap,
  UserCog,
  Building2,
  BookOpen,
  UserPlus,
  Plus,
  CheckCircle2,
  Clock,
  XCircle,
  X,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { UserProfile, UserRole } from '../types';
import { StatCard } from '../components/StatCard';
import { DataTable, ColumnDef } from '../components/DataTable';
import { Button } from '../components/Button';

export const AdminDashboard: React.FC = () => {
  const { users, departments, addUser, updateUserStatus, addDepartment } = useApp();

  // Modal state: 'student' | 'faculty' | 'department' | null
  const [modalMode, setModalMode] = useState<'student' | 'faculty' | 'department' | null>(
    null
  );

  // User Form State
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [rollOrId, setRollOrId] = useState('');
  const [deptName, setDeptName] = useState(departments[0]?.name || 'Computer Science & Engineering');
  const [formError, setFormError] = useState('');

  // Department Form State
  const [newDeptCode, setNewDeptCode] = useState('');
  const [newDeptName, setNewDeptName] = useState('');
  const [newDeptHod, setNewDeptHod] = useState('');
  const [newDeptCourses, setNewDeptCourses] = useState('16');

  const openModal = (mode: 'student' | 'faculty' | 'department') => {
    setFormError('');
    setName('');
    setEmail('');
    setRollOrId('');
    setNewDeptCode('');
    setNewDeptName('');
    setNewDeptHod('');
    setModalMode(mode);
  };

  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim().length < 3) {
      setFormError('Full name must be at least 3 characters.');
      return;
    }
    if (!email.includes('@')) {
      setFormError('Enter a valid institutional email.');
      return;
    }
    if (rollOrId.trim().length < 4) {
      setFormError('Enter a valid Roll Number or Employee ID.');
      return;
    }

    const isFaculty = modalMode === 'faculty';
    addUser({
      name: name.trim(),
      email: email.trim(),
      role: isFaculty ? UserRole.FACULTY : UserRole.STUDENT,
      department: deptName,
      rollOrEmpId: rollOrId.trim().toUpperCase(),
      semester: isFaculty ? undefined : 'Semester 5 (B.Tech)',
      designation: isFaculty ? 'Assistant Professor' : undefined,
      status: 'Active',
      attendance: isFaculty ? undefined : 90,
      cgpaOrScore: isFaculty ? undefined : 78,
    });
    setModalMode(null);
  };

  const handleCreateDept = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDeptCode.trim() || !newDeptName.trim() || !newDeptHod.trim()) {
      setFormError('All department fields are required.');
      return;
    }
    addDepartment({
      code: newDeptCode.trim().toUpperCase(),
      name: newDeptName.trim(),
      hodName: newDeptHod.trim(),
      totalFaculty: 18,
      totalStudents: 240,
      totalCourses: Number(newDeptCourses) || 16,
      avgPerformance: 77.0,
      attendanceRate: 86.0,
      atRiskCount: 8,
    });
    setModalMode(null);
  };

  const totalStudentsCount =
    departments.reduce((acc, d) => acc + d.totalStudents, 0) +
    users.filter((u) => u.role === UserRole.STUDENT).length;
  const totalFacultyCount =
    departments.reduce((acc, d) => acc + d.totalFaculty, 0) +
    users.filter((u) => u.role === UserRole.FACULTY).length;
  const totalCoursesCount = departments.reduce((acc, d) => acc + d.totalCourses, 0);

  const userColumns: ColumnDef<UserProfile>[] = [
    {
      key: 'name',
      header: 'User & Email',
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
      header: 'ID / Roll No.',
      render: (u) => <span className="font-mono text-xs text-slate-700">{u.rollOrEmpId}</span>,
    },
    {
      key: 'role',
      header: 'Role',
      sortable: true,
      sortValue: (u) => u.role,
      render: (u) => (
        <span className="text-xs font-semibold capitalize text-slate-700">{u.role}</span>
      ),
    },
    {
      key: 'department',
      header: 'Department',
      sortable: true,
      sortValue: (u) => u.department,
      render: (u) => <span className="text-xs text-slate-600">{u.department}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (u) => (
        <span
          className={`inline-flex items-center gap-1.5 text-xs font-medium ${
            u.status === 'Active'
              ? 'text-emerald-700'
              : u.status === 'Pending'
              ? 'text-amber-700'
              : 'text-red-700'
          }`}
        >
          {u.status === 'Active' && <CheckCircle2 className="w-3.5 h-3.5" />}
          {u.status === 'Pending' && <Clock className="w-3.5 h-3.5" />}
          {u.status === 'Inactive' && <XCircle className="w-3.5 h-3.5" />}
          <span>{u.status}</span>
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Governance',
      align: 'right',
      render: (u) => (
        <Button
          size="sm"
          variant="outline"
          onClick={() =>
            updateUserStatus(u.id, u.status === 'Active' ? 'Inactive' : 'Active')
          }
        >
          {u.status === 'Active' ? 'Deactivate' : 'Activate'}
        </Button>
      ),
    },
  ];

  const recentRegistrations = [...users]
    .sort((a, b) => (a.joinedDate < b.joinedDate ? 1 : -1))
    .slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Header + Action Buttons */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs font-medium text-slate-500">
            Institutional Campus Administration · Academic Year 2026–27
          </p>
          <h1 className="text-2xl font-bold font-display text-slate-900 tracking-tight">
            University Governance & Directory Control
          </h1>
          <p className="text-sm text-slate-600">
            Provision student and faculty credentials, configure engineering departments,
            and manage curriculum hierarchy.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <Button
            variant="outline"
            leftIcon={<Building2 className="w-4 h-4 text-slate-700" />}
            onClick={() => openModal('department')}
          >
            Create Department
          </Button>
          <Button
            variant="outline"
            leftIcon={<UserPlus className="w-4 h-4 text-[#7C3AED]" />}
            onClick={() => openModal('faculty')}
          >
            Add Faculty
          </Button>
          <Button
            variant="primary"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => openModal('student')}
          >
            Add Student
          </Button>
        </div>
      </div>

      {/* 5 Admin KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          label="Total Active Users"
          value={(totalStudentsCount + totalFacultyCount + 14).toLocaleString()}
          subtext={`${users.length} directory records`}
          icon={<Users className="w-5 h-5" />}
          accentTone="blue"
        />
        <StatCard
          label="Total Students"
          value={totalStudentsCount.toLocaleString()}
          subtext="B.Tech & M.Tech"
          icon={<GraduationCap className="w-5 h-5" />}
          accentTone="emerald"
        />
        <StatCard
          label="Total Faculty"
          value={totalFacultyCount}
          subtext="Teaching & Lab Staff"
          icon={<UserCog className="w-5 h-5" />}
          accentTone="purple"
        />
        <StatCard
          label="Total Departments"
          value={departments.length}
          subtext="Engineering Programs"
          icon={<Building2 className="w-5 h-5" />}
          accentTone="blue"
        />
        <StatCard
          label="Total Courses"
          value={totalCoursesCount}
          subtext="CBCS Curriculum"
          icon={<BookOpen className="w-5 h-5" />}
          accentTone="amber"
        />
      </div>

      {/* User Management DataTable */}
      <DataTable
        title="Institutional User Management"
        subtitle="Search, filter by role, and manage account access across the engineering college"
        data={users}
        columns={userColumns}
        rowKey={(u) => u.id}
        searchPlaceholder="Search name, email, roll number, or department..."
        searchMatcher={(u, q) =>
          u.name.toLowerCase().includes(q) ||
          u.email.toLowerCase().includes(q) ||
          u.rollOrEmpId.toLowerCase().includes(q) ||
          u.department.toLowerCase().includes(q)
        }
        filterOptions={[
          { label: 'Students', value: UserRole.STUDENT },
          { label: 'Faculty', value: UserRole.FACULTY },
          { label: 'HOD', value: UserRole.HOD },
          { label: 'Admin', value: UserRole.ADMIN },
        ]}
        filterMatcher={(u, f) => u.role === f}
      />

      {/* Department Overview + Recent Registrations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <section className="lg:col-span-8 bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="p-5 border-b border-slate-200 flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold font-display text-slate-900">
                Engineering Department Overview
              </h3>
              <p className="text-xs text-slate-500">
                Faculty strength, student enrollment, and active courses per department
              </p>
            </div>
            <Button size="sm" variant="outline" onClick={() => openModal('department')}>
              + New Department
            </Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/70 text-xs font-semibold text-slate-600">
                  <th className="px-5 py-3">Code</th>
                  <th className="px-5 py-3">Department</th>
                  <th className="px-5 py-3">Head of Dept</th>
                  <th className="px-5 py-3 text-right">Faculty</th>
                  <th className="px-5 py-3 text-right">Students</th>
                  <th className="px-5 py-3 text-right">Courses</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {departments.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-50/80">
                    <td className="px-5 py-3 font-mono font-semibold text-[#2563EB] text-xs">
                      {d.code}
                    </td>
                    <td className="px-5 py-3 font-medium text-slate-900">{d.name}</td>
                    <td className="px-5 py-3 text-slate-600 text-xs">{d.hodName}</td>
                    <td className="px-5 py-3 text-right font-mono tabular-nums">
                      {d.totalFaculty}
                    </td>
                    <td className="px-5 py-3 text-right font-mono tabular-nums">
                      {d.totalStudents}
                    </td>
                    <td className="px-5 py-3 text-right font-mono tabular-nums">
                      {d.totalCourses}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="lg:col-span-4 bg-white border border-slate-200 rounded-xl p-5">
          <h3 className="text-base font-semibold font-display text-slate-900">
            Recent Registrations
          </h3>
          <p className="text-xs text-slate-500 mb-4">Latest onboarded campus accounts</p>
          <div className="divide-y divide-slate-100">
            {recentRegistrations.map((reg) => (
              <div
                key={reg.id}
                className="py-3 first:pt-0 last:pb-0 flex items-center justify-between gap-2"
              >
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-900 truncate">
                    {reg.name}
                  </p>
                  <p className="text-xs text-slate-500 capitalize truncate">
                    {reg.role} · {reg.department}
                  </p>
                </div>
                <span className="text-xs font-mono text-slate-400 shrink-0 tabular-nums">
                  {reg.joinedDate}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Add Student / Add Faculty / Create Department Modal */}
      {modalMode && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          <div
            className="fixed inset-0 bg-slate-900/45 backdrop-blur-[1px]"
            onClick={() => setModalMode(null)}
          />
          <div className="relative z-10 bg-white border border-slate-200 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold font-display text-slate-900">
                {modalMode === 'student' && 'Enroll New Student'}
                {modalMode === 'faculty' && 'Onboard New Faculty Member'}
                {modalMode === 'department' && 'Create Engineering Department'}
              </h3>
              <button
                type="button"
                onClick={() => setModalMode(null)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {formError && (
              <p className="text-xs font-medium text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                {formError}
              </p>
            )}

            {modalMode === 'department' ? (
              <form onSubmit={handleCreateDept} className="space-y-3.5">
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Dept Code
                    </label>
                    <input
                      type="text"
                      value={newDeptCode}
                      onChange={(e) => setNewDeptCode(e.target.value)}
                      placeholder="AIML"
                      className="w-full px-3 py-2 text-sm font-mono border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Initial Courses
                    </label>
                    <input
                      type="number"
                      min={1}
                      max={50}
                      value={newDeptCourses}
                      onChange={(e) => setNewDeptCourses(e.target.value)}
                      className="w-full px-3 py-2 text-sm font-mono border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Department Full Name
                  </label>
                  <input
                    type="text"
                    value={newDeptName}
                    onChange={(e) => setNewDeptName(e.target.value)}
                    placeholder="Artificial Intelligence & Data Science"
                    className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Head of Department (HOD)
                  </label>
                  <input
                    type="text"
                    value={newDeptHod}
                    onChange={(e) => setNewDeptHod(e.target.value)}
                    placeholder="Prof. S. Radhakrishnan"
                    className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <Button variant="outline" onClick={() => setModalMode(null)}>
                    Cancel
                  </Button>
                  <Button type="submit" variant="primary">
                    Create Department
                  </Button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleCreateUser} className="space-y-3.5">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={
                      modalMode === 'faculty' ? 'Dr. Vivek Raghuraman' : 'Ishaan Verma'
                    }
                    className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      {modalMode === 'faculty' ? 'Employee ID' : 'Roll Number'}
                    </label>
                    <input
                      type="text"
                      value={rollOrId}
                      onChange={(e) => setRollOrId(e.target.value)}
                      placeholder={modalMode === 'faculty' ? 'FAC-CS-241' : '23CS1120'}
                      className="w-full px-3.5 py-2 text-sm font-mono border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Department
                    </label>
                    <select
                      value={deptName}
                      onChange={(e) => setDeptName(e.target.value)}
                      className="w-full px-3 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                    >
                      {departments.map((d) => (
                        <option key={d.id} value={d.name}>
                          {d.code} — {d.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Institutional Email
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="user@nitk-edu.ac.in"
                    className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <Button variant="outline" onClick={() => setModalMode(null)}>
                    Cancel
                  </Button>
                  <Button type="submit" variant="primary">
                    {modalMode === 'faculty' ? 'Add Faculty' : 'Add Student'}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
