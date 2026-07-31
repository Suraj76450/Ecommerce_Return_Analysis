import os
import sys
import nbformat as nbf

def convert_py_to_ipynb(py_path, ipynb_path):
    if not os.path.exists(py_path):
        print(f"Source file not found: {py_path}")
        return
        
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    nb = nbf.v4.new_notebook()
    cells = []
    
    # Split content by # %%
    parts = content.split('# %%')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        lines = part.split('\n')
        header = lines[0].strip()
        
        if header == '[markdown]':
            md_lines = []
            for line in lines[1:]:
                if line.startswith('# '):
                    md_lines.append(line[2:])
                elif line.startswith('#'):
                    md_lines.append(line[1:])
                else:
                    md_lines.append(line)
            cells.append(nbf.v4.new_markdown_cell('\n'.join(md_lines).strip()))
        elif header == '[code]':
            cell_body = '\n'.join(lines[1:])
            cells.append(nbf.v4.new_code_cell(cell_body.strip()))
        else:
            # Fallback to code if not explicitly headered but contains code
            cells.append(nbf.v4.new_code_cell(part.strip()))
                
    nb['cells'] = cells
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(ipynb_path), exist_ok=True)
    
    with open(ipynb_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Successfully converted {py_path} -> {ipynb_path}")

if __name__ == "__main__":
    # Define files relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    notebooks = [
        ("01_data_cleaning.py", "../notebooks/01_data_cleaning.ipynb"),
        ("02_eda.py", "../notebooks/02_eda.ipynb"),
        ("03_business_analysis.py", "../notebooks/03_business_analysis.ipynb"),
        ("04_returns_prediction.py", "../notebooks/04_returns_prediction.ipynb")
    ]
    
    for src, dest in notebooks:
        src_path = os.path.join(script_dir, "notebooks_src", src)
        dest_path = os.path.abspath(os.path.join(script_dir, dest))
        convert_py_to_ipynb(src_path, dest_path)
