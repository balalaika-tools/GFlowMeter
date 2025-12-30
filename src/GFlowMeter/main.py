from . import utils as util
from .logger import setup_logger
import sys

def main():
    """Main entry point for GFlowMeter."""
    logger = setup_logger()
    
    try:
        logger.debug("Starting GFlowMeter")
        
        # Load and validate configuration
        config = util.load_config_with_fallback('config.yaml')
        required_keys = ['pcap_path', 'save_folder', 'capture_interval', 'sample_type',
                        'target_sample_length', 'dataset_type', 'padding_per_packet']
        util.validate_config(config, required_keys)
        
        # Get list of PCAP files to process
        pcap_files = util.get_pcap_files_list(config['pcap_path'])
        if not pcap_files:
            return
        
        # Process each PCAP file
        global_index = 0
        for pcap_idx, pcap in enumerate(pcap_files, 1):
            try:
                num_samples = util.process_pcap_file(
                    pcap,
                    pcap_idx,
                    len(pcap_files),
                    config,
                    global_index
                )
                global_index += num_samples
            except Exception as e:
                logger.error(f"Error processing PCAP file {pcap}: {e}", exc_info=True)
                continue
        
        logger.debug(f"GFlowMeter completed successfully. Total samples generated: {global_index}")
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"Unexpected error in main: {e}", exc_info=True)
        sys.exit(1)
        

if __name__ == "__main__":
    main()