export enum UserRole {
  STUDENT = 'student',
  FACULTY = 'faculty',
  HOD = 'hod',
  ADMIN = 'admin',
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  department: string;
  rollOrEmpId: string;
  semester?: string;
  designation?: string;
  status: 'Active' | 'Pending' | 'Inactive';
  joinedDate: string;
  attendance?: number;
  cgpaOrScore?: number;
}

export interface CourseItem {
  id: string;
  code: string;
  name: string;
  department: string;
  semester: number;
  credits: number;
  faculty: string;
  enrolledStudents: number;
  avgScore: number;
  attendanceRate: number;
  completionProgress: number;
  topicsCount: number;
}

export interface ExamResult {
  id: string;
  testTitle: string;
  subjectCode: string;
  subjectName: string;
  date: string;
  score: number;
  maxScore: number;
  percentile: number;
  status: 'Passed' | 'Needs Review' | 'Distinction';
}

export interface UpcomingTest {
  id: string;
  title: string;
  subjectCode: string;
  subjectName: string;
  date: string;
  time: string;
  durationMinutes: number;
  totalQuestions: number;
  maxMarks: number;
  difficulty: 'Adaptive' | 'Medium' | 'Hard';
}

export interface TestQuestion {
  id: string;
  number: number;
  subject: string;
  topic: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  type: 'MCQ' | 'Descriptive';
  questionText: string;
  codeSnippet?: string;
  options?: string[];
  correctOptionIndex?: number;
  correctAnswerText: string;
  explanation: string;
  marks: number;
  approved?: boolean;
}

export interface StudyTask {
  id: string;
  day: string;
  dayTitle: string;
  subject: string;
  topic: string;
  activityType: 'Concept Review' | 'SQL Lab' | 'Guided Practice' | 'Adaptive Quiz';
  durationMinutes: number;
  priority: 'High' | 'Medium' | 'Standard';
  completed: boolean;
  description: string;
  targetMasteryGain: number;
}

export interface DepartmentRecord {
  id: string;
  code: string;
  name: string;
  hodName: string;
  totalFaculty: number;
  totalStudents: number;
  totalCourses: number;
  avgPerformance: number;
  attendanceRate: number;
  atRiskCount: number;
}

export interface AssignmentRecord {
  id: string;
  title: string;
  subjectCode: string;
  subjectName: string;
  dueDate: string;
  status: 'Pending' | 'Submitted' | 'Evaluated' | 'Overdue';
  marksObtained?: number;
  maxMarks: number;
  submissionsCount?: number;
  totalStudents?: number;
}

export interface AtRiskStudent {
  id: string;
  rollNo: string;
  name: string;
  department: string;
  semester: number;
  avgMarks: number;
  attendance: number;
  weakSubjects: string[];
  riskLevel: 'Critical' | 'Moderate';
  mentorAssigned: string;
}

export interface ToastMessage {
  id: string;
  title: string;
  description?: string;
  variant: 'success' | 'warning' | 'error' | 'info';
}

export interface ConfirmDialogState {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  cancelLabel?: string;
  variant?: 'primary' | 'danger';
  onConfirm: () => void;
}
