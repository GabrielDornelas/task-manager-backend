#!/bin/bash

# Carregar variáveis de ambiente
set -a
source .env
set +a

# Limpar base de teste
docker-compose exec mongo mongosh test_db --eval "db.dropDatabase()"

# Executar testes com cobertura
docker-compose run --rm web pytest -v --cov=flaskr tests/ 