import os
import subprocess
import shutil




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

    # Paths to new Statistical and Tabular folders
    statistical_folder = os.path.join(main_folder_path, 'Statistical')
    tabular_folder = os.path.join(main_folder_path, 'Tabular')

    # Create new Statistical and Tabular folders in the main folder if they don't exist
    os.makedirs(statistical_folder, exist_ok=True)
    os.makedirs(tabular_folder, exist_ok=True)

    # List all subfolders in the main folder, excluding 'Statistical' and 'Tabular'
    with os.scandir(main_folder_path) as entries:
        subfolders = [entry.path for entry in entries if entry.is_dir() and entry.name not in ('Statistical', 'Tabular')]

    # Iterate over each subfolder
    for subfolder in subfolders:
        # Paths to 'Statistical' and 'Tabular' inside the subfolder
        statistical_subfolder = os.path.join(subfolder, 'Statistical')
        tabular_subfolder = os.path.join(subfolder, 'Tabular')

        # Move all CSV files from the statistical_subfolder to the main Statistical folder
        if os.path.exists(statistical_subfolder):
            with os.scandir(statistical_subfolder) as stat_entries:
                for entry in stat_entries:
                    src_path = entry.path
                    dest_path = os.path.join(statistical_folder, entry.name)
                    os.rename(src_path, dest_path)

        # Move all CSV files from the tabular_subfolder to the main Tabular folder
        if os.path.exists(tabular_subfolder):
            with os.scandir(tabular_subfolder) as tab_entries:
                for entry in tab_entries:
                    src_path = entry.path
                    dest_path = os.path.join(tabular_folder, entry.name)
                    os.rename(src_path, dest_path)

        # Delete the original subfolder
        shutil.rmtree(subfolder)

    print("\n\033[93mFiles have been moved successfully.\033[0m")


