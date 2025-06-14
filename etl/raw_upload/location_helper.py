import glob


class LocationHelper:
    def __init__(self, cities, all_country, io_helper):
        self.cities = cities
        self.all_country_csv = all_country
        self.io_helper = io_helper
        self.lookup_list = list()

    def locations_lookup_dump(self):
        files = glob.glob(f"{self.cities}*.txt")
        for file in files:
            self.add_txt_to_lookup(file)
        with open(self.all_country_csv, "r") as csv:
            self.add_csv_to_lookup(csv.read())
        # Write to S3 here

    def add_txt_to_lookup(self, file):
        pass

    def add_csv_to_lookup(self, param):
        pass
