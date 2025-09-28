CREATE DATABASE IF NOT EXISTS desarrollo_web;
USE desarrollo_web;
--Crear tabla de usuarios

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    edad INT NOT NULL,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Crear tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL
);
