import pyarrow as pa


class AthenaDataCatalog:
    """
    AthenaDataCatalog is a class that makes it easy to build a custom data connector for Athena using Python.

    The class is designed to be used as a base class for a custom data connector.
    It handles the majority of encoding your responses in the format necessary for the Athena SDK.

    For simple cases, you can use the class as is and pass in the desired database and table names.
    For more complex use cases, you can override the methods in the class to build your own custom connector.

    You can initialize a static example by passing in the schema, database, table, and column names. And then overriding the
    `records` method to return a list of records. Every column is assumed to be a string.

    In order to have more control over the table schema, you need to override the `schema` method and provide pyarrow-specific data types.
    """

    def __init__(self, schema: list() = None) -> None:
        """
        Initializes the data connector.

        :param schema: The schema name, database name, and list of tables.

        If no schema is provided, we generate a simple default example.
        """
        self.data_source_type = "athena_python_sdk"

        if not schema:
            schema = [
                {
                    "database": "sampledb",
                    "tables": [{"name": "demo", "columns": ["id", "name"]}],
                }
            ]
        self._initialize_schema_map(schema)

    def _initialize_schema_map(self, schema: list()) -> None:
        """
        Sets the schema variable and also creates a schema hashmap for easy lookups.
        """
        self.schema = schema
        self.schema_map = {}

        for db in self.schema:
            self.schema_map[db["database"]] = {}
            for table in db.get("tables", []):
                self.schema_map[db["database"]][table["name"]] = table["columns"]

    def get_database_names(self) -> list:
        return [d["database"] for d in self.schema]

    def get_table_names(self, database: str) -> list:
        return self.schema_map[database].keys()

    def get_schema_for_table(self, database: str, table: str) -> pa.Schema:
        """
        Returns the pyarrow schema for the provided database and table.
        """
        columns = self.schema_map[database][table]
        return pa.schema([(col, pa.string()) for col in columns])

    def get_records(self, database: str, table: str) -> list:
        """
        Returns a list of records from the given database and table.

        :param database: The database name.
        :param table: The table name.
        :return: A list of records.
        """
        return {
            "id": ["1", "2", "3", "4"],
            "name": ["damon", "dacort", "dpc", "cortesi"],
        }
