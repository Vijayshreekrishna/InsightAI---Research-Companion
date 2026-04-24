import os

pages_dir = r'c:\Users\vijay\Downloads\vsk\I-AI\pages'
css_path = "assets/styles.css"

for filename in os.listdir(pages_dir):
    if filename.endswith(".py") and filename != "_Paper_Formatter_AI.py":
        filepath = os.path.join(pages_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check if already imported
        if "from utils.ui_components import load_css" in "".join(lines):
            continue
            
        # Add import and call
        new_lines = []
        imported = False
        called = False
        for line in lines:
            new_lines.append(line)
            if not imported and ("import streamlit" in line or "from utils.api" in line):
                new_lines.insert(len(new_lines)-1, "from utils.ui_components import load_css\n")
                imported = True
            if not called and "st.title" in line:
                new_lines.append(f'load_css("{css_path}")\n')
                called = True
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Applied global scaling to {filename}")
