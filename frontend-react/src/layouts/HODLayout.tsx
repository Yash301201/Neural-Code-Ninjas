import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  Users,
  GraduationCap,
  BookOpen,
  LineChart,
  AlertTriangle,
  CalendarCheck,
  FileSpreadsheet,
  UserCircle,
} from 'lucide-react';
import { Sidebar, SidebarNavItem } from '../components/Sidebar';
import { Header } from '../components/Header';

const HOD_NAV: SidebarNavItem[] = [
  { label: 'AI Knowledge Assistant', to: '/hod/rag-assistant', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Dataset Analytics', to: '/hod/dataset-analytics', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Dashboard', to: '/hod', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Departments', to: '/hod/departments', icon: <Building2 className="w-4 h-4" /> },
  { label: 'Faculty', to: '/hod/faculty', icon: <Users className="w-4 h-4" /> },
  { label: 'Students', to: '/hod/students', icon: <GraduationCap className="w-4 h-4" /> },
  { label: 'Courses', to: '/hod/courses', icon: <BookOpen className="w-4 h-4" /> },
  {
    label: 'Subject Analytics',
    to: '/hod/analytics',
    icon: <LineChart className="w-4 h-4" />,
  },
  {
    label: 'At-Risk Students',
    to: '/hod/at-risk',
    icon: <AlertTriangle className="w-4 h-4" />,
  },
  {
    label: 'Attendance Analytics',
    to: '/hod/attendance-analytics',
    icon: <CalendarCheck className="w-4 h-4" />,
  },
  { label: 'Reports', to: '/hod/reports', icon: <FileSpreadsheet className="w-4 h-4" /> },
  { label: 'Profile', to: '/hod/profile', icon: <UserCircle className="w-4 h-4" /> },
];

export const HODLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen flex bg-[#F8FAFC] text-slate-900">
      <Sidebar
        roleLabel="HOD"
        items={HOD_NAV}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header roleTitle="HOD Portal" onOpenMobileMenu={() => setMobileOpen(true)} />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1440px] w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
