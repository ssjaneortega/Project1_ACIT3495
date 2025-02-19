CREATE DATABASE IF NOT EXISTS data_collection;
USE data_collection;

CREATE TABLE IF NOT EXISTS entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_input INT NOT NULL
);
