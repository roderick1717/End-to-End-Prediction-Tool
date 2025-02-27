# End-to-End-Prediction-Tool
This repository contains a tool for end-to-end prediction of molecular properties starting from SMILES strings in the AD-HoC system. It automates the process of generating molecular descriptors using quantum chemical calculations and extracting features, followed by predictions using pre-trained machine learning models. The workflow integrates Gaussian for quantum chemical calculations, Multiwfn and RDKit for descriptor extraction, and pre-trained models for final predictions.
## Dependencies
To use this tool, ensure the following software and Python packages are installed:
### Software
**Gaussian 16：** Required for quantum chemical calculations.
**Multiwfn：** Used to extract descriptors from Gaussian output files.
**OpenBabel：** Converts SMILES strings to 3D structures.
### Python Packages
Panda joblib rdkit cclib periodictable
