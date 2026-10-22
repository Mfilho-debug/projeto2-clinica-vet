# Especificação – Clínica Veterinária (Projeto 2 · 5J11)

**Grupo:** <nomes dos integrantes>  **Domínio:** gestão de clínica veterinária

## 1. Problema
Pequenas clínicas veterinárias controlam tutores e pets em planilhas e papel: dados duplicados,
difícil achar o histórico de um animal e nenhum lugar para guardar exames (PDF/imagem).

## 2. Personas
- **Recepcionista (Ana):** cadastra tutores e pets, precisa de agilidade e dados corretos.
- **Veterinário (Dr. Paulo):** consulta o pet e anexa exames/fotos.
- **Gerente (Carla):** quer relatórios (quantos pets por tutor/espécie, exames por período).

## 3. Histórias de usuário e critérios de aceite
| ID | História | Critérios de aceite |
|----|----------|---------------------|
| US-01 | Como recepcionista, quero cadastrar um tutor | Nome e e-mail obrigatórios; e-mail duplicado retorna 409; tutor aparece na listagem |
| US-02 | Como recepcionista, quero editar/excluir um tutor | PUT atualiza e retorna o registro; DELETE retorna 204; inexistente retorna 404; pets do tutor são removidos junto (cascade) |
| US-03 | Como recepcionista, quero cadastrar um pet vinculado a um tutor | Nome, espécie e tutor_id obrigatórios; tutor inexistente retorna 409; listagem mostra o nome do tutor |
| US-04 | Como recepcionista, quero editar/excluir um pet | Mesmos critérios de US-02 para pets |
| US-05 | Como veterinário, quero anexar exame (PDF/imagem) a um pet | Upload via URL pré-assinada; arquivo fica no S3; registro em `arquivos` ligado ao pet (RF-02) |
| US-06 | Como veterinário, quero que o sistema extraia metadados do arquivo enviado | Ao chegar no S3, Lambda grava tipo e tamanho no RDS (RF-03) |
| US-07 | Como gerente, quero um relatório de pets por tutor/espécie | `GET /relatorios/pets-por-tutor` retorna contagem com JOIN/GROUP BY (RF-04) |

## 4. Como cada requisito se aplica ao domínio
- **RF-01:** CRUD de `tutores` e `pets` (1:N) no RDS MySQL.
- **RF-02:** upload de exame (PDF/imagem) de um pet para o S3 via URL pré-assinada gerada pelo backend.
- **RF-03:** evento S3 `ObjectCreated` → Lambda lê tipo/tamanho do objeto e grava em `arquivos`.
- **RF-04:** relatório "quantidade de pets e exames por tutor" (JOIN + GROUP BY) em Lambda via API Gateway.
- **RF-05:** front-end web (HTML/JS) consumindo a API.
- **RNF-01..05:** ver `specs/design.md` e `README.md`.
