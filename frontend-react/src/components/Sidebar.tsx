import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { GraduationCap, LogOut, X } from 'lucide-react';
import { useApp } from '../context/AppContext';

export interface SidebarNavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
  isAiFeature?: boolean;
}

interface SidebarProps {
  roleLabel: string;
  items: SidebarNavItem[];
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  roleLabel,
  items,
  mobileOpen,
  onCloseMobile,
}) => {
  const { logout, requestConfirm, addToast } = useApp();
  const navigate = useNavigate();

  const handleLogoutClick = () => {
    requestConfirm({
      title: 'Sign out of LearnPath AI?',
      message:
        'Saved study progress and academic records remain in MySQL. Unsaved form inputs and view filters will be lost.',
      confirmLabel: 'Sign Out',
      variant: 'danger',
      onConfirm: () => {
        logout();
        addToast('Signed Out', 'You have been securely logged out.', 'info');
        navigate('/login');
      },
    });
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-white border-r border-slate-200 w-[260px] select-none">
      {/* Brand Header */}
      <div className="h-16 px-5 flex items-center justify-between border-b border-slate-200 shrink-0">
        <button
          type="button"
          onClick={() => {
            if (items[0]) navigate(items[0].to);
            onCloseMobile();
          }}
          className="flex items-center gap-2.5 text-left cursor-pointer focus:outline-none"
        >
          <div className="w-8 h-8 rounded-lg bg-[#2563EB] flex items-center justify-center text-white shrink-0">
            <GraduationCap className="w-5 h-5" />
          </div>
          <span className="text-base font-bold font-display tracking-tight text-slate-900 whitespace-nowrap">
            LearnPath AI
          </span>
        </button>

        <button
          type="button"
          onClick={onCloseMobile}
          aria-label="Close navigation menu"
          className="lg:hidden p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-900"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Role Context Label */}
      <div className="px-5 pt-4 pb-2">
        <p className="text-xs font-medium text-slate-400">{roleLabel} Workspace</p>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto px-3 py-1 space-y-0.5">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={
              item.to === '/student' ||
              item.to === '/faculty' ||
              item.to === '/hod' ||
              item.to === '/admin'
            }
            onClick={onCloseMobile}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 whitespace-nowrap ${
                isActive
                  ? item.isAiFeature
                    ? 'bg-violet-50 text-[#7C3AED]'
                    : 'bg-blue-50 text-[#2563EB]'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`
            }
          >
            <span className="shrink-0">{item.icon}</span>
            <span className="truncate">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Logout Footer */}
      <div className="p-3 border-t border-slate-200 shrink-0">
        <button
          type="button"
          onClick={handleLogoutClick}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:block shrink-0 h-screen sticky top-0">{sidebarContent}</aside>

      {/* Mobile Drawer Overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-[1px]"
            onClick={onCloseMobile}
          />
          <div className="relative z-10 h-full">{sidebarContent}</div>
        </div>
      )}
    </>
  );
};
