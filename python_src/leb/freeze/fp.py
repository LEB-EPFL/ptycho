from enum import Enum
import numpy as np

class Method(Enum):
    rPIE = "rPIE"
    GD = "GD"

def fp_recover(images: np.array, num_iterations: int = 10, method: Method = Method.rPIE):
    num_images = images.shape[0]

    for i in range(num_iterations):
        for j in range(num_images):
        
            pass
