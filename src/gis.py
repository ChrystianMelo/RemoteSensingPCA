import os
import ee
import glob
import rasterio
import numpy as np
from sklearn.cluster import KMeans

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

def getBands(output_folder) :
    # Cria e preenche com as bandas se necessario
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        donwloadBands(output_folder)

    # Encontra todos os arquivos de bandas (B1.tif, B2.tif, ..., B7.tif)
    band_paths = sorted(glob.glob(os.path.join(output_folder, '*.tif')))

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

def classify_kmeans(input_multiband_path, n_clusters, output_path):
    """
    Executa classificação KMeans em um raster multibanda.
    
    Parameters:
        input_multiband_path (str): Caminho do arquivo tif multibanda.
        n_clusters (int): Número de clusters para o KMeans.
        output_path (str): Caminho para salvar o resultado da classificação.
    """
    with rasterio.open(input_multiband_path) as src:
        bands = src.read()  # shape: (n_bands, height, width)
        profile = src.profile
        height, width = src.height, src.width

    # Reorganiza os dados para shape: (n_pixels, n_bands)
    data = bands.reshape(bands.shape[0], -1).T

    # Aplica KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init=10)
    labels = kmeans.fit_predict(data)

    # Reorganiza rótulos no formato original da imagem
    classified = labels.reshape((height, width)).astype(np.uint8)

    # Atualiza perfil do raster para uma banda só
    profile.update(count=1, dtype=rasterio.uint8)

    # Salva a classificação
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(classified, 1)