USE clinica;
INSERT IGNORE INTO tutores (id, nome, email, telefone) VALUES
 (1,'Maria Silva','maria@example.com','11999990001'),
 (2,'João Souza','joao@example.com','11999990002');
INSERT IGNORE INTO pets (id, tutor_id, nome, especie, raca, data_nascimento) VALUES
 (1,1,'Rex','Cachorro','Labrador','2020-05-10'),
 (2,1,'Mia','Gato','SRD','2022-01-20'),
 (3,2,'Thor','Cachorro','Bulldog','2019-09-03');
