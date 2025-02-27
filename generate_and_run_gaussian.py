import os
import subprocess
import time
import sys
from cclib.io import ccopen
from periodictable import elements
from rdkit import Chem
from rdkit.Chem import Descriptors
import pandas as pd
def generate_gaussian_input(smiles_string, solvent, output_filename):
    molecule_name = os.path.splitext(os.path.basename(output_filename))[0]
    solvent_mapping = {
        'DMA': 'n,n-DiMethylAcetamide',
        'DMSO': 'DMSO',
        'DMF': 'N,N-Dimethylformamide',
        'ACN': 'acetonitrile'
    }
    gaussian_solvent = solvent_mapping.get(solvent.upper())
    if not gaussian_solvent:
        raise ValueError(f"Unknown solvent: {solvent}. Please use 'DMA', 'DMSO', 'DMF', or 'ACN'.")
    with open('temp.smi', 'w', encoding='utf-8') as file:
        file.write(smiles_string)
    subprocess.run(['obabel', 'temp.smi', '--gen3d', '--slowest', '-O', 'temp.gjf'])
    with open('temp.gjf', 'r') as file:
        data = file.readlines()
    data = data[5:]
    keyword_line = (
        f'%chk={molecule_name}.chk\n'
        '%nprocshared=16\n'
        '%mem=16GB\n'
        f'#p opt freq B3LYP/gen EmpiricalDispersion=GD3BJ '
        f'scrf=(smd,solvent={gaussian_solvent}) gfinput\n\n'
        'opt\n\n'
    )
    data.insert(0, keyword_line)
    current_directory = os.getcwd()
    basis_set_path = os.path.join(current_directory, 'ma-TZVP.txt')
    data.append(f'@{basis_set_path}/N\n')
    with open(output_filename, 'w') as file:
        file.writelines(data)
    os.remove('temp.smi')
    os.remove('temp.gjf')
def run_gaussian_calculation(output_filename):
    molecule_name = os.path.splitext(os.path.basename(output_filename))[0]
    log_file = output_filename.replace('.gjf', '.log')
    chk_file = output_filename.replace('.gjf', '.chk')
    fchk_file = output_filename.replace('.gjf', '.fchk')
    with open(log_file, 'w') as logfile:
        subprocess.run(['chemg16', output_filename], stdout=logfile)
    while True:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                if 'Normal termination of Gaussian' in f.read():
                    break
        time.sleep(60)
    subprocess.run(['g16formchk', chk_file, fchk_file])
def generate_modifications_for_cdft(smiles_string, solvent, base_output_filename):
    generate_gaussian_input(smiles_string, solvent, base_output_filename)
    run_gaussian_calculation(base_output_filename)
    fchk_file = base_output_filename.replace('.gjf', '.fchk')
    data = ccopen(fchk_file).parse()
    last_coords = data.atomcoords[-1]
    atomic_numbers = data.atomnos
    solvent_mapping = {
        'DMA': 'n,n-DiMethylAcetamide',
        'DMSO': 'DMSO',
        'DMF': 'N,N-Dimethylformamide',
        'ACN': 'acetonitrile'
    }
    gaussian_solvent = solvent_mapping.get(solvent.upper())
    for sign, modification in [('+1', '1 2'), ('-1', '-1 2')]:
        filename = f"{base_output_filename.replace('.gjf', '')}{sign}.gjf"
        with open(filename, 'w') as file:
            file.write(f"%chk={filename.replace('.gjf', '.chk')}\n")
            file.write("%nprocshared=16\n")
            file.write("%mem=16GB\n")
            file.write(f"#p B3LYP/gen EmpiricalDispersion=GD3BJ scf=(maxcycle=80,xqc) stable gfinput scrf=(smd,solvent={gaussian_solvent})\n\n")
            file.write("CDFT\n\n")
            file.write(modification + "\n")
            for atomic_number, coords in zip(atomic_numbers, last_coords):
                element_symbol = elements[atomic_number].symbol
                file.write(f"{element_symbol}  {coords[0]:.7f} {coords[1]:.7f} {coords[2]:.7f}\n")
            current_directory = os.getcwd()
            basis_set_path = os.path.join(current_directory, 'ma-TZVP.txt')
            file.write(f"\n@{basis_set_path}/N\n")
def generate_rdkit_descriptors(smiles_string, sample_name, output_filename="rdkit.csv"):
    mol = Chem.MolFromSmiles(smiles_string)
    if mol is None:
        print(f"Invalid SMILES string: {smiles_string}")
        return
    descriptors = {'SampleName': sample_name}
    for descriptor, function in Descriptors.descList:
        try:
            descriptors[descriptor] = function(mol)
        except:
            descriptors[descriptor] = None
    df = pd.DataFrame([descriptors])
    if not pd.io.common.file_exists(output_filename):
        df.to_csv(output_filename, index=False)
    else:
        df.to_csv(output_filename, mode='a', header=False, index=False)
def main(smiles_string, solvent, output_filename):
    sample_name = output_filename.replace('.gjf', '')
    generate_rdkit_descriptors(smiles_string, sample_name, output_filename="rdkit.csv")
    generate_gaussian_input(smiles_string, solvent, output_filename)
    generate_modifications_for_cdft(smiles_string, solvent, output_filename)
    run_gaussian_calculation(output_filename)
    base_name = os.path.splitext(output_filename)[0]
    for charge_suffix in ['+1', '-1']:
        modified_output_filename = f"{base_name}{charge_suffix}.gjf"
        run_gaussian_calculation(modified_output_filename)
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_and_run_gaussian.py <SMILES_STRING> <SOLVENT> <OUTPUT_FILENAME>")
        sys.exit(1)
    smiles_string = sys.argv[1]
    solvent = sys.argv[2]
    output_filename = sys.argv[3]
    main(smiles_string, solvent, output_filename)
