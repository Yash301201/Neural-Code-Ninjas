import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Clock,
  ChevronLeft,
  ChevronRight,
  Bookmark,
  CheckCircle2,
  Send,
  RotateCcw,
  Compass,
  Award,
  AlertCircle,
  Save,
} from 'lucide-react';
import { ONLINE_EXAM_QUESTIONS } from '../data/mockData';
import { useApp } from '../context/AppContext';
import { Button } from '../components/Button';

type QuestionStatus = 'not-visited' | 'unanswered' | 'answered' | 'review';

export const OnlineTest: React.FC = () => {
  const { addToast, requestConfirm } = useApp();
  const navigate = useNavigate();

  const totalDurationSeconds = 25 * 60; // 25 minutes
  const [secondsLeft, setSecondsLeft] = useState<number>(totalDurationSeconds);
  const [currentIdx, setCurrentIdx] = useState<number>(0);

  // Draft selection before clicking "Save Answer" (also auto-selects visually, with explicit Save Answer support)
  const [savedAnswers, setSavedAnswers] = useState<Record<string, number>>({});
  const [draftSelection, setDraftSelection] = useState<number | null>(null);
  const [markedForReview, setMarkedForReview] = useState<Record<string, boolean>>({});
  const [visited, setVisited] = useState<Record<string, boolean>>({
    [ONLINE_EXAM_QUESTIONS[0].id]: true,
  });
  const [submitted, setSubmitted] = useState<boolean>(false);

  const currentQuestion = ONLINE_EXAM_QUESTIONS[currentIdx];

  // Sync draft selection when changing questions
  useEffect(() => {
    const existing = savedAnswers[currentQuestion.id];
    setDraftSelection(existing !== undefined ? existing : null);
    setVisited((prev) => ({ ...prev, [currentQuestion.id]: true }));
  }, [currentIdx, currentQuestion.id, savedAnswers]);

  // Countdown Timer
  useEffect(() => {
    if (submitted) return;
    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setSubmitted(true);
          addToast(
            'Time Expired — Exam Auto-Submitted',
            'Your saved responses have been recorded for evaluation.',
            'warning'
          );
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [submitted, addToast]);

  const formatTimer = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${String(mins).padStart(2, '0')}:${String(rem).padStart(2, '0')}`;
  };

  const getQuestionStatus = (qId: string): QuestionStatus => {
    if (markedForReview[qId]) return 'review';
    if (savedAnswers[qId] !== undefined) return 'answered';
    if (visited[qId]) return 'unanswered';
    return 'not-visited';
  };

  const handleSaveAnswer = (advanceNext = false) => {
    if (draftSelection === null) {
      addToast('Select an Option First', 'Choose one of the four options before saving.', 'warning');
      return;
    }
    setSavedAnswers((prev) => ({ ...prev, [currentQuestion.id]: draftSelection }));
    addToast(
      `Question ${currentQuestion.number} Saved`,
      `Recorded Option ${String.fromCharCode(65 + draftSelection)}.`,
      'success'
    );
    if (advanceNext && currentIdx < ONLINE_EXAM_QUESTIONS.length - 1) {
      setCurrentIdx((idx) => idx + 1);
    }
  };

  const handleClearResponse = () => {
    setDraftSelection(null);
    setSavedAnswers((prev) => {
      const next = { ...prev };
      delete next[currentQuestion.id];
      return next;
    });
  };

  const handleToggleReview = () => {
    if (draftSelection !== null) {
      setSavedAnswers((prev) => ({ ...prev, [currentQuestion.id]: draftSelection }));
    }
    const nextState = !markedForReview[currentQuestion.id];
    setMarkedForReview((prev) => ({ ...prev, [currentQuestion.id]: nextState }));
    addToast(
      nextState ? 'Marked for Review' : 'Review Flag Cleared',
      `Question ${currentQuestion.number} ${nextState ? 'flagged for revisit' : 'unflagged'}.`,
      'info'
    );
  };

  const answeredCount = Object.keys(savedAnswers).length;
  const reviewCount = Object.values(markedForReview).filter(Boolean).length;
  const unansweredCount = ONLINE_EXAM_QUESTIONS.length - answeredCount;

  const handleSubmitExamClick = () => {
    // Also persist current draft if selected
    const effectiveAnswered =
      draftSelection !== null && savedAnswers[currentQuestion.id] === undefined
        ? answeredCount + 1
        : answeredCount;
    const effectiveUnanswered = ONLINE_EXAM_QUESTIONS.length - effectiveAnswered;

    requestConfirm({
      title: 'Submit Online Examination?',
      message: `You have answered ${effectiveAnswered} of ${ONLINE_EXAM_QUESTIONS.length} questions (${effectiveUnanswered} unanswered, ${reviewCount} marked for review). Once submitted, answers cannot be modified.`,
      confirmLabel: 'Submit Final Answers',
      variant: 'primary',
      onConfirm: () => {
        if (draftSelection !== null && savedAnswers[currentQuestion.id] === undefined) {
          setSavedAnswers((prev) => ({ ...prev, [currentQuestion.id]: draftSelection }));
        }
        setSubmitted(true);
        addToast(
          'Examination Submitted Successfully',
          'Diagnostic evaluation and topic mastery breakdown generated.',
          'success'
        );
      },
    });
  };

  const handleRetake = () => {
    setSavedAnswers({});
    setDraftSelection(null);
    setMarkedForReview({});
    setVisited({ [ONLINE_EXAM_QUESTIONS[0].id]: true });
    setCurrentIdx(0);
    setSecondsLeft(totalDurationSeconds);
    setSubmitted(false);
  };

  // Final Test Submission Screen
  if (submitted) {
    let correctCount = 0;
    let earnedMarks = 0;
    const totalMarks = ONLINE_EXAM_QUESTIONS.reduce((acc, q) => acc + q.marks, 0);

    ONLINE_EXAM_QUESTIONS.forEach((q) => {
      if (savedAnswers[q.id] === q.correctOptionIndex) {
        correctCount += 1;
        earnedMarks += q.marks;
      }
    });

    const percentage = Math.round((earnedMarks / totalMarks) * 100);
    const timeSpentSeconds = totalDurationSeconds - secondsLeft;
    const spentMins = Math.floor(timeSpentSeconds / 60);
    const spentSecs = timeSpentSeconds % 60;

    return (
      <div className="space-y-6 max-w-5xl mx-auto">
        {/* Result Summary Banner */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
            <div className="space-y-1">
              <p className="text-xs font-medium text-emerald-700 inline-flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                <span>Examination Submitted & Evaluated</span>
              </p>
              <h1 className="text-2xl font-bold font-display text-slate-900">
                DBMS Normalization & SQL Joins Adaptive Diagnostic
              </h1>
              <p className="text-sm text-slate-500">
                CS302 · Database Management Systems · Semester 5 Assessment
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2.5">
              <Button
                variant="outline"
                leftIcon={<RotateCcw className="w-4 h-4" />}
                onClick={handleRetake}
              >
                Retake Exam
              </Button>
              <Button
                variant="ai"
                leftIcon={<Compass className="w-4 h-4" />}
                onClick={() => navigate('/student/study-coach')}
              >
                Update AI Study Plan
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <p className="text-xs text-slate-500">Score Obtained</p>
              <p className="text-2xl font-bold font-display text-slate-900 tabular-nums mt-1">
                {earnedMarks} / {totalMarks}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <p className="text-xs text-slate-500">Percentage</p>
              <p className="text-2xl font-bold font-display text-[#2563EB] tabular-nums mt-1">
                {percentage}%
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <p className="text-xs text-slate-500">Correct Answers</p>
              <p className="text-2xl font-bold font-display text-emerald-600 tabular-nums mt-1">
                {correctCount} / {ONLINE_EXAM_QUESTIONS.length}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <p className="text-xs text-slate-500">Time Taken</p>
              <p className="text-2xl font-bold font-display text-slate-900 tabular-nums mt-1">
                {spentMins}m {spentSecs}s
              </p>
            </div>
          </div>
        </div>

        {/* Question-by-Question Review */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold font-display text-slate-900">
                Detailed Answer Key & Concept Explanations
              </h2>
              <p className="text-xs text-slate-500">
                Review every question with step-by-step engineering justifications
              </p>
            </div>
            <Award className="w-5 h-5 text-[#2563EB]" />
          </div>

          <div className="divide-y divide-slate-200">
            {ONLINE_EXAM_QUESTIONS.map((q) => {
              const userChoice = savedAnswers[q.id];
              const isCorrect = userChoice === q.correctOptionIndex;
              const isSkipped = userChoice === undefined;

              return (
                <div key={q.id} className="py-5 first:pt-0 last:pb-0 space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <p className="text-sm font-semibold text-slate-900 leading-relaxed">
                      Q{q.number}. {q.questionText}
                    </p>
                    <span
                      className={`text-xs font-semibold shrink-0 inline-flex items-center gap-1 ${
                        isCorrect
                          ? 'text-emerald-700'
                          : isSkipped
                          ? 'text-slate-500'
                          : 'text-red-600'
                      }`}
                    >
                      {isCorrect ? (
                        <CheckCircle2 className="w-4 h-4" />
                      ) : (
                        <AlertCircle className="w-4 h-4" />
                      )}
                      <span>
                        {isCorrect
                          ? `+${q.marks} Marks`
                          : isSkipped
                          ? 'Unattempted (0)'
                          : 'Incorrect (0)'}
                      </span>
                    </span>
                  </div>

                  <div className="text-xs space-y-1 text-slate-600">
                    <p>
                      <span className="font-semibold text-slate-700">Your Answer: </span>
                      {isSkipped
                        ? 'Not answered'
                        : q.options?.[userChoice] || 'Invalid selection'}
                    </p>
                    <p>
                      <span className="font-semibold text-emerald-700">
                        Correct Answer:{' '}
                      </span>
                      {q.correctAnswerText}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed">
                    <span className="font-semibold text-slate-900">Explanation: </span>
                    {q.explanation}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  // Active Examination Screen
  return (
    <div className="space-y-5">
      {/* Top Exam Control Bar */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-0.5">
          <p className="text-xs font-medium text-slate-500">
            CS302 · Database Management Systems · Duration: 25 Minutes · Max Marks: 32
          </p>
          <h1 className="text-lg sm:text-xl font-bold font-display text-slate-900">
            DBMS Normalization & SQL Joins Adaptive Diagnostic
          </h1>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {/* Countdown Timer */}
          <div
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg border font-mono text-sm font-semibold tabular-nums ${
              secondsLeft < 300
                ? 'bg-red-50 border-red-200 text-red-700'
                : 'bg-slate-50 border-slate-200 text-slate-900'
            }`}
          >
            <Clock className="w-4 h-4 text-[#2563EB]" />
            <span>{formatTimer(secondsLeft)}</span>
          </div>

          <Button
            variant="primary"
            leftIcon={<Send className="w-4 h-4" />}
            onClick={handleSubmitExamClick}
          >
            Submit Examination
          </Button>
        </div>
      </div>

      {/* Main Split Workspace: Question Stage (8 cols) + Question Palette (4 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Question Stage */}
        <section className="lg:col-span-8 bg-white border border-slate-200 rounded-xl p-6 flex flex-col justify-between min-h-[480px]">
          <div className="space-y-6">
            {/* Question Header Metadata */}
            <div className="flex flex-wrap items-center justify-between gap-2 pb-4 border-b border-slate-200">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <span className="font-semibold text-slate-900 text-sm font-display">
                  Question {currentQuestion.number} of {ONLINE_EXAM_QUESTIONS.length}
                </span>
                <span aria-hidden="true">·</span>
                <span>{currentQuestion.topic}</span>
                <span aria-hidden="true">·</span>
                <span>Difficulty: {currentQuestion.difficulty}</span>
              </div>
              <span className="text-xs font-mono font-semibold text-slate-700 tabular-nums">
                +{currentQuestion.marks} Marks · No Negative Marking
              </span>
            </div>

            {/* Question Stem */}
            <p className="text-base font-medium text-slate-900 leading-relaxed">
              {currentQuestion.questionText}
            </p>

            {/* 4 Multiple Choice Options */}
            <div className="space-y-3">
              {currentQuestion.options?.map((opt, idx) => {
                const isSelected = draftSelection === idx;
                const isSaved = savedAnswers[currentQuestion.id] === idx;
                const optionLetter = String.fromCharCode(65 + idx);

                return (
                  <button
                    key={optionLetter}
                    type="button"
                    onClick={() => setDraftSelection(idx)}
                    className={`w-full text-left p-4 rounded-xl border transition-all duration-150 flex items-start gap-3.5 cursor-pointer ${
                      isSelected
                        ? 'border-[#2563EB] bg-blue-50/60'
                        : 'border-slate-200 bg-white hover:bg-slate-50'
                    }`}
                  >
                    <span
                      className={`w-7 h-7 rounded-lg text-xs font-mono font-semibold flex items-center justify-center shrink-0 border ${
                        isSelected
                          ? 'bg-[#2563EB] text-white border-[#2563EB]'
                          : 'bg-slate-50 text-slate-700 border-slate-200'
                      }`}
                    >
                      {optionLetter}
                    </span>
                    <div className="flex-1 pt-0.5">
                      <span className="text-sm text-slate-800 leading-relaxed">
                        {opt}
                      </span>
                      {isSaved && (
                        <span className="ml-2 text-xs font-medium text-emerald-700">
                          (Saved)
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Question Footer Action Controls */}
          <div className="pt-6 mt-6 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="outline"
                size="md"
                onClick={handleToggleReview}
                leftIcon={
                  <Bookmark
                    className={`w-4 h-4 ${
                      markedForReview[currentQuestion.id]
                        ? 'fill-[#7C3AED] text-[#7C3AED]'
                        : 'text-slate-500'
                    }`}
                  />
                }
              >
                {markedForReview[currentQuestion.id]
                  ? 'Unmark Review'
                  : 'Mark for Review'}
              </Button>

              {draftSelection !== null && (
                <Button variant="ghost" size="md" onClick={handleClearResponse}>
                  Clear Selection
                </Button>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="outline"
                size="md"
                disabled={currentIdx === 0}
                onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))}
                leftIcon={<ChevronLeft className="w-4 h-4" />}
              >
                Previous
              </Button>

              <Button
                variant="outline"
                size="md"
                onClick={() => handleSaveAnswer(false)}
                leftIcon={<Save className="w-4 h-4 text-[#2563EB]" />}
              >
                Save Answer
              </Button>

              {currentIdx < ONLINE_EXAM_QUESTIONS.length - 1 ? (
                <Button
                  variant="primary"
                  size="md"
                  onClick={() => {
                    if (draftSelection !== null) {
                      handleSaveAnswer(true);
                    } else {
                      setCurrentIdx((i) => i + 1);
                    }
                  }}
                  rightIcon={<ChevronRight className="w-4 h-4" />}
                >
                  {draftSelection !== null ? 'Save & Next' : 'Next'}
                </Button>
              ) : (
                <Button
                  variant="primary"
                  size="md"
                  onClick={handleSubmitExamClick}
                  rightIcon={<Send className="w-4 h-4" />}
                >
                  Finish & Submit
                </Button>
              )}
            </div>
          </div>
        </section>

        {/* Right: Question Navigation Palette & Status Indicators */}
        <aside className="lg:col-span-4 bg-white border border-slate-200 rounded-xl p-5 space-y-5">
          <div>
            <h2 className="text-base font-semibold font-display text-slate-900">
              Question Palette
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Click any question number to jump directly
            </p>
          </div>

          <div className="grid grid-cols-4 gap-2.5">
            {ONLINE_EXAM_QUESTIONS.map((q, idx) => {
              const status = getQuestionStatus(q.id);
              const isCurrent = idx === currentIdx;

              const paletteStyles: Record<QuestionStatus, string> = {
                answered: 'bg-emerald-600 text-white border-emerald-600',
                review: 'bg-[#7C3AED] text-white border-[#7C3AED]',
                unanswered: 'bg-amber-50 text-amber-800 border-amber-300',
                'not-visited': 'bg-slate-50 text-slate-600 border-slate-200',
              };

              return (
                <button
                  key={q.id}
                  type="button"
                  onClick={() => setCurrentIdx(idx)}
                  className={`h-11 rounded-lg border font-mono text-sm font-semibold tabular-nums transition-all cursor-pointer ${
                    paletteStyles[status]
                  } ${isCurrent ? 'ring-2 ring-[#2563EB] ring-offset-2' : ''}`}
                >
                  {q.number}
                </button>
              );
            })}
          </div>

          {/* Question Status Legend */}
          <div className="pt-4 border-t border-slate-200 space-y-2.5 text-xs">
            <p className="font-semibold text-slate-800">Status Summary</p>
            <div className="grid grid-cols-2 gap-2.5">
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                <span className="text-slate-600">Answered</span>
                <span className="font-mono font-bold text-emerald-700 tabular-nums">
                  {answeredCount}
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                <span className="text-slate-600">Marked Review</span>
                <span className="font-mono font-bold text-[#7C3AED] tabular-nums">
                  {reviewCount}
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                <span className="text-slate-600">Unanswered</span>
                <span className="font-mono font-bold text-amber-700 tabular-nums">
                  {unansweredCount}
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                <span className="text-slate-600">Total Items</span>
                <span className="font-mono font-bold text-slate-900 tabular-nums">
                  {ONLINE_EXAM_QUESTIONS.length}
                </span>
              </div>
            </div>
          </div>

          <Button
            variant="primary"
            className="w-full"
            leftIcon={<Send className="w-4 h-4" />}
            onClick={handleSubmitExamClick}
          >
            Submit Examination
          </Button>
        </aside>
      </div>
    </div>
  );
};
