import os
import subprocess
import shutil
from tqdm import tqdm



def load_config(file_path):
    import yaml
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config



def find_pcap_files(folder_path):
    pcap_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.pcap') or file.endswith('.pcapng'):
                pcap_files.append(os.path.join(root, file))
    return pcap_files




def Split_Cap(capture_interval, pcap_path, save_folder):
    try:
        # Split The Pcap File Into Smaller Parts
        subprocess.run(["editcap", "-i", str(capture_interval), pcap_path, os.path.join(save_folder, 'Split.pcap')])
        # Rename the split files based on a naming convention
        split_files = os.listdir(save_folder)
        for i, file_name in enumerate(split_files):
            # Get the file extension
            file_base, file_extension = os.path.splitext(file_name)
            # Check if the file has a valid extension
            if file_extension in (".pcap", ".pcapng"):
                new_name = f"split_{i + 1}{file_extension}"
                os.rename(os.path.join(save_folder, file_name), os.path.join(save_folder, new_name))
    except subprocess.CalledProcessError as e:
        print(f"Error executing Pcap Split Subprocess: {e}")




def ReOrganize_Files(main_folder_path):
    print("\n\033[93mReorganizing Files.\033[0m")
    # Define the names of the new folders
    statistical_folder = os.path.join(main_folder_path, 'Statistical')
    tabular_folder = os.path.join(main_folder_path, 'Tabular')
    # Create the new folders
    os.makedirs(statistical_folder, exist_ok=True)
    os.makedirs(tabular_folder, exist_ok=True)

    # Get a list of split folders
    split_folders = [item for item in os.scandir(main_folder_path) if item.name.startswith('split_') and item.is_dir()]

    # Iterate through the sorted split folders with tqdm progress bar
    for split_folder in tqdm(split_folders, desc="Processing subfolders"):
        print(f"\nProcessing folder: {split_folder.name}")
        split_folder_path = split_folder.path
        
        if len(os.listdir(split_folder_path)) == 0:
            shutil.rmtree(split_folder_path)
            continue

        # Paths to the statistical and tabular data within the split folder
        split_statistical_path = os.path.join(split_folder_path, 'Statistical')
        split_tabular_path = os.path.join(split_folder_path, 'Tabular')

        # Move Statistical files using os.scandir (no need to load all files into memory)
        with os.scandir(split_statistical_path) as it:
            for entry in it:
                if entry.is_file() and entry.name.endswith('.csv'):
                    src_path = entry.path
                    dest_path = os.path.join(statistical_folder, entry.name)
                    shutil.move(src_path, dest_path)

        # Move Tabular files using os.scandir
        with os.scandir(split_tabular_path) as it:
            for entry in it:
                if entry.is_file() and entry.name.endswith('.csv'):
                    src_path = entry.path
                    dest_path = os.path.join(tabular_folder, entry.name)
                    shutil.move(src_path, dest_path)

        # Delete the now empty split folder
        print(f"Deleting folder: {split_folder_path}")
        try:
            shutil.rmtree(split_folder_path)
        except Exception as e:
            print(f"Failed to delete {split_folder_path}: {e}")

    print("\n\033[93mFiles have been moved successfully.\033[0m")
    