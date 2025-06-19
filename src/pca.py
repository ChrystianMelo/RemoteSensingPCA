import numpy as np

def simple_pca(X, n_components):
    # Centraliza os dados
    X_centered = X - np.mean(X, axis=0)
    # Matriz de covariância
    cov = np.cov(X_centered, rowvar=False)
    # Autovalores e autovetores
    eigvals, eigvecs = np.linalg.eigh(cov)
    # Ordena em ordem decrescente
    sorted_idx = np.argsort(eigvals)[::-1]
    eigvecs = eigvecs[:, sorted_idx[:n_components]]
    # Projeção
    X_pca = np.dot(X_centered, eigvecs)
    return X_pca, eigvecs, eigvals[sorted_idx[:n_components]]

def get_selected_pcs(Y_pca, eigvals, threshold=0.95, verbose=True):
    """
    Retorna os PCs de Y_pca suficientes para explicar a variância acumulada desejada.

    Parâmetros:
        Y_pca (ndarray): matriz projetada (n_amostras x n_pcs).
        eigvals (array): autovalores associados aos PCs.
        threshold (float): variância acumulada alvo (ex: 0.95).
        verbose (bool): se True, imprime o relatório.

    Retorna:
        Y_selected (ndarray): subconjunto de Y_pca com PCs selecionadas.
        num_pcs (int): número de PCs usadas.
    """
    total_var = np.sum(eigvals)
    explained_ratios = eigvals / total_var
    cumulative = np.cumsum(explained_ratios)
    num_pcs = np.searchsorted(cumulative, threshold) + 1

    if verbose:
        print(f"Selecionando {num_pcs} PCs para atingir {threshold*100:.1f}% da variância explicada.")
        for i, (e, c) in enumerate(zip(explained_ratios, cumulative), 1):
            status = "<-- usar" if i <= num_pcs else ""
            print(f"PC{i}: {e:.4f} explicada | Acumulada: {c:.4f} {status}")

    Y_selected = Y_pca[:, :num_pcs]
    return Y_selected, num_pcs