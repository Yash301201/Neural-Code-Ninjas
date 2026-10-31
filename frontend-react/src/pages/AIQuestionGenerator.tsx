import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Wand2,
  CheckCircle2,
  Trash2,
  Pencil,
  Save,
  CheckCheck,
  Database,
  X,
} from 'lucide-react';
import { SUBJECT_TOPICS_MAP } from '../data/mockData';
import { TestQuestion } from '../types';
import { useApp } from '../context/AppContext';
import { Button } from '../components/Button';

const SUBJECT_NAMES = Object.keys(SUBJECT_TOPICS_MAP);

function synthesizeEngineeringQuestions(
  subject: string,
  topic: string,
  difficulty: 'Easy' | 'Medium' | 'Hard',
  type: 'MCQ' | 'Descriptive',
  count: number,
  instructions: string
): TestQuestion[] {
  const marks = difficulty === 'Easy' ? 2 : difficulty === 'Medium' ? 4 : 6;
  const templates = [
    {
      stem: `In ${subject}, when analyzing ${topic}, which condition guarantees optimal worst-case execution and preserves data consistency under concurrent engineering workloads?`,
      options: [
        `Enforcing strict two-phase validation with logarithmic index lookup on ${topic}`,
        `Executing unindexed linear scans across all partitioned buckets`,
        `Disabling integrity invariants during peak write bursts`,
        `Replacing deterministic scheduling with unbounded busy-waiting`,
      ],
      correctIdx: 0,
      explanation: `Strict validation combined with logarithmic lookup bounds worst-case latency while maintaining full ACID / structural invariants for ${topic}.`,
    },
    {
      stem: `Given an engineering system implementing ${topic} (${difficulty} tier), evaluate the asymptotic overhead when input scale doubles from N to 2N records.`,
      options: [
        `Overhead grows logarithmically as O(log N) per transaction`,
        `Overhead scales quadratically as Θ(N²) regardless of indexing`,
        `Throughput drops to zero due to mandatory global table locking`,
        `Memory footprint grows exponentially as O(2^N)`,
      ],
      correctIdx: 0,
      explanation: `Balanced hierarchical structures in ${topic} bound height by O(log_B N), keeping lookup and split overhead logarithmic.`,
    },
    {
      stem: `Which failure mode occurs in ${topic} if boundary preconditions are omitted during ${subject} implementation?`,
      options: [
        `Phantom anomalies or non-recoverable state divergence across dependent nodes`,
        `Automatic hardware cache expansion without latency penalty`,
        `Guaranteed lossless compression of all intermediate tuples`,
        `Zero-cost serialization across distributed replicas`,
      ],
      correctIdx: 0,
      explanation: `Omitting boundary preconditions in ${topic} permits anomalous interleavings or lossy decompositions that violate canonical ${subject} theorems.`,
    },
    {
      stem: `A B.Tech lab benchmark tests ${topic} under ${
        instructions.trim() ? `"${instructions.trim().slice(0, 48)}"` : 'high contention'
      }. Which design metric directly measures structural efficiency?`,
      options: [
        `Block I/O amplification ratio and amortized operation cost`,
        `Source file line count excluding comments`,
        `Identifier string length in symbol tables`,
        `Number of whitespace characters in query syntax`,
      ],
      correctIdx: 0,
      explanation: `In ${subject}, physical efficiency of ${topic} is governed by disk/memory block transfers and amortized algorithmic complexity.`,
    },
    {
      stem: `Which formal verification step confirms correctness of a student solution for ${topic} in ${subject}?`,
      options: [
        `Proving invariant preservation across initialization, maintenance, and termination`,
        `Testing a single trivial empty-set input only`,
        `Checking variable naming conventions without executing edge cases`,
        `Assuming correctness whenever compilation succeeds without warnings`,
      ],
      correctIdx: 0,
      explanation: `Loop/protocol invariants across initialization, maintenance, and termination establish rigorous mathematical correctness for ${topic}.`,
    },
  ];

  return Array.from({ length: count }).map((_, idx) => {
    const tpl = templates[idx % templates.length];
    if (type === 'Descriptive') {
      return {
        id: `gen-${Date.now()}-${idx}`,
        number: idx + 1,
        subject,
        topic,
        difficulty,
        type: 'Descriptive',
        questionText: `[${difficulty}] Derive the formal model for ${topic} in ${subject}. ${
          instructions.trim() ? `Context: ${instructions.trim()}. ` : ''
        }Provide step-by-step mathematical justification and analyze edge-case trade-offs (Question ${
          idx + 1
        }).`,
        correctAnswerText: `Expected Rubric: (1) Formal definition & invariants of ${topic}, (2) Step-by-step derivation or algorithm trace, (3) Complexity / I/O cost analysis (${tpl.options[0]}).`,
        explanation: tpl.explanation,
        marks: marks * 2,
        approved: false,
      };
    }

    return {
      id: `gen-${Date.now()}-${idx}`,
      number: idx + 1,
      subject,
      topic,
      difficulty,
      type: 'MCQ',
      questionText: tpl.stem,
      options: tpl.options,
      correctOptionIndex: tpl.correctIdx,
      correctAnswerText: tpl.options[tpl.correctIdx],
      explanation: tpl.explanation,
      marks,
      approved: false,
    };
  });
}

export const AIQuestionGenerator: React.FC = () => {
  const { saveQuestionsToBank, questionBank, requestConfirm, addToast } = useApp();
  const navigate = useNavigate();

  const [subject, setSubject] = useState<string>(SUBJECT_NAMES[0]);
  const [topic, setTopic] = useState<string>(SUBJECT_TOPICS_MAP[SUBJECT_NAMES[0]][0]);
  const [difficulty, setDifficulty] = useState<'Easy' | 'Medium' | 'Hard'>('Medium');
  const [questionType, setQuestionType] = useState<'MCQ' | 'Descriptive'>('MCQ');
  const [numQuestions, setNumQuestions] = useState<number>(3);
  const [instructions, setInstructions] = useState<string>(
    'Align with GATE CS & NBA Course Outcome CO3 analytical rigor.'
  );

  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generatedList, setGeneratedList] = useState<TestQuestion[]>(() =>
    synthesizeEngineeringQuestions(
      SUBJECT_NAMES[0],
      SUBJECT_TOPICS_MAP[SUBJECT_NAMES[0]][1],
      'Medium',
      'MCQ',
      3,
      'Include BCNF candidate key analysis'
    )
  );

  // Edit Question Modal State
  const [editingQuestion, setEditingQuestion] = useState<TestQuestion | null>(null);

  const handleSubjectChange = (nextSubject: string) => {
    setSubject(nextSubject);
    const availableTopics = SUBJECT_TOPICS_MAP[nextSubject] || [];
    setTopic(availableTopics[0] || '');
  };

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    setTimeout(() => {
      const fresh = synthesizeEngineeringQuestions(
        subject,
        topic,
        difficulty,
        questionType,
        numQuestions,
        instructions
      );
      setGeneratedList(fresh);
      setIsGenerating(false);
      addToast(
        `Generated ${numQuestions} ${questionType} Questions`,
        `${subject} · ${topic} (${difficulty})`,
        'success'
      );
    }, 850);
  };

  const toggleApprove = (id: string) => {
    setGeneratedList((prev) =>
      prev.map((q) => (q.id === id ? { ...q, approved: !q.approved } : q))
    );
  };

  const handleApproveAll = () => {
    setGeneratedList((prev) => prev.map((q) => ({ ...q, approved: true })));
    addToast(
      'All Questions Approved',
      `${generatedList.length} generated questions marked ready for the Question Bank.`,
      'success'
    );
  };

  const handleDeleteQuestion = (id: string, num: number) => {
    requestConfirm({
      title: `Discard Generated Question #${num}?`,
      message: 'This question will be removed from the current preview batch.',
      confirmLabel: 'Delete Question',
      variant: 'danger',
      onConfirm: () => {
        setGeneratedList((prev) => prev.filter((q) => q.id !== id));
        addToast('Question Deleted', `Removed Question #${num} from preview.`, 'info');
      },
    });
  };

  const handleSaveEdit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingQuestion) return;
    setGeneratedList((prev) =>
      prev.map((q) => (q.id === editingQuestion.id ? editingQuestion : q))
    );
    setEditingQuestion(null);
    addToast('Question Updated', 'Saved faculty edits to question preview.', 'success');
  };

  const handleSaveToBank = () => {
    const approvedItems = generatedList.filter((q) => q.approved);
    const batchToSave = approvedItems.length > 0 ? approvedItems : generatedList;
    if (batchToSave.length === 0) {
      addToast('No Questions to Save', 'Generate questions first.', 'warning');
      return;
    }
    saveQuestionsToBank(batchToSave);
  };

  const approvedCount = generatedList.filter((q) => q.approved).length;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs font-medium text-[#7C3AED]">
            <Wand2 className="w-4 h-4" />
            <span>Faculty Authoring Studio · Bloom’s Taxonomy Calibrated</span>
          </div>
          <h1 className="text-2xl font-bold font-display text-slate-900 tracking-tight">
            AI Question Generator & Verification Workbench
          </h1>
          <p className="text-sm text-slate-600">
            Configure subject, topic, difficulty, and format to synthesize exam-ready
            engineering questions with verified solutions.
          </p>
        </div>

        <Button
          variant="outline"
          leftIcon={<Database className="w-4 h-4 text-[#2563EB]" />}
          onClick={() => navigate('/faculty/question-bank')}
        >
          View Question Bank ({questionBank.length})
        </Button>
      </div>

      {/* Main Split: Configuration Form (4 cols) + Generated Question Preview (8 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Generator Parameter Controls */}
        <form
          onSubmit={handleGenerate}
          className="lg:col-span-4 bg-white border border-slate-200 rounded-xl p-5 space-y-4"
        >
          <h2 className="text-base font-semibold font-display text-slate-900">
            Assessment Specification
          </h2>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Engineering Subject
            </label>
            <select
              value={subject}
              onChange={(e) => handleSubjectChange(e.target.value)}
              className="w-full px-3.5 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
            >
              {SUBJECT_NAMES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Syllabus Topic
            </label>
            <select
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full px-3.5 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
            >
              {(SUBJECT_TOPICS_MAP[subject] || []).map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          {/* Difficulty Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Difficulty Level
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['Easy', 'Medium', 'Hard'] as const).map((lvl) => (
                <button
                  key={lvl}
                  type="button"
                  onClick={() => setDifficulty(lvl)}
                  className={`py-2 px-3 text-xs font-semibold rounded-lg border transition-colors cursor-pointer ${
                    difficulty === lvl
                      ? 'border-[#2563EB] bg-blue-50 text-[#2563EB]'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          {/* Question Type Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Question Format
            </label>
            <div className="grid grid-cols-2 gap-2">
              {(['MCQ', 'Descriptive'] as const).map((qType) => (
                <button
                  key={qType}
                  type="button"
                  onClick={() => setQuestionType(qType)}
                  className={`py-2 px-3 text-xs font-semibold rounded-lg border transition-colors cursor-pointer ${
                    questionType === qType
                      ? 'border-[#7C3AED] bg-violet-50 text-[#7C3AED]'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {qType}
                </button>
              ))}
            </div>
          </div>

          {/* Number of Questions */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-slate-700">
                Number of Questions
              </label>
              <span className="text-xs font-mono font-bold text-[#2563EB] tabular-nums">
                {numQuestions} Questions
              </span>
            </div>
            <input
              type="range"
              min={1}
              max={5}
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
              className="w-full accent-[#2563EB] cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-slate-400 font-mono">
              <span>1</span>
              <span>2</span>
              <span>3</span>
              <span>4</span>
              <span>5</span>
            </div>
          </div>

          {/* Additional Instructions */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Additional Pedagogical Instructions
            </label>
            <textarea
              rows={3}
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              placeholder="e.g., Include numerical problem solving or SQL edge cases..."
              className="w-full px-3.5 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB] leading-relaxed"
            />
          </div>

          <Button
            type="submit"
            variant="ai"
            size="lg"
            isLoading={isGenerating}
            leftIcon={<Wand2 className="w-4 h-4" />}
            className="w-full"
          >
            {isGenerating ? 'Synthesizing Questions...' : 'Generate Questions'}
          </Button>
        </form>

        {/* Right: Generated Preview & Faculty Review */}
        <section className="lg:col-span-8 space-y-4">
          {/* Batch Toolbar */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold font-display text-slate-900">
                Generated Question Preview ({generatedList.length})
              </h2>
              <p className="text-xs text-slate-500 tabular-nums">
                {approvedCount} of {generatedList.length} approved · Edit or verify before
                saving to Question Bank
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                leftIcon={<CheckCheck className="w-4 h-4 text-emerald-600" />}
                onClick={handleApproveAll}
                disabled={generatedList.length === 0 || isGenerating}
              >
                Approve Questions
              </Button>
              <Button
                size="sm"
                variant="primary"
                leftIcon={<Save className="w-4 h-4" />}
                onClick={handleSaveToBank}
                disabled={generatedList.length === 0 || isGenerating}
              >
                Save to Question Bank
              </Button>
            </div>
          </div>

          {/* Loading Animation State */}
          {isGenerating ? (
            <div className="bg-white border border-slate-200 rounded-xl p-8 text-center space-y-4">
              <div className="w-12 h-12 rounded-xl bg-violet-50 text-[#7C3AED] flex items-center justify-center mx-auto">
                <Wand2 className="w-6 h-6 animate-pulse" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-slate-900">
                  Generating {numQuestions} {difficulty} {questionType} questions for {topic}...
                </p>
                <p className="text-xs text-slate-500">
                  Constructing distractors, verifying answer key, and drafting solution rubric
                </p>
              </div>
              <div className="max-w-md mx-auto space-y-2.5 pt-2 animate-pulse">
                <div className="h-3 bg-slate-200 rounded w-full" />
                <div className="h-3 bg-slate-200 rounded w-5/6 mx-auto" />
                <div className="h-3 bg-slate-200 rounded w-2/3 mx-auto" />
              </div>
            </div>
          ) : generatedList.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-12 text-center space-y-2">
              <p className="text-sm font-semibold text-slate-800">
                No questions in preview batch
              </p>
              <p className="text-xs text-slate-500">
                Configure subject and topic on the left and click Generate Questions.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {generatedList.map((q, idx) => (
                <article
                  key={q.id}
                  className="bg-white border border-slate-200 rounded-xl p-5 space-y-4"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2 pb-3 border-b border-slate-100">
                    <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                      <span className="font-mono font-bold text-slate-900">
                        Q{idx + 1}
                      </span>
                      <span aria-hidden="true">·</span>
                      <span>{q.subject}</span>
                      <span aria-hidden="true">·</span>
                      <span>{q.topic}</span>
                      <span aria-hidden="true">·</span>
                      <span className="font-medium text-slate-700">
                        {q.difficulty} ({q.marks} Marks)
                      </span>
                      {q.approved && (
                        <>
                          <span aria-hidden="true">·</span>
                          <span className="inline-flex items-center gap-1 font-semibold text-emerald-700">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Approved
                          </span>
                        </>
                      )}
                    </div>

                    <div className="flex items-center gap-1.5">
                      <Button
                        size="sm"
                        variant={q.approved ? 'outline' : 'ghost'}
                        onClick={() => toggleApprove(q.id)}
                      >
                        {q.approved ? 'Approved' : 'Approve'}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        leftIcon={<Pencil className="w-3.5 h-3.5" />}
                        onClick={() => setEditingQuestion({ ...q })}
                      >
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        leftIcon={<Trash2 className="w-3.5 h-3.5 text-red-600" />}
                        onClick={() => handleDeleteQuestion(q.id, idx + 1)}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>

                  <p className="text-sm font-medium text-slate-900 leading-relaxed">
                    {q.questionText}
                  </p>

                  {q.type === 'MCQ' && q.options && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                      {q.options.map((opt, optIdx) => {
                        const isCorrect = optIdx === q.correctOptionIndex;
                        return (
                          <div
                            key={optIdx}
                            className={`p-3 rounded-lg border text-xs flex items-start gap-2 ${
                              isCorrect
                                ? 'border-emerald-300 bg-emerald-50/50 text-emerald-950 font-medium'
                                : 'border-slate-200 bg-slate-50/50 text-slate-700'
                            }`}
                          >
                            <span className="font-mono font-bold shrink-0">
                              {String.fromCharCode(65 + optIdx)}.
                            </span>
                            <span>{opt}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Correct Answer & Explanation */}
                  <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5 text-xs">
                    <p className="text-emerald-800">
                      <span className="font-semibold">Correct Answer: </span>
                      {q.correctAnswerText}
                    </p>
                    <p className="text-slate-600 leading-relaxed">
                      <span className="font-semibold text-slate-800">Explanation: </span>
                      {q.explanation}
                    </p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Edit Question Modal */}
      {editingQuestion && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          <div
            className="fixed inset-0 bg-slate-900/45 backdrop-blur-[1px]"
            onClick={() => setEditingQuestion(null)}
          />
          <form
            onSubmit={handleSaveEdit}
            className="relative z-10 bg-white border border-slate-200 rounded-xl shadow-xl max-w-lg w-full p-6 space-y-4"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold font-display text-slate-900">
                Edit Generated Question
              </h3>
              <button
                type="button"
                onClick={() => setEditingQuestion(null)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Question Stem
              </label>
              <textarea
                rows={3}
                required
                value={editingQuestion.questionText}
                onChange={(e) =>
                  setEditingQuestion({ ...editingQuestion, questionText: e.target.value })
                }
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Correct Answer
              </label>
              <input
                type="text"
                required
                value={editingQuestion.correctAnswerText}
                onChange={(e) =>
                  setEditingQuestion({
                    ...editingQuestion,
                    correctAnswerText: e.target.value,
                  })
                }
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Solution Explanation
              </label>
              <textarea
                rows={2}
                required
                value={editingQuestion.explanation}
                onChange={(e) =>
                  setEditingQuestion({ ...editingQuestion, explanation: e.target.value })
                }
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-[#2563EB]"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setEditingQuestion(null)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                Save Changes
              </Button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
