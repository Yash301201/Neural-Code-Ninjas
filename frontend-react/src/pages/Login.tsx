import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  GraduationCap,
  Eye,
  EyeOff,
  ArrowRight,
  CheckCircle2,
  BookOpen,
  Users,
  Building2,
  ShieldCheck,
} from 'lucide-react';
import loginIllustration from '../assets/images/login_engineering_illustration_1793426956858.jpg';
import { useApp } from '../context/AppContext';
import { UserRole } from '../types';
const ROLE_EMAILS:Record<string,string>={student:'student@learnpath.dev',faculty:'faculty@learnpath.dev',hod:'hod@learnpath.dev',admin:'admin@learnpath.dev'};
import { Button } from '../components/Button';

const ROLE_OPTIONS: {
  role: UserRole;
  label: string;
  desc: string;
  icon: React.ReactNode;
  route: string;
}[] = [
  {
    role: UserRole.STUDENT,
    label: 'Student',
    desc: 'Tests & Study Coach',
    icon: <BookOpen className="w-4 h-4" />,
    route: '/student',
  },
  {
    role: UserRole.FACULTY,
    label: 'Faculty',
    desc: 'AI Questions & Grading',
    icon: <Users className="w-4 h-4" />,
    route: '/faculty',
  },
  {
    role: UserRole.HOD,
    label: 'HOD',
    desc: 'Department Analytics',
    icon: <Building2 className="w-4 h-4" />,
    route: '/hod',
  },
  {
    role: UserRole.ADMIN,
    label: 'Admin',
    desc: 'Institution Governance',
    icon: <ShieldCheck className="w-4 h-4" />,
    route: '/admin',
  },
];

export const Login: React.FC = () => {
  const { login, addToast } = useApp();
  const navigate = useNavigate();

  const [selectedRole, setSelectedRole] = useState<UserRole>(UserRole.STUDENT);
  const [email, setEmail] = useState<string>(ROLE_EMAILS.student);
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [rememberMe, setRememberMe] = useState<boolean>(true);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [imgError, setImgError] = useState<boolean>(false);

  // Forgot Password modal state
  const [forgotModalOpen, setForgotModalOpen] = useState<boolean>(false);
  const [resetEmail, setResetEmail] = useState<string>('');
  const [resetSent, setResetSent] = useState<boolean>(false);

  const handleRoleSelect = (role: UserRole) => {
    setSelectedRole(role);
    setEmail(ROLE_EMAILS[role]);
    setPassword('');
    setErrors({});
  };

  const validate = () => {
    const nextErrors: { email?: string; password?: string } = {};
    if (!email.trim()) {
      nextErrors.email = 'Institutional email address is required.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      nextErrors.email = 'Enter a valid academic email (e.g., name@college.ac.in).';
    }
    if (!password) {
      nextErrors.password = 'Password is required.';
    } else if (password.length < 6) {
      nextErrors.password = 'Password must contain at least 6 characters.';
    }
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();if(!validate())return;setIsSubmitting(true);
    try{const user=await login(email,password,selectedRole);addToast('Welcome back',user.name+' · authenticated with MySQL');navigate('/'+user.role,{replace:true})}
    catch(err){setErrors({password:(err as Error).message})}finally{setIsSubmitting(false)}
  };
  const handleForgotSubmit = (e: React.FormEvent) => {e.preventDefault();addToast('Contact your administrator','Password recovery email is not configured. An administrator can reset your password in User Management.','info');};
  return (
    <div className="min-h-screen bg-[#F8FAFC] grid grid-cols-1 lg:grid-cols-12 items-stretch">
      {/* Left Column: Authentication Form */}
      <div className="lg:col-span-6 bg-white flex flex-col justify-between px-6 sm:px-12 xl:px-20 py-8 border-r border-slate-200">
        {/* Top Brand Mark */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-[#2563EB] flex items-center justify-center text-white">
              <GraduationCap className="w-5 h-5" />
            </div>
            <span className="text-lg font-bold font-display tracking-tight text-slate-900">
              LearnPath AI
            </span>
          </div>
          <Link
            to="/register"
            className="text-sm font-medium text-[#2563EB] hover:text-blue-700 transition-colors"
          >
            Create account
          </Link>
        </div>

        {/* Center Form */}
        <div className="max-w-md w-full mx-auto my-10 space-y-6">
          <div className="space-y-1.5">
            <h1 className="text-2xl sm:text-3xl font-bold font-display text-slate-900 tracking-tight text-balance">
              Sign in to your academic workspace
            </h1>
            <p className="text-sm text-slate-500">
              Adaptive assessments, personalized study coaching, and department analytics.
            </p>
          </div>

          {/* Role Selector */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold text-slate-700">
              Select Institutional Role
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {ROLE_OPTIONS.map((item) => {
                const active = selectedRole === item.role;
                return (
                  <button
                    key={item.role}
                    type="button"
                    onClick={() => handleRoleSelect(item.role)}
                    className={`flex flex-col items-start p-2.5 rounded-lg border text-left transition-all duration-150 cursor-pointer ${
                      active
                        ? 'border-[#2563EB] bg-blue-50/70 text-[#2563EB]'
                        : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 font-semibold text-xs">
                      {item.icon}
                      <span>{item.label}</span>
                    </div>
                    <span className="text-[11px] text-slate-500 mt-1 line-clamp-1">
                      {item.desc}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            <div>
              <label
                htmlFor="login-email"
                className="block text-xs font-semibold text-slate-700 mb-1.5"
              >
                Account Email
              </label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }));
                }}
                placeholder="student@learnpath.dev"
                className={`w-full px-3.5 py-2.5 text-sm bg-white border rounded-lg text-slate-900 placeholder:text-slate-400 focus:outline-none transition-colors ${
                  errors.email
                    ? 'border-red-500 focus:border-red-600'
                    : 'border-slate-200 focus:border-[#2563EB]'
                }`}
              />
              {errors.email && (
                <p className="mt-1 text-xs text-red-600 font-medium">{errors.email}</p>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label
                  htmlFor="login-password"
                  className="block text-xs font-semibold text-slate-700"
                >
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => {
                    setResetEmail(email);
                    setResetSent(false);
                    setForgotModalOpen(true);
                  }}
                  className="text-xs font-medium text-[#2563EB] hover:text-blue-700 cursor-pointer"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errors.password)
                      setErrors((prev) => ({ ...prev, password: undefined }));
                  }}
                  placeholder="Enter your password"
                  className={`w-full pl-3.5 pr-10 py-2.5 text-sm bg-white border rounded-lg text-slate-900 placeholder:text-slate-400 focus:outline-none transition-colors ${
                    errors.password
                      ? 'border-red-500 focus:border-red-600'
                      : 'border-slate-200 focus:border-[#2563EB]'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 cursor-pointer"
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-xs text-red-600 font-medium">{errors.password}</p>
              )}
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">Session retained in this browser tab until expiry.</span>
              <span className="text-xs text-slate-400 font-mono">Secure role-based login</span>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isSubmitting}
              rightIcon={<ArrowRight className="w-4 h-4" />}
              className="w-full"
            >
              Sign in as {ROLE_OPTIONS.find((r) => r.role === selectedRole)?.label}
            </Button>
          </form>

          <p className="text-center text-xs text-slate-500 pt-2">
            New to LearnPath AI?{' '}
            <Link
              to="/register"
              className="font-semibold text-[#2563EB] hover:text-blue-700"
            >
              Register an institutional account
            </Link>
          </p>
        </div>

        {/* Footer */}
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
          <span>LearnPath AI · Adaptive Engineering Education Platform</span>
          <span>FastAPI + MySQL · Synthetic showcase data</span>
        </div>
      </div>

      {/* Right Column: Clean Educational Illustration & Outcome Proof */}
      <div className="hidden lg:flex lg:col-span-6 bg-[#F8FAFC] p-10 xl:p-16 flex-col justify-between">
        <div className="max-w-xl mx-auto w-full my-auto space-y-8">
          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
            {!imgError ? (
              <img
                src={loginIllustration}
                alt="Isometric illustration of engineering blueprints, study notebooks, and academic performance charts"
                referrerPolicy="no-referrer"
                onError={() => setImgError(true)}
                className="w-full aspect-[4/3] object-cover"
              />
            ) : (
              <div className="w-full aspect-[4/3] bg-gradient-to-br from-blue-50 via-white to-violet-50 flex flex-col items-center justify-center p-8 text-center">
                <GraduationCap className="w-14 h-14 text-[#2563EB] mb-3" />
                <p className="text-base font-semibold text-slate-900">
                  Adaptive Engineering Curriculum Intelligence
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Diagnostic Assessments · Study Roadmaps · Outcome Analytics
                </p>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <h2 className="text-2xl font-bold font-display text-slate-900 tracking-tight text-balance">
              Adaptive Assessment and GenAI Study Coach for Engineering Colleges
            </h2>
            <p className="text-sm text-slate-600 leading-relaxed">
              Identify conceptual gaps across engineering subjects, generate faculty-reviewed
              question drafts, and connect assessments, attendance and study plans
              with your academic records.
            </p>

            <div className="grid grid-cols-3 gap-4 pt-2 border-t border-slate-200">
              <div>
                <p className="text-xl font-bold font-display text-slate-900 tabular-nums">
                  MySQL
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
                  Persistent academic records and evaluated results
                </p>
              </div>
              <div>
                <p className="text-xl font-bold font-display text-slate-900 tabular-nums">
                  4 Roles
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
                  Unified Student, Faculty, HOD & Admin workflows
                </p>
              </div>
              <div>
                <p className="text-xl font-bold font-display text-slate-900 tabular-nums">
                  Argon2id
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
                  Hashed passwords and authenticated role access
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Forgot Password Dialog */}
      {forgotModalOpen && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          <div
            className="fixed inset-0 bg-slate-900/45 backdrop-blur-[1px]"
            onClick={() => setForgotModalOpen(false)}
          />
          <div className="relative z-10 bg-white border border-slate-200 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-semibold text-slate-900 font-display">
              Reset Institutional Password
            </h3>
            {resetSent ? (
              <div className="space-y-4">
                <div className="flex items-start gap-3 p-3.5 rounded-lg bg-emerald-50/70 border border-emerald-200">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                  <p className="text-xs text-emerald-900 leading-relaxed">
                    A password reset link has been sent to{' '}
                    <span className="font-semibold">{resetEmail}</span>. Check your academic
                    inbox within 15 minutes.
                  </p>
                </div>
                <div className="flex justify-end">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => setForgotModalOpen(false)}
                  >
                    Back to Sign In
                  </Button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleForgotSubmit} className="space-y-4">
                <p className="text-xs text-slate-600 leading-relaxed">
                  Enter your registered college email address and we will send you a
                  password reset through the administrator. Email recovery is not configured for this local project.
                </p>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Registered Email
                  </label>
                  <input
                    type="email"
                    required
                    value={resetEmail}
                    onChange={(e) => setResetEmail(e.target.value)}
                    placeholder="name@nitk-edu.ac.in"
                    className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setForgotModalOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" variant="primary" size="sm">
                    Contact administrator
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
