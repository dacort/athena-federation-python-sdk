from typing import Any, Dict, List, Mapping, Iterable

import pyarrow as pa
from athena_federation.athena_data_source import AthenaDataSource


class SampleDataSource(AthenaDataSource):
    """
    An example Athena Data Source

    A hard-coded example that shows the different methods you can implement.
    """

    @staticmethod
    def TransposeData(
        columns: List[str], data: List[List[Any]]
    ) -> Dict[str, List[Any]]:
        """
        Transpose the data so that it is a dictionary of columns.
        """
        zipped: Iterable[list[Any]] = zip(*data)  # type: ignore
        return dict(zip(columns, list(zipped)))

    def __init__(self):
        super().__init__()

    def databases(self) -> List[str]:
        return ["sampledb"]

    def tables(self, database_name: str) -> List[str]:
        return ["demo"]

    def columns(self, database_name: str, table_name: str) -> List[str]:
        return ["id", "name"]

    def schema(self, database_name: str, table_name: str) -> pa.Schema:
        return super().schema(database_name, table_name)

    def splits(self, database_name: str, table_name: str) -> List[Dict]:
        return [
            {"name": "split1", "action": "normal"},
            {"name": "split2", "action": "spill"},
        ]

    def records(
        self, database: str, table: str, split: Mapping[str, str]
    ) -> Dict[str, List[Any]]:
        """
        Generate example records
        """
        records = [
            [1, "John"],
            [2, "Jane"],
            [3, "Joe"],
            [4, "Janice"],
        ]
        # Demonstrate how splits work by generating a huge response. :)
        if split.get("action", "") == "spill":
            records = records * 4000
        return self.TransposeData(self.columns(database, table), records)
