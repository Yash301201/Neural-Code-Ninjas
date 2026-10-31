import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { Button } from './Button';

export const ConfirmModal: React.FC = () => {
  const { confirmDialog, closeConfirm } = useApp();

  if (!confirmDialog.isOpen) return null;

  const handleConfirm = () => {
    confirmDialog.onConfirm();
    closeConfirm();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div
        className="fixed inset-0 bg-slate-900/45 backdrop-blur-[1px]"
        onClick={closeConfirm}
      />
      <div className="relative z-10 bg-white border border-slate-200 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
        <div className="flex items-start gap-3.5">
          <div
            className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
              confirmDialog.variant === 'danger'
                ? 'bg-red-50 text-red-600'
                : 'bg-blue-50 text-[#2563EB]'
            }`}
          >
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h3
              id="confirm-modal-title"
              className="text-base font-semibold text-slate-900 font-display"
            >
              {confirmDialog.title}
            </h3>
            <p className="text-sm text-slate-600 leading-relaxed">{confirmDialog.message}</p>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2.5 pt-2">
          <Button variant="outline" size="md" onClick={closeConfirm}>
            {confirmDialog.cancelLabel || 'Cancel'}
          </Button>
          <Button
            variant={confirmDialog.variant === 'danger' ? 'danger' : 'primary'}
            size="md"
            onClick={handleConfirm}
          >
            {confirmDialog.confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
};
