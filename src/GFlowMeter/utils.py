import os
import subprocess
import shutil
from typing import Dict, List, Any
from tqdm import tqdm
from .logger import get_logger

logger = get_logger()


def load_config(file_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        file_path: Path to the YAML configuration file
        
    Returns:
        Dictionary containing configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    import yaml
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        
        if config is None:
            raise ValueError("Configuration file is empty or invalid")
        
        logger.debug(f"Configuration loaded from {file_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration file {file_path}: {e}", exc_info=True)
        raise



def find_pcap_files(folder_path: str) -> List[str]:
    """
    Find all PCAP files in a directory tree.
    
    Args:
        folder_path: Path to the directory to search
        
    Returns:
        List of paths to PCAP files
        
    Raises:
        FileNotFoundError: If folder doesn't exist
        PermissionError: If folder is not accessible
    """
    try:
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Directory not found: {folder_path}")
        
        if not os.path.isdir(folder_path):
            raise ValueError(f"Path is not a directory: {folder_path}")
        
        pcap_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.pcap') or file.endswith('.pcapng'):
                    pcap_files.append(os.path.join(root, file))
        
        logger.debug(f"Found {len(pcap_files)} PCAP files in {folder_path}")
        return pcap_files
    except FileNotFoundError:
        logger.error(f"Directory not found: {folder_path}")
        raise
    except PermissionError as e:
        logger.error(f"Permission denied accessing directory {folder_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error finding PCAP files in {folder_path}: {e}", exc_info=True)
        raise




def Split_Cap(capture_interval: int, pcap_path: str, save_folder: str) -> None:
    """
    Split a PCAP file into smaller files based on time intervals.
    
    Args:
        capture_interval: Time interval in seconds for splitting
        pcap_path: Path to the input PCAP file
        save_folder: Directory where split files will be saved
        
    Raises:
        FileNotFoundError: If PCAP file or editcap command not found
        subprocess.CalledProcessError: If editcap command fails
        OSError: If file operations fail
    """
    try:
        if not os.path.exists(pcap_path):
            raise FileNotFoundError(f"PCAP file not found: {pcap_path}")
        
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
            logger.debug(f"Created save folder: {save_folder}")
        
        logger.debug(f"Splitting PCAP file {pcap_path} with interval {capture_interval}s")
        
        # Split The Pcap File Into Smaller Parts
        output_path = os.path.join(save_folder, 'Split.pcap')
        result = subprocess.run(
            ["editcap", "-i", str(capture_interval), pcap_path, output_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Rename the split files based on a naming convention
        split_files = os.listdir(save_folder)
        pcap_files = [f for f in split_files if f.endswith(('.pcap', '.pcapng'))]
        
        for i, file_name in enumerate(pcap_files, 1):
            try:
                file_base, file_extension = os.path.splitext(file_name)
                new_name = f"split_{i}{file_extension}"
                old_path = os.path.join(save_folder, file_name)
                new_path = os.path.join(save_folder, new_name)
                os.rename(old_path, new_path)
                logger.debug(f"Renamed {file_name} to {new_name}")
            except OSError as e:
                logger.warning(f"Failed to rename {file_name}: {e}")
                continue
        
        logger.debug(f"Successfully split PCAP file into {len(pcap_files)} parts")
        
    except FileNotFoundError as e:
        if 'editcap' in str(e) or not os.path.exists(pcap_path):
            logger.error(f"File or command not found: {e}")
        else:
            logger.error(f"File not found: {e}")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing editcap command: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        raise
    except OSError as e:
        logger.error(f"OS error during PCAP splitting: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error splitting PCAP file: {e}", exc_info=True)
        raise




def ReOrganize_Files(main_folder_path: str) -> None:
    """
    Reorganize files from split folders into Statistical and Tabular folders.
    
    Args:
        main_folder_path: Path to the main folder containing split folders
        
    Raises:
        FileNotFoundError: If main folder doesn't exist
        OSError: If file operations fail
    """
    try:
        if not os.path.exists(main_folder_path):
            raise FileNotFoundError(f"Main folder not found: {main_folder_path}")
        
        logger.debug("Reorganizing files")
        
        # Define the names of the new folders
        statistical_folder = os.path.join(main_folder_path, 'Statistical')
        tabular_folder = os.path.join(main_folder_path, 'Tabular')
        
        # Create the new folders
        os.makedirs(statistical_folder, exist_ok=True)
        os.makedirs(tabular_folder, exist_ok=True)
        logger.debug(f"Created Statistical and Tabular folders in {main_folder_path}")

        # Get a list of split folders
        split_folders = [item for item in os.scandir(main_folder_path) 
                        if item.name.startswith('split_') and item.is_dir()]
        
        if not split_folders:
            logger.warning(f"No split folders found in {main_folder_path}")
            return

        logger.debug(f"Found {len(split_folders)} split folders to process")

        # Iterate through the sorted split folders with tqdm progress bar
        for split_folder in tqdm(split_folders, desc="Processing subfolders", disable=len(split_folders) == 0):
            split_folder_path = split_folder.path
            logger.debug(f"Processing folder: {split_folder.name}")
            
            try:
                if len(os.listdir(split_folder_path)) == 0:
                    shutil.rmtree(split_folder_path)
                    logger.debug(f"Removed empty folder: {split_folder_path}")
                    continue

                # Paths to the statistical and tabular data within the split folder
                split_statistical_path = os.path.join(split_folder_path, 'Statistical')
                split_tabular_path = os.path.join(split_folder_path, 'Tabular')

                # Move Statistical files using os.scandir (no need to load all files into memory)
                if os.path.exists(split_statistical_path):
                    moved_count = 0
                    with os.scandir(split_statistical_path) as it:
                        for entry in it:
                            if entry.is_file() and entry.name.endswith('.csv'):
                                try:
                                    src_path = entry.path
                                    dest_path = os.path.join(statistical_folder, entry.name)
                                    shutil.move(src_path, dest_path)
                                    moved_count += 1
                                except OSError as e:
                                    logger.warning(f"Failed to move statistical file {entry.name}: {e}")
                                    continue
                    logger.debug(f"Moved {moved_count} statistical files from {split_folder.name}")

                # Move Tabular files using os.scandir
                if os.path.exists(split_tabular_path):
                    moved_count = 0
                    with os.scandir(split_tabular_path) as it:
                        for entry in it:
                            if entry.is_file() and entry.name.endswith('.csv'):
                                try:
                                    src_path = entry.path
                                    dest_path = os.path.join(tabular_folder, entry.name)
                                    shutil.move(src_path, dest_path)
                                    moved_count += 1
                                except OSError as e:
                                    logger.warning(f"Failed to move tabular file {entry.name}: {e}")
                                    continue
                    logger.debug(f"Moved {moved_count} tabular files from {split_folder.name}")

                # Delete the now empty split folder
                try:
                    shutil.rmtree(split_folder_path)
                    logger.debug(f"Deleted split folder: {split_folder_path}")
                except OSError as e:
                    logger.warning(f"Failed to delete {split_folder_path}: {e}")
                    
            except Exception as e:
                logger.error(f"Error processing split folder {split_folder_path}: {e}", exc_info=True)
                continue

        logger.debug("Files have been reorganized successfully")
        
    except FileNotFoundError as e:
        logger.error(f"Folder not found: {e}")
        raise
    except OSError as e:
        logger.error(f"OS error during file reorganization: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error reorganizing files: {e}", exc_info=True)
        raise


def load_config_with_fallback(config_name: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load configuration file with fallback to project root.
    
    Args:
        config_name: Name of the config file (default: 'config.yaml')
        
    Returns:
        Dictionary containing configuration
        
    Raises:
        FileNotFoundError: If config file not found
        SystemExit: If config cannot be loaded
    """
    import sys
    from pathlib import Path
    
    try:
        config = load_config(config_name)
        logger.debug("Configuration file loaded successfully")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file '{config_name}' not found in current directory")
        # Try to find it in project root
        try:
            # Get project root (assuming this is called from src/GFlowMeter/)
            # We need to go up 3 levels: src/GFlowMeter -> src -> project root
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            config_path = project_root / config_name
            if config_path.exists():
                config = load_config(str(config_path))
                logger.debug(f"Configuration file loaded from project root: {config_path}")
                return config
            else:
                raise FileNotFoundError(f"{config_name} not found in current directory or project root")
        except Exception as e:
            logger.error(f"Failed to load configuration file: {e}", exc_info=True)
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading configuration file: {e}", exc_info=True)
        sys.exit(1)


def validate_config(config: Dict[str, Any], required_keys: List[str]) -> None:
    """
    Validate that all required keys are present in the configuration.
    
    Args:
        config: Configuration dictionary
        required_keys: List of required configuration keys
        
    Raises:
        SystemExit: If any required keys are missing
    """
    import sys
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        logger.error(f"Missing required configuration keys: {missing_keys}")
        sys.exit(1)


def get_pcap_files_list(pcap_path: str) -> List[str]:
    """
    Get list of PCAP files from a path (single file or directory).
    
    Args:
        pcap_path: Path to a PCAP file or directory containing PCAP files
        
    Returns:
        List of PCAP file paths
        
    Raises:
        SystemExit: If path doesn't exist or no files found
    """
    import sys
    
    try:
        pcap_files = []
        if os.path.isfile(pcap_path):
            pcap_files.append(pcap_path)
            logger.debug(f"Processing single PCAP file: {pcap_path}")
        else:
            pcap_files = find_pcap_files(pcap_path)
            logger.debug(f"Found {len(pcap_files)} PCAP files in directory: {pcap_path}")
        
        if not pcap_files:
            logger.warning(f"No PCAP files found at path: {pcap_path}")
            return []
        
        return pcap_files
    except Exception as e:
        logger.error(f"Error finding PCAP files: {e}", exc_info=True)
        sys.exit(1)


def process_split_file(
    file_path: str,
    file_name: str,
    sub_save_folder: str,
    config: Dict[str, Any],
    start_index: int
) -> int:
    """
    Process a single split PCAP file and generate dataset.
    
    Args:
        file_path: Full path to the split PCAP file
        file_name: Name of the split file
        sub_save_folder: Folder where results will be saved
        config: Configuration dictionary
        start_index: Starting index for sample numbering
        
    Returns:
        Number of samples generated
        
    Raises:
        Exception: If processing fails
    """
    from . import gflow
    
    logger.debug(f"Processing split file: {file_name}")
    
    tool = gflow.GFlow_Meter(
        file_path,
        sub_save_folder,
        config['sample_type'],
        config['target_sample_length'],
        config['dataset_type'],
        config['padding_per_packet']
    )
    
    num_samples = tool.Generate_Dataset(start_index=start_index)
    logger.debug(f"Generated {num_samples} samples from {file_name}")
    
    os.remove(file_path)
    logger.debug(f"Removed processed file: {file_path}")
    
    return num_samples


def process_pcap_file(
    pcap: str,
    pcap_idx: int,
    total_pcaps: int,
    config: Dict[str, Any],
    start_index: int
) -> int:
    """
    Process a single PCAP file: split, process splits, and reorganize.
    
    Args:
        pcap: Path to the PCAP file
        pcap_idx: Current PCAP file index (1-based)
        total_pcaps: Total number of PCAP files to process
        config: Configuration dictionary
        start_index: Starting index for sample numbering
        
    Returns:
        Number of samples generated from this PCAP file
    """
    logger.debug(f"Processing PCAP file {pcap_idx}/{total_pcaps}: {os.path.basename(pcap)}")
    
    # Create save folder for this PCAP
    sub_save_folder = os.path.join(config['save_folder'], os.path.basename(pcap).split('.')[0])
    if not os.path.exists(sub_save_folder):
        os.makedirs(sub_save_folder)
        logger.debug(f"Created save folder: {sub_save_folder}")
    
    # Split the PCAP file
    try:
        Split_Cap(config['capture_interval'], pcap, sub_save_folder)
        logger.debug(f"Split PCAP file into sub-files")
    except Exception as e:
        logger.error(f"Error splitting PCAP file {pcap}: {e}", exc_info=True)
        return 0
    
    # Get list of split files
    split_files = [f for f in os.listdir(sub_save_folder)
                   if f.endswith('.pcap') or f.endswith('.pcapng')]
    
    # Print to console how many sub-pcaps were created
    print(f"\n📦 Split '{os.path.basename(pcap)}' into \033[94m{len(split_files)}\033[0m sub-PCAP files")
    
    # Process each split file
    global_index = start_index
    for file_name in split_files:
        try:
            file_path = os.path.join(sub_save_folder, file_name)
            num_samples = process_split_file(
                file_path,
                file_name,
                sub_save_folder,
                config,
                global_index
            )
            global_index += num_samples
        except Exception as e:
            logger.error(f"Error processing split file {file_name}: {e}", exc_info=True)
            continue
    
    # Reorganize files
    try:
        ReOrganize_Files(sub_save_folder)
        logger.debug(f"Reorganized files for {os.path.basename(pcap)}")
    except Exception as e:
        logger.error(f"Error reorganizing files for {pcap}: {e}", exc_info=True)
    
    return global_index - start_index
    