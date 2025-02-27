#!/bin/bash
# Job submission script for SLURM:
# Usage: sbatch <this_script>
#SBATCH -p public
#SBATCH -J SMILES_target
#SBATCH -o SMILES_target.o%j
#SBATCH -N 1
#SBATCH --ntasks-per-node=8
#SBATCH -t 1538:00:00
#############################################################################
#    -J: name of job
#    -o: file for batch script's standard output
#    -e: file for batch script's standard error
#    -N: number of nodes on which to run (N = min[-max])
#    -n: number of tasks to run
#    -t: time limit
#    -p: partition requested
#    -w: request a specific list of hosts
#############################################################################
# Need to activate the conda environment that has OpenBabel/cclib installed 
# Created by Roderick
module load anaconda3
module load gauss/g16c01
export Multiwfnpath="/opt/soft/Multiwfn/3.8_dev_20231225"
export PATH="$PATH:$Multiwfnpath"
export BABEL_LIBDIR="/datapool/home/fanly/.conda/envs/chem/lib/openbabel/3.1.0"
export KMP_STACKSIZE=100000000
export GAUSS_MEMDEF=16GB
cd $SLURM_SUBMIT_DIR
SMILES_STRINGS=("CCOC(=O)CCS" "CCOC(=O)C1=CC=C(Br)C=C1") 
SOLVENTS=("DMA" "DMA")
OUTPUT_FILES=("Nu.gjf" "E.gjf")
for i in ${!SMILES_STRINGS[@]}; do
    SMILES_STRING=${SMILES_STRINGS[$i]}
    SOLVENT=${SOLVENTS[$i]}
    OUTPUT_FILE=${OUTPUT_FILES[$i]}
    MOLECULE_NAME=$(basename "$OUTPUT_FILE" .gjf)
    python generate_and_run_gaussian.py "$SMILES_STRING" "$SOLVENT" "$OUTPUT_FILE"
done
mkdir -p Phorgdesc
cp E.fchk Nu.fchk Phorgdesc/
cp MultiwfnMLhelper.py Phorgdesc/
cp settings.ini Phorgdesc/
cd Phorgdesc
python MultiwfnMLhelper.py
cd ..
for prefix in "E" "Nu"; do
    echo "Starting Multiwfn run for $prefix at $(date)"
    echo -e "22\n2\n${prefix}.fchk\n${prefix}-1.fchk\n${prefix}+1.fchk\nq" | Multiwfn ${prefix}.fchk
    echo "Finished Multiwfn run for $prefix at $(date)"
    mv CDFT.txt ${prefix}_CDFT.txt  
done
echo "Multiwfn calculation completed at $(date)"
python generate_descriptors.py