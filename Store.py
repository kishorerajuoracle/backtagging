from Instance import Instance
from Volume import Volume
from Compartment import Compartment
from UniqueKeyDict import UniqueKeyDict
import logging
import sys
import logs
import oci
import time
import traceback

HTTPS_PROXY="http://proxy.verizon.com:80/"
HTTP_PROXY="http://proxy.verizon.com:80/"
https_proxy="http://proxy.verizon.com:80/"
http_proxy="http://proxy.verizon.com:80/"
no_proxy="localhost.localdomain,169.254.169.254,verizon.com,ebiz.verizon.com,vpc.verizon.com"


class Store:
    def __init__(self, compartment_id=None):
        self.volume_attachments = list()
        self.volume_backups = list()
        self.volume_backups_volume = UniqueKeyDict()
        self.attached_volume = UniqueKeyDict()
        self.instance_tags = UniqueKeyDict()
        self.volume_tags = UniqueKeyDict()
        self.compartment_id = compartment_id
        self.instanceObj = Instance()
        self.volumeObj = Volume()
        self.compartment_list = list()
        self.compartment_obj = Compartment()
        self.initialize()
        logging.info("VERSION 1.1")

    def update_compartment_list(self):
        if self.compartment_id:
            self.compartment_list.append(self.compartment_id)
        else:
            self.compartment_obj.store_compartments()
            self.compartment_list = [i.id for i in self.compartment_obj.compartments]

    def initialize(self):
        self.update_compartment_list()
        for i in self.compartment_list:
            self.store_volume_attachments(i)
            self.store_volume_backups_details(i)
        self.store_volume_and_volume_backups()
        self.store_attached_volume_instance()

    # Store the volume attachments so that we no need to request
    # each time to get the list of volume attachments
    def store_volume_attachments(self, compartment_id):
        for i in self.instanceObj.list_volume_attachments(compartment_id):
            if i.lifecycle_state == "ATTACHED":
                self.volume_attachments.append(i)

    def store_volume_backups_details(self, compartment_id):
        for i in self.volumeObj.list_volume_backups(compartment_id):
            self.volume_backups.append(i)

    def store_volume_and_volume_backups(self):
        for i in self.volume_backups:
            vol_id = i.volume_id
            backup_id = i.id
            self.volume_backups_volume.update({backup_id: vol_id})

    # storing the values of attached Volumes to Instance
    def store_attached_volume_instance(self):
        try:
            for i in self.volume_attachments:
                vol_id = i.volume_id
                inst_id = i.instance_id
                self.attached_volume.update({vol_id: inst_id})
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error(e)

    def get_attached_volume(self):
        return self.attached_volume

    def get_instance_tags(self, instance_id):
        try:
            return self.instance_tags[instance_id]
        except KeyError as identifier:
            logging.error(traceback.format_exc())
            logging.error(identifier)
            logging.error("Instance not present in the compartment" + instance_id)
            raise

    def get_volume_tags(self, volume_id):
        volume_id=str(volume_id)
        try:
            volume_id=str(volume_id)
            return self.volume_tags[volume_id]
        except KeyError:
            logging.error(traceback.format_exc())
            logging.error("Volume Id Incorrect " + volume_id)
            raise KeyError

    def get_volume_from_backup(self, volume_backup_id):
        try:
            return self.volume_backups_volume[volume_backup_id]
        except Exception:
            logging.error(traceback.format_exc())
            logging.error("Block Volume Backup Id Incorrect " + volume_backup_id)
            raise KeyError

    # gets the instance tag and caches the instance tags to reduce number of request
    def store_instance_tags(self, instance_id):
        print(instance_id)
        try:
            tags = self.instance_tags[instance_id]
        except KeyError:
            try:
                instance_details = self.instanceObj.get_instance_details(instance_id)
                tags = dict()
                defined_tags = instance_details.defined_tags
                tags["InstanceName"] = defined_tags["Compute-Tag"]["InstanceName"]
                tags["VSAD"] = instance_details.defined_tags["Compute-Tag"]["VSAD"]
                self.instance_tags.update({instance_id: tags})
            except KeyError:
                logging.error("Compute-tags not declared", instance_id)

    # caches the volume tags to reduce the number of request while udpating volume backup
    def store_volume_tags(self, volume_id):
        print(volume_id)
        try:
            self.volume_tags[volume_id] = self.instance_tags[
                self.attached_volume[volume_id]
            ]
        except KeyError:
            logging.error("Volume is not attached to any instance " + volume_id)

