#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para exibir mensagens de erro e sair
error_exit() {
    echo -e "${RED}Erro: $1${NC}" >&2
    exit 1
}

# Função para verificar dependências
check_dependencies() {
    echo -e "${YELLOW}Verificando dependências...${NC}"
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        error_exit "Docker não está instalado"
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error_exit "Docker Compose não está instalado"
    fi
    
    echo -e "${GREEN}✓ Todas as dependências estão instaladas${NC}"
}

# Função para verificar e criar arquivo .env
check_env_file() {
    echo -e "${YELLOW}Verificando arquivo .env...${NC}"
    
    if [ ! -f .env ]; then
        if [ ! -f .env.example ]; then
            error_exit "Arquivo .env.example não encontrado"
        fi
        
        echo -e "${YELLOW}Arquivo .env não encontrado. Criando a partir do .env.example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Por favor, edite o arquivo .env com suas configurações antes de continuar${NC}"
        exit 1
    fi
    
    # Verificar variáveis obrigatórias
    required_vars=("SECRET_KEY" "MONGO_URI" "REDIS_URL" "MAIL_USERNAME" "MAIL_PASSWORD")
    missing_vars=()
    
    while IFS= read -r line; do
        if [[ $line =~ ^[^#]*= ]]; then
            var_name=$(echo "$line" | cut -d'=' -f1)
            var_value=$(echo "$line" | cut -d'=' -f2)
            if [[ " ${required_vars[@]} " =~ " ${var_name} " ]] && [[ -z "$var_value" ]]; then
                missing_vars+=("$var_name")
            fi
        fi
    done < .env
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo -e "${RED}As seguintes variáveis obrigatórias não estão configuradas:${NC}"
        printf '%s\n' "${missing_vars[@]}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Arquivo .env está configurado corretamente${NC}"
}

# Função para construir imagens Docker
build_images() {
    echo -e "${YELLOW}Construindo imagens Docker...${NC}"
    
    # Parar containers existentes
    docker-compose down
    
    # Construir imagens
    docker-compose build --no-cache || error_exit "Falha ao construir imagens Docker"
    
    echo -e "${GREEN}✓ Imagens Docker construídas com sucesso${NC}"
}

# Função para iniciar aplicação
start_application() {
    echo -e "${YELLOW}Iniciando aplicação...${NC}"
    
    # Iniciar containers
    docker-compose up -d || error_exit "Falha ao iniciar containers"
    
    echo -e "${GREEN}✓ Aplicação iniciada com sucesso${NC}"
    echo -e "${GREEN}A API está disponível em: http://localhost:5000${NC}"
    echo -e "${GREEN}Documentação Swagger: http://localhost:5000/api/docs${NC}"
}

# Execução principal
main() {
    echo -e "${YELLOW}Iniciando processo de build...${NC}"
    
    check_dependencies
    check_env_file
    build_images
    start_application
    
    echo -e "${GREEN}✓ Processo de build concluído com sucesso!${NC}"
}

# Executar script
main
