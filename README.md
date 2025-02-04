# Task Manager API

API RESTful para gerenciamento de tarefas com autenticação JWT, desenvolvida com Flask, MongoDB e Redis.

## 🚀 Funcionalidades

- Autenticação de usuários com JWT
- Gerenciamento de tarefas (CRUD)
- Reset de senha via email
- Cache com Redis
- Métricas do sistema
- Documentação Swagger

## 🛠️ Tecnologias

- Python 3.11
- Flask (Framework Web)
- MongoDB (Banco de dados)
- Redis (Cache e JWT)
- Docker & Docker Compose
- JWT para autenticação
- Flask-Mail para emails

## 📋 Pré-requisitos

- Docker
- Docker Compose
- Make (opcional)

## 🔧 Instalação

1. Clone o repositório:

git clone https://github.com/GabrielDornelas/task-manager-backend.git
cd task-manager-backend

2. Configure as variáveis de ambiente:

cp .env.example .env

3. Execute o script de build:

chmod +x build.sh

./build.sh

## 🚀 Uso

### Endpoints Principais

#### Autenticação

- `POST /auth/register` - Registro de usuário
- `POST /auth/login` - Login (retorna JWT)
- `POST /auth/logout` - Logout (invalida JWT)
- `POST /auth/reset-password` - Solicita reset de senha
- `POST /auth/reset-password/<token>` - Efetua reset de senha

#### Tarefas

- `GET /task` - Lista todas as tarefas do usuário
- `POST /task` - Cria nova tarefa
- `GET /task/<id>` - Obtém detalhes de uma tarefa
- `PUT /task/<id>` - Atualiza uma tarefa
- `DELETE /task/<id>` - Remove uma tarefa

#### Sistema

- `GET /metrics` - Métricas do sistema
- `GET /health` - Status da API
- `GET /api/docs` - Documentação Swagger

### Exemplos de Uso

#### Registro de Usuário

curl -X POST http://localhost:5000/auth/register \
-H "Content-Type: application/json" \
-d '{"username":"user1","password":"pass123","email":"user@example.com"}'

#### Login

curl -X POST http://localhost:5000/auth/login \
-H "Content-Type: application/json" \
-d '{"username":"user1","password":"pass123"}'

#### Criar Tarefa

curl -X POST http://localhost:5000/task \
-H "Authorization: Bearer <seu-token>" \
-H "Content-Type: application/json" \
-d '{"title":"Nova Tarefa","description":"Descrição","status":"pending"}'

## 🔍 Testes

Execute os testes com:

docker-compose exec app python -m pytest tests/ -v

## 📦 Estrutura do Projeto

task-manager-backend/
├── flaskr/ # Código fonte
│ ├── controllers/ # Controladores
│ ├── models/ # Modelos
│ ├── routes/ # Rotas
│ ├── infra/ # Infraestrutura (DB, Redis, etc)
│ └── init.py # Inicialização do app
├── tests/ # Testes
├── docker/ # Arquivos Docker
├── .env.example # Template de variáveis de ambiente
├── build.sh # Script de build
└── docker-compose.yml # Configuração Docker Compose

## 🔐 Variáveis de Ambiente

Veja `.env.example` para todas as variáveis necessárias e suas descrições.

Variáveis obrigatórias:

- `SECRET_KEY`: Chave secreta para JWT
- `MONGO_URI`: URI de conexão com MongoDB
- `REDIS_URL`: URI de conexão com Redis
- `MAIL_USERNAME`: Email para envio
- `MAIL_PASSWORD`: Senha do email

## 📈 Métricas

O endpoint `/metrics` fornece:

- Número de usuários ativos
- Tasks por status
- Tempo médio de resposta
- Taxa de erros

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
