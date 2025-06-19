#!/bin/bash

# Para o script se houver um erro
set -e

echo "--- Iniciando o script de build ---"

# 1. Instala as dependências do Python
echo "Instalando dependências do requirements.txt..."
pip install -r requirements.txt

# 2. Executa o script de preparação de dados para criar o GeoJSON
echo "Executando main.py para gerar os arquivos de dados..."
python3 main.py

echo "--- Script de build concluído com sucesso! ---"
