-- Schema da clínica veterinária (MySQL 8). Reexecutável.
CREATE DATABASE IF NOT EXISTS clinica CHARACTER SET utf8mb4;
USE clinica;

CREATE TABLE IF NOT EXISTS tutores (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  nome      VARCHAR(120) NOT NULL,
  email     VARCHAR(120) NOT NULL UNIQUE,
  telefone  VARCHAR(20),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pets (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  tutor_id        INT NOT NULL,
  nome            VARCHAR(80) NOT NULL,
  especie         VARCHAR(40) NOT NULL,
  raca            VARCHAR(60),
  data_nascimento DATE,
  criado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_pet_tutor FOREIGN KEY (tutor_id)
    REFERENCES tutores(id) ON DELETE CASCADE
);

-- (RF-02/RF-03, próximas entregas) arquivos ligados ao pet
CREATE TABLE IF NOT EXISTS arquivos (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  pet_id    INT NOT NULL,
  s3_key    VARCHAR(255) NOT NULL,
  tipo      VARCHAR(60),
  tamanho   BIGINT,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_arq_pet FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
);
