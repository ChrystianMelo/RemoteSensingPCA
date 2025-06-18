# PCA para Análise de Imagens de Satélite

Este projeto implementa a Análise de Componentes Principais (PCA) do zero para o realce de feições geográficas em imagens de satélite multiespectrais. A metodologia é fundamentada em conceitos da Álgebra Linear Numérica conforme apresentados no livro *Fundamentals of Matrix Computations* de David S. Watkins.

## 🎯 Objetivos

- Aplicar PCA em bandas espectrais de imagens Landsat/Sentinel.
- Realçar feições como vegetação, água e áreas urbanas.
- Implementar a PCA utilizando autovalores/autovetores sem bibliotecas de machine learning.
- Relacionar resultados visuais com a estrutura matemática por trás da transformação.

## 🧠 Fundamentação Teórica

A implementação está baseada em conceitos como:
- Matriz de covariância e decomposição espectral.
- Autovalores e autovetores (Capítulo 6 - Watkins).
- Espaços invariantes e subespaços associados à matriz de covariância.

## 🛰 Dados Utilizados

- Imagens Landsat 8/9 ou Sentinel-2 com baixa cobertura de nuvens.
- Bandas espectrais utilizadas: visível e infravermelho próximo.

## 🛠 Tecnologias

- Python 3
- NumPy
- Rasterio
- Matplotlib

## 📊 Etapas

1. Leitura e empilhamento das bandas
2. Cálculo da matriz de covariância
3. Cálculo dos autovalores e autovetores
4. Projeção dos dados na nova base
5. Visualização dos componentes principais

## 📖 Referências

- Watkins, D. *Fundamentals of Matrix Computations*, Wiley, 3rd Edition.
- Projeto didático: "PCA Satélite.pdf"
- Estornell et al., *Principal Component Analysis Applied to Remote Sensing* (2013)
