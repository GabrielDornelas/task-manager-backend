#!/bin/bash

# Carregar variáveis de ambiente
set -a
source .env
set +a

# Parar containers existentes
docker-compose down

# Construir e iniciar os containers
docker-compose up --build 