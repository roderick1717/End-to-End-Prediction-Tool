# End-to-End Prediction Tool

This tool is designed for the rapid prediction of reactivity and additive selection in the AD-HoC catalytic system. It automates the process of generating molecular descriptors using quantum chemical calculations and feature extraction, followed by predictions using pre-trained machine learning models. The workflow integrates Gaussian for quantum chemical calculations, Multiwfn and RDKit for descriptor extraction, and pre-trained models for final predictions.

## Dependencies

To use this tool, ensure the following software and Python packages are installed:

### Software

- **Gaussian 16**: Required for quantum chemical calculations. 
- **Multiwfn**: Used to extract descriptors from Gaussian output files.
- **OpenBabel**: Converts SMILES strings to 3D structures.

### Python Packages

- `pandas`: For data manipulation.
- `joblib`: For loading pre-trained models.
- `RDkit`: For generating cheminformatics descriptors.
- `cclib`: For parsing Gaussian output files.

Install the Python packages with:

```bash
pip install pandas joblib rdkit cclib
```

## Usage

You need to first modify the SMILES of the substrate molecules and their solvents in the SMILES-target.slurm script, ensuring that the appropriate environment variables for related software packages (such as Open Babel, Gaussian, and Multiwfn) are correctly set, then submit the job using SLURM, and finally run the load_model.py file to obtain predictions. The supported solvents include **DMA** (N,N-Dimethylacetamide), **DMF** (N,N-Dimethylformamide), **DMSO** (Dimethyl sulfoxide), and **ACN** (Acetonitrile).

## Citation
L. Fan, X. Li, X. Luo, B. Zhu, W. Guan, “Data‐Driven Prediction of Reactivity and Additive Selection for C(sp2 )–(Hetero)Atom Bond Couplings in an Adaptive Dynamic Homogeneous Catalysis” Chemistry A European J 2025, e202500935.




