# GFlowMeter - A Tool for Generating Datasets from PCAP Files

GFlowMeter is a Python-based tool designed to process network traffic captured in PCAP files and generate datasets suitable for machine learning applications. It can extract both tabular (hexadecimal representations) and statistical features from network flows, supporting both unidirectional and bidirectional flow types.

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Output Format](#output-format)
7. [Folder Structure](#folder-structure)
8. [Notes](#notes)


## Features

- **PCAP Processing**: Supports both individual PCAP files and folders containing multiple PCAP files.
- **Flow Types**: Processes both unidirectional and bidirectional flows.
- **Dataset Generation**: Generates tabular datasets (hexadecimal representations) and statistical feature datasets.
- **Configurable Parameters**: Customizable settings via a YAML configuration file.
- **Automatic Splitting**: Splits large PCAP files into smaller segments based on time intervals.
- **Output Organization**: Organizes output files into structured folders for easy access.

## Requirements

- **Python 3.9+**
- **Scapy**: For packet manipulation and network traffic analysis.
- **PyYAML**: For reading YAML configuration files.
- **Tqdm**: For progress bars in the terminal.
- **Editcap**: A command-line utility from the Wireshark suite for splitting PCAP files.
- **Hexdump**: For converting packet data into hexadecimal format.
- **NumPy**: For numerical operations.
- **Pandas**: For data manipulation and DataFrame support.
- **Wireshark**: Must be installed, and the `editcap` utility should be accessible via your system's environment variables (PATH).

## Installation

1. **Install Dependencies**

   Open your terminal or command prompt and run:

   ```bash
   pip install scapy pyyaml tqdm hexdump numpy pandas
   ```

2. **Install Wireshark**

   Ensure that Wireshark is installed and that the `editcap` utility is accessible from the command line (i.e., it's in your PATH environment variable).

   You can download Wireshark from [https://www.wireshark.org/download.html](https://www.wireshark.org/download.html).

3. **Verify `editcap` Installation**

   Run the following command to ensure `editcap` is accessible:

   ```bash
   editcap -h
   ```

   If the command outputs help information, `editcap` is correctly installed and accessible.

4. **Set Up the Project**

   Place the provided code files into a directory of your choice. Ensure the directory structure matches the following:

   ```
   GFlowMeter/
   ├── main.py
   ├── config.yaml
   ├── Scripts/
   │   ├── GFlowMeter/
   │   │   ├── GFlowMeter.py
   │   │   ├── Uni_Feature_Names.txt
   │   │   └── Bi_Feature_Names.txt
   │   └── utils.py
   ```

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

1. **Prepare the Configuration**

   Edit the `config.yaml` file to suit your needs. Ensure that all paths are correct and that the parameters are set as desired.

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

2. **Run the Tool**

   Open a terminal or command prompt in the project directory and execute:

   ```bash
   python main.py
   ```

3. **Monitor the Output**

   The tool will display progress bars and status messages in the terminal. It will process each PCAP file according to the configurations and generate the datasets.

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

## Folder Structure

Assuming the following configuration:

- `save_folder: 'output'`
- `pcap_path: 'pcaps'`

### Initial Structure

```
GFlowMeter/
├── main.py
├── config.yaml
├── Scripts/
│   ├── GFlowMeter/
│   │   ├── GFlowMeter.py
│   │   ├── Uni_Feature_Names.txt
│   │   └── Bi_Feature_Names.txt
│   └── utils.py
└── pcaps/
    ├── pcap1.pcap
    ├── pcap2.pcap
    └── pcap3.pcap
```

### After Running the Tool

```
GFlowMeter/
├── main.py
├── config.yaml
├── Scripts/
│   └── ...
├── output/
│   ├── pcap1_bidirectional_1024/
│   │   ├── Tabular/
│   │   │   ├── Sample_0.csv
│   │   │   ├── Sample_1.csv
│   │   │   └── ...
│   │   └── Statistical/
│   │       ├── Sample_0.csv
│   │       ├── Sample_1.csv
│   │       └── ...
│   ├── pcap2_bidirectional_1024/
│   │   ├── Tabular/
│   │   │   └── ...
│   │   └── Statistical/
│   │       └── ...
│   └── pcap3_bidirectional_1024/
│       ├── Tabular/
│       │   └── ...
│       └── Statistical/
│           └── ...
└── pcaps/
    ├── pcap1.pcap
    ├── pcap2.pcap
    └── pcap3.pcap
```

## Notes

- **PCAP Path Flexibility**: The `pcap_path` in the configuration can point to a single PCAP file or a folder containing multiple PCAP files. The tool will handle both cases appropriately.
- **Wireshark Requirement**: Ensure that Wireshark is installed and that the `editcap` utility is accessible via your system's environment variables (PATH). This is necessary for splitting PCAP files.
- **Data Cleanup**: Intermediate split PCAP files are removed after processing to conserve disk space.
- **Dependencies**: Ensure that all required Python packages and external tools like `editcap` are installed and accessible.
- **Performance**: Processing large PCAP files can be resource-intensive. It's recommended to monitor system resources and adjust parameters as needed.



---

