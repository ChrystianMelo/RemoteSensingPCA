import os
import pca
import gis
import rasterio
import glob
import numpy as np

if __name__ == '__main__':
    bands_folder = "data/bandsLandsat5"
    bands = gis.getBands(bands_folder)

    X = np.array(bands).T  # (n_pixels, n_bandas)

    # Aplica PCA
    Y_pca, eigvecs, eigvals = pca.simple_pca(X, 6)

    # Calcula a variância total
    Y_selected, num_pcs = pca.get_selected_pcs(Y_pca, eigvals, 0.95, True)

    # Garante pasta de saída
    os.makedirs("data/pca_components", exist_ok=True)

    band_paths = sorted(glob.glob(os.path.join(bands_folder, '*.tif')))
    with rasterio.open(band_paths[0]) as ref:
        height, width = ref.height, ref.width
        profile = ref.profile

    # Salva cada PC como um .tif separado
    for i in range(num_pcs):
        img = Y_selected[:, i].reshape((height, width)).astype('float32')
        output_path = f"data/pca_components/pc{i+1}.tif"

        profile.update({
            'count': 1,
            'dtype': 'float32'
        })

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(img, 1)

        print(f"Salvo: {output_path}")