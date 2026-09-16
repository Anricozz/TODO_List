#.sql文件用于建表，但是主程序不会主动调用该文件，需主动执行该文件。
#若使用该方式建表，需手动输入指令mysql -u root -p < schema.sql 或docker自动执行
#本项目main中写有create_all ，可以不执行.sql文件

CREATE DATABASE IF NOT EXISTS todo_list
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE todo_list;

CREATE TABLE IF NOT EXISTS todos (
    id BIGINT NOT NULL AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB;
