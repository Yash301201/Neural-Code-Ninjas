import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Building2,
  BookOpen,
  BookMarked,
  ListTree,
  Layers,
  Calendar,
  Settings,
  UserCircle,
} from 'lucide-react';
import { Sidebar, SidebarNavItem } from '../components/Sidebar';
import { Header } from '../components/Header';

const ADMIN_NAV: SidebarNavItem[] = [
 {label:'Years, Curriculum & Teaching',to:'/admin/curriculum',icon:<LayoutDashboard className="w-4 h-4"/>},
 {label:'AI Question Generator',to:'/admin/question-generator',icon:<LayoutDashboard className="w-4 h-4"/>},
 {label:'Answer Evaluation',to:'/admin/evaluation',icon:<LayoutDashboard className="w-4 h-4"/>},
 {label:'Exam Performance',to:"/admin/performance-insights",icon:<LayoutDashboard className="w-4 h-4"/>},
 {label:'Colleague Feedback',to:"/admin/teaching-feedback",icon:<LayoutDashboard className="w-4 h-4"/>},
 {label:'Staff Development',to:"/admin/staff-development",icon:<LayoutDashboard className="w-4 h-4"/>},
 {label:'Academic Data Centre',to:"/admin/academic-data",icon:<LayoutDashboard className="w-4 h-4"/>},
 {label:'Question Bank',to:"/admin/question-bank",icon:<LayoutDashboard className="w-4 h-4"/>},
 {label:'Assignments',to:"/admin/assignments",icon:<LayoutDashboard className="w-4 h-4"/>},
  {label:'Student Directory · UG / PG',to:'/admin/student-directory',icon:<Users className="w-4 h-4"/>},
  {label:'Faculty & HOD Directory',to:'/admin/staff-directory',icon:<Users className="w-4 h-4"/>},
  { label: 'Institution Operations', to: '/admin/management', icon: <Users className="w-4 h-4" /> },
  { label: 'Exam Studio', to: '/admin/exam-studio', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Attendance Register', to: '/admin/attendance', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Learner Register', to: '/admin/learner-register', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Weekly Timetable', to: '/admin/timetable', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Faculty Leave Approvals', to: '/admin/faculty-leave', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'UG / PG Programs', to: '/admin/programs', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'AI Knowledge Assistant', to: '/admin/rag-assistant', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Engineering Dataset', to: '/admin/dataset-analytics', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Dashboard', to: '/admin', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'User Management', to: '/admin/users', icon: <Users className="w-4 h-4" /> },
  { label: 'Departments', to: '/admin/departments', icon: <Building2 className="w-4 h-4" /> },
  { label: 'Courses', to: '/admin/courses', icon: <BookOpen className="w-4 h-4" /> },
  { label: 'Subjects', to: '/admin/subjects', icon: <BookMarked className="w-4 h-4" /> },
  { label: 'Topics', to: '/admin/topics', icon: <ListTree className="w-4 h-4" /> },
  { label: 'Sections', to: '/admin/sections', icon: <Layers className="w-4 h-4" /> },
  { label: 'Academic Calendar', to: '/admin/calendar', icon: <Calendar className="w-4 h-4" /> },
  { label: 'System Settings', to: '/admin/settings', icon: <Settings className="w-4 h-4" /> },
  { label: 'Profile', to: '/admin/profile', icon: <UserCircle className="w-4 h-4" /> },
];

export const AdminLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen flex bg-[#F8FAFC] text-slate-900">
      <Sidebar
        roleLabel="Admin"
        items={ADMIN_NAV}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header roleTitle="Admin Portal" onOpenMobileMenu={() => setMobileOpen(true)} />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1440px] w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
