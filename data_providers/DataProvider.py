class DataProvider:
    def fetch(self, match_id: str):
        raise NotImplementedError("fetch() not implemented")

    def parse(self, match_json):
        raise NotImplementedError("parse() not implemented")
