# PCA via SVD para Realce de Feições em Imagens de Satélite 🚀

Este repositório demonstra **passo‑a‑passo** como aplicamos os conceitos vistos nas aulas de Álgebra Linear Numérica para construir uma pipeline de PCA do **zero**, sem bibliotecas de ML, a fim de realçar vegetação, água e áreas urbanas em cenas Landsat.

---

## 📚 Conexão direta com o conteúdo da disciplina

| Etapa do projeto | Conceito teórico usado | Fonte da aula |
|------------------|------------------------|---------------|
| **Centralização** das bandas (X ← X − μ) | Necessidade de dados de média zero antes de calcular covariância | Tutorial *PCA Satelite*, Fase 2‑2 (a) |
| **Matriz de covariância**  \(S = \frac{1}{N-1} X^{\mathsf T} X\) | Definição de correlação entre variáveis | Tutorial *PCA Satelite*, Fase 2‑2 (b) |
| **Decomposição em Valores Singulares (DVS)**  \(X = U\,\Sigma\,V^{\mathsf T}\) | Teorema 1: existe a fatoração ortogonal com σ₁ ≥ σ₂ … | Módulo 3 – DVS |
| Relação **autovalor ↔ valor singular**  \(\lambda_i = \sigma_i^2/(N-1)\) | Derivada de \(X^{\mathsf T} X = V\,\Sigma^2 V^{\mathsf T}\) | Tutorial *PCA Satelite*, Fase 2 |
| **Componentes principais**  (loadings = linhas de \(V^{\mathsf T}\)) | Bases ortonormais que maximizam variância | Módulo 3 – DVS |
| **Projeção**  \(Y = X P\) | Mudança de base para reduzir dimensionalidade | Tutorial *PCA Satelite*, Fase 2‑4 |
| **Variância explicada**  (\(\sum \lambda_i\)) | Análise de contribuição de cada PC | Tutorial *PCA Satelite*, Fase 3‑3 |

---

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

- Imagens Landsat 9.
- Bandas espectrais utilizadas: Bandas de 1 a 9 (exceto a 8)

## 🛠 Tecnologias

- Python 3
- Google Earth Engine 

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
