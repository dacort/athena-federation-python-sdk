from athena.federation.athena_data_source import AthenaDataSource

import pyarrow as pa

from typing import Mapping, Dict, List, Any

class SampleDataSource(AthenaDataSource):
    """
    An example Athena Data Source

    A hard-coded example that shows the different methods you can implement.
    """
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
            {
                "name": "split1",
                "action": "normal"
            },
            {
                "name": "split2",
                "action": "spill"
            }
        ]

    def records(self, database: str, table: str, split: Mapping[str,str]) -> Dict[str,List[Any]]:
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
        if split.get('action', "") == "spill":
            records = records * 4000
        # We unfortunately need to transpose the data - we should add a helper for this
        return dict(zip(self.columns(database, table), list(zip(*records))))