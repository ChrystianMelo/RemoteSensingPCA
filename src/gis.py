import os
import ee
import glob
import rasterio
import numpy as np
from sklearn.cluster import KMeans
from scipy.ndimage import generic_filter
from pathlib import Path
import rasterio
from rasterio.mask import mask
import geopandas as gpd


def downloadBands(output_folder):
    """
    Faz o download de bandas espectrais do satélite Landsat 9 (nível 1 - TOA) usando o Google Earth Engine.

    Esta função deve ser implementada para se conectar ao GEE, selecionar a melhor imagem disponível
    em determinada área de interesse, extrair bandas específicas e exportar as imagens para o Google Drive.

    Detalhes do processo:

    1. **Fonte de Dados**:
       - Coleção utilizada: `LANDSAT/LC09/C02/T1_TOA` (Top of Atmosphere Reflectance)
       - Nível: Level 1 (não atmospherically corrected)
       - Satélite: Landsat 9

    2. **Área de Interesse (AOI)**:
       - Definida como um retângulo em coordenadas UTM (EPSG:31983 - SIRGAS 2000 Zona 23S).
       - Representa a região de interesse onde as bandas serão recortadas.

    3. **Filtro Temporal e de Qualidade**:
       - Período analisado: de `'2022-01-01'` a `'2022-12-31'`
       - Apenas imagens com `CLOUD_COVER < 10` são consideradas, garantindo baixa nebulosidade.

    4. **Seleção da Imagem**:
       - A imagem com **menor cobertura de nuvens** é selecionada automaticamente usando `.sort('CLOUD_COVER').first()`.

    5. **Bandas Selecionadas**:
       - Bandas espectrais de interesse: `B1` a `B9`, **excluindo** `B8` por ser pancromática (opcional incluir).
       - Resolução nativa: 30 metros (exceto `B8`, que tem 15m e será reamostrada se usada).

    6. **Reprojeção e Recorte**:
       - Todas as bandas selecionadas são recortadas à área de interesse e reprojetadas para `EPSG:31983` com resolução de 30m.

    7. **Exportação**:
       - Cada banda é exportada separadamente para o Google Drive.
       - Os arquivos serão nomeados com o padrão: `'Landsat9_{BANDA}_Ibirite_{DATA}'`
       - Parâmetros de exportação:
         - `region`: área recortada (AOI)
         - `scale`: 30 metros
         - `crs`: EPSG:31983
         - `folder`: pasta no Drive chamada `'GEE_Exports'`
         - `maxPixels`: 1e13 (permite grandes imagens)

    Observações:
    - Para que o Earth Engine funcione, o usuário deve estar autenticado no ambiente GEE (via browser ou API Python).
    - Este processo exige que o Earth Engine esteja devidamente configurado no ambiente (API ativa e permissões concedidas).
    - O processo de exportação para o Drive não é imediato e pode ser monitorado via [GEE Tasks](https://code.earthengine.google.com/tasks).
    
    Parâmetros:
    ----------
    output_folder : str
        Caminho ou nome da pasta onde os arquivos serão organizados após exportação via Drive.
    
    Retorno:
    -------
    Nenhum retorno direto. Os arquivos .tif serão enviados para o Google Drive e podem ser baixados manualmente ou via API.
    """
    print("Esse metodo ainda precisa ser escrito e testado corretamente.")

def getBands(folder) :
    """
    Recupera e agrupa as bandas *.tif presente na pasta passada
    """
    # Cria e preenche com as bandas se necessario
    if not os.path.exists(folder):
        os.makedirs(folder)
        donwloadBands(folder)

    # Encontra todos os arquivos de bandas (B1.tif, B2.tif, ..., B7.tif)
    band_paths = sorted(glob.glob(os.path.join(folder, '*.tif')))

    # Lê e empilha as bandas
    bands = []
    for path in band_paths:
        with rasterio.open(path) as src:
            bands.append(src.read(1).flatten())  # vetoriza

    return bands

def combine_bands(band_paths, output_path):
    """
    Combina várias bandas tif em um único arquivo multibanda.
    
    Parameters:
        band_paths (list of str): Caminhos dos arquivos .tif de cada banda.
        output_path (str): Caminho de saída do .tif combinado.
    """
    with rasterio.open(band_paths[0]) as src_ref:
        profile = src_ref.profile
        height, width = src_ref.shape

    profile.update(count=len(band_paths))

    with rasterio.open(output_path, 'w', **profile) as dst:
        for i, path in enumerate(band_paths):
            with rasterio.open(path) as src:
                dst.write(src.read(1), i + 1)

# === 1. Gerador compatível com java.util.Random ============================
class JavaRandom:
    _MULT = 0x5DEECE66D
    _ADD  = 0xB
    _MASK = (1 << 48) - 1

    def __init__(self, seed: int):
        # Mesmo scrambling que o construtor do Java
        self.seed = (seed ^ self._MULT) & self._MASK

    def _next_bits(self, bits: int) -> int:
        self.seed = (self.seed * self._MULT + self._ADD) & self._MASK
        return self.seed >> (48 - bits)

    def next_int(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError("bound must be positive")
        if (bound & (bound - 1)) == 0:                 # potência de 2
            return (bound * self._next_bits(31)) >> 31
        while True:
            bits = self._next_bits(31)
            val  = bits % bound
            if bits - val + (bound - 1) >= 0:
                return val

# === 2. K-Means exatamente como no SNAP ===================================
def _snap_like_kmeans(X, n_clusters=6, max_iter=30, seed=31415, tol=1e-6, sample_size=50_000):
    """
    Implementa o K-Means do SNAP.
    Parâmetros
    ----------
    X : ndarray (n amostras, n_bandas)
        Pixels válidos já vetorizados.
    n_clusters : int
    max_iter : int
    seed : int
    tol : float
        Limite absoluto para considerar que os centróides não mudaram.
    Retorno
    -------
    labels_sorted : ndarray (n amostras,)
        Índices de classe já reordenados pelo tamanho do cluster.
    """
    rnd = np.random.RandomState(seed)

    # (A) -------- PADRONIZAÇÃO (z-score) ----------
    X_std = (X - X.mean(axis=0)) / X.std(axis=0)

    # (B) --------- AMOSTRAGEM p/ treinamento ------
    if X_std.shape[0] > sample_size:
        idx_sample = rnd.choice(X_std.shape[0], sample_size, replace=False)
        X_train = X_std[idx_sample]
    else:
        X_train = X_std

    # (C) --------- K-means sobre o ‘treino’ --------
    centroids = X_train[rnd.choice(X_train.shape[0], n_clusters, replace=False)]
    for _ in range(max_iter):
        d = np.linalg.norm(X_train[:, None] - centroids, axis=2)
        labels = np.argmin(d, axis=1)

        new_c = centroids.copy()
        for k in range(n_clusters):
            pts = X_train[labels == k]
            new_c[k] = pts.mean(axis=0) if len(pts) else X_train[rnd.randint(len(X_train))]
        if np.allclose(new_c, centroids, atol=tol):
            break
        centroids = new_c

    # (D) --------- rotula TODOS os pixels ----------
    d_full = np.linalg.norm(X_std[:, None] - centroids, axis=2)
    lbl_full = np.argmin(d_full, axis=1)

    # (E) --------- reordena pelo tamanho -----------
    sizes = np.bincount(lbl_full, minlength=n_clusters)
    order = np.argsort(-sizes)
    relabel = np.empty_like(order)
    relabel[order] = np.arange(n_clusters)
    return relabel[lbl_full]

def classify_map(src_path, dst_path, n_clusters=6, max_iter=30, seed=31415, 
                 sample_size=50_000,      # << NOVO
                 post_smooth=3,           # raio (pixels) p/ filtro majoritário
                 nodata_value=65535):
    """
    Executa o K-Means no arquivo `src_path` e salva o mapa classificado.

    Parâmetros
    ----------
    src_path : str  – GeoTIFF multibanda combinado
    dst_path : str  – GeoTIFF de saída com 1 banda (classes)
    n_clusters, max_iter, seed : idem SNAP
    nodata_value : valor inteiro para áreas sem dados
    """
    # --- Lê dado inteiro em memória (mais próximo do SNAP)
    with rasterio.open(src_path) as src:
        arr = src.read()               # (bands, rows, cols)
        meta = src.profile
        nodata_in = src.nodata
        rows, cols = meta['height'], meta['width']

    # --- Cria máscara de áreas válidas
    if nodata_in is None:
        mask_valid = np.ones((rows, cols), dtype=bool)
    else:
        mask_valid = ~(np.any(arr == nodata_in, axis=0))

    # --- Vetoriza pixels válidos
    X = arr[:, mask_valid].T          # (n_valid, n_bands)

    # aplica k-means
    labels_valid = _snap_like_kmeans(X,
                                     n_clusters=n_clusters,
                                     max_iter=max_iter,
                                     seed=seed,
                                     sample_size=sample_size)

    # reconstrução
    class_img = np.full(rows*cols, nodata_value, np.uint16)
    class_img[mask_valid.ravel()] = labels_valid
    class_img = class_img.reshape(rows, cols)

    # (F) --------- SUAVIZAÇÃO opcional -------------
    if post_smooth:
        def majority_filter(window):
            vals = window.astype(np.int32)
            vals = vals[vals != nodata_value]
            return np.bincount(vals).argmax() if vals.size else nodata_value
        class_img = generic_filter(class_img,
                                   majority_filter,
                                   size=post_smooth,
                                   mode='nearest')

    # --- Reconstrói imagem cheia
    class_img = np.full(rows * cols, nodata_value, dtype=np.uint16)
    class_img[mask_valid.ravel()] = labels_valid
    class_img = class_img.reshape(rows, cols)

    # --- Salva GeoTIFF
    meta.update(count=1, dtype='uint16', nodata=nodata_value)
    with rasterio.open(dst_path, 'w', **meta) as dst:
        dst.write(class_img, 1)

def clipRasterFromMask(tif_in, shp_mask, tif_out) :
    # --- lê máscara como GeoJSON (WGS-84 ou mesma projeção do raster) ---
    gdf = gpd.read_file(shp_mask)
    geom = [g.__geo_interface__ for g in gdf.geometry]  # list-of-dicts esperado pelo rasterio

    with rasterio.open(tif_in) as src:
        recortado, _ = mask(src, geom, crop=True, nodata=src.nodata)

        meta = src.meta.copy()
        meta.update({
            "height": recortado.shape[1],
            "width":  recortado.shape[2],
            "transform": _,
        })

        with rasterio.open(tif_out, "w", **meta) as dst:
            dst.write(recortado)