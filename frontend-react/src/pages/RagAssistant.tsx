import React,{useState,useEffect,useRef} from 'react';
import {Sparkles,Database,BookOpen,Send,Plus,RefreshCw,MessageSquare,ExternalLink} from 'lucide-react';
import {api,useApp,Row} from '../context/AppContext';
import {AssistantAnswer} from './AssistantAnswer';

const paperCode = /\b(?:AAA|BBB|CCC|DDD|EEE|FFF|GGG)-20\d{2}[BJ]-M[12]-[AB]\b/g;
const actionStyle = 'rounded-lg border border-indigo-200 bg-white px-3 py-2 text-xs font-semibold text-indigo-700 hover:bg-indigo-50 disabled:opacity-50';

function MockResponse({message, busy, send, storageKey}: {message: Row; busy: boolean; send: (text: string) => void; storageKey: string}) {
 const answer = String(message.answer);
 if (message.answer_mode === 'mock_paper' && !answer.includes('20 marks · 5 questions')) {
  const codes = [...new Set(answer.match(paperCode) ?? [])];
  if (codes.length) return <div className="mt-3 space-y-3">
   <p className="text-sm text-slate-600">{codes.length} practice {codes.length === 1 ? 'paper' : 'papers'}. Choose a set to get started.</p>
   {codes.map(code => <section key={code} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
    <h3 className="text-sm font-semibold">{code}</h3>
    <p className="mt-1 text-xs text-slate-600">Data Structures · 5 questions · 20 marks</p>
    <div className="mt-3 flex flex-wrap gap-2">
     <button type="button" className={actionStyle} disabled={busy} onClick={() => send('Show ' + code)}>Open paper</button>
     <button type="button" className={actionStyle} disabled={busy} onClick={() => send('Quiz me on ' + code)}>Start quiz</button>
     <button type="button" className={actionStyle} disabled={busy} onClick={() => send('Show ' + code + ' with worked solutions')}>View solutions</button>
    </div>
   </section>)}
  </div>;
 }
 if (message.answer_mode === 'mock_paper' && answer.includes('20 marks · 5 questions')) {
  const [intro, ...questions] = answer.split(/\n\n+/);
  return <div className="mt-3 space-y-3">
   <p className="whitespace-pre-line text-sm leading-6">{intro}</p>
   {questions.map((block, i) => {
    const [heading, question, ...solution] = block.split('\n');
    return <section key={i} className="rounded-xl border border-slate-200 p-4">
     <h3 className="text-xs font-semibold text-indigo-700">{heading}</h3>
     <p className="mt-2 text-sm">{question}</p>
     {solution.length > 0 && <p className="mt-3 whitespace-pre-line rounded-lg bg-indigo-50 p-3 text-sm">{solution.join('\n')}</p>}
    </section>;
   })}
  </div>;
 }
 return <AssistantAnswer text={answer} storageKey={storageKey}/>;
}

export function RagAssistant(){
 const {currentUser}=useApp();const [status,setStatus]=useState<Row|null>(null),[history,setHistory]=useState<Row[]>([]),[messages,setMessages]=useState<Row[]>([]),[id,setId]=useState<number|null>(null),[question,setQuestion]=useState(''),[busy,setBusy]=useState(false),[error,setError]=useState(''),[cohort,setCohort]=useState(''),[cohorts,setCohorts]=useState<Row[]>([]),[retrieveOnly,setRetrieveOnly]=useState(false);
 const roadmapPrompt = 'Create a 14-day Data Structures semester exam roadmap for 90 minutes per day. Cover arrays, linked lists, stacks, queues, trees, and graphs. Include two timed practice tests, mistake review, and one self-check without its answer. Use the retrieved study guidance as the planning framework. Start with a roadmap heading, then give one Markdown table with exactly four columns: Day | What to revise | What to practice | How to check. Number days 1 through 14. Use bold to highlight the main topic or task in each cell.';
 const isStudent = currentUser?.role === 'student';
 const isAdmin = currentUser?.role === 'admin';
 const activeQuiz = messages.at(-1)?.answer_mode === 'mock_quiz';
 const latestResult = useRef<HTMLElement>(null);
 const scrollToReply = useRef(false);
 useEffect(() => {
  if (!scrollToReply.current) return;
  scrollToReply.current = false;
  latestResult.current?.scrollIntoView({block: 'nearest'});
 }, [messages]);
 const refresh=async()=>{const [s,h]=await Promise.all([api('/rag/status'),api('/rag/conversations')]);setStatus(s);setHistory(h)};
 useEffect(()=>{refresh().catch(e=>setError(e.message));api('/dataset/oulad/catalog').then(r=>setCohorts(r.courses)).catch(()=>{})},[]);
 const open=async(n:number)=>{setBusy(true);setError('');try{const rows=await api('/rag/conversations/'+n);setId(n);setQuestion('');setMessages(rows)}catch(e){setError((e as Error).message)}finally{setBusy(false)}};
 const send = async (draft = question) => {
  const text = draft.trim();
  if (!text || busy) return;
  setBusy(true);
  setError('');
  try {
   const reply = await api('/rag/ask', 'POST', {
    question: text, conversation_id: id, cohort: cohort || null,
    mode: retrieveOnly ? 'retrieve' : 'generate',
   });
   scrollToReply.current = true;
   setId(reply.conversation_id);
   setMessages(current => [...current, reply]);
   setQuestion('');
   await refresh();
  } catch (err) {
   setError((err as Error).message);
  } finally {
   setBusy(false);
  }
 };
 const reindex=async()=>{setBusy(true);setError('');try{await api('/rag/reindex','POST');await refresh()}catch(e){setError((e as Error).message)}finally{setBusy(false)}};
 return <div className="space-y-5 min-w-0"><section className="rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-violet-900 text-white p-6 md:p-8"><div className="flex items-center gap-2 text-indigo-200 text-xs tracking-widest"><Sparkles size={16}/> GROUNDED LEARNING ASSISTANT</div><h1 className="text-3xl font-bold mt-4">AI Knowledge Assistant</h1><p className="text-sm text-indigo-200 mt-3 max-w-2xl">{isStudent ? 'Practice Data Structures with mock papers and worked solutions, or ask about the research dataset.' : 'Review public research cohorts and ask about LearnPathAI.'}</p><div className="flex flex-wrap gap-3 mt-5 text-xs"><span className="rounded-lg bg-white/10 p-2 flex gap-2 items-center"><Database size={14}/>{status?.chunks??'—'} MySQL knowledge chunks</span><span className="rounded-lg bg-white/10 p-2">{status?.configured?'Groq configured':'Groq key needed · retrieval available'}</span>{isStudent && <span className="rounded-lg bg-white/10 p-2">{status?.mock_papers??0} Data Structures mock papers</span>}</div></section>
 {!status?.configured&&status&&<p className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">Add LLM_API_KEY to backend/.env and restart the backend to enable Groq answers. Source retrieval and saved history work now. Never enter an API key in this chat box.</p>}
 <div className="grid lg:grid-cols-[230px_minmax(0,1fr)] gap-5"><aside className="bg-white border border-slate-200 rounded-xl p-4 self-start"><button disabled={busy} onClick={()=>{setId(null);setMessages([]);setQuestion('');setError('');setRetrieveOnly(false)}} className="w-full bg-indigo-600 text-white rounded-lg px-3 py-2 text-sm flex items-center gap-2"><Plus size={16}/>New conversation</button><h2 className="mt-5 mb-2 text-xs font-semibold text-slate-500">YOUR SAVED CONVERSATIONS</h2><div className="space-y-1 max-h-80 overflow-y-auto">{history.map(h=><button disabled={busy} key={h.conversation_id} onClick={()=>open(h.conversation_id)} className={'w-full text-left p-2 rounded-lg text-xs flex gap-2 '+(id===h.conversation_id?'bg-indigo-50 text-indigo-700':'hover:bg-slate-50 text-slate-600')}><MessageSquare size={14} className="shrink-0"/><span className="truncate">{h.title}</span></button>)}{!history.length&&<p className="text-xs text-slate-400 p-2">Your questions will be saved in MySQL.</p>}</div>{currentUser?.role==='admin'&&<button disabled={busy} onClick={reindex} className="mt-5 text-xs text-indigo-600 flex items-center gap-2"><RefreshCw size={13}/>Refresh public knowledge index</button>}<p className="text-[11px] text-slate-400 mt-4 leading-relaxed">History is private to your account. Continue a quiz here or start a new conversation.</p></aside>
 <section className="min-w-0 space-y-4"><div className="bg-white rounded-xl border border-slate-200 p-4 flex flex-wrap items-center gap-3 text-xs"><label className="text-slate-500">Cohort <select aria-label="Cohort" value={cohort} onChange={e=>setCohort(e.target.value)} className="border rounded-lg px-2 py-2 ml-2 max-w-full"><option value="">All cohorts</option>{cohorts.map(c=><option key={c.code_module+c.code_presentation} value={c.code_module+'-'+c.code_presentation}>{c.code_module} / {c.code_presentation}</option>)}</select></label><label className="flex items-center gap-2 text-slate-600"><input type="checkbox" checked={retrieveOnly} onChange={e=>setRetrieveOnly(e.target.checked)}/>Research evidence only (no Groq call)</label></div>
 {isStudent && <div className="flex flex-wrap gap-2" aria-label="Browse mock exams">
  <button type="button" className={actionStyle} disabled={busy} onClick={() => send('List Data Structures Mid-1 mock papers')}>Browse Mid-1 papers</button>
  <button type="button" className={actionStyle} disabled={busy} onClick={() => send('List Data Structures Mid-2 mock papers')}>Browse Mid-2 papers</button>
  <button type="button" className={actionStyle} disabled={busy || activeQuiz} onClick={() => {setRetrieveOnly(false);setQuestion(roadmapPrompt);document.getElementById("rag-question")?.focus();}}>Plan my semester revision</button>
 </div>}
 {isAdmin && <button type="button" className={actionStyle} disabled={busy || !cohort}
  onClick={() => {setRetrieveOnly(false);setQuestion('Summarize total enrollments and the outcome breakdown for ' + cohort + '. Cite each count and give two questions for a department review meeting.');}}>
  Prepare cohort review
 </button>}
 {!messages.length&&<div className="rounded-xl border border-dashed border-indigo-200 bg-indigo-50/40 p-6"><BookOpen className="text-indigo-400 mb-3"/><h2 className="font-semibold">{isStudent ? 'Start with a practice or research question' : 'Start with a research question'}</h2><div className="grid sm:grid-cols-2 gap-2 mt-4">{[...(isStudent ? ['Quiz me on Data Structures Mid-1 mock papers'] : []),'What is OULAD and what are its limitations?','How many enrollments and outcomes are in BBB 2014J?','What happened in BBB 2014J week 0 engagement?','How does RAG work in LearnPathAI?'].map(q=><button key={q} onClick={()=>setQuestion(q)} className="rounded-lg p-3 bg-white border border-indigo-100 text-xs text-left text-slate-600 hover:border-indigo-400">{q}</button>)}</div></div>}
 {messages.map((m, index)=><article key={m.message_id} ref={index === messages.length - 1 ? latestResult : undefined} className="rounded-xl bg-white border border-slate-200 overflow-hidden"><div className="bg-slate-50 p-4 border-b border-slate-100 text-sm font-semibold">{m.question}</div><div className="p-5"><span className={'text-[10px] uppercase tracking-wider font-bold '+(m.answer_mode==='llm'?'text-violet-600':'text-amber-700')}>{m.answer_mode==='cohort_summary'?'Cited cohort summary':m.answer_mode==='mock_paper'?'Demo mock paper':m.answer_mode==='mock_quiz'?'Mock exam practice':m.answer_mode==='mock_feedback'?'Mock exam feedback':m.answer_mode==='practice'?'Syllabus-based practice':m.answer_mode==='practice_feedback'?'Practice feedback':m.answer_mode==='llm'?'Groq generated · check cited evidence':m.answer_mode==='no_evidence'?'Insufficient evidence':'Retrieved evidence · no LLM generation'}</span>{m.provider_note==='invalid_citations'&&<p className="text-xs text-amber-700 mt-2">The generated answer did not pass citation checks.</p>}{m.provider_note==='invalid_response'&&<p className="text-xs text-amber-700 mt-2">Groq did not return a usable answer.</p>}{m.provider_note==='provider_unavailable'&&<p className="text-xs text-amber-700 mt-2">Groq could not be reached. Showing source excerpts.</p>}<MockResponse message={m} busy={busy} send={send} storageKey={"learnpath-roadmap:" + currentUser?.id + ":" + m.message_id}/><div className="space-y-2 mt-5">{m.citations.filter((source: Row) => source.id !== 'P1').map((s:Row)=><details key={s.id} className="border border-slate-200 rounded-lg p-3 text-xs"><summary className="cursor-pointer font-semibold text-indigo-700">[{s.id}] {s.title}</summary><p className="mt-3 whitespace-pre-wrap text-slate-500 leading-6 break-words">{s.excerpt}</p>{s.source_url&&<a href={s.source_url} target="_blank" rel="noreferrer" className="text-indigo-600 inline-flex items-center gap-1 mt-2">Original dataset documentation <ExternalLink size={12}/></a>}</details>)}</div></div></article>)}
 {error&&<p role="alert" className="bg-red-50 border border-red-200 p-3 rounded-lg text-sm text-red-700">{error}</p>}
 <form onSubmit={e => {e.preventDefault(); void send();}} className="rounded-xl border border-slate-200 bg-white p-4">
  <label htmlFor="rag-question" className="text-sm font-semibold text-slate-700">
   {activeQuiz ? 'Your answer' : 'Your question'}
  </label>
  <div className="mt-2 flex flex-wrap items-end gap-3">
   {activeQuiz ? <input id="rag-question" inputMode="numeric" required pattern="-?[0-9]{1,9}" maxLength={10}
    value={question} onChange={e => setQuestion(e.target.value)} placeholder="Enter a number"
    className="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2.5 text-sm"/>
   : <textarea id="rag-question" value={question} maxLength={2000} required
     onChange={e => setQuestion(e.target.value)} placeholder={isStudent ? 'Ask for a mock paper, worked solution, or research evidence' : 'Ask about a research cohort or how LearnPathAI works'}
     className="min-h-24 w-full rounded-lg border border-slate-300 p-3 text-sm"/>}
   <button disabled={busy || !question.trim()} className="ml-auto flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-xs text-white disabled:opacity-50">
    <Send size={15}/>{busy ? 'Working…' : activeQuiz ? 'Check my answer' : 'Ask assistant'}
   </button>
  </div>
 </form><p className="text-[11px] text-slate-400 px-1">Historical research evidence is descriptive. This assistant does not change grades, make student decisions, or access private academic records. Retrieved citations are evidence to inspect, not a guarantee of answer accuracy.</p></section></div></div>
}
