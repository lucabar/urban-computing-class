# folder_processing.py
import rasterio as rio
import numpy as np

def norm_diff(x,y):
    try:
        return (x-y)/(x+y)
    except Exception as e:
        print(e)
        return None

def process_folder(folder):
    try:
        base_path = f"data/{folder}/{folder}"
        with rio.open(f"{base_path}_B04.tif") as red, \
             rio.open(f"{base_path}_B03.tif") as green, \
             rio.open(f"{base_path}_B02.tif") as blue, \
             rio.open(f"{base_path}_B8A.tif") as nir, \
             rio.open(f"{base_path}_B11.tif") as swir:
            
            rgb = np.stack([red.read(1), green.read(1), blue.read(1)], axis=0)
            nir = nir.read(1).astype('float32')
            swir = swir.read(1).astype('float32')

            ndmi = norm_diff(nir.squeeze(), swir.squeeze())
            label = np.mean(ndmi)

            return rgb, label

    except Exception as e:
        print(e)
        return None, None
