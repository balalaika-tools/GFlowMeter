# GFlowMeter - A Tool for Generating Datasets from PCAP Files

GFlowMeter is a Python-based tool designed to process network traffic captured in PCAP files and generate datasets suitable for machine learning applications. It can extract both tabular (hexadecimal representations) and statistical features from network flows, supporting both unidirectional and bidirectional flow types.

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Output Format](#output-format)
7. [Project Structure](#project-structure)
8. [Troubleshooting](#troubleshooting)
9. [Notes](#notes)


## Features

- **PCAP Processing**: Supports both individual PCAP files and folders containing multiple PCAP files.
- **Flow Types**: Processes both unidirectional and bidirectional flows.
- **Dataset Generation**: Generates tabular datasets (hexadecimal representations) and statistical feature datasets.
- **Configurable Parameters**: Customizable settings via a YAML configuration file.
- **Automatic Splitting**: Splits large PCAP files into smaller segments based on time intervals.
- **Output Organization**: Organizes output files into structured folders for easy access.

## Requirements


- **uv**: Fast Python package installer and resolver (recommended)
- **Editcap**: A command-line utility from the Wireshark suite for splitting PCAP files.
- **Wireshark**: Must be installed, and the `editcap` utility should be accessible via your system's environment variables (PATH).

## Installation

### 1. Install uv

**uv** is a fast Python package installer and resolver written in Rust. It's recommended for managing dependencies and running the project.

#### macOS and Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Alternative: Using pip

```bash
pip install uv
```

After installation, restart your terminal or run `source ~/.bashrc` (Linux) or `source ~/.zshrc` (macOS) to add uv to your PATH.

Verify the installation:

```bash
uv --version
```

### 2. Install Wireshark

Ensure that Wireshark is installed and that the `editcap` utility is accessible from the command line (i.e., it's in your PATH environment variable).

You can download Wireshark from [https://www.wireshark.org/download.html](https://www.wireshark.org/download.html).

### 3. Verify `editcap` Installation

Run the following command to ensure `editcap` is accessible:

```bash
editcap -h
```

If the command outputs help information, `editcap` is correctly installed and accessible.

### 4. Clone or Download the Project

```bash
git clone <repository-url>
cd GFlowMeter
```

Or download and extract the project to a directory of your choice.

### 5. Install Project Dependencies

Using **uv** (recommended):

```bash
cd GFLowMeter # if not already there
# Install the project in editable mode with all dependencies
uv sync
```

This will:
- Create a virtual environment automatically
- Install all dependencies specified in `pyproject.toml`
- Install the project in editable mode so you can use the `gflow` command



## Configuration

All configurations are managed via the `config.yaml` file located in the project's root directory.

```yaml
save_folder: 'path/to/save/output'
pcap_path: 'path/to/pcap/or/folder'

capture_interval: 1            # Time interval in seconds for splitting PCAP files
sample_type: "bidirectional"   # "bidirectional" or "unidirectional"
target_sample_length: 1024     # Number of bytes to keep per flow
dataset_type: "C"              # "A" for tabular, "B" for statistical, "C" for both
padding_per_packet: False      # Whether to pad each packet uniformly
```

### Parameters Explained

- **save_folder**: Directory where the output datasets will be saved.
- **pcap_path**: Path to a single PCAP file or a folder containing multiple PCAP files.
- **capture_interval**: The time interval (in seconds) to split large PCAP files.
- **sample_type**: Type of flow to process. Options are `"unidirectional"` or `"bidirectional"`.
- **target_sample_length**: The desired length (in bytes) for each sample in the dataset.
- **dataset_type**: Type of dataset to generate.
  - `"A"`: Tabular dataset (hexadecimal representation).
  - `"B"`: Statistical feature dataset.
  - `"C"`: Both tabular and statistical datasets.
- **padding_per_packet**: If `True`, pads each packet uniformly to reach the `target_sample_length`.

## Usage

### 1. Prepare the Configuration

Edit the `config.yaml` file in the project root directory to suit your needs. Ensure that all paths are correct and that the parameters are set as desired.

- To process multiple PCAP files, set `pcap_path` to the directory containing your PCAP files.
- Example:

  ```yaml
  save_folder: 'output'
  pcap_path: 'pcaps'
  capture_interval: 1
  sample_type: "bidirectional"
  target_sample_length: 1024
  dataset_type: "C"
  padding_per_packet: False
  ```

### 2. Run the Tool

#### Using the `gflow` Command (Recommended)


```bash
# Activate the virtual environment (uv creates it automatically)
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Then run
gflow
```

#### Using Python Directly

You can also run the module directly:

```bash
# From the project root directory
python -m GFlowMeter.main
```

Or:

```bash
# From the project root directory
uv run python -m GFlowMeter.main
```

### 3. Monitor the Output

The tool will:
- Display progress bars and status messages in the terminal
- Process each PCAP file according to the configurations
- Generate the datasets
- Log all operations and errors to the `logs/` directory

Check the `logs/` folder for detailed log files with timestamps (e.g., `gflowmeter_20241230_132828.log`).

## Output Format

The output datasets are saved in the directory specified by the `save_folder` parameter in the configuration file. The tool organizes the output into subfolders for each PCAP file processed.

### For Each PCAP File

- A subfolder is created with the name based on the original PCAP file and processing parameters.
  - Example: `pcap1_bidirectional_1024`

### Inside Each Subfolder

- **Split PCAP Files**: The original PCAP is split into smaller PCAP files based on the `capture_interval`.
  - Files are named as `split_1.pcap`, `split_2.pcap`, etc.
- **Processed Data**:
  - **Tabular**: If `dataset_type` is `"A"` or `"C"`, a `Tabular` folder is created containing CSV files.
    - Each CSV file represents a sample with hexadecimal values.
    - Files are named as `Sample_0.csv`, `Sample_1.csv`, etc.
  - **Statistical**: If `dataset_type` is `"B"` or `"C"`, a `Statistical` folder is created containing CSV files.
    - Each CSV file contains statistical features extracted from the flows.
    - Files are named as `Sample_0.csv`, `Sample_1.csv`, etc.

### Final Organization

After processing, the output structure will be:

```
output/
├── pcap1/
│   ├── Tabular/
│   │   ├── Sample_0.csv
│   │   ├── Sample_1.csv
│   │   └── ...
│   └── Statistical/
│       ├── Sample_0.csv
│       ├── Sample_1.csv
│       └── ...
├── pcap2/
│   ├── Tabular/
│   │   ├── Sample_0.csv
│   │   ├── Sample_1.csv
│   │   └── ...
│   └── Statistical/
│       ├── Sample_0.csv
│       ├── Sample_1.csv
│       └── ...
└── pcap3/
    ├── Tabular/
    │   ├── Sample_0.csv
    │   ├── Sample_1.csv
    │   └── ...
    └── Statistical/
        ├── Sample_0.csv
        ├── Sample_1.csv
        └── ...
```

Each `pcapX` folder contains the processed data for that specific PCAP file.

## Project Structure

The project follows a modern Python package structure:

```
GFlowMeter/
├── src/
│   └── GFlowMeter/
│       ├── __init__.py
│       ├── main.py              # Main entry point
│       ├── gflow.py             # GFlow_Meter class
│       ├── utils.py             # Utility functions
│       ├── logger.py            # Logging configuration
│       └── misc/
│           ├── Bi_Feature_Names.txt
│           └── Uni_Feature_Names.txt
├── logs/                        # Log files (auto-generated)
├── config.yaml                  # Configuration file
├── pyproject.toml              # Project metadata and dependencies
├── README.md                    # This file
└── .gitignore                  # Git ignore rules
```

## Output Structure

Assuming the following configuration:

- `save_folder: 'output'`
- `pcap_path: 'pcaps'`

### After Running the Tool

```
GFlowMeter/
├── src/
│   └── ...
├── logs/
│   └── gflowmeter_YYYYMMDD_HHMMSS.log
├── config.yaml
├── output/
│   ├── pcap1/
│   │   ├── Tabular/
│   │   │   ├── Sample_0.csv
│   │   │   ├── Sample_1.csv
│   │   │   └── ...
│   │   └── Statistical/
│   │       ├── Sample_0.csv
│   │       ├── Sample_1.csv
│   │       └── ...
│   ├── pcap2/
│   │   ├── Tabular/
│   │   │   └── ...
│   │   └── Statistical/
│   │       └── ...
│   └── pcap3/
│       ├── Tabular/
│       │   └── ...
│       └── Statistical/
│           └── ...
└── pcaps/
    ├── pcap1.pcap
    ├── pcap2.pcap
    └── pcap3.pcap
```

## Troubleshooting

### Common Issues

1. **`gflow: command not found`**
   - Make sure you've installed the project with `uv pip install -e .` or `pip install -e .`
   - Verify the installation: `which gflow` (Linux/macOS) or `where gflow` (Windows)
   - Try running with: `uv run gflow`

2. **`editcap: command not found`**
   - Install Wireshark and ensure `editcap` is in your PATH
   - On macOS: `brew install wireshark`
   - On Linux: `sudo apt-get install wireshark` (Ubuntu/Debian) or `sudo yum install wireshark` (RHEL/CentOS)
   - On Windows: Add Wireshark installation directory to your PATH

3. **Configuration file not found**
   - Ensure `config.yaml` exists in the current working directory
   - Or place it in the project root directory

4. **Import errors**
   - Make sure all dependencies are installed: `uv pip install -e .`
   - Check that you're using Python 3.12 or higher: `python --version`

5. **Permission errors**
   - Ensure you have read access to PCAP files and write access to the output directory
   - Check file permissions on the save folder

## Notes

- **PCAP Path Flexibility**: The `pcap_path` in the configuration can point to a single PCAP file or a folder containing multiple PCAP files. The tool will handle both cases appropriately.
- **Wireshark Requirement**: Ensure that Wireshark is installed and that the `editcap` utility is accessible via your system's environment variables (PATH). This is necessary for splitting PCAP files.
- **Data Cleanup**: Intermediate split PCAP files are removed after processing to conserve disk space.
- **Logging**: All operations and errors are logged to timestamped files in the `logs/` directory for debugging and monitoring.
- **Performance**: Processing large PCAP files can be resource-intensive. It's recommended to monitor system resources and adjust parameters as needed.
- **Virtual Environment**: When using `uv`, a virtual environment is automatically created in `.venv/`. You can activate it manually if needed.



---

