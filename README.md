# Projeto 2 – Clínica Veterinária na AWS (Learner Lab)

Grupo: <nomes> · Turma 5J11 · Domínio: clínica veterinária (Tutores 1:N Pets)

## Onde está cada coisa
| Item | Caminho |
|---|---|
| Especificação | `specs/spec.md` |
| Design (arquitetura, ER, rotas, SGs, ADRs) | `specs/design.md` |
| Tarefas | `specs/tasks.md` |
| Log de IA | `docs/ia-log.md` |
| Scripts SQL | `db/schema.sql`, `db/seed.sql` |
| API + página do CRUD | `backend/` |
| Script de deploy na EC2 | `deploy/setup_ec2.sh` |
| Evidências | `docs/evidencias/` |

## Como criar a infraestrutura (console AWS, região us-east-1) — sem IaC
> Nenhum IP fixo no código. A cada nova sessão do Learner Lab o IP público da EC2 muda: use o novo IP/DNS.

### 1. VPC (assistente "VPC and more")
- Name: `vet`; IPv4 CIDR `10.0.0.0/16`
- **2 AZs**, **2 subnets públicas**, **2 subnets privadas**
- **NAT gateways: None** (custa caro) · **VPC endpoints: S3 Gateway**
- DNS hostnames/resolution: habilitados → *Create VPC*.

### 2. Security Groups (na VPC `vet`)
| Nome | Inbound |
|---|---|
| `sg-api` | HTTP 80 de `0.0.0.0/0`; SSH 22 de `0.0.0.0/0` (para EC2 Instance Connect) |
| `sg-rds` | MySQL/Aurora 3306 com origem **`sg-api`** (selecione o SG, não um IP) |

### 3. RDS
- RDS → *Create database* → **Standard create** → **MySQL 8**, template **Free tier/Dev**
- Identifier `vet-db`; Master `admin` + senha (anote, **não commitar**)
- Instance `db.t3.micro`; storage 20 GB; sem Multi-AZ
- Connectivity: VPC `vet`; **Public access = No**; SG = `sg-rds`
- *Additional configuration*: DB Subnet Group criado com as **2 subnets privadas**; deixe *Initial database name* vazio (o schema cria `clinica`); desative backups automáticos/monitoramento extra para economizar.
- Quando ficar *Available*, copie o **Endpoint**.

### 4. EC2 (API + página)
- Amazon Linux 2023, `t3.micro`, key pair `vockey` (ou use EC2 Instance Connect pelo navegador)
- Network: VPC `vet`, **subnet pública**, **Auto-assign public IP: Enable**, SG `sg-api`
- Advanced → **IAM instance profile: `LabInstanceProfile`**

### 5. Colocar o código na EC2
Conecte via *EC2 → Connect → EC2 Instance Connect*. Escolha uma opção:

**A) Repositório público no GitHub (a EC2 acessa o GitHub mesmo que sua rede de trabalho não acesse):**
```bash
sudo dnf install -y git
sudo git clone https://github.com/<usuario>/<repo>.git /opt/app
```
**B) Repositório privado: envie um ZIP pelo S3**
```bash
# pelo console S3: crie um bucket e faça upload do projeto.zip; depois na EC2:
sudo dnf install -y unzip
aws s3 cp s3://<seu-bucket>/projeto.zip /tmp/projeto.zip
sudo mkdir -p /opt/app && sudo unzip /tmp/projeto.zip -d /opt/app   # ajuste se criar subpasta
```

### 6. Banco de dados
```bash
sudo dnf install -y mariadb105
mysql -h <ENDPOINT_RDS> -u admin -p < /opt/app/db/schema.sql
mysql -h <ENDPOINT_RDS> -u admin -p < /opt/app/db/seed.sql    # opcional
```

### 7. Configurar segredos (fora do git) e subir a API
```bash
sudo tee /opt/app/.env > /dev/null <<'ENV'
DB_HOST=<ENDPOINT_RDS>
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=<SENHA>
DB_NAME=clinica
ENV
sudo chmod 600 /opt/app/.env
sudo bash /opt/app/deploy/setup_ec2.sh
```

### 8. Testar
- Navegador: `http://<IP_PUBLICO_EC2>/` (página do CRUD)
- `curl http://<IP_PUBLICO_EC2>/health` → `{"status":"ok","db":"ok"}`
- API: `curl http://<IP>/api/tutores`
- Prova de persistência: `mysql -h <ENDPOINT_RDS> -u admin -p -e "SELECT * FROM clinica.pets"`

## Nova sessão do Learner Lab (RNF-03)
1. Start Lab; confira se RDS e EC2 estão *running* (o RDS pode ser parado automaticamente; inicie-o).
2. Pegue o **novo IP público** da EC2 e acesse `http://<IP>/`.
3. O endpoint do RDS não muda; se a API estiver parada: `sudo systemctl restart vet-api`.
Se os recursos tiverem sido apagados, refaça os passos 1–8.

## Segurança
- RDS em subnet privada, *Public access = No*, entrada 3306 somente do `sg-api`.
- Credenciais só em `/opt/app/.env` na EC2 (no `.gitignore`).
