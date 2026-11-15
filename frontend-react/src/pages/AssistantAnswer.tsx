import React, {useState} from 'react';
import {BookOpen, CalendarDays, Check, ClipboardCheck, PencilLine} from 'lucide-react';

type Day = {number: number; revise: string; practice: string; check: string};
const divider = /^:?-{3,}:?$/;
const action = 'rounded-lg border border-indigo-200 px-3 py-2 text-sm font-semibold text-indigo-700 hover:bg-indigo-50 disabled:opacity-40';

function normalize(text: string) {
 return text.replace(/\\(?=[*|_#])/g, '').replace(/\\(?=\r?$)/gm, '');
}

function cells(line: string) {
 const row = line.trim();
 return row.startsWith('|') && row.endsWith('|') ? row.slice(1, -1).split('|').map(cell => cell.trim()) : [];
}

export function parseRoadmap(text: string) {
 const lines = normalize(text).split(/\r?\n/);
 const start = lines.findIndex(line => {
  const header = cells(line);
  return header.length === 4 && /^day$/i.test(header[0].replace(/\*/g, '')) &&
   /revis/i.test(header[1]) && /practi/i.test(header[2]) && /check/i.test(header[3]);
 });
 if (start < 0) return null;
 const separators = cells(lines[start + 1] ?? '');
 if (separators.length !== 4 || !separators.every(cell => divider.test(cell))) return null;
 const days: Day[] = [];
 let end = start + 2;
 for (; end < lines.length; end++) {
  const row = cells(lines[end]);
  if (!row.length) break;
  const number = Number(row[0].replace(/\*/g, '').replace(/^day\s+/i, ''));
  if (row.length !== 4 || !row.slice(1).every(Boolean) || number !== days.length + 1) return null;
  days.push({number, revise: row[1], practice: row[2], check: row[3]});
 }
 if (!days.length) return null;
 const intro = lines.slice(0, start).join('\n').trim();
 const title = intro.split('\n').find(line => /roadmap|study plan/i.test(line))?.replace(/^[#* ]+|[* ]+$/g, '');
 return {days, intro, title, after: lines.slice(end).join('\n').trim()};
}

function Inline({text}: {text: string}) {
 return <>{text.split(/(\*\*[^*\n]+\*\*|__[^_\n]+__|\*[^*\n]+\*|`[^`\n]+`|\[S\d+\])/g).map((part, i) => {
  if (part.startsWith('**') && part.endsWith('**') || part.startsWith('__') && part.endsWith('__'))
   return <strong className="font-semibold text-slate-950" key={i}>{part.slice(2, -2)}</strong>;
  if (part.startsWith('*') && part.endsWith('*') && part.length > 2) return <em key={i}>{part.slice(1, -1)}</em>;
  if (part.startsWith('`') && part.endsWith('`')) return <code className="rounded bg-slate-100 px-1" key={i}>{part.slice(1, -1)}</code>;
  if (/^\[S\d+\]$/.test(part)) return <span className="mx-0.5 rounded bg-indigo-50 px-1 text-xs font-semibold text-indigo-700" key={i}>{part}</span>;
  return part;
 })}</>;
}

function FormattedText({text}: {text: string}) {
 return <div className="space-y-2 text-sm leading-7 text-slate-700">{normalize(text).split(/\r?\n/).map((line, i) => {
  if (!line.trim()) return null;
  if (/^\s*---+\s*$/.test(line)) return <hr className="border-slate-200" key={i}/>;
  const heading = line.match(/^#{1,6}\s+(.+)/);
  if (heading) return <h4 className="mt-3 font-semibold text-slate-950" key={i}><Inline text={heading[1]}/></h4>;
  return <p className="whitespace-pre-wrap break-words" key={i}><Inline text={line}/></p>;
 })}</div>;
}

function restoreProgress(key: string, count: number): number[] {
 try {
  const saved: unknown = JSON.parse(localStorage.getItem(key) ?? '[]');
  return Array.isArray(saved) ? [...new Set(saved.filter(day => Number.isInteger(day) && day >= 1 && day <= count))] : [];
 } catch {
  return [];
 }
}

function Roadmap({plan, storageKey}: {plan: NonNullable<ReturnType<typeof parseRoadmap>>; storageKey: string}) {
 const [done, setDone] = useState(() => restoreProgress(storageKey, plan.days.length));
 const [index, setIndex] = useState(() => Math.max(0, plan.days.findIndex(day => !done.includes(day.number))));
 const day = plan.days[index];
 const completed = done.includes(day.number);
 const steps = [
  {title: 'Revise', icon: BookOpen, text: day.revise, accent: 'bg-indigo-50 text-indigo-700'},
  {title: 'Practice', icon: PencilLine, text: day.practice, accent: 'bg-amber-50 text-amber-800'},
  {title: 'Check your understanding', icon: ClipboardCheck, text: day.check, accent: 'bg-emerald-50 text-emerald-800'},
 ];

 function toggleDay() {
  const updated = completed ? done.filter(value => value !== day.number) : [...done, day.number];
  setDone(updated);
  try {
   localStorage.setItem(storageKey, JSON.stringify(updated));
  } catch {
   // The current session can still track progress when storage is unavailable.
  }
  if (!completed) {
   const next = plan.days.findIndex((candidate, i) => i > index && !updated.includes(candidate.number));
   if (next >= 0) setIndex(next);
  }
 }

 return <section className="my-3 overflow-hidden rounded-2xl border border-indigo-100 bg-white" aria-label="Study roadmap">
  <header className="bg-gradient-to-br from-slate-950 to-indigo-900 p-5 text-white sm:p-6">
   <div className="flex items-center gap-2"><CalendarDays size={20} aria-hidden="true"/><h3 className="text-lg font-semibold">{plan.title ?? 'Study roadmap'}</h3></div>
   <p className="mt-3 text-sm text-indigo-100" aria-live="polite">{done.length} of {plan.days.length} days complete</p>
   <progress aria-label="Roadmap progress" className="mt-2 block h-2 w-full accent-emerald-400" value={done.length} max={plan.days.length}/>
  </header>
  <div className="space-y-5 p-4 sm:p-6">
   <nav aria-label="Roadmap days" className="flex flex-wrap gap-2">
    {plan.days.map((item, i) => <button type="button" key={item.number} aria-pressed={index === i}
     aria-label={'Day ' + item.number + (done.includes(item.number) ? ', complete' : '')}
     onClick={() => setIndex(i)}
     className={'inline-flex min-h-10 min-w-10 items-center justify-center gap-1 rounded-lg px-2 text-sm font-semibold transition-colors ' +
      (index === i ? 'bg-indigo-700 text-white' : done.includes(item.number) ? 'bg-emerald-50 text-emerald-800' : 'bg-slate-100 text-slate-700 hover:bg-indigo-50')}>
     {item.number}{done.includes(item.number) && <Check size={13} aria-hidden="true"/>}
    </button>)}
   </nav>
   <div aria-live="polite">
    <h4 className="mb-3 text-base font-semibold text-slate-900">Day {day.number}</h4>
    <ol className="grid gap-3">
     {steps.map(({title, icon: Icon, text, accent}) => <li key={title} className="flex items-start gap-3 rounded-xl border border-slate-200 p-4">
      <span className={'rounded-lg p-2 ' + accent}><Icon size={18} aria-hidden="true"/></span>
      <div className="min-w-0">
       <h5 className="text-sm font-semibold text-slate-900">{title}</h5>
       <p className="mt-1 break-words text-sm leading-6 text-slate-700"><Inline text={text}/></p>
      </div>
     </li>)}
    </ol>
   </div>
   <div className="flex flex-wrap gap-2">
    <button type="button" className={action} onClick={() => setIndex(index - 1)} disabled={index === 0}>Previous day</button>
    <button type="button" className={action} onClick={() => setIndex(index + 1)} disabled={index === plan.days.length - 1}>Next day</button>
    <button type="button" className="rounded-lg bg-indigo-700 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-800" onClick={toggleDay}>
     {completed ? 'Mark incomplete' : 'Mark day complete'}
    </button>
   </div>
   {(plan.intro || plan.after) && <details className="rounded-xl bg-slate-50 px-4 py-3">
    <summary className="cursor-pointer text-sm font-semibold text-slate-800">Study tips and quick check</summary>
    <div className="mt-2 space-y-3">
     {plan.intro && <FormattedText text={plan.intro}/>}
     {plan.after && <FormattedText text={plan.after}/>}
    </div>
   </details>}
  </div>
 </section>;
}

export function AssistantAnswer({text, storageKey}: {text: string; storageKey: string}) {
 const plan = parseRoadmap(text);
 return plan ? <Roadmap key={storageKey} plan={plan} storageKey={storageKey}/> : <div className="mt-3"><FormattedText text={text}/></div>;
}
