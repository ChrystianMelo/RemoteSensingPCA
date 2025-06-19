import os
import ee
import glob
import rasterio


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