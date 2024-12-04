import numpy as np

def normalize_distances(data):
    normalization_factor = np.sqrt(255**2 + 255**2 + 255**2)
    
    data_normalized = data / normalization_factor
  
    return data_normalized

