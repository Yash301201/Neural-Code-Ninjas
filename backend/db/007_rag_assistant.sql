-- Additive migration. Run on the application's configured MySQL database.
CREATE TABLE IF NOT EXISTS rag_chunks (
 chunk_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
 source_key VARCHAR(180) NOT NULL,
 title VARCHAR(250) NOT NULL,
 content TEXT NOT NULL,
 source_url VARCHAR(500) NULL,
 source_kind VARCHAR(30) NOT NULL,
 cohort VARCHAR(20) NULL,
 content_sha256 CHAR(64) NOT NULL,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE KEY uq_rag_source(source_key), KEY ix_rag_cohort(cohort)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS rag_conversations (
 conversation_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
 user_id BIGINT NOT NULL,
 title VARCHAR(120) NOT NULL,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_rag_owner FOREIGN KEY(user_id) REFERENCES users(user_id),
 KEY ix_rag_owner(user_id,conversation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS rag_messages (
 message_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
 conversation_id BIGINT NOT NULL,
 question TEXT NOT NULL,
 answer TEXT NOT NULL,
 citations JSON NOT NULL,
 answer_mode VARCHAR(30) NOT NULL,
 model_name VARCHAR(120) NULL,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_rag_conversation FOREIGN KEY(conversation_id) REFERENCES rag_conversations(conversation_id),
 KEY ix_rag_history(conversation_id,message_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
