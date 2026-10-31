import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  BookMarked,
  ListTree,
  Database,
  Wand2,
  FilePlus2,
  ClipboardList,
  BarChart3,
  CheckSquare,
  CalendarCheck,
  UserCircle,
} from 'lucide-react';
import { Sidebar, SidebarNavItem } from '../components/Sidebar';
import { Header } from '../components/Header';

const FACULTY_NAV: SidebarNavItem[] = [
  { label: 'AI Knowledge Assistant', to: '/faculty/rag-assistant', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Dataset Analytics', to: '/faculty/dataset-analytics', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Dashboard', to: '/faculty', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'My Subjects', to: '/faculty/subjects', icon: <BookMarked className="w-4 h-4" /> },
  { label: 'Manage Topics', to: '/faculty/topics', icon: <ListTree className="w-4 h-4" /> },
  { label: 'Question Bank', to: '/faculty/question-bank', icon: <Database className="w-4 h-4" /> },
  {
    label: 'AI Question Generator',
    to: '/faculty/question-generator',
    icon: <Wand2 className="w-4 h-4" />,
    isAiFeature: true,
  },
  { label: 'Create Tests', to: '/faculty/create-test', icon: <FilePlus2 className="w-4 h-4" /> },
  { label: 'Assignments', to: '/faculty/assignments', icon: <ClipboardList className="w-4 h-4" /> },
  {
    label: 'Student Performance',
    to: '/faculty/performance',
    icon: <BarChart3 className="w-4 h-4" />,
  },
  {
    label: 'Answer Evaluation',
    to: '/faculty/evaluation',
    icon: <CheckSquare className="w-4 h-4" />,
  },
  { label: 'Attendance', to: '/faculty/attendance', icon: <CalendarCheck className="w-4 h-4" /> },
  { label: 'Profile', to: '/faculty/profile', icon: <UserCircle className="w-4 h-4" /> },
];

export const FacultyLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen flex bg-[#F8FAFC] text-slate-900">
      <Sidebar
        roleLabel="Faculty"
        items={FACULTY_NAV}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          roleTitle="Faculty Portal"
          onOpenMobileMenu={() => setMobileOpen(true)}
        />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1440px] w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
