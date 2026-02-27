from pathlib import Path
import sys

# Prefer the installed dmri-amico package in the venv over the local source tree.
script_dir = Path(__file__).resolve().parent
sys.path = [p for p in sys.path if Path(p or ".").resolve() != script_dir]

import amico
amico.setup()

ae = amico.Evaluation()
ae.set_config('nthreads', 4)
ae.set_config('BLAS_nthreads', 1)
# 信号のデバイアスを有効にする。これにより、SNRが低い場合のフィッティング精度が向上すると考えられる。
# ae.set_config('doDebiasSignal', True)
# ae.set_config('DWI-SNR', 30.0)
ae.set_config('doSaveModulatedMaps', True)

amico.util.fsl2scheme('bvals', 'bvecs')
ae.load_data(
    dwi_filename='data.nii.gz',
    scheme_filename='bvals.scheme',
    mask_filename='nodif_brain_mask.nii.gz',
    b0_thr=20
)

# NODDI parameters: default values for WM are used. See the documentation for more details.
# - 'Parallel diffusivity': 1.7e-9,  # m^2/s
# - "Isotropic diffusivity": 3.0e-9,  # m^2/s
# -See https://github.com/daducci/AMICO/wiki/Model-configuration#noddi-parameters for more details.
ae.set_model('NODDI')
ae.generate_kernels(ndirs=32761, regenerate=True)

ae.load_kernels()

ae.fit()

ae.save_results()
