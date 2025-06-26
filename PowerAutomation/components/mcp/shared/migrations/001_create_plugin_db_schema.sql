-- PluginDB Schema Migration Script
-- Version: 001
-- Description: 創建插件數據庫的基礎表結構
-- Created: 2025-06-26

-- 代碼項目表
CREATE TABLE IF NOT EXISTS code_projects (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    language VARCHAR(50),
    git_branch VARCHAR(255),
    git_commit_hash VARCHAR(255),
    git_remote_url TEXT,
    project_root TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_name (name),
    INDEX idx_language (language)
);

-- 代碼文件表
CREATE TABLE IF NOT EXISTS code_files (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255),
    file_path TEXT NOT NULL,
    content_hash VARCHAR(255) NOT NULL,
    file_size INTEGER DEFAULT 0,
    last_modified TIMESTAMP,
    status VARCHAR(20) DEFAULT 'unchanged',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES code_projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_content_hash (content_hash),
    INDEX idx_status (status),
    INDEX idx_file_path (file_path(255))
);

-- 代碼文件內容表（去重存儲）
CREATE TABLE IF NOT EXISTS code_file_contents (
    content_hash VARCHAR(255) PRIMARY KEY,
    content LONGTEXT NOT NULL,
    content_size INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_content_size (content_size)
);

-- 同步會話表
CREATE TABLE IF NOT EXISTS sync_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    project_id VARCHAR(255),
    sync_type VARCHAR(20) NOT NULL DEFAULT 'incremental',
    files_count INTEGER DEFAULT 0,
    files_added INTEGER DEFAULT 0,
    files_modified INTEGER DEFAULT 0,
    files_deleted INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES code_projects(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_project_id (project_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 用戶請求與代碼上下文關聯表
CREATE TABLE IF NOT EXISTS user_request_contexts (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    request_id VARCHAR(255) NOT NULL,
    project_id VARCHAR(255),
    sync_session_id VARCHAR(255),
    context_type VARCHAR(50) DEFAULT 'code_sync',
    context_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES code_projects(id) ON DELETE SET NULL,
    FOREIGN KEY (sync_session_id) REFERENCES sync_sessions(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_request_id (request_id),
    INDEX idx_project_id (project_id),
    INDEX idx_context_type (context_type)
);

-- 代碼搜索索引表（用於快速搜索）
CREATE TABLE IF NOT EXISTS code_search_index (
    id VARCHAR(255) PRIMARY KEY,
    file_id VARCHAR(255),
    project_id VARCHAR(255),
    keywords TEXT,
    content_snippet TEXT,
    relevance_score DECIMAL(5,4) DEFAULT 0.0000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES code_files(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES code_projects(id) ON DELETE CASCADE,
    INDEX idx_file_id (file_id),
    INDEX idx_project_id (project_id),
    INDEX idx_relevance_score (relevance_score),
    FULLTEXT idx_keywords (keywords),
    FULLTEXT idx_content_snippet (content_snippet)
);

-- 插件配置表
CREATE TABLE IF NOT EXISTS plugin_configurations (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    config_key VARCHAR(255) NOT NULL,
    config_value JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_config (user_id, config_key),
    INDEX idx_user_id (user_id),
    INDEX idx_config_key (config_key)
);

-- 創建視圖：項目統計
CREATE VIEW IF NOT EXISTS project_statistics AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    p.user_id,
    COUNT(f.id) as total_files,
    SUM(f.file_size) as total_size,
    MAX(f.last_modified) as last_file_modified,
    COUNT(DISTINCT f.status) as status_types,
    p.created_at as project_created,
    p.updated_at as project_updated
FROM code_projects p
LEFT JOIN code_files f ON p.id = f.project_id
GROUP BY p.id, p.name, p.user_id, p.created_at, p.updated_at;

-- 創建視圖：用戶活動統計
CREATE VIEW IF NOT EXISTS user_activity_statistics AS
SELECT 
    user_id,
    COUNT(DISTINCT project_id) as total_projects,
    COUNT(*) as total_sync_sessions,
    SUM(files_count) as total_files_synced,
    MAX(created_at) as last_activity,
    AVG(TIMESTAMPDIFF(SECOND, created_at, completed_at)) as avg_sync_duration
FROM sync_sessions
WHERE status = 'completed'
GROUP BY user_id;

-- 插入初始配置數據
INSERT IGNORE INTO plugin_configurations (id, user_id, config_key, config_value) VALUES
('default_sync_config', 'system', 'default_sync_settings', JSON_OBJECT(
    'max_file_size', 10485760,
    'excluded_extensions', JSON_ARRAY('.log', '.tmp', '.cache'),
    'auto_sync_interval', 300,
    'compression_enabled', true
)),
('default_search_config', 'system', 'default_search_settings', JSON_OBJECT(
    'max_results', 50,
    'relevance_threshold', 0.3,
    'include_content_snippet', true,
    'snippet_length', 200
));

-- 創建觸發器：自動更新 updated_at 字段
DELIMITER $$

CREATE TRIGGER IF NOT EXISTS update_code_projects_timestamp
    BEFORE UPDATE ON code_projects
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER IF NOT EXISTS update_code_files_timestamp
    BEFORE UPDATE ON code_files
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER IF NOT EXISTS update_plugin_configurations_timestamp
    BEFORE UPDATE ON plugin_configurations
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

DELIMITER ;

-- 創建存儲過程：清理舊數據
DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS CleanupOldSyncSessions(IN days_to_keep INT)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE session_id VARCHAR(255);
    DECLARE cur CURSOR FOR 
        SELECT id FROM sync_sessions 
        WHERE created_at < DATE_SUB(NOW(), INTERVAL days_to_keep DAY)
        AND status IN ('completed', 'failed');
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO session_id;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        DELETE FROM sync_sessions WHERE id = session_id;
    END LOOP;
    CLOSE cur;
END$$

DELIMITER ;

-- 創建索引優化查詢性能
CREATE INDEX IF NOT EXISTS idx_code_files_composite ON code_files(project_id, status, last_modified);
CREATE INDEX IF NOT EXISTS idx_sync_sessions_composite ON sync_sessions(user_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_user_request_contexts_composite ON user_request_contexts(user_id, context_type, created_at);

-- 完成遷移
-- 記錄遷移版本（如果有版本管理表的話）
-- INSERT INTO schema_migrations (version, applied_at) VALUES ('001', NOW());

