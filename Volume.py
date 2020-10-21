import oci
from oci.pagination import list_call_get_all_results
import Config
import sys
import logging
import logs
import time
import traceback

HTTPS_PROXY="http://proxy.verizon.com:80/"
HTTP_PROXY="http://proxy.verizon.com:80/"
https_proxy="http://proxy.verizon.com:80/"
http_proxy="http://proxy.verizon.com:80/"
no_proxy="localhost.localdomain,169.254.169.254,verizon.com,ebiz.verizon.com,vpc.verizon.com"

class Volume:
    def __init__(self):
        config = {}
        try:
            signer = Config.signer
            self.block_storage_client = oci.core.BlockstorageClient(
                config=config, signer=signer
            )
        except Exception:
            config = Config.config
            self.block_storage_client = oci.core.BlockstorageClient(config=config)

    # Request to list all volume backups
    def list_volume_backups(self, compartment_id):
        try:
            return list_call_get_all_results(
                self.block_storage_client.list_volume_backups, compartment_id, retry_strategy = oci.retry.DEFAULT_RETRY_STRATEGY
            ).data
        except oci.exceptions.ServiceError as identifier:
            logging.error(traceback.format_exc())
            logging.error(identifier+" "+compartment_id)
            exit()

    
    # Request to update the volume tags
    def update_volume_tag(self, volume_id, tag):
        try:
            volume_detail = self.block_storage_client.get_volume(volume_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            tags = volume_detail.defined_tags
            temp = dict()
            temp["InstanceName"] = tag["InstanceName"]
            temp["VSAD"] = tag["VSAD"]
            tags["Block-Storage-tags"] = temp
            if(volume_detail.lifecycle_state == "TERMINATED"):
                logging.warning("Already terminated "+" "+volume_id)
            else:
                volume_details = oci.core.models.UpdateVolumeDetails(
                    defined_tags=tags, 
                )
                self.block_storage_client.update_volume(volume_id, volume_details,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
                logging.info("Updated Volume tags", volume_id)
        except oci.exceptions.ServiceError as identifier:
            if(identifier.status == 400):
                logging.warning(volume_id+" already updated")
            else:
                logging.error(traceback.format_exc())
                logging.warning(identifier+" "+volume_id)
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error(e)
            logging.error("Volume is not present "+" "+ volume_id)

    # Request to update the volume backup tags
    def update_volume_backup_tag(self, volume_backup_id, tag):
        try:
            volume_detail = self.block_storage_client.get_volume_backup(volume_backup_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            tags = volume_detail.defined_tags
            temp = dict()
            temp["InstanceName"] = tag["InstanceName"]
            temp["VSAD"] = tag["VSAD"]
            tags["Block-Storage-tags"] = temp
            volume_backup_details = oci.core.models.UpdateVolumeBackupDetails(
                defined_tags=tags
            )
            if(volume_detail.lifecycle_state == "TERMINATED"):
                logging.warning("Already terminated "+" "+ volume_backup_id)
            else:
                self.block_storage_client.update_volume_backup(
                    volume_backup_id, volume_backup_details, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY
                )
                logging.info("Updated Volume Backup tags"+" "+ volume_backup_id)
        except oci.exceptions.ServiceError as identifier:
            if(identifier.status == 400):
                logging.error(traceback.format_exc())
                logging.warning(volume_backup_id+" already updated")
            else:
                logging.error(traceback.format_exc())
                logging.error(identifier, volume_backup_id)
        except Exception:
            logging.error(traceback.format_exc())
            logging.error("Volume Backup is not present "+" "+ volume_backup_id)
