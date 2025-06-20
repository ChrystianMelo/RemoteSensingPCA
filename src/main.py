import os
import pca
import gis
import rasterio
import glob
import numpy as np

if __name__ == '__main__':
    bands_folder = "data/bandsLandsat5"
    bands = gis.getBands(bands_folder)

    band_paths = sorted(glob.glob(os.path.join(bands_folder, '*.tif')))
    
    os.makedirs("data/results", exist_ok=True)

    combinedBands = "data/results/combinedBands.tif"
    classifiedCombinedBands = "data/results/classifiedCombinedBands.tif"

    gis.combine_bands(band_paths, combinedBands)
    gis.classify_kmeans(combinedBands, n_clusters=4, output_path=classifiedCombinedBands)

    X = np.array(bands).T  # (n_pixels, n_bandas)

    # Aplica PCA
    Y_pca, eigvecs, eigvals = pca.simple_pca(X, 6)

    # Calcula a variância total
    Y_selected, num_pcs = pca.get_selected_pcs(Y_pca, eigvals, 0.95, True)

    # Garante pasta de saída
    pcFolder = "data/pca_components"
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
    
    combinedPCs = "data/results/combinedPCs.tif"
    classifiedCombinedPCs = "data/results/classifiedCombinedPCs.tif"

    pcPaths = sorted(glob.glob(os.path.join(pcFolder, '*.tif')))

    gis.combine_bands(pcPaths, combinedPCs)
    gis.classify_kmeans(combinedPCs, n_clusters=4, output_path=classifiedCombinedPCs)