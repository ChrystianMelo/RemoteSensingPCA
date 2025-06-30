import numpy as np


def svd_manual(X, full_matrices=False, compute_uv=True):
    """
    Pequena implementação de SVD via autovalores de X.T * X.
    Retorna U, s, Vt tal como np.linalg.svd (reduced).
    """
    X = np.asarray(X, dtype=float)

    # 1. Produto cruzado
    C = X.T @ X                                   # (p × p)

    # 2. Autovalores (simétrica) – mais estável que eig geral
    eigvals, V = np.linalg.eigh(C)                # ascendente
    idx = eigvals.argsort()[::-1]                 # ↓
    eigvals, V = eigvals[idx], V[:, idx]

    # 3. Valores singulares
    s = np.sqrt(np.clip(eigvals, 0, None))        # evita negativos

    if not compute_uv:                            # só s
        return s

    # 4. U = X V Σ^{-1}
    nonzero = s > 1e-12                           # tolerância
    U = np.zeros((X.shape[0], V.shape[1]))
    U[:, nonzero] = (X @ V[:, nonzero]) / s[nonzero]

    # 5. Corte para forma reduzida, se desejado
    if not full_matrices:
        r = np.count_nonzero(nonzero)
        U = U[:, :r]
        V = V[:, :r]
        s = s[:r]

    Vt = V.T
    return U, s, Vt

def pca_svd(X, n_components=None, center=True, scale=False):
    """
    PCA via SVD (DVS).

    Parâmetros
    ----------
    X : array-like, shape (n_amostras, n_variáveis)
        Matriz de dados, cada linha é um pixel (ou amostra) e cada coluna uma banda.
    n_components : int ou None
        Quantos componentes principais retornar.  None -> todos.
    center : bool
        Se True, subtrai a média de cada coluna (passo de centralização).
    scale : bool
        Se True, divide pelo desvio-padrão de cada coluna (opcional).

    Retorna
    -------
    scores : ndarray (n_amostras, n_components)
        Dados projetados (Y no tutorial).
    loadings : ndarray (n_components, n_variáveis)
        Autovetores (componentes principais, linhas de Vᵀ).
    eigvals : ndarray (n_components,)
        Autovalores (variância explicada por componente).
    """
    X = np.asarray(X, dtype=float)
    n, p = X.shape
    if center:
        X = X - X.mean(axis=0, keepdims=True)
    if scale:
        X = X / X.std(axis=0, ddof=1, keepdims=True)

    U, s, Vt = svd_manual(X, full_matrices=False)

    eigvals_full = (s**2) / (n - 1)

    if n_components is None or n_components > len(s):
        n_components = len(s)

    loadings = Vt[:n_components]
    scores = X @ loadings.T

    eigvals = eigvals_full[:n_components]
    return scores, loadings, eigvals

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
        print(
            f"Selecionando {num_pcs} PCs para atingir {threshold*100:.1f}% da variância explicada.")
        for i, (e, c) in enumerate(zip(explained_ratios, cumulative), 1):
            status = "<-- usar" if i <= num_pcs else ""
            print(f"PC{i}: {e:.4f} explicada | Acumulada: {c:.4f} {status}")

    Y_selected = Y_pca[:, :num_pcs]
    return Y_selected, num_pcs
