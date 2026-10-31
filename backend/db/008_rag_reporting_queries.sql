-- Read-only evaluator queries. Choose the configured learnpath_ai database first.
SELECT source_kind, COUNT(*) AS chunks FROM rag_chunks GROUP BY source_kind;
SELECT source_key, title, cohort, content_sha256 FROM rag_chunks ORDER BY chunk_id LIMIT 20;
SELECT conversation_id, user_id, title, created_at FROM rag_conversations ORDER BY conversation_id DESC LIMIT 20;
SELECT message_id, conversation_id, question, answer_mode, model_name, created_at FROM rag_messages ORDER BY message_id DESC LIMIT 20;
SELECT message_id, question, answer, citations FROM rag_messages ORDER BY message_id DESC LIMIT 5;
