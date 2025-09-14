CREATE DATABASE IF NOT EXISTS desarrollo_web;
USE desarrollo_web;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    edad INT NOT NULL,
    email VARCHAR(100)
);