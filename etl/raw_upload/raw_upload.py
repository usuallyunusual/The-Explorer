import json
import glob
import logging

from etl.counters import Counters
from etl.io.s3_io_helper import S3IOHelper
from etl.serde.avro_serde import AvroSerde
from etl.raw_upload.sts_helper import STSHelper
from etl.raw_upload.wiki_helper import WikiHelper


class RawUpload:

    def __init__(self, config_file, decrypt):
        self.LOGGER = logging.getLogger(self.__class__.__name__)
        self.config_file = config_file
        self.decrypt = decrypt

    def raw_upload(self):
        self.LOGGER.info("Running RawUpload.")
        parsed_configs = self.parse_config()
        self.LOGGER.info(f"Configuration : \n{json.dumps(parsed_configs, indent=2)}")
        sts_helper = STSHelper(
            parsed_configs["aws_s3_role_arn"],
            "explorer-etl-session",
            parsed_configs["aws_iam_user_key"],
            parsed_configs["aws_iam_user_secret"]
        )
        self.LOGGER.info(f"Created STSHelper.")
        with open(parsed_configs["schema_file"], "r") as schema_file:
            schema = schema_file.read()
        self.LOGGER.info(f"Read schema from {parsed_configs['schema_file']} successfully.")
        serde = AvroSerde(
            schema,
            parsed_configs["temp_directory"]
        )
        self.LOGGER.info(f"Created serializer/deserializer.")
        io_helper = S3IOHelper(
            serde,
            sts_helper,
            parsed_configs["bucket_name"])
        self.LOGGER.info(f"Created IO helper.")
        wiki_helper = WikiHelper(
            parsed_configs["source"],
            parsed_configs["destination"],
            io_helper,
            parsed_configs["chunk_num_records"]
        )
        self.LOGGER.info(f"Created WikiHelper. Beginning extract and upload.")
        wiki_helper.extract_to_destination()

    def parse_config(self):
        parsed_configs = dict()
        try:
            with open(self.config_file, 'r') as file:
                configs = json.loads(file.read())
        except FileNotFoundError as fe:
            self.LOGGER.error(f"File {self.config_file} does not exist", fe)
            return
        except json.JSONDecodeError as je:
            self.LOGGER.error(f"Error parsing JSON config file {self.config_file}", je)
            return
        except Exception as e:
            self.LOGGER.error("Unknown error", e)
            return
        try:
            parsed_configs["source"] = configs["source"]
            parsed_configs["schema_file"] = configs["schema_file"]
            parsed_configs["destination"] = configs["destination"]
            parsed_configs["bucket_name"] = configs["bucket_name"]
            parsed_configs["temp_directory"] = configs["temp_directory"]
            parsed_configs["chunk_num_records"] = int(configs["chunk_num_records"])
            parsed_configs["aws_s3_role_key"] = self.decrypt.decrypt(configs["secrets"]["aws_s3_role_key"]).decode()
            parsed_configs["aws_s3_role_arn"] = self.decrypt.decrypt(configs["secrets"]["aws_s3_role_arn"]).decode()
            parsed_configs["aws_iam_user_key"] = self.decrypt.decrypt(configs["secrets"]["aws_iam_user_key"]).decode()
            parsed_configs["aws_iam_user_secret"] = self.decrypt.decrypt(
                configs["secrets"]["aws_iam_user_secret"]).decode()
            return parsed_configs
        except KeyError as ke:
            self.LOGGER.error("Key not found", ke)
