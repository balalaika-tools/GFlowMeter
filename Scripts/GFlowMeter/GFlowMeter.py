import warnings, logging, os, tqdm, hexdump, time
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
warnings.simplefilter("ignore", DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, message="No IPv4 address found on .*")
import scapy.all
import pandas as pd
import numpy as np
from sys import platform
if platform == 'darwin' or platform == 'linux1' or platform == 'linux2':
    from scapy.config import conf
    conf.use_pcap = True

'''
A: Tabular
B: Statistical
C: Tabular + Statistical
'''

class GFlow_Meter():
    def __init__(self, pcap_path, save_folder_path=None, sample_type='bidirectional', target_sample_length=784,
                dataset_type='C', padding_per_packet=False):
        # Path Handling
        self.pcap_path = pcap_path
        self.save_folder_name = os.path.basename(self.pcap_path).split('.')[0] + f'_{sample_type}_{target_sample_length}'
        if save_folder_path is None:
            pcap_folder = os.path.dirname(os.path.abspath(self.pcap_path))
            self.save_folder = os.path.join(pcap_folder, self.save_folder_name)
        else:
            self.save_folder = os.path.join(save_folder_path, self.save_folder_name)
        if not os.path.exists(self.save_folder): os.makedirs(self.save_folder)

        # Save Parameters
        self.dataset_type = dataset_type
        self.sample_type = sample_type
        self.target_sample_length = target_sample_length
        self.padding_per_packet = padding_per_packet

        # Check Dataset Type
        valid_dataset_types= {'A', 'B', 'C'}
        if self.dataset_type not in valid_dataset_types:
            raise Exception("Wrong Dataset Type. Try 'A', 'B' or 'C'")

        # Check Flow-Types
        if self.sample_type!= 'unidirectional' and self.sample_type!= 'bidirectional':
            raise Exception("Wrong Sample Type. Try 'unidirectional' or 'bidirectional'")

        # Layers Setup
        self.tcp_layer = scapy.layers.inet.TCP
        self.udp_layer = scapy.layers.inet.UDP
        self.sctp_layer = scapy.layers.sctp.SCTP

        # Read_Feature_Names
        if self.Check_For_Statistical():
            self.feature_names = []
            feature_names_path = 'Scripts/GFlowMeter/Bi_Feature_Names.txt' if sample_type == 'bidirectional' \
            else 'Scripts/GFlowMeter/Uni_Feature_Names.txt'
            with open(os.path.join(os.getcwd(), feature_names_path)) as file:
                self.feature_names = [line.rstrip() for line in file]
            self.df_statistical = pd.DataFrame(columns=self.feature_names, dtype=float)




    def Check_For_Statistical(self):
        if self.dataset_type == 'B' or self.dataset_type =='C':
            return True
        else:
            return False




    def Check_For_Tabular (self):
        if self.dataset_type == 'A' or self.dataset_type =='C':
            return True
        else:
            return False




    def Generate_Dataset(self, start_index=0):
        capture = self.Capture_Flows()
        # Check for Sub-cases
        if self.Check_For_Tabular():
            samples, num_samples, session_sample_index = self.Get_Hex_Flows(capture, start_index)
            if len(samples) == 0: return 0
            self.Generate_Tabular_Dataset(samples)
            # Check for statistical
            if self.Check_For_Statistical():
                self.Generate_Statistical_Dataset(capture, session_sample_index)
            return num_samples

        # Sub-Case 3
        if self.Check_For_Statistical():
            self.Generate_Statistical_Dataset(capture, session_sample_index)
            return num_samples




    def Generate_Tabular_Dataset(self, samples):
        print('\033[92mGenerating Tabular Dataset\033[0m')
        tic = time.time()
        samples_df = pd.DataFrame(samples)
        samples_df.reset_index(drop=True, inplace=True)

        # Export Data
        save_folder_path = os.path.join(self.save_folder, 'Tabular')
        if not os.path.exists(save_folder_path): os.makedirs(save_folder_path)
        # Iterate over each row in the dataframe
        for idx, row in samples_df.iterrows():
            filename = f"Sample_{row['Sample_Index']}.csv"
            # Convert the row to a dataframe and drop the Sample_Index column
            row_df = pd.DataFrame([row.drop('Sample_Index')])
            # Save the row as a CSV file
            row_df.to_csv(os.path.join(save_folder_path, filename), index=False)

        toc = time.time()
        print(f"Tabular Generated, \033[94m{(toc - tic) / 60:.3}\033[0m minutes")




    def Generate_Statistical_Dataset(self, capture, session_sample_index):
        print('\033[92mGenerating Statistical Dataset\033[0m')
        tic = time.time()
        samples = self.Get_Statistical_Features(capture, session_sample_index)
        if len(samples) == 0: return

        # Export Data
        save_folder_path = os.path.join(self.save_folder, 'Statistical')
        if not os.path.exists(save_folder_path): os.makedirs(save_folder_path)
        # Iterate over each row in the dataframe
        for idx, row in samples.iterrows():
            filename = f"Sample_{int(row['Sample_Index'])}.csv"
            # Convert the row to a dataframe and drop the Sample_Index column
            row_df = pd.DataFrame([row.drop('Sample_Index')])
            # Save the row as a CSV file
            row_df.to_csv(os.path.join(save_folder_path, filename), index=False)

        toc = time.time()
        print(f"Statistical Generated, \033[94m{(toc - tic) / 60:.3}\033[0m minutes")




    def Capture_Flows(self):
        tic = time.time()
        print(f'\n\033[94mCapturing\033[0m {os.path.basename(self.pcap_path)}')
        capture = scapy.all.sniff(offline=self.pcap_path)
        if self.sample_type == 'unidirectional':
            capture = capture.sessions(self.Unidirectional_Flows_Split)
        elif self.sample_type == 'bidirectional':
            capture = capture.sessions(self.Bidirectional_Sessions_Split)
        else:
            raise Exception("PROVIDED sample_type IS INVALID")
        toc = time.time()
        print(f'Capture Ended, \033[94m{(toc - tic) / 60:.3}\033[0m minutes')
        return capture




    def Unidirectional_Flows_Split(self, packet):
        ip_layer = scapy.layers.inet.IP if 'IP' in packet else scapy.layers.inet6.IPv6
        if ('IP' in packet) or ('IPv6' in packet):
            if 'TCP' in packet:
                sess = str(['TCP', packet[ip_layer].src, packet[self.tcp_layer].sport,
                            packet[ip_layer].dst, packet[self.tcp_layer].dport])
            elif 'UDP' in packet:
                sess = str(['UDP', packet[ip_layer].src, packet[self.udp_layer].sport,
                            packet[ip_layer].dst, packet[self.udp_layer].dport])

            elif 'SCTP' in packet:
                sess = str(['SCTP', packet[ip_layer].src, packet[self.sctp_layer].sport,
                            packet[ip_layer].dst, packet[self.sctp_layer].sport])
            else:
                sess = str(['IP_Based_Sorted', packet[ip_layer].src, packet[ip_layer].dst])
        else:
            sess = packet.sprintf("No_IPv4_or_IPV6 --> Ethernet type=%04xr,Ether.type%")
        return sess




    def Bidirectional_Sessions_Split(self, packet):
        ip_layer = scapy.layers.inet.IP if 'IP' in packet else scapy.layers.inet6.IPv6
        if ('IP' in packet) or ('IPv6' in packet):
            if 'TCP' in packet:
                sess = str(['TCP'] + sorted([packet[ip_layer].src, str(packet[self.tcp_layer].sport),
                                             packet[ip_layer].dst, str(packet[self.tcp_layer].dport)],
                                            key=str))
            elif 'UDP' in packet:
                sess = str(['UDP'] + sorted([packet[ip_layer].src, str(packet[self.udp_layer].sport),
                                             packet[ip_layer].dst, str(packet[self.udp_layer].dport)],
                                            key=str))
            elif 'SCTP' in packet:
                sess = str(['SCTP'] + sorted([packet[ip_layer].src, str(packet[self.sctp_layer].sport),
                                              packet[ip_layer].dst, str(packet[self.sctp_layer].dport)],
                                             key=str))
            else:
                sess = str(['IP_Based_Sorted', packet[ip_layer].src, packet[ip_layer].dst])
        else:
            sess = packet.sprintf("No_IPv4_or_IPV6 --> Ethernet type=%04xr,Ether.type%")
        return sess




    def Get_Hex_Flows(self, capture, start_index):
        samples = []
        sample_index = start_index
        session_sample_index = {}  # Map session keys to sample indices
        for packet_description, packet_list in tqdm.tqdm(capture.items(), total=len(capture),
                                                         desc='\033[97mProcess Flows\033[0m', colour='green'):
            sample_packets = []
            if self.Check_For_Protocols(packet_description):
                session_sample_index[packet_description] = sample_index  # Assign sample_index to session
                for packet in packet_list:
                    processed_packet = self.Process_Packet(packet)
                    if self.padding_per_packet is True:
                        processed_packet = self.Pad_Sample(processed_packet,
                                                           int(self.target_sample_length / len(packet_list)))
                    sample_packets += processed_packet
                sample_packets = self.Pad_Sample(sample_packets, self.target_sample_length)
                # Add the sample index to the sample data
                sample_data = {'Sample_Index': sample_index}
                sample_data.update({i: val for i, val in enumerate(sample_packets)})
                samples.append(sample_data)
                sample_index += 1
            else:
                continue
        num_samples = sample_index - start_index
        return samples, num_samples, session_sample_index




    def Check_For_Protocols(self, packet_description):
        ck1, ck2, ck3, ck4 = False, False, False, False
        if 'TCP' in packet_description:
            ck1 = True
        elif 'UDP' in packet_description:
            ck2 = True
        elif 'ICMPv4' in packet_description:
            ck3 = True
        elif 'SCTP' in packet_description:
            ck4 = True
        return ck1 or ck2 or ck3 or ck4




    def Process_Packet(self, packet):
        ip_layer = scapy.layers.inet.IP if 'IP' in packet else scapy.layers.inet6.IPv6
        hex_stream = hexdump.dump(scapy.all.Raw(packet).load, sep=' ')

        # Remove Mac Addresses
        if 'Ether' in packet:
            hex_stream = hex_stream[42:]
        elif 'CookedLinux' in packet:
            hex_stream = hex_stream[48:]
        elif 'CookedLinuxV2' in packet:
            hex_stream = hex_stream[60:]

        # Remove IPs and Ports
        if ip_layer is scapy.layers.inet6.IPv6:
            # hex_stream = hex_stream[0:36] + hex_stream[132:]  # Use this for Keeping Src and Dst Ports
            hex_stream = hex_stream[0:36] + hex_stream[144:]
            hex_stream = [int(element, base=16) for element in hex_stream.split(" ")]
            return hex_stream
        else:
            if packet.getlayer(ip_layer).version == 4:
                # hex_stream = hex_stream[0:36] + hex_stream[60:] # Use this for Keeping Src and Dst Ports
                hex_stream = hex_stream[0:36] + hex_stream[72:]
            elif packet.getlayer(ip_layer).version == 6:
                # hex_stream = hex_stream[0:36] + hex_stream[132:] # Use this for Keeping Src and Dst Ports
                hex_stream = hex_stream[0:36] + hex_stream[144:]
            hex_stream = [int(element, base=16) for element in hex_stream.split(" ")]
            return hex_stream




    def Pad_Sample(self, sample, target_sample_length):
        sample_length = len(sample)
        pad = target_sample_length - sample_length
        if pad == 0:
            return sample
        elif pad > 0:
            sample = sample + [0 for i in range(pad)]
        else:
            sample = sample[:target_sample_length]
        return sample




    def Get_Statistical_Features(self, capture, session_sample_index):
        if self.sample_type == 'unidirectional':
            fwd = self.Get_Unidirectional_Flow_List(capture, session_sample_index)
        else:
            fwd, bwd = self.Get_Bidirectional_Flow_List(capture, session_sample_index)
        # Return if no sessions of desired protocols are found
        if len(fwd) == 0: return []
        # Extract Unidirectional Features
        Dataframes, Fwd_Timestamps = [], []

        for idx, fwd_flow in enumerate(fwd):
            fwd_df = self.df_statistical.copy()
            fwd_df, fwd_timestamps = self.Extract_Fwd_Features(fwd_flow, fwd_df)
            fwd_df['Sample_Index'] = fwd_flow[0].sample_index  # Assign the sample index
            Dataframes.append(fwd_df)
            Fwd_Timestamps.append(fwd_timestamps)
        if self.sample_type == 'unidirectional':
            return pd.concat(Dataframes, ignore_index=True)

        # Extract Bidirectional and Total Features
        for idx, (bwd_flow, df, fwd_timestamps) in enumerate(zip(bwd, Dataframes, Fwd_Timestamps)):
            # Extract Bwd Features
            df, bwd_timestamps = self.Extract_Bwd_Features(bwd_flow, df)
            # Extract Total Features
            df = self.Calculate_Total_Size_Features(df)
            timestamps = fwd_timestamps + bwd_timestamps
            df = self.Calculate_Temporal_Features(timestamps, df, 'Flow ')
            Dataframes[idx] = df
        return pd.concat(Dataframes, ignore_index=True)




    def Get_Unidirectional_Flow_List(self, capture, session_sample_index):
        fwd = []
        for packet_description, packet_list in tqdm.tqdm(capture.items(), total=len(capture),
                                                         desc='\033[97mProcess Unidirectional Flows\033[0m',
                                                         colour='green'):
            if self.Check_For_Protocols(packet_description):
                sample_index = session_sample_index.get(packet_description)
                if sample_index is None:
                    continue  # or handle error
                # Assign sample_index to packets
                for packet in packet_list:
                    packet.sample_index = sample_index
                fwd.append(packet_list)
        return fwd




    def Get_Bidirectional_Flow_List(self, capture, session_sample_index):
        fwd, bwd = [], []
        for packet_description, packet_list in tqdm.tqdm(capture.items(), total=len(capture),
                                                         desc='\033[97mProcess Bidirectional Flows\033[0m',
                                                         colour='green'):
            if self.Check_For_Protocols(packet_description):
                sample_index = session_sample_index.get(packet_description)
                if sample_index is None:
                    continue  # or handle error
                # Get the srcIP of the first packet
                ip_layer = scapy.layers.inet.IP if 'IP' in packet_list[0] else scapy.layers.inet6.IPv6
                src_IP = packet_list[0][ip_layer].src
                fwd_flow, bwd_flow = [], []
                for packet in packet_list:
                    packet.sample_index = sample_index  # Assign sample_index
                    if packet[ip_layer].src == src_IP:
                        fwd_flow.append(packet)
                    else:
                        bwd_flow.append(packet)
                fwd.append(fwd_flow)
                bwd.append(bwd_flow)
        return fwd, bwd




    def Extract_Fwd_Features(self, fwd_flow, fwd_df):
        fwd_timestamps, fwd_total_bytes, fwd_payload_bytes = [], [], []
        for packet in fwd_flow:
            fwd_timestamps.append(float(packet.time))
            fwd_total_bytes.append(packet.__len__())
            fwd_payload_bytes.append(packet.payload.__len__())

        description = 'Fwd ' if self.sample_type == 'bidirectional' else 'Flow '
        # Calculate Size Features
        fwd_df = self.Calculate_Size_Features(len(fwd_flow), fwd_total_bytes, fwd_payload_bytes, fwd_df, description)

        # Calculate Temporal Features
        fwd_df = self.Calculate_Temporal_Features(fwd_timestamps, fwd_df, description)
        return fwd_df, fwd_timestamps




    def Calculate_Size_Features(self, packet_num, total_bytes, payload_bytes, df, description='Flow '):
        # These Feature have no problem if the flow contains only one packet
        df.loc[0, f'{description}Total Packets'] = packet_num
        df.loc[0, f'{description}Total Bytes'] = sum(total_bytes)

        df.loc[0, f'{description}Packet Bytes Min'] = min(total_bytes)
        df.loc[0, f'{description}Packet Bytes Max'] = max(total_bytes)
        df.loc[0, f'{description}Packet Bytes Avg'] = sum(total_bytes) / len(total_bytes)
        df.loc[0, f'{description}Packet Bytes Variance'] = np.var(total_bytes)

        df.loc[0, f'{description}Payload Bytes Min'] = min(payload_bytes)
        df.loc[0, f'{description}Payload Bytes Max'] = max(payload_bytes)
        df.loc[0, f'{description}Payload Bytes Avg'] = sum(payload_bytes) / len(payload_bytes)
        df.loc[0, f'{description}Payload Bytes Variance'] = np.var(payload_bytes)

        df.loc[0, f'{description}Header Bytes'] = np.sum(np.array(total_bytes) - np.array(payload_bytes))
        return df




    def Calculate_Temporal_Features(self, timestamps, df, description='Flow '):
        timestamps.sort()
        if (len(timestamps) == 1) or (timestamps[0] == 0 and len(timestamps) == 2):
            df = self.Handle_Temporal_Exceptions(df, description)
        else:
            pairwise_diff = np.diff(timestamps)
            if timestamps[0] == 0:
                df.loc[0, f'{description}Duration'] = timestamps[-1] - timestamps[1]
                pairwise_diff = pairwise_diff[1:]
            else:
                df.loc[0, f'{description}Duration'] = timestamps[-1] - timestamps[0]

            # Exception where timestamps are all the same for some reason (maybe the split)
            if df[f'{description}Duration'][0] == 0:
                df = self.Handle_Temporal_Exceptions(df, description)
                return df
            df.loc[0, f'{description}Bytes/s'] = df[f'{description}Total Bytes'][0] / df.loc[
                0, f'{description}Duration']
            df.loc[0, f'{description}Packets/s'] = len(timestamps) / (timestamps[-1] - timestamps[0])

            df.loc[0, f'{description}IAT Total'] = pairwise_diff.sum()
            df.loc[0, f'{description}IAT Min'] = pairwise_diff.min()
            df.loc[0, f'{description}IAT Max'] = pairwise_diff.max()
            df.loc[0, f'{description}IAT Avg'] = pairwise_diff.mean()
            df.loc[0, f'{description}IAT Variance'] = np.var(pairwise_diff)
        return df




    def Handle_Temporal_Exceptions(self, df, description):
        # Handles the cases where you have only one timestamp or zero timestamps (and assign 0 on the value)
        df.loc[0, f'{description}Duration'] = 0
        df.loc[0, f'{description}Bytes/s'] = 0

        df.loc[0, f'{description}Packets/s'] = 0
        df.loc[0, f'{description}IAT Total'] = 0
        df.loc[0, f'{description}IAT Min'] = 0
        df.loc[0, f'{description}IAT Max'] = 0
        df.loc[0, f'{description}IAT Avg'] = 0
        df.loc[0, f'{description}IAT Variance'] = 0
        return df




    def Extract_Bwd_Features(self, bwd_flow, df):
        if len(bwd_flow) == 0:
            bwd_timestamps, bwd_total_bytes, bwd_payload_bytes = [0], [0], [0]
        else:
            bwd_timestamps, bwd_total_bytes, bwd_payload_bytes = [], [], []
            for packet in bwd_flow:
                bwd_timestamps.append(float(packet.time))
                bwd_total_bytes.append(packet.__len__())
                bwd_payload_bytes.append(packet.payload.__len__())
        description = 'Bwd '
        # Calculate Size Features
        df = self.Calculate_Size_Features(len(bwd_flow), bwd_total_bytes, bwd_payload_bytes, df, description)

        # Calculate Temporal Features
        df = self.Calculate_Temporal_Features(bwd_timestamps, df, description)
        return df, bwd_timestamps




    def Calculate_Total_Size_Features(self, df):
        df.loc[0, 'Flow Total Packets'] = df['Fwd Total Packets'][0] + df['Bwd Total Packets'][0]
        df.loc[0, 'Flow Total Bytes'] = df['Fwd Total Bytes'][0] + df['Bwd Total Bytes'][0]

        df.loc[0, 'Flow Packet Bytes Min'] = min(df['Fwd Packet Bytes Min'][0], df['Bwd Packet Bytes Min'][0])
        df.loc[0, 'Flow Packet Bytes Max'] = max(df['Fwd Packet Bytes Max'][0], df['Bwd Packet Bytes Max'][0])
        df.loc[0, 'Flow Packet Bytes Avg'] = (df['Fwd Packet Bytes Avg'][0] + df['Bwd Packet Bytes Avg'][0]) / 2
        df.loc[0, f'Flow Packet Bytes Variance'] = ((df['Fwd Packet Bytes Variance'][0] * df['Fwd Total Packets'][0])
                                                    + (df['Bwd Packet Bytes Variance'][0] * df['Bwd Total Packets'][
                    0])) / (df['Fwd Total Packets'][0] + df['Bwd Total Packets'][0])

        df.loc[0, 'Flow Payload Bytes Min'] = min(df['Fwd Payload Bytes Min'][0], df['Bwd Payload Bytes Min'][0])
        df.loc[0, 'Flow Payload Bytes Max'] = max(df['Fwd Payload Bytes Max'][0], df['Bwd Payload Bytes Max'][0])
        df.loc[0, 'Flow Payload Bytes Avg'] = (df['Fwd Payload Bytes Avg'][0] + df['Bwd Payload Bytes Avg'][0]) / 2
        df.loc[0, 'Flow Payload Bytes Variance'] = ((df['Fwd Payload Bytes Variance'][0] * df['Fwd Total Packets'][0])
                                                    + (df['Bwd Payload Bytes Variance'][0] * df['Bwd Total Packets'][
                    0])) / (df['Fwd Total Packets'][0] + df['Bwd Total Packets'][0])

        df.loc[0, 'Flow Header Bytes'] = df['Fwd Header Bytes'][0] + df['Bwd Header Bytes'][0]
        return df
