#!/bin/bash
set -e

echo "🚀 Iniciando deploy no Ubuntu..."

# Atualizando repositório
git pull origin main

# Construindo e subindo os containers (rebuild)
docker compose up -d --build

# Removendo imagens órfãs
docker image prune -f

# Ajuste permissões para que o Docker acesse perfeitamente os volumes caso criado em root
sudo chown -R 1000:1000 execucoes/ evid_provas.db || true

echo "✅ Deploy concluído com sucesso!"
docker compose ps
