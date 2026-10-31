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
  { label: 'AI Knowledge Assistant', to: '/admin/rag-assistant', icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: 'Dataset Analytics', to: '/admin/dataset-analytics', icon: <LayoutDashboard className="w-4 h-4" /> },
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
