import oci
from Volume import Volume
from Instance import Instance
from Store import Store
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

class Tag:
    def __init__(self, compartment_id=None):
        self.storeObj = Store(compartment_id)
        self.volumeObj = Volume()
        self.initialize()

    def initialize(self):
        self.store_tags()
        

    # updates all the volume tags present in volume attachments
    def store_tags(self):
        for i in self.storeObj.volume_attachments:
            self.storeObj.store_instance_tags(i.instance_id)
            self.storeObj.store_volume_tags(i.volume_id)

    def list_backups_from_volume(self, volume_id):
        try:
            volume_backups = [backup_id for backup_id, vol_id in self.storeObj.volume_backups_volume.items() if vol_id==volume_id]
            # print(self.storeObj.volume_backups_volume)
        except Exception:
            logging.error(traceback.format_exc())
            logging.error("No backups")
            volume_backups = None
        return volume_backups


    # updates the volume tag
    def update_volume_tag(self, volume_id):
        volume_id=str(volume_id)
        try:
            self.volumeObj.update_volume_tag(str(volume_id),self.storeObj.get_volume_tags(volume_id))
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error(volume_id+" "+e)

    def update_volume_backup_tag(self, volume_backup_id, tag):
        self.volumeObj.update_volume_backup_tag(volume_backup_id, tag)

 
    def get_volume_from_backup(self, volume_backup_id):
        try:
            return self.storeObj.get_volume_from_backup(volume_backup_id)
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error(volume_backup_id+" "+e)
            raise KeyError

    def update_backup_tags_from_volume(self, volume_id):
        try:
            for backup_id in self.list_backups_from_volume(volume_id):
                self.update_volume_backup_tag(backup_id, self.storeObj.get_volume_tags(volume_id))
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error(volume_id+" "+e)

    def update_tags_from_compartment(self):
        try:
            for volume_id in self.storeObj.attached_volume.keys():
                self.update_volume_tag(volume_id)
                self.update_backup_tags_from_volume(volume_id)
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error(e)
        
