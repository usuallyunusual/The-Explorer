import io
import logging
import os

from etl.counters import Counters
from etl.serde.serde import Serde
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
import glob


class AvroSerde(Serde):
    __TMP_FOLDERS_WRITTEN = "Number of temporary files written to disk"
    __TMP_FOLDERS_REMOVED = "Number of temporary files deleted from disk"
    __RECORDS_SERIALIZED = "Number of records serialized"

    def __init__(self, avro_schema, tmp_directory):
        self.avro_schema = self.parse_avro_schema(avro_schema)
        self.tmp_directory = tmp_directory[:-1] if tmp_directory[-1] == "/" else tmp_directory
        self.LOGGER = logging.getLogger(self.__class__.__name__)
        self.count = 0

    def serialize(self, data_bytes_io):
        filename = f"{self.tmp_directory}/avro-{self.count}.avro"
        self.LOGGER.info(f"Serializing to temp file {filename}")
        writefile = open(filename, "wb+")
        serializer = DataFileWriter(writefile, DatumWriter(), self.avro_schema)
        for datum in data_bytes_io:
            serializer.append(datum)
            Counters.increment(self.__RECORDS_SERIALIZED)
        serializer.close()
        self.count += 1
        writefile.close()
        Counters.increment(self.__TMP_FOLDERS_WRITTEN)
        return filename

    def deserialize(self, data_bytes_io):
        data_bytes_io = io.IO(data_bytes_io)
        deserializer = DataFileReader(data_bytes_io, DatumReader(self.avro_schema))
        return [datum for datum in deserializer]

    def parse_avro_schema(self, avro_schema):
        return avro.schema.parse(avro_schema)

    def cleanup(self):
        files = glob.glob(f"{self.tmp_directory}/*.avro")
        self.LOGGER.info(f"Cleaning up {len(files)} temp files in directory {self.tmp_directory} ")
        for file in files:
            os.remove(file)
        self.LOGGER.info(f"Done cleaning up tmp files.")
        Counters.increment_by_number(self.__TMP_FOLDERS_REMOVED, len(files))
