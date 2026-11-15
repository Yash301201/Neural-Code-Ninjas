"""Original Data Structures mock papers for the demo cohort selectors."""

import re

COHORTS = (
    'AAA-2013J', 'AAA-2014J', 'BBB-2013B', 'BBB-2013J', 'BBB-2014B', 'BBB-2014J',
    'CCC-2014B', 'CCC-2014J', 'DDD-2013B', 'DDD-2013J', 'DDD-2014B', 'DDD-2014J',
    'EEE-2013J', 'EEE-2014B', 'EEE-2014J', 'FFF-2013B', 'FFF-2013J', 'FFF-2014B',
    'FFF-2014J', 'GGG-2013J', 'GGG-2014B', 'GGG-2014J',
)
MID = re.compile(r'\bmid(?:term)?[\s\-\u2010-\u2015]*(1|2|ii?)\b', re.I)
CODE = re.compile(r'\b[A-G]{3}-20\d\d[BJ]-M[12]-[AB]\b', re.I)
PAPER = re.compile(r'\b(?:mock|past|previous(?:[ -]years?)?)\s+(?:(?:exam|question)\s+)?papers?\b', re.I)
NOTICE = 'Original mock paper for practice. The cohort code is a demo label.'


def exercises(exam, n):
    a, b, c = n + 3, n + 11, n + 20
    if exam == 1:
        return (
            ('Arrays', f'Insert {b+1} at index 1 in [{a}, {b}, {c}], then delete the element at index 2. Using zero-based indices, what is the final sum?',
             a+b+1+c, f'The final array is [{a}, {b+1}, {c}]. Add those three values.'),
            ('Linked lists', f'A linked list contains {a} → {b} → {c}. Insert {a+1} after the head, then remove the original tail. What is the new tail value?',
             b, f'After insertion the list is {a} → {a+1} → {b} → {c}. Removing {c} leaves {b} at the tail.'),
            ('Stacks', f'Push {a}, then {b}. Pop once, push {c}, then pop again. What value remains on top?',
             a, f'The pops remove {b} and {c}, the most recently pushed items. The original bottom value {a} remains.'),
            ('Queues', f'Enqueue {a}, {b}, and {c} in order. Dequeue twice, then enqueue {c+2}. What is at the front?',
             c, f'FIFO removes {a} and {b}. Enqueuing {c+2} adds it behind {c}.'),
            ('Circular queues', f'A circular queue has capacity {a} and front index {a-2}. After three successful dequeues, what is the zero-based front index?',
             1, f'The front advances modulo capacity. ({a}-2+3) mod {a} is 1.'),
        )
    return (
        ('Binary search', f'An ascending array has {a} distinct values. Binary search targets the value at index {(a-1)//2}. Using the lower midpoint, how many midpoint probes are needed?',
         1, 'The first probe visits the lower midpoint, which is the target.'),
        ('Binary search trees', f'Insert {b}, {a}, {c}, and {b+1} into an empty binary search tree in order. What value is the left child of {c}?',
         b+1, f'{b+1} is larger than the root {b} and smaller than {c}.'),
        ('Graph traversal', f'A graph is a path from vertex 0 to vertex {a}, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to {a}?',
         a, f'The only path visits 0, 1, …, {a}. Each increment crosses one edge.'),
        ('Hashing', f'A hash table has {a} slots. Using h(k) = k mod {a}, which index does key {2*a+3} map to?',
         3, f'{2*a+3} = 2 × {a} + 3, so the remainder is 3.'),
        ('Sorting', f'How many pairwise comparisons does standard selection sort make when sorting {a} values?',
         a*(a-1)//2, f'The passes make {a-1}, {a-2}, …, 1 comparisons. Sum them using {a} × {a-1} / 2.'),
    )


PAPERS = {
    f'{cohort}-M{exam}-{variant}': exercises(exam, 1 + 3*i + j)
    for i, cohort in enumerate(COHORTS)
    for j, (exam, variant) in enumerate(((1, 'A'), (1, 'B'), (2, 'A')))
}


def label(key):
    return f'Data Structures Mid-{key.split("-")[-2][1]} mock paper {key}'


def question_text(key, index):
    topic, question, _, _ = PAPERS[key][index]
    return f'{key}, Q{index+1} · {topic} (4 marks)\n{question}'


def solution(key, index):
    _, _, answer, explanation = PAPERS[key][index]
    return f'Answer: {answer}. {explanation}'


def paper_text(key, solutions=False):
    questions = []
    for i in range(len(PAPERS[key])):
        text = question_text(key, i)
        if solutions:
            text += '\n' + solution(key, i)
        questions.append(text)
    return f'{label(key)}\n{NOTICE}\n20 marks · 5 questions\n\n' + '\n\n'.join(questions)


def quiz_state(key, remaining, missed):
    return [{'id': 'P1', 'title': label(key), 'excerpt': question_text(key, remaining[0]),
             'source_key': key, 'remaining': remaining, 'missed': missed}]


def respond(question, cohort, previous):
    lowered = question.casefold()
    code = CODE.search(question)
    mid = MID.search(question)
    requested = code or (('data structures' in lowered or 'mock paper' in lowered) and (mid or PAPER.search(question)))
    if not requested:
        if previous and previous['answer_mode'] == 'mock_quiz':
            return grade(question, previous['citations'])
        return None
    exam = 2 if mid and mid[1].lower() in ('2', 'ii') else 1
    keys = ([code[0].upper()] if code[0].upper() in PAPERS else []) if code else [
        key for key in PAPERS if f'-M{exam}-' in key and (not cohort or key.startswith(cohort + '-'))
    ]
    if not keys:
        return 'No mock paper matches that code or cohort. Choose All cohorts or a listed cohort.', 'no_evidence', []
    if not code and re.search(r'\b(?:list|browse)\b', lowered):
        return NOTICE + '\n\n' + '\n'.join(map(label, keys)), 'mock_paper', []
    key = keys[0]
    if ('practice question' in lowered or 'test my knowledge' in lowered or 'quiz me' in lowered) and 'show solutions' not in lowered:
        indices = list(range(len(PAPERS[key])))
        if re.search(r'\bone practice question\b', lowered):
            indices = [next((i for i in indices if PAPERS[key][i][0].casefold() in lowered), 0)]
        return f'{NOTICE}\n\n{question_text(key, indices[0])}\n\nReply with the number you calculated.', 'mock_quiz', quiz_state(key, indices, [])
    show_solutions = bool(re.search(r'\b(?:solutions?|answer key)\b', lowered))
    return paper_text(key, show_solutions), 'mock_paper', []


def grade(question, citations):
    state = citations[0]
    key, remaining, missed = state['source_key'], state['remaining'], state['missed']
    index, *following = remaining
    attempt = re.fullmatch(r'\s*(?:(?:my )?answer(?: is|:)?\s*)?(-?\d{1,9})[.!]?\s*', question, re.I)
    if not attempt:
        return 'Reply with a single number for the current practice question.', 'mock_quiz', citations
    topic, _, expected, _ = PAPERS[key][index]
    correct = int(attempt[1]) == expected
    feedback = ('Correct. ' if correct else 'Incorrect. ') + solution(key, index)
    missed = missed if correct else [*missed, topic]
    if following:
        answer = f'{feedback}\n\n{question_text(key, following[0])}\n\nReply with a number.'
        return answer, 'mock_quiz', quiz_state(key, following, missed)
    if index == len(PAPERS[key]) - 1:
        topics = ', '.join(missed) if missed else 'the topics covered by this paper'
        feedback += (f'\n\nDay 1: Review worked examples for {topics}.'
                     '\nDay 2: Try fresh problems and check each step.'
                     '\nDay 3: Take another timed mock paper and review mistakes.')
    return feedback, 'mock_feedback', []
