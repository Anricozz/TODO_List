#.sql文件用于建表，但是主程序不会主动调用该文件，需主动执行该文件。
#若使用该方式建表，需手动输入指令mysql -u root -p < schema.sql 或docker自动执行
#本项目main中写有create_all ，可以不执行.sql文件
#注意：v0.2 起 todos 依赖 users，脚本会先 DROP 旧表，旧数据会丢失

CREATE DATABASE IF NOT EXISTS TODO_List_DB
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE TODO_List_DB;

#删表顺序：先删子表 todos，再删父表 users
DROP TABLE IF EXISTS todos;
DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS todos (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY ix_todos_user_id (user_id),
    CONSTRAINT fk_todos_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB;
