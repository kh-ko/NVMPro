import os

base_dir = r"e:\04_Working\01_APC_VALVE\003_NVMPro\01_Working\SW\NVMPro"

files_to_modify = [
    r"main.py",
    r"c_ui\c_windows\a_home\_home_model.py",
    r"c_ui\c_windows\a_home\home_win.py",
    r"c_ui\c_windows\a_home\sub_parts\home_valve_status_frame.py",
    r"c_ui\c_windows\a_home\sub_parts\home_valve_control_mode_frame.py",
    r"c_ui\c_windows\a_home\sub_parts\home_top_menu_frame.py",
    r"c_ui\c_windows\a_home\sub_parts\home_pressure_frame.py",
    r"c_ui\c_windows\a_home\sub_parts\home_position_frame.py",
    r"c_ui\c_windows\a_home\sub_parts\home_chart_frame.py"
]

def replace_in_file(filepath):
    abs_path = os.path.join(base_dir, filepath)
    if not os.path.exists(abs_path):
        print(f"File not found: {abs_path}")
        return
    with open(abs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace("Home", "Main")
    content = content.replace("home", "main")
    
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated content in {filepath}")

for f in files_to_modify:
    replace_in_file(f)

a_home_dir = os.path.join(base_dir, r"c_ui\c_windows\a_home")

if os.path.exists(a_home_dir):
    for root, dirs, files in os.walk(a_home_dir, topdown=False):
        for name in files:
            if "home" in name:
                old_path = os.path.join(root, name)
                new_name = name.replace("home", "main")
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)
                print(f"Renamed file: {name} -> {new_name}")
        for name in dirs:
            if "home" in name:
                old_path = os.path.join(root, name)
                new_name = name.replace("home", "main")
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)
                print(f"Renamed dir: {name} -> {new_name}")
                
    a_main_dir = os.path.join(base_dir, r"c_ui\c_windows\a_main")
    os.rename(a_home_dir, a_main_dir)
    print(f"Renamed main dir: a_home -> a_main")
else:
    print(f"Directory not found: {a_home_dir}")
