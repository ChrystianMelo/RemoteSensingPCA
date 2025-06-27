import os
import pca
import gis
import rasterio
import glob
import numpy as np

if __name__ == '__main__':
    bandsFolder = "data/Landsat Bands"
    bands = gis.getBands(bandsFolder)

    band_paths = sorted(glob.glob(os.path.join(bandsFolder, '*.tif')))
    
    resultsFolder = "data/Results"
    os.makedirs(resultsFolder, exist_ok=True)

    combinedBands = resultsFolder + "/combinedBands.tif"
    classifiedCombinedBands = resultsFolder + "/classifiedCombinedBands.tif"

    gis.combine_bands(band_paths, combinedBands)
    gis.classify_map(combinedBands, classifiedCombinedBands, n_clusters=6, max_iter=30, seed=31415)
    gis.clipRasterFromMask(classifiedCombinedBands, "data/SHP_Bacia/bacia_regap_SirgasUTM23S.shp", resultsFolder + "/classifiedCombinedBands_clip.tif")

    X = np.array(bands).T  # (n_pixels, n_bandas)

    # Aplica PCA
    Y_pca, eigvecs, eigvals = pca.pca_svd(X, len(bands))

    # Calcula a variância total
    Y_selected, num_pcs = pca.get_selected_pcs(Y_pca, eigvals, 0.99, True)

    # Garante pasta de saída
    pcFolder = "data/PCA Components"
    os.makedirs(pcFolder, exist_ok=True)

    with rasterio.open(band_paths[0]) as ref:
        height, width = ref.height, ref.width
        profile = ref.profile

    # Salva cada PC como um .tif separado
    for i in range(num_pcs):
        img = Y_selected[:, i].reshape((height, width)).astype('float32')
        output_path = pcFolder + f"/pc{i+1}.tif"

        profile.update({
            'count': 1,
            'dtype': 'float32'
        })

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(img, 1)

        print(f"Salvo: {output_path}")
    
    combinedPCs = resultsFolder + "/combinedPCs.tif"
    classifiedCombinedPCs = resultsFolder + "/classifiedCombinedPCs.tif"

    pcPaths = sorted(glob.glob(os.path.join(pcFolder, '*.tif')))

    gis.combine_bands(pcPaths, combinedPCs)
    gis.classify_map(combinedPCs, classifiedCombinedPCs,6)
    gis.clipRasterFromMask(classifiedCombinedPCs, "data/SHP_Bacia/bacia_regap_SirgasUTM23S.shp", resultsFolder + "/classifiedCombinedPCs_clip.tif")