from leb.freeze.fp import fp_recover, Method
import numpy as np

def test_fp_recover():
    imgs = np.random.random((10,32,32))

    method = Method.rPIE
    fp_recover(imgs, method=method)
    raise NotImplementedError