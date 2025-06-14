from datetime import datetime

import boto3
import logging

from etl.counters import Counters


class STSHelper:
    __CREDENTIALS = None
    __STS_CALL_COUNTER = "Calls made to STS service"
    __REUSED_CREDENTIAL_COUNTER = "Reused-existing credentials"

    def __init__(self, role_arn, session_name, user_key, secret):
        self.user_key = user_key
        self.secret = secret
        self.sts = boto3.client(
            "sts",
            aws_access_key_id=self.user_key,
            aws_secret_access_key=self.secret
        )
        self.role_arn = role_arn
        self.session_name = session_name
        self.LOGGER = logging.getLogger(self.__class__.__name__)

    def get_role_creds(self):
        if self.__CREDENTIALS is None:
            self.LOGGER.info("No credentials exist. Assuming role and fetching new credentials.")
            Counters.increment(self.__STS_CALL_COUNTER)
            self.__CREDENTIALS = self.sts.assume_role(
                RoleArn=self.role_arn,
                RoleSessionName=self.session_name
            )
            return self.__CREDENTIALS["Credentials"]
        if not self.__CREDENTIALS["Credentials"]["Expiration"].timestamp() > datetime.now().timestamp():
            self.LOGGER.info("Credentials have expired, refreshing credentials")
            Counters.increment(self.__STS_CALL_COUNTER)
            self.__CREDENTIALS = self.sts.assume_role(
                RoleArn=self.role_arn,
                RoleSessionName=self.session_name
            )
            return self.__CREDENTIALS["Credentials"]
        self.LOGGER.info("Credentials already exist, returning existing credentials.")
        Counters.increment(self.__REUSED_CREDENTIAL_COUNTER)
        return self.__CREDENTIALS["Credentials"]
