import Scripts.GFlowMeter.GFlowMeter as gflow
import Scripts.utils as util
import os 

def main():
    # Read config file 
    config = util.load_config('config.yaml')

    # Get The Pcap Files Paths, if the input is a folder
    pcap_files = []
    if os.path.isfile(config['pcap_path']): pcap_files.append(config['pcap_path'])
    else: pcap_files = util.find_pcap_files(config['pcap_path'])

    # Initialize the global sample index
    global_index = 0

    # Run GFlowMeter for each pcap file
    for pcap in pcap_files:
        sub_save_folder = os.path.join(config['save_folder'], os.path.basename(pcap).split('.')[0])
        if not os.path.exists(sub_save_folder): os.makedirs(sub_save_folder)
        
        # Split The pcap in sub pcaps based on time intervals
        util.Split_Cap(config['capture_interval'], pcap, sub_save_folder)
        for file_name in os.listdir(sub_save_folder):
            # Check if the file is a pcap or pcapng file
            if file_name.endswith('.pcap') or file_name.endswith('.pcapng'):
                file_path = os.path.join(sub_save_folder, file_name)
                tool = gflow.GFlow_Meter(file_path, sub_save_folder, config['sample_type'], config['target_sample_length'],
                                        config['dataset_type'], config['padding_per_packet'])
                num_samples = tool.Generate_Dataset(start_index=global_index)
                global_index += num_samples  # Update the global index
                os.remove(file_path)

        util.ReOrganize_Files(sub_save_folder)
        

if __name__ == "__main__":
    main()
