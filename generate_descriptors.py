import re
import os
import pandas as pd

def extract_cdd_e(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    cdd_values = []
    is_in_cdd_section = False
    for line in lines:
        if "Atom     q(N)    q(N+1)   q(N-1)     f-       f+       f0      CDD" in line:
            is_in_cdd_section = True
            continue  
        if is_in_cdd_section:
            if line.strip() == "":  
                break
            match = re.match(r'\s+\d+\([A-Za-z]+\)\s+[-\d\.]+\s+[-\d\.]+\s+[-\d\.]+\s+[-.\d]+\s+[-.\d]+\s+[-.\d]+\s+([-.\d]+)', line)
            if match:
                cdd_value = float(match.group(1))
                cdd_values.append(cdd_value)
    
    min_cdd = min(cdd_values) if cdd_values else None
    return min_cdd


def extract_hardness_e(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    hardness_pattern = re.compile(r'Hardness\s*\(=fundamental gap\):\s*([\d.]+)\s*Hartree')
    hardness_match = hardness_pattern.search(content)
    hardness_value = float(hardness_match.group(1)) if hardness_match else None
    return hardness_value


def extract_f_plus_max(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    
    f_plus_values = []
    is_in_f_plus_section = False
    
    for line in lines:
        if "Atom     q(N)    q(N+1)   q(N-1)     f-       f+       f0      CDD" in line:
            is_in_f_plus_section = True
            print(f"Found f+ section in {file_path}")
            continue
        if is_in_f_plus_section:
            if line.strip() == "":
                break
            match = re.match(r'\s*\d+\s*\(\w+\)\s+([-+]?\d*\.\d+)\s+([-+]?\d*\.\d+)\s+([-+]?\d*\.\d+)\s+([-+]?\d*\.\d+)\s+([-+]?\d*\.\d+)\s+([-+]?\d*\.\d+)\s+([-+]?\d*\.\d+)', line)
            if match:
                f_plus = float(match.group(5))  
                f_plus_values.append(f_plus)
                print(f"Extracted f+: {f_plus}")
    if f_plus_values:
        max_f_plus = max(f_plus_values)
        print(f"Max f+: {max_f_plus}")
        return max_f_plus
    else:
        print(f"No f+ values found in {file_path}")
        return None




def process_multiwfn_descriptors(multiwfn_file_path, rdkit_file_path):
    multiwfn_df = pd.read_csv(multiwfn_file_path)
    e_row_mw = multiwfn_df.loc[multiwfn_df['SampleName'] == 'E'].drop(columns=['SampleName'])
    nu_row_mw = multiwfn_df.loc[multiwfn_df['SampleName'] == 'Nu'].drop(columns=['SampleName'])
    e_row_mw.columns = [f"{col}_E" for col in e_row_mw.columns]
    nu_row_mw.columns = [f"{col}_Nu" for col in nu_row_mw.columns]
    rdkit_df = pd.read_csv(rdkit_file_path)
    e_row_rdkit = rdkit_df.loc[rdkit_df['SampleName'] == 'E'].drop(columns=['SampleName'])
    nu_row_rdkit = rdkit_df.loc[rdkit_df['SampleName'] == 'Nu'].drop(columns=['SampleName'])
    e_row_rdkit.columns = [f"{col}_E" for col in e_row_rdkit.columns]
    nu_row_rdkit.columns = [f"{col}_Nu" for col in nu_row_rdkit.columns]
    processed_df = pd.concat(
        [e_row_mw.reset_index(drop=True), nu_row_mw.reset_index(drop=True),
         e_row_rdkit.reset_index(drop=True), nu_row_rdkit.reset_index(drop=True)],
        axis=1
    )
    return processed_df


def process_files_and_merge(directory_path):
    e_cdft_file = os.path.join(directory_path, 'E_CDFT.txt')
    nu_cdft_file = os.path.join(directory_path, 'Nu_CDFT.txt')
    multiwfn_file = os.path.join(directory_path, './Phorgdesc/Multiwfn_descriptors.csv')
    rdkit_file = os.path.join(directory_path, 'rdkit.csv')
    cdd_e = extract_cdd_e(e_cdft_file) if os.path.exists(e_cdft_file) else None
    hardness_e = extract_hardness_e(e_cdft_file) if os.path.exists(e_cdft_file) else None
    f_plus_nu = extract_f_plus_max(nu_cdft_file) if os.path.exists(nu_cdft_file) else None
    extracted_results_df = pd.DataFrame([{
        'CDD_E': cdd_e,
        'Hardness_E': hardness_e,
        'f+_Nu': f_plus_nu
    }])
    processed_multiwfn_df = process_multiwfn_descriptors(multiwfn_file, rdkit_file)
    final_df = pd.concat([processed_multiwfn_df, extracted_results_df], axis=1)
    return final_df

directory_path = '.'  
final_results_df = process_files_and_merge(directory_path)
final_output_path = 'Descriptors.csv'
final_results_df.to_csv(final_output_path, index=False)
