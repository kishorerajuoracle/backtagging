import oci
import configparser


from oci.config import from_file
config = from_file(file_location="~/.oci/config")
