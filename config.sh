#!/bin/bash

# Execute este script uma vez com: ./setup.sh
set -e

echo "--- Criando ambiente virtual Python na pasta 'venv' ---"
python3 -m venv venv

echo ""
echo "--- Instalando pacotes do requirements.txt no ambiente virtual ---"
# Ativa o venv para o processo de instalação dentro deste script
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo ""
echo "--- Setup concluído! ---"
echo "Para executar o projeto, use o script 'run.sh'."
