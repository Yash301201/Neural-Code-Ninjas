import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  GraduationCap,
  Eye,
  EyeOff,
  UserPlus,
  BookOpen,
  Users,
  Building2,
  ShieldCheck,
} from 'lucide-react';
import loginIllustration from '../assets/images/login_engineering_illustration_1793426956858.jpg';
import { useApp } from '../context/AppContext';
import { UserRole } from '../types';
import { Button } from '../components/Button';

const ROLES: {
  role: UserRole;
  label: string;
  icon: React.ReactNode;
  route: string;
}[] = [
  {
    role: UserRole.STUDENT,
    label: 'Student',
    icon: <BookOpen className="w-4 h-4" />,
    route: '/student',
  },
  {
    role: UserRole.FACULTY,
    label: 'Faculty',
    icon: <Users className="w-4 h-4" />,
    route: '/faculty',
  },
  {
    role: UserRole.HOD,
    label: 'HOD',
    icon: <Building2 className="w-4 h-4" />,
    route: '/hod',
  },
  {
    role: UserRole.ADMIN,
    label: 'Admin',
    icon: <ShieldCheck className="w-4 h-4" />,
    route: '/admin',
  },
];

const DEPARTMENTS = [
  'Computer Science & Engineering',
  'Electronics & Communication',
  'Electrical & Electronics',
  'Mechanical Engineering',
  'Civil & Infrastructure Engineering',
];

export const Register: React.FC = () => {
  const { addUser, loginAsRole } = useApp();
  const navigate = useNavigate();

  const [role, setRole] = useState<UserRole>(UserRole.STUDENT);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [rollOrEmpId, setRollOrEmpId] = useState('');
  const [department, setDepartment] = useState(DEPARTMENTS[0]);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [imgError, setImgError] = useState(false);

  const validate = () => {
    const errs: Record<string, string> = {};
    if (fullName.trim().length < 3) {
      errs.fullName = 'Enter your full name (minimum 3 characters).';
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      errs.email = 'Enter a valid institutional email address.';
    }
    if (rollOrEmpId.trim().length < 4) {
      errs.rollOrEmpId =
        role === UserRole.STUDENT
          ? 'Enter a valid university Roll Number (e.g., 23CS1099).'
          : 'Enter a valid Employee ID (e.g., FAC-CS-220).';
    }
    if (password.length < 8) {
      errs.password = 'Password must be at least 8 characters long.';
    }
    if (password !== confirmPassword) {
      errs.confirmPassword = 'Passwords do not match.';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    setTimeout(() => {
      addUser({
        name: fullName.trim(),
        email: email.trim(),
        role,
        department,
        rollOrEmpId: rollOrEmpId.trim().toUpperCase(),
        semester: role === UserRole.STUDENT ? 'Semester 5 (B.Tech)' : undefined,
        designation: role !== UserRole.STUDENT ? 'Faculty Member' : undefined,
        status: 'Active',
        attendance: role === UserRole.STUDENT ? 100 : undefined,
        cgpaOrScore: role === UserRole.STUDENT ? 80 : undefined,
      });
      loginAsRole(role, email.trim(), fullName.trim());
      setIsSubmitting(false);
      const dest = ROLES.find((r) => r.role === role)?.route || '/student';
      navigate(dest);
    }, 400);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] grid grid-cols-1 lg:grid-cols-12 items-stretch">
      {/* Left Column: Registration Form */}
      <div className="lg:col-span-6 bg-white flex flex-col justify-between px-6 sm:px-12 xl:px-20 py-8 border-r border-slate-200">
        <div className="flex items-center justify-between">
          <Link to="/login" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-[#2563EB] flex items-center justify-center text-white">
              <GraduationCap className="w-5 h-5" />
            </div>
            <span className="text-lg font-bold font-display tracking-tight text-slate-900">
              LearnPath AI
            </span>
          </Link>
          <Link
            to="/login"
            className="text-sm font-medium text-[#2563EB] hover:text-blue-700"
          >
            Sign in instead
          </Link>
        </div>

        <div className="max-w-md w-full mx-auto my-8 space-y-5">
          <div className="space-y-1">
            <h1 className="text-2xl sm:text-3xl font-bold font-display text-slate-900 tracking-tight">
              Create institutional account
            </h1>
            <p className="text-sm text-slate-500">
              Enroll in adaptive assessments, study coaching, or faculty analytics.
            </p>
          </div>

          {/* Role Selection */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-700">
              Account Role
            </label>
            <div className="grid grid-cols-4 gap-2">
              {ROLES.map((item) => {
                const active = role === item.role;
                return (
                  <button
                    key={item.role}
                    type="button"
                    onClick={() => setRole(item.role)}
                    className={`flex items-center justify-center gap-1.5 py-2 px-2.5 rounded-lg border text-xs font-semibold transition-colors cursor-pointer ${
                      active
                        ? 'border-[#2563EB] bg-blue-50 text-[#2563EB]'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <form onSubmit={handleSubmit} noValidate className="space-y-3.5">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Neha Venkataraman"
                  className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                />
                {errors.fullName && (
                  <p className="mt-1 text-xs text-red-600">{errors.fullName}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  {role === UserRole.STUDENT ? 'University Roll No.' : 'Employee ID'}
                </label>
                <input
                  type="text"
                  value={rollOrEmpId}
                  onChange={(e) => setRollOrEmpId(e.target.value)}
                  placeholder={role === UserRole.STUDENT ? '23CS1094' : 'FAC-CS-230'}
                  className="w-full px-3.5 py-2 text-sm font-mono border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                />
                {errors.rollOrEmpId && (
                  <p className="mt-1 text-xs text-red-600">{errors.rollOrEmpId}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Engineering Department
              </label>
              <select
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full px-3.5 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
              >
                {DEPARTMENTS.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                College Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="neha.v@nitk-edu.ac.in"
                className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
              />
              {errors.email && (
                <p className="mt-1 text-xs text-red-600">{errors.email}</p>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPass ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min. 8 characters"
                    className="w-full pl-3.5 pr-9 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass(!showPass)}
                    aria-label={showPass ? 'Hide password' : 'Show password'}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 cursor-pointer"
                  >
                    {showPass ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1 text-xs text-red-600">{errors.password}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Confirm Password
                </label>
                <input
                  type={showPass ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat password"
                  className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                />
                {errors.confirmPassword && (
                  <p className="mt-1 text-xs text-red-600">{errors.confirmPassword}</p>
                )}
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isSubmitting}
              leftIcon={<UserPlus className="w-4 h-4" />}
              className="w-full mt-2"
            >
              Complete Registration
            </Button>
          </form>

          <p className="text-center text-xs text-slate-500">
            Already registered?{' '}
            <Link to="/login" className="font-semibold text-[#2563EB] hover:text-blue-700">
              Sign in to your account
            </Link>
          </p>
        </div>

        <div className="text-xs text-slate-400">
          <span>Protected under Institutional Academic Data Policy</span>
        </div>
      </div>

      {/* Right Column: Educational Visual */}
      <div className="hidden lg:flex lg:col-span-6 bg-[#F8FAFC] p-10 xl:p-16 flex-col justify-center">
        <div className="max-w-xl mx-auto w-full space-y-7">
          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
            {!imgError ? (
              <img
                src={loginIllustration}
                alt="Engineering notebooks, data graphs, and adaptive curriculum architecture"
                referrerPolicy="no-referrer"
                onError={() => setImgError(true)}
                className="w-full aspect-[4/3] object-cover"
              />
            ) : (
              <div className="w-full aspect-[4/3] bg-slate-100 flex items-center justify-center">
                <GraduationCap className="w-12 h-12 text-[#2563EB]" />
              </div>
            )}
          </div>

          <div className="space-y-3">
            <h2 className="text-2xl font-bold font-display text-slate-900 tracking-tight text-balance">
              Built for Modern Engineering Campuses
            </h2>
            <p className="text-sm text-slate-600 leading-relaxed">
              Students receive daily targeted remediation schedules for weak topics, while
              faculty and department heads automate question authoring and continuous
              assessment analytics.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
