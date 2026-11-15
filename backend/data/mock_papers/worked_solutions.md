# Data Structures mock papers with worked solutions

Original practice materials. Cohort codes are demo labels.

## Data Structures Mid-1 mock paper AAA-2013J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

AAA-2013J-M1-A, Q1 · Arrays (4 marks)
Insert 13 at index 1 in [4, 12, 21], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 38. The final array is [4, 13, 21]. Add those three values.

AAA-2013J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 4 → 12 → 21. Insert 5 after the head, then remove the original tail. What is the new tail value?
Answer: 12. After insertion the list is 4 → 5 → 12 → 21. Removing 21 leaves 12 at the tail.

AAA-2013J-M1-A, Q3 · Stacks (4 marks)
Push 4, then 12. Pop once, push 21, then pop again. What value remains on top?
Answer: 4. The pops remove 12 and 21, the most recently pushed items. The original bottom value 4 remains.

AAA-2013J-M1-A, Q4 · Queues (4 marks)
Enqueue 4, 12, and 21 in order. Dequeue twice, then enqueue 23. What is at the front?
Answer: 21. FIFO removes 4 and 12. Enqueuing 23 adds it behind 21.

AAA-2013J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 4 and front index 2. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (4-2+3) mod 4 is 1.

## Data Structures Mid-1 mock paper AAA-2013J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

AAA-2013J-M1-B, Q1 · Arrays (4 marks)
Insert 14 at index 1 in [5, 13, 22], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 41. The final array is [5, 14, 22]. Add those three values.

AAA-2013J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 5 → 13 → 22. Insert 6 after the head, then remove the original tail. What is the new tail value?
Answer: 13. After insertion the list is 5 → 6 → 13 → 22. Removing 22 leaves 13 at the tail.

AAA-2013J-M1-B, Q3 · Stacks (4 marks)
Push 5, then 13. Pop once, push 22, then pop again. What value remains on top?
Answer: 5. The pops remove 13 and 22, the most recently pushed items. The original bottom value 5 remains.

AAA-2013J-M1-B, Q4 · Queues (4 marks)
Enqueue 5, 13, and 22 in order. Dequeue twice, then enqueue 24. What is at the front?
Answer: 22. FIFO removes 5 and 13. Enqueuing 24 adds it behind 22.

AAA-2013J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 5 and front index 3. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (5-2+3) mod 5 is 1.

## Data Structures Mid-2 mock paper AAA-2013J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

AAA-2013J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 6 distinct values. Binary search targets the value at index 2. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

AAA-2013J-M2-A, Q2 · Binary search trees (4 marks)
Insert 14, 6, 23, and 15 into an empty binary search tree in order. What value is the left child of 23?
Answer: 15. 15 is larger than the root 14 and smaller than 23.

AAA-2013J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 6, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 6?
Answer: 6. The only path visits 0, 1, …, 6. Each increment crosses one edge.

AAA-2013J-M2-A, Q4 · Hashing (4 marks)
A hash table has 6 slots. Using h(k) = k mod 6, which index does key 15 map to?
Answer: 3. 15 = 2 × 6 + 3, so the remainder is 3.

AAA-2013J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 6 values?
Answer: 15. The passes make 5, 4, …, 1 comparisons. Sum them using 6 × 5 / 2.

## Data Structures Mid-1 mock paper AAA-2014J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

AAA-2014J-M1-A, Q1 · Arrays (4 marks)
Insert 16 at index 1 in [7, 15, 24], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 47. The final array is [7, 16, 24]. Add those three values.

AAA-2014J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 7 → 15 → 24. Insert 8 after the head, then remove the original tail. What is the new tail value?
Answer: 15. After insertion the list is 7 → 8 → 15 → 24. Removing 24 leaves 15 at the tail.

AAA-2014J-M1-A, Q3 · Stacks (4 marks)
Push 7, then 15. Pop once, push 24, then pop again. What value remains on top?
Answer: 7. The pops remove 15 and 24, the most recently pushed items. The original bottom value 7 remains.

AAA-2014J-M1-A, Q4 · Queues (4 marks)
Enqueue 7, 15, and 24 in order. Dequeue twice, then enqueue 26. What is at the front?
Answer: 24. FIFO removes 7 and 15. Enqueuing 26 adds it behind 24.

AAA-2014J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 7 and front index 5. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (7-2+3) mod 7 is 1.

## Data Structures Mid-1 mock paper AAA-2014J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

AAA-2014J-M1-B, Q1 · Arrays (4 marks)
Insert 17 at index 1 in [8, 16, 25], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 50. The final array is [8, 17, 25]. Add those three values.

AAA-2014J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 8 → 16 → 25. Insert 9 after the head, then remove the original tail. What is the new tail value?
Answer: 16. After insertion the list is 8 → 9 → 16 → 25. Removing 25 leaves 16 at the tail.

AAA-2014J-M1-B, Q3 · Stacks (4 marks)
Push 8, then 16. Pop once, push 25, then pop again. What value remains on top?
Answer: 8. The pops remove 16 and 25, the most recently pushed items. The original bottom value 8 remains.

AAA-2014J-M1-B, Q4 · Queues (4 marks)
Enqueue 8, 16, and 25 in order. Dequeue twice, then enqueue 27. What is at the front?
Answer: 25. FIFO removes 8 and 16. Enqueuing 27 adds it behind 25.

AAA-2014J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 8 and front index 6. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (8-2+3) mod 8 is 1.

## Data Structures Mid-2 mock paper AAA-2014J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

AAA-2014J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 9 distinct values. Binary search targets the value at index 4. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

AAA-2014J-M2-A, Q2 · Binary search trees (4 marks)
Insert 17, 9, 26, and 18 into an empty binary search tree in order. What value is the left child of 26?
Answer: 18. 18 is larger than the root 17 and smaller than 26.

AAA-2014J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 9, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 9?
Answer: 9. The only path visits 0, 1, …, 9. Each increment crosses one edge.

AAA-2014J-M2-A, Q4 · Hashing (4 marks)
A hash table has 9 slots. Using h(k) = k mod 9, which index does key 21 map to?
Answer: 3. 21 = 2 × 9 + 3, so the remainder is 3.

AAA-2014J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 9 values?
Answer: 36. The passes make 8, 7, …, 1 comparisons. Sum them using 9 × 8 / 2.

## Data Structures Mid-1 mock paper BBB-2013B-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2013B-M1-A, Q1 · Arrays (4 marks)
Insert 19 at index 1 in [10, 18, 27], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 56. The final array is [10, 19, 27]. Add those three values.

BBB-2013B-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 10 → 18 → 27. Insert 11 after the head, then remove the original tail. What is the new tail value?
Answer: 18. After insertion the list is 10 → 11 → 18 → 27. Removing 27 leaves 18 at the tail.

BBB-2013B-M1-A, Q3 · Stacks (4 marks)
Push 10, then 18. Pop once, push 27, then pop again. What value remains on top?
Answer: 10. The pops remove 18 and 27, the most recently pushed items. The original bottom value 10 remains.

BBB-2013B-M1-A, Q4 · Queues (4 marks)
Enqueue 10, 18, and 27 in order. Dequeue twice, then enqueue 29. What is at the front?
Answer: 27. FIFO removes 10 and 18. Enqueuing 29 adds it behind 27.

BBB-2013B-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 10 and front index 8. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (10-2+3) mod 10 is 1.

## Data Structures Mid-1 mock paper BBB-2013B-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2013B-M1-B, Q1 · Arrays (4 marks)
Insert 20 at index 1 in [11, 19, 28], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 59. The final array is [11, 20, 28]. Add those three values.

BBB-2013B-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 11 → 19 → 28. Insert 12 after the head, then remove the original tail. What is the new tail value?
Answer: 19. After insertion the list is 11 → 12 → 19 → 28. Removing 28 leaves 19 at the tail.

BBB-2013B-M1-B, Q3 · Stacks (4 marks)
Push 11, then 19. Pop once, push 28, then pop again. What value remains on top?
Answer: 11. The pops remove 19 and 28, the most recently pushed items. The original bottom value 11 remains.

BBB-2013B-M1-B, Q4 · Queues (4 marks)
Enqueue 11, 19, and 28 in order. Dequeue twice, then enqueue 30. What is at the front?
Answer: 28. FIFO removes 11 and 19. Enqueuing 30 adds it behind 28.

BBB-2013B-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 11 and front index 9. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (11-2+3) mod 11 is 1.

## Data Structures Mid-2 mock paper BBB-2013B-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2013B-M2-A, Q1 · Binary search (4 marks)
An ascending array has 12 distinct values. Binary search targets the value at index 5. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

BBB-2013B-M2-A, Q2 · Binary search trees (4 marks)
Insert 20, 12, 29, and 21 into an empty binary search tree in order. What value is the left child of 29?
Answer: 21. 21 is larger than the root 20 and smaller than 29.

BBB-2013B-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 12, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 12?
Answer: 12. The only path visits 0, 1, …, 12. Each increment crosses one edge.

BBB-2013B-M2-A, Q4 · Hashing (4 marks)
A hash table has 12 slots. Using h(k) = k mod 12, which index does key 27 map to?
Answer: 3. 27 = 2 × 12 + 3, so the remainder is 3.

BBB-2013B-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 12 values?
Answer: 66. The passes make 11, 10, …, 1 comparisons. Sum them using 12 × 11 / 2.

## Data Structures Mid-1 mock paper BBB-2013J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2013J-M1-A, Q1 · Arrays (4 marks)
Insert 22 at index 1 in [13, 21, 30], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 65. The final array is [13, 22, 30]. Add those three values.

BBB-2013J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 13 → 21 → 30. Insert 14 after the head, then remove the original tail. What is the new tail value?
Answer: 21. After insertion the list is 13 → 14 → 21 → 30. Removing 30 leaves 21 at the tail.

BBB-2013J-M1-A, Q3 · Stacks (4 marks)
Push 13, then 21. Pop once, push 30, then pop again. What value remains on top?
Answer: 13. The pops remove 21 and 30, the most recently pushed items. The original bottom value 13 remains.

BBB-2013J-M1-A, Q4 · Queues (4 marks)
Enqueue 13, 21, and 30 in order. Dequeue twice, then enqueue 32. What is at the front?
Answer: 30. FIFO removes 13 and 21. Enqueuing 32 adds it behind 30.

BBB-2013J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 13 and front index 11. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (13-2+3) mod 13 is 1.

## Data Structures Mid-1 mock paper BBB-2013J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2013J-M1-B, Q1 · Arrays (4 marks)
Insert 23 at index 1 in [14, 22, 31], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 68. The final array is [14, 23, 31]. Add those three values.

BBB-2013J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 14 → 22 → 31. Insert 15 after the head, then remove the original tail. What is the new tail value?
Answer: 22. After insertion the list is 14 → 15 → 22 → 31. Removing 31 leaves 22 at the tail.

BBB-2013J-M1-B, Q3 · Stacks (4 marks)
Push 14, then 22. Pop once, push 31, then pop again. What value remains on top?
Answer: 14. The pops remove 22 and 31, the most recently pushed items. The original bottom value 14 remains.

BBB-2013J-M1-B, Q4 · Queues (4 marks)
Enqueue 14, 22, and 31 in order. Dequeue twice, then enqueue 33. What is at the front?
Answer: 31. FIFO removes 14 and 22. Enqueuing 33 adds it behind 31.

BBB-2013J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 14 and front index 12. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (14-2+3) mod 14 is 1.

## Data Structures Mid-2 mock paper BBB-2013J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2013J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 15 distinct values. Binary search targets the value at index 7. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

BBB-2013J-M2-A, Q2 · Binary search trees (4 marks)
Insert 23, 15, 32, and 24 into an empty binary search tree in order. What value is the left child of 32?
Answer: 24. 24 is larger than the root 23 and smaller than 32.

BBB-2013J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 15, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 15?
Answer: 15. The only path visits 0, 1, …, 15. Each increment crosses one edge.

BBB-2013J-M2-A, Q4 · Hashing (4 marks)
A hash table has 15 slots. Using h(k) = k mod 15, which index does key 33 map to?
Answer: 3. 33 = 2 × 15 + 3, so the remainder is 3.

BBB-2013J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 15 values?
Answer: 105. The passes make 14, 13, …, 1 comparisons. Sum them using 15 × 14 / 2.

## Data Structures Mid-1 mock paper BBB-2014B-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2014B-M1-A, Q1 · Arrays (4 marks)
Insert 25 at index 1 in [16, 24, 33], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 74. The final array is [16, 25, 33]. Add those three values.

BBB-2014B-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 16 → 24 → 33. Insert 17 after the head, then remove the original tail. What is the new tail value?
Answer: 24. After insertion the list is 16 → 17 → 24 → 33. Removing 33 leaves 24 at the tail.

BBB-2014B-M1-A, Q3 · Stacks (4 marks)
Push 16, then 24. Pop once, push 33, then pop again. What value remains on top?
Answer: 16. The pops remove 24 and 33, the most recently pushed items. The original bottom value 16 remains.

BBB-2014B-M1-A, Q4 · Queues (4 marks)
Enqueue 16, 24, and 33 in order. Dequeue twice, then enqueue 35. What is at the front?
Answer: 33. FIFO removes 16 and 24. Enqueuing 35 adds it behind 33.

BBB-2014B-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 16 and front index 14. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (16-2+3) mod 16 is 1.

## Data Structures Mid-1 mock paper BBB-2014B-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2014B-M1-B, Q1 · Arrays (4 marks)
Insert 26 at index 1 in [17, 25, 34], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 77. The final array is [17, 26, 34]. Add those three values.

BBB-2014B-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 17 → 25 → 34. Insert 18 after the head, then remove the original tail. What is the new tail value?
Answer: 25. After insertion the list is 17 → 18 → 25 → 34. Removing 34 leaves 25 at the tail.

BBB-2014B-M1-B, Q3 · Stacks (4 marks)
Push 17, then 25. Pop once, push 34, then pop again. What value remains on top?
Answer: 17. The pops remove 25 and 34, the most recently pushed items. The original bottom value 17 remains.

BBB-2014B-M1-B, Q4 · Queues (4 marks)
Enqueue 17, 25, and 34 in order. Dequeue twice, then enqueue 36. What is at the front?
Answer: 34. FIFO removes 17 and 25. Enqueuing 36 adds it behind 34.

BBB-2014B-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 17 and front index 15. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (17-2+3) mod 17 is 1.

## Data Structures Mid-2 mock paper BBB-2014B-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2014B-M2-A, Q1 · Binary search (4 marks)
An ascending array has 18 distinct values. Binary search targets the value at index 8. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

BBB-2014B-M2-A, Q2 · Binary search trees (4 marks)
Insert 26, 18, 35, and 27 into an empty binary search tree in order. What value is the left child of 35?
Answer: 27. 27 is larger than the root 26 and smaller than 35.

BBB-2014B-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 18, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 18?
Answer: 18. The only path visits 0, 1, …, 18. Each increment crosses one edge.

BBB-2014B-M2-A, Q4 · Hashing (4 marks)
A hash table has 18 slots. Using h(k) = k mod 18, which index does key 39 map to?
Answer: 3. 39 = 2 × 18 + 3, so the remainder is 3.

BBB-2014B-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 18 values?
Answer: 153. The passes make 17, 16, …, 1 comparisons. Sum them using 18 × 17 / 2.

## Data Structures Mid-1 mock paper BBB-2014J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2014J-M1-A, Q1 · Arrays (4 marks)
Insert 28 at index 1 in [19, 27, 36], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 83. The final array is [19, 28, 36]. Add those three values.

BBB-2014J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 19 → 27 → 36. Insert 20 after the head, then remove the original tail. What is the new tail value?
Answer: 27. After insertion the list is 19 → 20 → 27 → 36. Removing 36 leaves 27 at the tail.

BBB-2014J-M1-A, Q3 · Stacks (4 marks)
Push 19, then 27. Pop once, push 36, then pop again. What value remains on top?
Answer: 19. The pops remove 27 and 36, the most recently pushed items. The original bottom value 19 remains.

BBB-2014J-M1-A, Q4 · Queues (4 marks)
Enqueue 19, 27, and 36 in order. Dequeue twice, then enqueue 38. What is at the front?
Answer: 36. FIFO removes 19 and 27. Enqueuing 38 adds it behind 36.

BBB-2014J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 19 and front index 17. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (19-2+3) mod 19 is 1.

## Data Structures Mid-1 mock paper BBB-2014J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2014J-M1-B, Q1 · Arrays (4 marks)
Insert 29 at index 1 in [20, 28, 37], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 86. The final array is [20, 29, 37]. Add those three values.

BBB-2014J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 20 → 28 → 37. Insert 21 after the head, then remove the original tail. What is the new tail value?
Answer: 28. After insertion the list is 20 → 21 → 28 → 37. Removing 37 leaves 28 at the tail.

BBB-2014J-M1-B, Q3 · Stacks (4 marks)
Push 20, then 28. Pop once, push 37, then pop again. What value remains on top?
Answer: 20. The pops remove 28 and 37, the most recently pushed items. The original bottom value 20 remains.

BBB-2014J-M1-B, Q4 · Queues (4 marks)
Enqueue 20, 28, and 37 in order. Dequeue twice, then enqueue 39. What is at the front?
Answer: 37. FIFO removes 20 and 28. Enqueuing 39 adds it behind 37.

BBB-2014J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 20 and front index 18. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (20-2+3) mod 20 is 1.

## Data Structures Mid-2 mock paper BBB-2014J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

BBB-2014J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 21 distinct values. Binary search targets the value at index 10. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

BBB-2014J-M2-A, Q2 · Binary search trees (4 marks)
Insert 29, 21, 38, and 30 into an empty binary search tree in order. What value is the left child of 38?
Answer: 30. 30 is larger than the root 29 and smaller than 38.

BBB-2014J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 21, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 21?
Answer: 21. The only path visits 0, 1, …, 21. Each increment crosses one edge.

BBB-2014J-M2-A, Q4 · Hashing (4 marks)
A hash table has 21 slots. Using h(k) = k mod 21, which index does key 45 map to?
Answer: 3. 45 = 2 × 21 + 3, so the remainder is 3.

BBB-2014J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 21 values?
Answer: 210. The passes make 20, 19, …, 1 comparisons. Sum them using 21 × 20 / 2.

## Data Structures Mid-1 mock paper CCC-2014B-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

CCC-2014B-M1-A, Q1 · Arrays (4 marks)
Insert 31 at index 1 in [22, 30, 39], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 92. The final array is [22, 31, 39]. Add those three values.

CCC-2014B-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 22 → 30 → 39. Insert 23 after the head, then remove the original tail. What is the new tail value?
Answer: 30. After insertion the list is 22 → 23 → 30 → 39. Removing 39 leaves 30 at the tail.

CCC-2014B-M1-A, Q3 · Stacks (4 marks)
Push 22, then 30. Pop once, push 39, then pop again. What value remains on top?
Answer: 22. The pops remove 30 and 39, the most recently pushed items. The original bottom value 22 remains.

CCC-2014B-M1-A, Q4 · Queues (4 marks)
Enqueue 22, 30, and 39 in order. Dequeue twice, then enqueue 41. What is at the front?
Answer: 39. FIFO removes 22 and 30. Enqueuing 41 adds it behind 39.

CCC-2014B-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 22 and front index 20. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (22-2+3) mod 22 is 1.

## Data Structures Mid-1 mock paper CCC-2014B-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

CCC-2014B-M1-B, Q1 · Arrays (4 marks)
Insert 32 at index 1 in [23, 31, 40], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 95. The final array is [23, 32, 40]. Add those three values.

CCC-2014B-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 23 → 31 → 40. Insert 24 after the head, then remove the original tail. What is the new tail value?
Answer: 31. After insertion the list is 23 → 24 → 31 → 40. Removing 40 leaves 31 at the tail.

CCC-2014B-M1-B, Q3 · Stacks (4 marks)
Push 23, then 31. Pop once, push 40, then pop again. What value remains on top?
Answer: 23. The pops remove 31 and 40, the most recently pushed items. The original bottom value 23 remains.

CCC-2014B-M1-B, Q4 · Queues (4 marks)
Enqueue 23, 31, and 40 in order. Dequeue twice, then enqueue 42. What is at the front?
Answer: 40. FIFO removes 23 and 31. Enqueuing 42 adds it behind 40.

CCC-2014B-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 23 and front index 21. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (23-2+3) mod 23 is 1.

## Data Structures Mid-2 mock paper CCC-2014B-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

CCC-2014B-M2-A, Q1 · Binary search (4 marks)
An ascending array has 24 distinct values. Binary search targets the value at index 11. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

CCC-2014B-M2-A, Q2 · Binary search trees (4 marks)
Insert 32, 24, 41, and 33 into an empty binary search tree in order. What value is the left child of 41?
Answer: 33. 33 is larger than the root 32 and smaller than 41.

CCC-2014B-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 24, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 24?
Answer: 24. The only path visits 0, 1, …, 24. Each increment crosses one edge.

CCC-2014B-M2-A, Q4 · Hashing (4 marks)
A hash table has 24 slots. Using h(k) = k mod 24, which index does key 51 map to?
Answer: 3. 51 = 2 × 24 + 3, so the remainder is 3.

CCC-2014B-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 24 values?
Answer: 276. The passes make 23, 22, …, 1 comparisons. Sum them using 24 × 23 / 2.

## Data Structures Mid-1 mock paper CCC-2014J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

CCC-2014J-M1-A, Q1 · Arrays (4 marks)
Insert 34 at index 1 in [25, 33, 42], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 101. The final array is [25, 34, 42]. Add those three values.

CCC-2014J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 25 → 33 → 42. Insert 26 after the head, then remove the original tail. What is the new tail value?
Answer: 33. After insertion the list is 25 → 26 → 33 → 42. Removing 42 leaves 33 at the tail.

CCC-2014J-M1-A, Q3 · Stacks (4 marks)
Push 25, then 33. Pop once, push 42, then pop again. What value remains on top?
Answer: 25. The pops remove 33 and 42, the most recently pushed items. The original bottom value 25 remains.

CCC-2014J-M1-A, Q4 · Queues (4 marks)
Enqueue 25, 33, and 42 in order. Dequeue twice, then enqueue 44. What is at the front?
Answer: 42. FIFO removes 25 and 33. Enqueuing 44 adds it behind 42.

CCC-2014J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 25 and front index 23. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (25-2+3) mod 25 is 1.

## Data Structures Mid-1 mock paper CCC-2014J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

CCC-2014J-M1-B, Q1 · Arrays (4 marks)
Insert 35 at index 1 in [26, 34, 43], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 104. The final array is [26, 35, 43]. Add those three values.

CCC-2014J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 26 → 34 → 43. Insert 27 after the head, then remove the original tail. What is the new tail value?
Answer: 34. After insertion the list is 26 → 27 → 34 → 43. Removing 43 leaves 34 at the tail.

CCC-2014J-M1-B, Q3 · Stacks (4 marks)
Push 26, then 34. Pop once, push 43, then pop again. What value remains on top?
Answer: 26. The pops remove 34 and 43, the most recently pushed items. The original bottom value 26 remains.

CCC-2014J-M1-B, Q4 · Queues (4 marks)
Enqueue 26, 34, and 43 in order. Dequeue twice, then enqueue 45. What is at the front?
Answer: 43. FIFO removes 26 and 34. Enqueuing 45 adds it behind 43.

CCC-2014J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 26 and front index 24. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (26-2+3) mod 26 is 1.

## Data Structures Mid-2 mock paper CCC-2014J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

CCC-2014J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 27 distinct values. Binary search targets the value at index 13. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

CCC-2014J-M2-A, Q2 · Binary search trees (4 marks)
Insert 35, 27, 44, and 36 into an empty binary search tree in order. What value is the left child of 44?
Answer: 36. 36 is larger than the root 35 and smaller than 44.

CCC-2014J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 27, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 27?
Answer: 27. The only path visits 0, 1, …, 27. Each increment crosses one edge.

CCC-2014J-M2-A, Q4 · Hashing (4 marks)
A hash table has 27 slots. Using h(k) = k mod 27, which index does key 57 map to?
Answer: 3. 57 = 2 × 27 + 3, so the remainder is 3.

CCC-2014J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 27 values?
Answer: 351. The passes make 26, 25, …, 1 comparisons. Sum them using 27 × 26 / 2.

## Data Structures Mid-1 mock paper DDD-2013B-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2013B-M1-A, Q1 · Arrays (4 marks)
Insert 37 at index 1 in [28, 36, 45], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 110. The final array is [28, 37, 45]. Add those three values.

DDD-2013B-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 28 → 36 → 45. Insert 29 after the head, then remove the original tail. What is the new tail value?
Answer: 36. After insertion the list is 28 → 29 → 36 → 45. Removing 45 leaves 36 at the tail.

DDD-2013B-M1-A, Q3 · Stacks (4 marks)
Push 28, then 36. Pop once, push 45, then pop again. What value remains on top?
Answer: 28. The pops remove 36 and 45, the most recently pushed items. The original bottom value 28 remains.

DDD-2013B-M1-A, Q4 · Queues (4 marks)
Enqueue 28, 36, and 45 in order. Dequeue twice, then enqueue 47. What is at the front?
Answer: 45. FIFO removes 28 and 36. Enqueuing 47 adds it behind 45.

DDD-2013B-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 28 and front index 26. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (28-2+3) mod 28 is 1.

## Data Structures Mid-1 mock paper DDD-2013B-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2013B-M1-B, Q1 · Arrays (4 marks)
Insert 38 at index 1 in [29, 37, 46], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 113. The final array is [29, 38, 46]. Add those three values.

DDD-2013B-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 29 → 37 → 46. Insert 30 after the head, then remove the original tail. What is the new tail value?
Answer: 37. After insertion the list is 29 → 30 → 37 → 46. Removing 46 leaves 37 at the tail.

DDD-2013B-M1-B, Q3 · Stacks (4 marks)
Push 29, then 37. Pop once, push 46, then pop again. What value remains on top?
Answer: 29. The pops remove 37 and 46, the most recently pushed items. The original bottom value 29 remains.

DDD-2013B-M1-B, Q4 · Queues (4 marks)
Enqueue 29, 37, and 46 in order. Dequeue twice, then enqueue 48. What is at the front?
Answer: 46. FIFO removes 29 and 37. Enqueuing 48 adds it behind 46.

DDD-2013B-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 29 and front index 27. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (29-2+3) mod 29 is 1.

## Data Structures Mid-2 mock paper DDD-2013B-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2013B-M2-A, Q1 · Binary search (4 marks)
An ascending array has 30 distinct values. Binary search targets the value at index 14. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

DDD-2013B-M2-A, Q2 · Binary search trees (4 marks)
Insert 38, 30, 47, and 39 into an empty binary search tree in order. What value is the left child of 47?
Answer: 39. 39 is larger than the root 38 and smaller than 47.

DDD-2013B-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 30, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 30?
Answer: 30. The only path visits 0, 1, …, 30. Each increment crosses one edge.

DDD-2013B-M2-A, Q4 · Hashing (4 marks)
A hash table has 30 slots. Using h(k) = k mod 30, which index does key 63 map to?
Answer: 3. 63 = 2 × 30 + 3, so the remainder is 3.

DDD-2013B-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 30 values?
Answer: 435. The passes make 29, 28, …, 1 comparisons. Sum them using 30 × 29 / 2.

## Data Structures Mid-1 mock paper DDD-2013J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2013J-M1-A, Q1 · Arrays (4 marks)
Insert 40 at index 1 in [31, 39, 48], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 119. The final array is [31, 40, 48]. Add those three values.

DDD-2013J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 31 → 39 → 48. Insert 32 after the head, then remove the original tail. What is the new tail value?
Answer: 39. After insertion the list is 31 → 32 → 39 → 48. Removing 48 leaves 39 at the tail.

DDD-2013J-M1-A, Q3 · Stacks (4 marks)
Push 31, then 39. Pop once, push 48, then pop again. What value remains on top?
Answer: 31. The pops remove 39 and 48, the most recently pushed items. The original bottom value 31 remains.

DDD-2013J-M1-A, Q4 · Queues (4 marks)
Enqueue 31, 39, and 48 in order. Dequeue twice, then enqueue 50. What is at the front?
Answer: 48. FIFO removes 31 and 39. Enqueuing 50 adds it behind 48.

DDD-2013J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 31 and front index 29. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (31-2+3) mod 31 is 1.

## Data Structures Mid-1 mock paper DDD-2013J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2013J-M1-B, Q1 · Arrays (4 marks)
Insert 41 at index 1 in [32, 40, 49], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 122. The final array is [32, 41, 49]. Add those three values.

DDD-2013J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 32 → 40 → 49. Insert 33 after the head, then remove the original tail. What is the new tail value?
Answer: 40. After insertion the list is 32 → 33 → 40 → 49. Removing 49 leaves 40 at the tail.

DDD-2013J-M1-B, Q3 · Stacks (4 marks)
Push 32, then 40. Pop once, push 49, then pop again. What value remains on top?
Answer: 32. The pops remove 40 and 49, the most recently pushed items. The original bottom value 32 remains.

DDD-2013J-M1-B, Q4 · Queues (4 marks)
Enqueue 32, 40, and 49 in order. Dequeue twice, then enqueue 51. What is at the front?
Answer: 49. FIFO removes 32 and 40. Enqueuing 51 adds it behind 49.

DDD-2013J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 32 and front index 30. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (32-2+3) mod 32 is 1.

## Data Structures Mid-2 mock paper DDD-2013J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2013J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 33 distinct values. Binary search targets the value at index 16. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

DDD-2013J-M2-A, Q2 · Binary search trees (4 marks)
Insert 41, 33, 50, and 42 into an empty binary search tree in order. What value is the left child of 50?
Answer: 42. 42 is larger than the root 41 and smaller than 50.

DDD-2013J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 33, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 33?
Answer: 33. The only path visits 0, 1, …, 33. Each increment crosses one edge.

DDD-2013J-M2-A, Q4 · Hashing (4 marks)
A hash table has 33 slots. Using h(k) = k mod 33, which index does key 69 map to?
Answer: 3. 69 = 2 × 33 + 3, so the remainder is 3.

DDD-2013J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 33 values?
Answer: 528. The passes make 32, 31, …, 1 comparisons. Sum them using 33 × 32 / 2.

## Data Structures Mid-1 mock paper DDD-2014B-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2014B-M1-A, Q1 · Arrays (4 marks)
Insert 43 at index 1 in [34, 42, 51], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 128. The final array is [34, 43, 51]. Add those three values.

DDD-2014B-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 34 → 42 → 51. Insert 35 after the head, then remove the original tail. What is the new tail value?
Answer: 42. After insertion the list is 34 → 35 → 42 → 51. Removing 51 leaves 42 at the tail.

DDD-2014B-M1-A, Q3 · Stacks (4 marks)
Push 34, then 42. Pop once, push 51, then pop again. What value remains on top?
Answer: 34. The pops remove 42 and 51, the most recently pushed items. The original bottom value 34 remains.

DDD-2014B-M1-A, Q4 · Queues (4 marks)
Enqueue 34, 42, and 51 in order. Dequeue twice, then enqueue 53. What is at the front?
Answer: 51. FIFO removes 34 and 42. Enqueuing 53 adds it behind 51.

DDD-2014B-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 34 and front index 32. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (34-2+3) mod 34 is 1.

## Data Structures Mid-1 mock paper DDD-2014B-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2014B-M1-B, Q1 · Arrays (4 marks)
Insert 44 at index 1 in [35, 43, 52], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 131. The final array is [35, 44, 52]. Add those three values.

DDD-2014B-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 35 → 43 → 52. Insert 36 after the head, then remove the original tail. What is the new tail value?
Answer: 43. After insertion the list is 35 → 36 → 43 → 52. Removing 52 leaves 43 at the tail.

DDD-2014B-M1-B, Q3 · Stacks (4 marks)
Push 35, then 43. Pop once, push 52, then pop again. What value remains on top?
Answer: 35. The pops remove 43 and 52, the most recently pushed items. The original bottom value 35 remains.

DDD-2014B-M1-B, Q4 · Queues (4 marks)
Enqueue 35, 43, and 52 in order. Dequeue twice, then enqueue 54. What is at the front?
Answer: 52. FIFO removes 35 and 43. Enqueuing 54 adds it behind 52.

DDD-2014B-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 35 and front index 33. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (35-2+3) mod 35 is 1.

## Data Structures Mid-2 mock paper DDD-2014B-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2014B-M2-A, Q1 · Binary search (4 marks)
An ascending array has 36 distinct values. Binary search targets the value at index 17. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

DDD-2014B-M2-A, Q2 · Binary search trees (4 marks)
Insert 44, 36, 53, and 45 into an empty binary search tree in order. What value is the left child of 53?
Answer: 45. 45 is larger than the root 44 and smaller than 53.

DDD-2014B-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 36, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 36?
Answer: 36. The only path visits 0, 1, …, 36. Each increment crosses one edge.

DDD-2014B-M2-A, Q4 · Hashing (4 marks)
A hash table has 36 slots. Using h(k) = k mod 36, which index does key 75 map to?
Answer: 3. 75 = 2 × 36 + 3, so the remainder is 3.

DDD-2014B-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 36 values?
Answer: 630. The passes make 35, 34, …, 1 comparisons. Sum them using 36 × 35 / 2.

## Data Structures Mid-1 mock paper DDD-2014J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2014J-M1-A, Q1 · Arrays (4 marks)
Insert 46 at index 1 in [37, 45, 54], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 137. The final array is [37, 46, 54]. Add those three values.

DDD-2014J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 37 → 45 → 54. Insert 38 after the head, then remove the original tail. What is the new tail value?
Answer: 45. After insertion the list is 37 → 38 → 45 → 54. Removing 54 leaves 45 at the tail.

DDD-2014J-M1-A, Q3 · Stacks (4 marks)
Push 37, then 45. Pop once, push 54, then pop again. What value remains on top?
Answer: 37. The pops remove 45 and 54, the most recently pushed items. The original bottom value 37 remains.

DDD-2014J-M1-A, Q4 · Queues (4 marks)
Enqueue 37, 45, and 54 in order. Dequeue twice, then enqueue 56. What is at the front?
Answer: 54. FIFO removes 37 and 45. Enqueuing 56 adds it behind 54.

DDD-2014J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 37 and front index 35. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (37-2+3) mod 37 is 1.

## Data Structures Mid-1 mock paper DDD-2014J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2014J-M1-B, Q1 · Arrays (4 marks)
Insert 47 at index 1 in [38, 46, 55], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 140. The final array is [38, 47, 55]. Add those three values.

DDD-2014J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 38 → 46 → 55. Insert 39 after the head, then remove the original tail. What is the new tail value?
Answer: 46. After insertion the list is 38 → 39 → 46 → 55. Removing 55 leaves 46 at the tail.

DDD-2014J-M1-B, Q3 · Stacks (4 marks)
Push 38, then 46. Pop once, push 55, then pop again. What value remains on top?
Answer: 38. The pops remove 46 and 55, the most recently pushed items. The original bottom value 38 remains.

DDD-2014J-M1-B, Q4 · Queues (4 marks)
Enqueue 38, 46, and 55 in order. Dequeue twice, then enqueue 57. What is at the front?
Answer: 55. FIFO removes 38 and 46. Enqueuing 57 adds it behind 55.

DDD-2014J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 38 and front index 36. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (38-2+3) mod 38 is 1.

## Data Structures Mid-2 mock paper DDD-2014J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

DDD-2014J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 39 distinct values. Binary search targets the value at index 19. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

DDD-2014J-M2-A, Q2 · Binary search trees (4 marks)
Insert 47, 39, 56, and 48 into an empty binary search tree in order. What value is the left child of 56?
Answer: 48. 48 is larger than the root 47 and smaller than 56.

DDD-2014J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 39, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 39?
Answer: 39. The only path visits 0, 1, …, 39. Each increment crosses one edge.

DDD-2014J-M2-A, Q4 · Hashing (4 marks)
A hash table has 39 slots. Using h(k) = k mod 39, which index does key 81 map to?
Answer: 3. 81 = 2 × 39 + 3, so the remainder is 3.

DDD-2014J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 39 values?
Answer: 741. The passes make 38, 37, …, 1 comparisons. Sum them using 39 × 38 / 2.

## Data Structures Mid-1 mock paper EEE-2013J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

EEE-2013J-M1-A, Q1 · Arrays (4 marks)
Insert 49 at index 1 in [40, 48, 57], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 146. The final array is [40, 49, 57]. Add those three values.

EEE-2013J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 40 → 48 → 57. Insert 41 after the head, then remove the original tail. What is the new tail value?
Answer: 48. After insertion the list is 40 → 41 → 48 → 57. Removing 57 leaves 48 at the tail.

EEE-2013J-M1-A, Q3 · Stacks (4 marks)
Push 40, then 48. Pop once, push 57, then pop again. What value remains on top?
Answer: 40. The pops remove 48 and 57, the most recently pushed items. The original bottom value 40 remains.

EEE-2013J-M1-A, Q4 · Queues (4 marks)
Enqueue 40, 48, and 57 in order. Dequeue twice, then enqueue 59. What is at the front?
Answer: 57. FIFO removes 40 and 48. Enqueuing 59 adds it behind 57.

EEE-2013J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 40 and front index 38. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (40-2+3) mod 40 is 1.

## Data Structures Mid-1 mock paper EEE-2013J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

EEE-2013J-M1-B, Q1 · Arrays (4 marks)
Insert 50 at index 1 in [41, 49, 58], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 149. The final array is [41, 50, 58]. Add those three values.

EEE-2013J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 41 → 49 → 58. Insert 42 after the head, then remove the original tail. What is the new tail value?
Answer: 49. After insertion the list is 41 → 42 → 49 → 58. Removing 58 leaves 49 at the tail.

EEE-2013J-M1-B, Q3 · Stacks (4 marks)
Push 41, then 49. Pop once, push 58, then pop again. What value remains on top?
Answer: 41. The pops remove 49 and 58, the most recently pushed items. The original bottom value 41 remains.

EEE-2013J-M1-B, Q4 · Queues (4 marks)
Enqueue 41, 49, and 58 in order. Dequeue twice, then enqueue 60. What is at the front?
Answer: 58. FIFO removes 41 and 49. Enqueuing 60 adds it behind 58.

EEE-2013J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 41 and front index 39. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (41-2+3) mod 41 is 1.

## Data Structures Mid-2 mock paper EEE-2013J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

EEE-2013J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 42 distinct values. Binary search targets the value at index 20. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

EEE-2013J-M2-A, Q2 · Binary search trees (4 marks)
Insert 50, 42, 59, and 51 into an empty binary search tree in order. What value is the left child of 59?
Answer: 51. 51 is larger than the root 50 and smaller than 59.

EEE-2013J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 42, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 42?
Answer: 42. The only path visits 0, 1, …, 42. Each increment crosses one edge.

EEE-2013J-M2-A, Q4 · Hashing (4 marks)
A hash table has 42 slots. Using h(k) = k mod 42, which index does key 87 map to?
Answer: 3. 87 = 2 × 42 + 3, so the remainder is 3.

EEE-2013J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 42 values?
Answer: 861. The passes make 41, 40, …, 1 comparisons. Sum them using 42 × 41 / 2.

## Data Structures Mid-1 mock paper EEE-2014B-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

EEE-2014B-M1-A, Q1 · Arrays (4 marks)
Insert 52 at index 1 in [43, 51, 60], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 155. The final array is [43, 52, 60]. Add those three values.

EEE-2014B-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 43 → 51 → 60. Insert 44 after the head, then remove the original tail. What is the new tail value?
Answer: 51. After insertion the list is 43 → 44 → 51 → 60. Removing 60 leaves 51 at the tail.

EEE-2014B-M1-A, Q3 · Stacks (4 marks)
Push 43, then 51. Pop once, push 60, then pop again. What value remains on top?
Answer: 43. The pops remove 51 and 60, the most recently pushed items. The original bottom value 43 remains.

EEE-2014B-M1-A, Q4 · Queues (4 marks)
Enqueue 43, 51, and 60 in order. Dequeue twice, then enqueue 62. What is at the front?
Answer: 60. FIFO removes 43 and 51. Enqueuing 62 adds it behind 60.

EEE-2014B-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 43 and front index 41. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (43-2+3) mod 43 is 1.

## Data Structures Mid-1 mock paper EEE-2014B-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

EEE-2014B-M1-B, Q1 · Arrays (4 marks)
Insert 53 at index 1 in [44, 52, 61], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 158. The final array is [44, 53, 61]. Add those three values.

EEE-2014B-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 44 → 52 → 61. Insert 45 after the head, then remove the original tail. What is the new tail value?
Answer: 52. After insertion the list is 44 → 45 → 52 → 61. Removing 61 leaves 52 at the tail.

EEE-2014B-M1-B, Q3 · Stacks (4 marks)
Push 44, then 52. Pop once, push 61, then pop again. What value remains on top?
Answer: 44. The pops remove 52 and 61, the most recently pushed items. The original bottom value 44 remains.

EEE-2014B-M1-B, Q4 · Queues (4 marks)
Enqueue 44, 52, and 61 in order. Dequeue twice, then enqueue 63. What is at the front?
Answer: 61. FIFO removes 44 and 52. Enqueuing 63 adds it behind 61.

EEE-2014B-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 44 and front index 42. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (44-2+3) mod 44 is 1.

## Data Structures Mid-2 mock paper EEE-2014B-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

EEE-2014B-M2-A, Q1 · Binary search (4 marks)
An ascending array has 45 distinct values. Binary search targets the value at index 22. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

EEE-2014B-M2-A, Q2 · Binary search trees (4 marks)
Insert 53, 45, 62, and 54 into an empty binary search tree in order. What value is the left child of 62?
Answer: 54. 54 is larger than the root 53 and smaller than 62.

EEE-2014B-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 45, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 45?
Answer: 45. The only path visits 0, 1, …, 45. Each increment crosses one edge.

EEE-2014B-M2-A, Q4 · Hashing (4 marks)
A hash table has 45 slots. Using h(k) = k mod 45, which index does key 93 map to?
Answer: 3. 93 = 2 × 45 + 3, so the remainder is 3.

EEE-2014B-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 45 values?
Answer: 990. The passes make 44, 43, …, 1 comparisons. Sum them using 45 × 44 / 2.

## Data Structures Mid-1 mock paper EEE-2014J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

EEE-2014J-M1-A, Q1 · Arrays (4 marks)
Insert 55 at index 1 in [46, 54, 63], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 164. The final array is [46, 55, 63]. Add those three values.

EEE-2014J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 46 → 54 → 63. Insert 47 after the head, then remove the original tail. What is the new tail value?
Answer: 54. After insertion the list is 46 → 47 → 54 → 63. Removing 63 leaves 54 at the tail.

EEE-2014J-M1-A, Q3 · Stacks (4 marks)
Push 46, then 54. Pop once, push 63, then pop again. What value remains on top?
Answer: 46. The pops remove 54 and 63, the most recently pushed items. The original bottom value 46 remains.

EEE-2014J-M1-A, Q4 · Queues (4 marks)
Enqueue 46, 54, and 63 in order. Dequeue twice, then enqueue 65. What is at the front?
Answer: 63. FIFO removes 46 and 54. Enqueuing 65 adds it behind 63.

EEE-2014J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 46 and front index 44. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (46-2+3) mod 46 is 1.

## Data Structures Mid-1 mock paper EEE-2014J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

EEE-2014J-M1-B, Q1 · Arrays (4 marks)
Insert 56 at index 1 in [47, 55, 64], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 167. The final array is [47, 56, 64]. Add those three values.

EEE-2014J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 47 → 55 → 64. Insert 48 after the head, then remove the original tail. What is the new tail value?
Answer: 55. After insertion the list is 47 → 48 → 55 → 64. Removing 64 leaves 55 at the tail.

EEE-2014J-M1-B, Q3 · Stacks (4 marks)
Push 47, then 55. Pop once, push 64, then pop again. What value remains on top?
Answer: 47. The pops remove 55 and 64, the most recently pushed items. The original bottom value 47 remains.

EEE-2014J-M1-B, Q4 · Queues (4 marks)
Enqueue 47, 55, and 64 in order. Dequeue twice, then enqueue 66. What is at the front?
Answer: 64. FIFO removes 47 and 55. Enqueuing 66 adds it behind 64.

EEE-2014J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 47 and front index 45. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (47-2+3) mod 47 is 1.

## Data Structures Mid-2 mock paper EEE-2014J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

EEE-2014J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 48 distinct values. Binary search targets the value at index 23. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

EEE-2014J-M2-A, Q2 · Binary search trees (4 marks)
Insert 56, 48, 65, and 57 into an empty binary search tree in order. What value is the left child of 65?
Answer: 57. 57 is larger than the root 56 and smaller than 65.

EEE-2014J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 48, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 48?
Answer: 48. The only path visits 0, 1, …, 48. Each increment crosses one edge.

EEE-2014J-M2-A, Q4 · Hashing (4 marks)
A hash table has 48 slots. Using h(k) = k mod 48, which index does key 99 map to?
Answer: 3. 99 = 2 × 48 + 3, so the remainder is 3.

EEE-2014J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 48 values?
Answer: 1128. The passes make 47, 46, …, 1 comparisons. Sum them using 48 × 47 / 2.

## Data Structures Mid-1 mock paper FFF-2013B-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2013B-M1-A, Q1 · Arrays (4 marks)
Insert 58 at index 1 in [49, 57, 66], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 173. The final array is [49, 58, 66]. Add those three values.

FFF-2013B-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 49 → 57 → 66. Insert 50 after the head, then remove the original tail. What is the new tail value?
Answer: 57. After insertion the list is 49 → 50 → 57 → 66. Removing 66 leaves 57 at the tail.

FFF-2013B-M1-A, Q3 · Stacks (4 marks)
Push 49, then 57. Pop once, push 66, then pop again. What value remains on top?
Answer: 49. The pops remove 57 and 66, the most recently pushed items. The original bottom value 49 remains.

FFF-2013B-M1-A, Q4 · Queues (4 marks)
Enqueue 49, 57, and 66 in order. Dequeue twice, then enqueue 68. What is at the front?
Answer: 66. FIFO removes 49 and 57. Enqueuing 68 adds it behind 66.

FFF-2013B-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 49 and front index 47. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (49-2+3) mod 49 is 1.

## Data Structures Mid-1 mock paper FFF-2013B-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2013B-M1-B, Q1 · Arrays (4 marks)
Insert 59 at index 1 in [50, 58, 67], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 176. The final array is [50, 59, 67]. Add those three values.

FFF-2013B-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 50 → 58 → 67. Insert 51 after the head, then remove the original tail. What is the new tail value?
Answer: 58. After insertion the list is 50 → 51 → 58 → 67. Removing 67 leaves 58 at the tail.

FFF-2013B-M1-B, Q3 · Stacks (4 marks)
Push 50, then 58. Pop once, push 67, then pop again. What value remains on top?
Answer: 50. The pops remove 58 and 67, the most recently pushed items. The original bottom value 50 remains.

FFF-2013B-M1-B, Q4 · Queues (4 marks)
Enqueue 50, 58, and 67 in order. Dequeue twice, then enqueue 69. What is at the front?
Answer: 67. FIFO removes 50 and 58. Enqueuing 69 adds it behind 67.

FFF-2013B-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 50 and front index 48. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (50-2+3) mod 50 is 1.

## Data Structures Mid-2 mock paper FFF-2013B-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2013B-M2-A, Q1 · Binary search (4 marks)
An ascending array has 51 distinct values. Binary search targets the value at index 25. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

FFF-2013B-M2-A, Q2 · Binary search trees (4 marks)
Insert 59, 51, 68, and 60 into an empty binary search tree in order. What value is the left child of 68?
Answer: 60. 60 is larger than the root 59 and smaller than 68.

FFF-2013B-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 51, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 51?
Answer: 51. The only path visits 0, 1, …, 51. Each increment crosses one edge.

FFF-2013B-M2-A, Q4 · Hashing (4 marks)
A hash table has 51 slots. Using h(k) = k mod 51, which index does key 105 map to?
Answer: 3. 105 = 2 × 51 + 3, so the remainder is 3.

FFF-2013B-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 51 values?
Answer: 1275. The passes make 50, 49, …, 1 comparisons. Sum them using 51 × 50 / 2.

## Data Structures Mid-1 mock paper FFF-2013J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2013J-M1-A, Q1 · Arrays (4 marks)
Insert 61 at index 1 in [52, 60, 69], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 182. The final array is [52, 61, 69]. Add those three values.

FFF-2013J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 52 → 60 → 69. Insert 53 after the head, then remove the original tail. What is the new tail value?
Answer: 60. After insertion the list is 52 → 53 → 60 → 69. Removing 69 leaves 60 at the tail.

FFF-2013J-M1-A, Q3 · Stacks (4 marks)
Push 52, then 60. Pop once, push 69, then pop again. What value remains on top?
Answer: 52. The pops remove 60 and 69, the most recently pushed items. The original bottom value 52 remains.

FFF-2013J-M1-A, Q4 · Queues (4 marks)
Enqueue 52, 60, and 69 in order. Dequeue twice, then enqueue 71. What is at the front?
Answer: 69. FIFO removes 52 and 60. Enqueuing 71 adds it behind 69.

FFF-2013J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 52 and front index 50. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (52-2+3) mod 52 is 1.

## Data Structures Mid-1 mock paper FFF-2013J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2013J-M1-B, Q1 · Arrays (4 marks)
Insert 62 at index 1 in [53, 61, 70], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 185. The final array is [53, 62, 70]. Add those three values.

FFF-2013J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 53 → 61 → 70. Insert 54 after the head, then remove the original tail. What is the new tail value?
Answer: 61. After insertion the list is 53 → 54 → 61 → 70. Removing 70 leaves 61 at the tail.

FFF-2013J-M1-B, Q3 · Stacks (4 marks)
Push 53, then 61. Pop once, push 70, then pop again. What value remains on top?
Answer: 53. The pops remove 61 and 70, the most recently pushed items. The original bottom value 53 remains.

FFF-2013J-M1-B, Q4 · Queues (4 marks)
Enqueue 53, 61, and 70 in order. Dequeue twice, then enqueue 72. What is at the front?
Answer: 70. FIFO removes 53 and 61. Enqueuing 72 adds it behind 70.

FFF-2013J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 53 and front index 51. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (53-2+3) mod 53 is 1.

## Data Structures Mid-2 mock paper FFF-2013J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2013J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 54 distinct values. Binary search targets the value at index 26. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

FFF-2013J-M2-A, Q2 · Binary search trees (4 marks)
Insert 62, 54, 71, and 63 into an empty binary search tree in order. What value is the left child of 71?
Answer: 63. 63 is larger than the root 62 and smaller than 71.

FFF-2013J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 54, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 54?
Answer: 54. The only path visits 0, 1, …, 54. Each increment crosses one edge.

FFF-2013J-M2-A, Q4 · Hashing (4 marks)
A hash table has 54 slots. Using h(k) = k mod 54, which index does key 111 map to?
Answer: 3. 111 = 2 × 54 + 3, so the remainder is 3.

FFF-2013J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 54 values?
Answer: 1431. The passes make 53, 52, …, 1 comparisons. Sum them using 54 × 53 / 2.

## Data Structures Mid-1 mock paper FFF-2014B-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2014B-M1-A, Q1 · Arrays (4 marks)
Insert 64 at index 1 in [55, 63, 72], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 191. The final array is [55, 64, 72]. Add those three values.

FFF-2014B-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 55 → 63 → 72. Insert 56 after the head, then remove the original tail. What is the new tail value?
Answer: 63. After insertion the list is 55 → 56 → 63 → 72. Removing 72 leaves 63 at the tail.

FFF-2014B-M1-A, Q3 · Stacks (4 marks)
Push 55, then 63. Pop once, push 72, then pop again. What value remains on top?
Answer: 55. The pops remove 63 and 72, the most recently pushed items. The original bottom value 55 remains.

FFF-2014B-M1-A, Q4 · Queues (4 marks)
Enqueue 55, 63, and 72 in order. Dequeue twice, then enqueue 74. What is at the front?
Answer: 72. FIFO removes 55 and 63. Enqueuing 74 adds it behind 72.

FFF-2014B-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 55 and front index 53. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (55-2+3) mod 55 is 1.

## Data Structures Mid-1 mock paper FFF-2014B-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2014B-M1-B, Q1 · Arrays (4 marks)
Insert 65 at index 1 in [56, 64, 73], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 194. The final array is [56, 65, 73]. Add those three values.

FFF-2014B-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 56 → 64 → 73. Insert 57 after the head, then remove the original tail. What is the new tail value?
Answer: 64. After insertion the list is 56 → 57 → 64 → 73. Removing 73 leaves 64 at the tail.

FFF-2014B-M1-B, Q3 · Stacks (4 marks)
Push 56, then 64. Pop once, push 73, then pop again. What value remains on top?
Answer: 56. The pops remove 64 and 73, the most recently pushed items. The original bottom value 56 remains.

FFF-2014B-M1-B, Q4 · Queues (4 marks)
Enqueue 56, 64, and 73 in order. Dequeue twice, then enqueue 75. What is at the front?
Answer: 73. FIFO removes 56 and 64. Enqueuing 75 adds it behind 73.

FFF-2014B-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 56 and front index 54. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (56-2+3) mod 56 is 1.

## Data Structures Mid-2 mock paper FFF-2014B-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2014B-M2-A, Q1 · Binary search (4 marks)
An ascending array has 57 distinct values. Binary search targets the value at index 28. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

FFF-2014B-M2-A, Q2 · Binary search trees (4 marks)
Insert 65, 57, 74, and 66 into an empty binary search tree in order. What value is the left child of 74?
Answer: 66. 66 is larger than the root 65 and smaller than 74.

FFF-2014B-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 57, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 57?
Answer: 57. The only path visits 0, 1, …, 57. Each increment crosses one edge.

FFF-2014B-M2-A, Q4 · Hashing (4 marks)
A hash table has 57 slots. Using h(k) = k mod 57, which index does key 117 map to?
Answer: 3. 117 = 2 × 57 + 3, so the remainder is 3.

FFF-2014B-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 57 values?
Answer: 1596. The passes make 56, 55, …, 1 comparisons. Sum them using 57 × 56 / 2.

## Data Structures Mid-1 mock paper FFF-2014J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2014J-M1-A, Q1 · Arrays (4 marks)
Insert 67 at index 1 in [58, 66, 75], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 200. The final array is [58, 67, 75]. Add those three values.

FFF-2014J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 58 → 66 → 75. Insert 59 after the head, then remove the original tail. What is the new tail value?
Answer: 66. After insertion the list is 58 → 59 → 66 → 75. Removing 75 leaves 66 at the tail.

FFF-2014J-M1-A, Q3 · Stacks (4 marks)
Push 58, then 66. Pop once, push 75, then pop again. What value remains on top?
Answer: 58. The pops remove 66 and 75, the most recently pushed items. The original bottom value 58 remains.

FFF-2014J-M1-A, Q4 · Queues (4 marks)
Enqueue 58, 66, and 75 in order. Dequeue twice, then enqueue 77. What is at the front?
Answer: 75. FIFO removes 58 and 66. Enqueuing 77 adds it behind 75.

FFF-2014J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 58 and front index 56. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (58-2+3) mod 58 is 1.

## Data Structures Mid-1 mock paper FFF-2014J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2014J-M1-B, Q1 · Arrays (4 marks)
Insert 68 at index 1 in [59, 67, 76], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 203. The final array is [59, 68, 76]. Add those three values.

FFF-2014J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 59 → 67 → 76. Insert 60 after the head, then remove the original tail. What is the new tail value?
Answer: 67. After insertion the list is 59 → 60 → 67 → 76. Removing 76 leaves 67 at the tail.

FFF-2014J-M1-B, Q3 · Stacks (4 marks)
Push 59, then 67. Pop once, push 76, then pop again. What value remains on top?
Answer: 59. The pops remove 67 and 76, the most recently pushed items. The original bottom value 59 remains.

FFF-2014J-M1-B, Q4 · Queues (4 marks)
Enqueue 59, 67, and 76 in order. Dequeue twice, then enqueue 78. What is at the front?
Answer: 76. FIFO removes 59 and 67. Enqueuing 78 adds it behind 76.

FFF-2014J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 59 and front index 57. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (59-2+3) mod 59 is 1.

## Data Structures Mid-2 mock paper FFF-2014J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

FFF-2014J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 60 distinct values. Binary search targets the value at index 29. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

FFF-2014J-M2-A, Q2 · Binary search trees (4 marks)
Insert 68, 60, 77, and 69 into an empty binary search tree in order. What value is the left child of 77?
Answer: 69. 69 is larger than the root 68 and smaller than 77.

FFF-2014J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 60, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 60?
Answer: 60. The only path visits 0, 1, …, 60. Each increment crosses one edge.

FFF-2014J-M2-A, Q4 · Hashing (4 marks)
A hash table has 60 slots. Using h(k) = k mod 60, which index does key 123 map to?
Answer: 3. 123 = 2 × 60 + 3, so the remainder is 3.

FFF-2014J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 60 values?
Answer: 1770. The passes make 59, 58, …, 1 comparisons. Sum them using 60 × 59 / 2.

## Data Structures Mid-1 mock paper GGG-2013J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

GGG-2013J-M1-A, Q1 · Arrays (4 marks)
Insert 70 at index 1 in [61, 69, 78], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 209. The final array is [61, 70, 78]. Add those three values.

GGG-2013J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 61 → 69 → 78. Insert 62 after the head, then remove the original tail. What is the new tail value?
Answer: 69. After insertion the list is 61 → 62 → 69 → 78. Removing 78 leaves 69 at the tail.

GGG-2013J-M1-A, Q3 · Stacks (4 marks)
Push 61, then 69. Pop once, push 78, then pop again. What value remains on top?
Answer: 61. The pops remove 69 and 78, the most recently pushed items. The original bottom value 61 remains.

GGG-2013J-M1-A, Q4 · Queues (4 marks)
Enqueue 61, 69, and 78 in order. Dequeue twice, then enqueue 80. What is at the front?
Answer: 78. FIFO removes 61 and 69. Enqueuing 80 adds it behind 78.

GGG-2013J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 61 and front index 59. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (61-2+3) mod 61 is 1.

## Data Structures Mid-1 mock paper GGG-2013J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

GGG-2013J-M1-B, Q1 · Arrays (4 marks)
Insert 71 at index 1 in [62, 70, 79], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 212. The final array is [62, 71, 79]. Add those three values.

GGG-2013J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 62 → 70 → 79. Insert 63 after the head, then remove the original tail. What is the new tail value?
Answer: 70. After insertion the list is 62 → 63 → 70 → 79. Removing 79 leaves 70 at the tail.

GGG-2013J-M1-B, Q3 · Stacks (4 marks)
Push 62, then 70. Pop once, push 79, then pop again. What value remains on top?
Answer: 62. The pops remove 70 and 79, the most recently pushed items. The original bottom value 62 remains.

GGG-2013J-M1-B, Q4 · Queues (4 marks)
Enqueue 62, 70, and 79 in order. Dequeue twice, then enqueue 81. What is at the front?
Answer: 79. FIFO removes 62 and 70. Enqueuing 81 adds it behind 79.

GGG-2013J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 62 and front index 60. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (62-2+3) mod 62 is 1.

## Data Structures Mid-2 mock paper GGG-2013J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

GGG-2013J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 63 distinct values. Binary search targets the value at index 31. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

GGG-2013J-M2-A, Q2 · Binary search trees (4 marks)
Insert 71, 63, 80, and 72 into an empty binary search tree in order. What value is the left child of 80?
Answer: 72. 72 is larger than the root 71 and smaller than 80.

GGG-2013J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 63, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 63?
Answer: 63. The only path visits 0, 1, …, 63. Each increment crosses one edge.

GGG-2013J-M2-A, Q4 · Hashing (4 marks)
A hash table has 63 slots. Using h(k) = k mod 63, which index does key 129 map to?
Answer: 3. 129 = 2 × 63 + 3, so the remainder is 3.

GGG-2013J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 63 values?
Answer: 1953. The passes make 62, 61, …, 1 comparisons. Sum them using 63 × 62 / 2.

## Data Structures Mid-1 mock paper GGG-2014B-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

GGG-2014B-M1-A, Q1 · Arrays (4 marks)
Insert 73 at index 1 in [64, 72, 81], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 218. The final array is [64, 73, 81]. Add those three values.

GGG-2014B-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 64 → 72 → 81. Insert 65 after the head, then remove the original tail. What is the new tail value?
Answer: 72. After insertion the list is 64 → 65 → 72 → 81. Removing 81 leaves 72 at the tail.

GGG-2014B-M1-A, Q3 · Stacks (4 marks)
Push 64, then 72. Pop once, push 81, then pop again. What value remains on top?
Answer: 64. The pops remove 72 and 81, the most recently pushed items. The original bottom value 64 remains.

GGG-2014B-M1-A, Q4 · Queues (4 marks)
Enqueue 64, 72, and 81 in order. Dequeue twice, then enqueue 83. What is at the front?
Answer: 81. FIFO removes 64 and 72. Enqueuing 83 adds it behind 81.

GGG-2014B-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 64 and front index 62. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (64-2+3) mod 64 is 1.

## Data Structures Mid-1 mock paper GGG-2014B-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

GGG-2014B-M1-B, Q1 · Arrays (4 marks)
Insert 74 at index 1 in [65, 73, 82], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 221. The final array is [65, 74, 82]. Add those three values.

GGG-2014B-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 65 → 73 → 82. Insert 66 after the head, then remove the original tail. What is the new tail value?
Answer: 73. After insertion the list is 65 → 66 → 73 → 82. Removing 82 leaves 73 at the tail.

GGG-2014B-M1-B, Q3 · Stacks (4 marks)
Push 65, then 73. Pop once, push 82, then pop again. What value remains on top?
Answer: 65. The pops remove 73 and 82, the most recently pushed items. The original bottom value 65 remains.

GGG-2014B-M1-B, Q4 · Queues (4 marks)
Enqueue 65, 73, and 82 in order. Dequeue twice, then enqueue 84. What is at the front?
Answer: 82. FIFO removes 65 and 73. Enqueuing 84 adds it behind 82.

GGG-2014B-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 65 and front index 63. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (65-2+3) mod 65 is 1.

## Data Structures Mid-2 mock paper GGG-2014B-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

GGG-2014B-M2-A, Q1 · Binary search (4 marks)
An ascending array has 66 distinct values. Binary search targets the value at index 32. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

GGG-2014B-M2-A, Q2 · Binary search trees (4 marks)
Insert 74, 66, 83, and 75 into an empty binary search tree in order. What value is the left child of 83?
Answer: 75. 75 is larger than the root 74 and smaller than 83.

GGG-2014B-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 66, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 66?
Answer: 66. The only path visits 0, 1, …, 66. Each increment crosses one edge.

GGG-2014B-M2-A, Q4 · Hashing (4 marks)
A hash table has 66 slots. Using h(k) = k mod 66, which index does key 135 map to?
Answer: 3. 135 = 2 × 66 + 3, so the remainder is 3.

GGG-2014B-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 66 values?
Answer: 2145. The passes make 65, 64, …, 1 comparisons. Sum them using 66 × 65 / 2.

## Data Structures Mid-1 mock paper GGG-2014J-M1-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

GGG-2014J-M1-A, Q1 · Arrays (4 marks)
Insert 76 at index 1 in [67, 75, 84], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 227. The final array is [67, 76, 84]. Add those three values.

GGG-2014J-M1-A, Q2 · Linked lists (4 marks)
A linked list contains 67 → 75 → 84. Insert 68 after the head, then remove the original tail. What is the new tail value?
Answer: 75. After insertion the list is 67 → 68 → 75 → 84. Removing 84 leaves 75 at the tail.

GGG-2014J-M1-A, Q3 · Stacks (4 marks)
Push 67, then 75. Pop once, push 84, then pop again. What value remains on top?
Answer: 67. The pops remove 75 and 84, the most recently pushed items. The original bottom value 67 remains.

GGG-2014J-M1-A, Q4 · Queues (4 marks)
Enqueue 67, 75, and 84 in order. Dequeue twice, then enqueue 86. What is at the front?
Answer: 84. FIFO removes 67 and 75. Enqueuing 86 adds it behind 84.

GGG-2014J-M1-A, Q5 · Circular queues (4 marks)
A circular queue has capacity 67 and front index 65. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (67-2+3) mod 67 is 1.

## Data Structures Mid-1 mock paper GGG-2014J-M1-B
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

GGG-2014J-M1-B, Q1 · Arrays (4 marks)
Insert 77 at index 1 in [68, 76, 85], then delete the element at index 2. Using zero-based indices, what is the final sum?
Answer: 230. The final array is [68, 77, 85]. Add those three values.

GGG-2014J-M1-B, Q2 · Linked lists (4 marks)
A linked list contains 68 → 76 → 85. Insert 69 after the head, then remove the original tail. What is the new tail value?
Answer: 76. After insertion the list is 68 → 69 → 76 → 85. Removing 85 leaves 76 at the tail.

GGG-2014J-M1-B, Q3 · Stacks (4 marks)
Push 68, then 76. Pop once, push 85, then pop again. What value remains on top?
Answer: 68. The pops remove 76 and 85, the most recently pushed items. The original bottom value 68 remains.

GGG-2014J-M1-B, Q4 · Queues (4 marks)
Enqueue 68, 76, and 85 in order. Dequeue twice, then enqueue 87. What is at the front?
Answer: 85. FIFO removes 68 and 76. Enqueuing 87 adds it behind 85.

GGG-2014J-M1-B, Q5 · Circular queues (4 marks)
A circular queue has capacity 68 and front index 66. After three successful dequeues, what is the zero-based front index?
Answer: 1. The front advances modulo capacity. (68-2+3) mod 68 is 1.

## Data Structures Mid-2 mock paper GGG-2014J-M2-A
Original mock paper for practice. The cohort code is a demo label.
20 marks · 5 questions

GGG-2014J-M2-A, Q1 · Binary search (4 marks)
An ascending array has 69 distinct values. Binary search targets the value at index 34. Using the lower midpoint, how many midpoint probes are needed?
Answer: 1. The first probe visits the lower midpoint, which is the target.

GGG-2014J-M2-A, Q2 · Binary search trees (4 marks)
Insert 77, 69, 86, and 78 into an empty binary search tree in order. What value is the left child of 86?
Answer: 78. 78 is larger than the root 77 and smaller than 86.

GGG-2014J-M2-A, Q3 · Graph traversal (4 marks)
A graph is a path from vertex 0 to vertex 69, with consecutive vertices adjacent. How many edges are in the BFS shortest path from 0 to 69?
Answer: 69. The only path visits 0, 1, …, 69. Each increment crosses one edge.

GGG-2014J-M2-A, Q4 · Hashing (4 marks)
A hash table has 69 slots. Using h(k) = k mod 69, which index does key 141 map to?
Answer: 3. 141 = 2 × 69 + 3, so the remainder is 3.

GGG-2014J-M2-A, Q5 · Sorting (4 marks)
How many pairwise comparisons does standard selection sort make when sorting 69 values?
Answer: 2346. The passes make 68, 67, …, 1 comparisons. Sum them using 69 × 68 / 2.
