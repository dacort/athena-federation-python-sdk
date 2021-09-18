from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping

import pyarrow as pa

class AthenaDataSource(ABC):
    def __init__(self) -> None:
        self._data_source_type = "athena_python_sdk"

    @property
    def data_source_type(self):
        """Get the data source type. Only used for PingRequest and debugging."""
        return self._data_source_type
    
    @abstractmethod
    def databases(self) -> List[str]:
        """
        Return a list of database names.
        """
        pass

    @abstractmethod
    def tables(self, database_name: str) -> List[str]:
        """
        Return a list of table names in the given database.
        """
        pass

    def columns(self, database_name: str, table_name: str) -> List[str]:
        """
        Return a list of column names in the given table.

        It is not necessary to override this method, but if you want to,
        you can use the default `schema` implementation to return a schema
        where all columns are of type `string`.

        You can choose to override this _or_ `table_schema` method.
        If you override this, all columns will be assumed to be of type string.
        If you want to be more specific, override the `table_schema` method instead.
        """
        return []
    
    @abstractmethod
    def schema(self, database_name: str, table_name: str) -> pa.Schema:
        """
        Return the PyArrow schema of the given table.

        The default implementation uses the `columns` method to get a list of
        of columns and returns them all of type `string`.
        """
        return pa.schema(
            [(col, pa.string()) for col in self.columns(database_name, table_name)]
        )
    
    def splits(self, database_name: str, table_name: str) -> List[Dict]:
        """
        Return a list of splits for the given table.

        A split is a dictionary of key-value pairs that are passed to the `records` method
        and can be used to retrieve a subset of the records.

        Splits are used by Athena to determine how to parallelize the query.
        If your data is small enough (6mb or less) that you don't need to parallelize,
        you can use the default implementation, which generates a single split.
        """
        return []
    
    @abstractmethod
    def records(self, database_name: str, table_name: str, split: Mapping[str,str]) -> Dict[str,List[Any]]:
        """
        Return a dictionary of records for the given table and split.

        The dictionary must have the column names as the keys and column data as a list.
        """
        pass
