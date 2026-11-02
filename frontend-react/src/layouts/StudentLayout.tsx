import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  FileCheck2,
  ClipboardList,
  CalendarCheck,
  TrendingUp,
  Compass,
  MessageSquareCode,
  UserCircle,
} from 'lucide-react';
import { Sidebar, SidebarNavItem } from '../components/Sidebar';
import { Header } from '../components/Header';

const STUDENT_NAV: SidebarNavItem[] = [
 {label:'Exam Performance',to:"/student/performance-insights",icon:<LayoutDashboard className="w-4 h-4"/>},
 {label:'Teaching Feedback',to:"/student/teaching-feedback",icon:<LayoutDashboard className="w-4 h-4"/>},
  { label: 'AI Knowledge Assistant', to: '/student/rag-assistant', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Engineering Dataset', to: '/student/dataset-analytics', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Dashboard', to: '/student', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'My Courses', to: '/student/courses', icon: <BookOpen className="w-4 h-4" /> },
  { label: 'Online Tests', to: '/student/online-test', icon: <FileCheck2 className="w-4 h-4" /> },
  { label: 'Assignments', to: '/student/assignments', icon: <ClipboardList className="w-4 h-4" /> },
  { label: 'Attendance', to: '/student/attendance', icon: <CalendarCheck className="w-4 h-4" /> },
  { label: 'Performance', to: '/student/performance', icon: <TrendingUp className="w-4 h-4" /> },
  {
    label: 'AI Study Coach',
    to: '/student/study-coach',
    icon: <Compass className="w-4 h-4" />,
    isAiFeature: true,
  },
  {
    label: 'AI Doubt Assistant',
    to: '/student/doubt-assistant',
    icon: <MessageSquareCode className="w-4 h-4" />,
    isAiFeature: true,
  },
  { label: 'Profile', to: '/student/profile', icon: <UserCircle className="w-4 h-4" /> },
];

export const StudentLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen flex bg-[#F8FAFC] text-slate-900">
      <Sidebar
        roleLabel="Student"
        items={STUDENT_NAV}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          roleTitle="Student Portal"
          onOpenMobileMenu={() => setMobileOpen(true)}
        />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1440px] w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
