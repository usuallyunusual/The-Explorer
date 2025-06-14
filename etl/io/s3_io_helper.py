import logging

from etl.counters import Counters
from etl.io.io_helper import IOHelper
import boto3


class S3IOHelper(IOHelper):
    __S3_GET_CALL = "Number of S3 GET calls"
    __S3_PUT_CALL = "Number of S3 PUT calls"

    def __init__(self, serde, sts_helper, bucket_name):
        super().__init__()
        self.LOGGER = logging.getLogger(self.__class__.__name__)
        self.role_key = None
        self.role_secret = None
        self.role_token = None
        self.serde = serde
        self.sts_helper = sts_helper
        self.bucket_name = bucket_name
        self.s3 = boto3.resource(
            "s3"
        )

    def read(self, file_name):
        if not self.bucket_name or self.bucket_name == "":
            self.LOGGER.info("Falling back to writing to LocalFS")
            data_bytes = self.read_local_fs(file_name)
        else:
            self.get_credentials()
            Counters.increment(self.__S3_GET_CALL)
            data_bytes = self.s3.get_object(
                Bucket=self.bucket_name,
                Key=file_name,
                aws_access_key_id=self.role_key,
                aws_secret_access_key=self.role_secret,
                aws_session_token=self.role_token,
            ).body()
        return self.serde.deserialize(data_bytes)

    def write(self, data, file_name=None):
        data_file = self.serde.serialize(data)
        file_name = f"{file_name}/{data_file.split('/')[-1]}"
        if not self.bucket_name or self.bucket_name == "":
            self.LOGGER.info("Falling back to LocalFS")
            return self.write_local_fs(data_file, file_name)
        else:
            self.get_credentials()
            Counters.increment(self.__S3_PUT_CALL)
            return self.s3.upload_file(
                data_file,
                self.bucket_name,
                file_name,
                aws_access_key_id=self.role_key,
                aws_secret_access_key=self.role_secret,
                aws_session_token=self.role_token,
            )

    def cleanup_serializer(self):
        self.LOGGER.info("Cleaning up temp outputs.")
        self.serde.cleanup()

    def get_credentials(self):
        credentials = self.sts_helper.get_role_creds()
        self.role_key = credentials["AccessKeyId"]
        self.role_secret = credentials["SecretAccessKey"]
        self.role_token = credentials["SessionToken"]

