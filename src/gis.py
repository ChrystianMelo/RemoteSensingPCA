import os
import ee
import glob
import rasterio
import numpy as np
from sklearn.cluster import KMeans

def donwloadBands(output_folder):
    # Inicializa a API
    ee.Initialize()

    # Define a área de interesse em EPSG:31983
    aoi = ee.Geometry.Rectangle(
        coords=[578524, 7774048, 609237, 7800187],
        proj=ee.Projection('EPSG:31983'),
        geodesic=False
    )

    # Define parâmetros
    colecao = 'LANDSAT/LT05/C02/T1_L2'
    bandas = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7']
    proj = 'EPSG:31983'

    # Filtra a coleção
    colecao_filtrada = (ee.ImageCollection(colecao)
        .filterDate('1990-01-01', '1990-05-04')
        .filterBounds(aoi)
        .filterMetadata('CLOUD_COVER', 'less_than', 10))

    # Seleciona imagem com menor cobertura de nuvens
    imagem = colecao_filtrada.sort('CLOUD_COVER').first()

    # Seleciona e reprojeta bandas
    imagem_bandas = imagem.select(bandas).clip(aoi).reproject(crs=proj, scale=30)

    # Define o caminho de saída (pasta local onde os arquivos serão salvos)
    geemap.ee_export_image(
        image=imagem_bandas,
        filename=f'{output_folder}/Landsat5_Composite_Ibirite.tif',
        region=aoi,
        scale=30,
        crs=proj,
        file_per_band=True  # salva cada banda como um arquivo separado
    )

    print("Download concluído.")

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
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    labels = kmeans.fit_predict(data)

    # Reorganiza rótulos no formato original da imagem
    classified = labels.reshape((height, width)).astype(np.uint8)

    # Atualiza perfil do raster para uma banda só
    profile.update(count=1, dtype=rasterio.uint8)

    # Salva a classificação
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(classified, 1)