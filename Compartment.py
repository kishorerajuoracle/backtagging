import Config
import oci
from oci.identity import IdentityClient


# Gets all the compartments from a tenancy
class Compartment:
	def __init__(self):
		config = {}
		try:
			signer = Config.signer
			self.identity = IdentityClient(config=config, signer=signer)
			self.compartment_id = Config.tenancy_id
		except Exception:
			config = Config.config
			self.identity = IdentityClient(config)
			self.compartment_id = config["tenancy"]
		
		self.compartments = list()
		self.availability_domain_list = list()
		self.update_ads()
		
    # send requests to list all compartments and its child
	def list_compartments(self):
		return oci.pagination.list_call_get_all_results(self.identity.list_compartments,
            self.compartment_id,
            compartment_id_in_subtree=True, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data

	# Return compartment data and store in a list		
	def store_compartments(self):
		for compartment in self.list_compartments():
			self.compartments.append(compartment)


	def list_availability_domain(self):
		return self.identity.list_availability_domains(self.compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data

	def update_ads(self):
		for i in self.list_availability_domain():
			self.availability_domain_list.append(i)

	def get_compartment_name(self, ids):
		return [i.name for i in self.compartments if i.id == ids][0]
			
	def get_compartment_id_list(self):
		return self.compartments
		

