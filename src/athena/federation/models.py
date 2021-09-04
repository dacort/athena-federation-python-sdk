from uuid import uuid4

from athena.federation.utils import AthenaSDKUtils

import pyarrow as pa

# https://github.com/awslabs/aws-athena-query-federation/blob/master/athena-federation-sdk/src/main/java/com/amazonaws/athena/connector/lambda/handlers/FederationCapabilities.java#L33
CAPABILITIES = 23


class PingResponse:
    def __init__(self, catalogName, queryId, sourceType) -> None:
        self.catalogName = catalogName
        self.queryId = queryId
        self.sourceType = sourceType

    def as_dict(self):
        return {
            "@type": "PingResponse",
            "catalogName":  self.catalogName,
            "queryId": self.queryId,
            "sourceType": self.sourceType,
            "capabilities": CAPABILITIES
        }


class ListSchemasResponse:
    requestType = 'LIST_SCHEMAS'

    def __init__(self, catalogName, schemas) -> None:
        self.catalogName = catalogName
        self.schemas = schemas

    def as_dict(self):
        return {
            "@type": 'ListSchemasResponse',
            "catalogName": self.catalogName,
            "schemas": self.schemas,
            "requestType": self.requestType
        }


class TableDefinition:
    def __init__(self, schemaName, tableName) -> None:
        self.schemaName = schemaName
        self.tableName = tableName

    def as_dict(self):
        return {"schemaName": self.schemaName, "tableName": self.tableName}


class ListTablesResponse:
    requestType = 'LIST_TABLES'

    def __init__(self, catalogName, tableDefinitions=None) -> None:
        self.catalogName = catalogName
        self.tables = tableDefinitions or []

    def addTableDefinition(self, schemaName, tableName) -> None:
        self.tables.append(TableDefinition(schemaName, tableName))

    def as_dict(self):
        return {
            "@type": "ListTablesResponse",
            "catalogName": self.catalogName,
            "tables": [t.as_dict() for t in self.tables],
            "requestType": self.requestType
        }
        # Missing nextToken - listtables can be paginated


class GetTableResponse:
    request_type = 'GET_TABLE'

    def __init__(self, catalogName, databaseName, tableName, schema, partitionColumns=None) -> None:
        self.catalogName = catalogName
        self.databaseName = databaseName
        self.tableName = tableName
        self.schema = schema
        self.partitions = partitionColumns or []

    def as_dict(self):
        return {
            "@type": "GetTableResponse",
            "catalogName": self.catalogName,
            "tableName": {'schemaName': self.databaseName, 'tableName': self.tableName},
            "schema": {"schema": AthenaSDKUtils.encode_pyarrow_object(self.schema)},
            "partitionColumns": self.partitions,
            "requestType": self.request_type
        }


class GetTableLayoutResponse:
    request_type = 'GET_TABLE_LAYOUT'

    def __init__(self, catalogName, databaseName, tableName, partitions=None) -> None:
        self.catalogName = catalogName
        self.databaseName = databaseName
        self.tableName = tableName
        self.partitions = partitions

    def encoded_partition_config(self):
        """
        Encodes the schema and each record in the partition config.
        """
        partition_keys = self.partitions.keys()
        data = [pa.array(self.partitions[key]) for key in partition_keys]
        batch = pa.RecordBatch.from_arrays(data, list(partition_keys))
        return {
            "aId": str(uuid4()),
            "schema": AthenaSDKUtils.encode_pyarrow_object(batch.schema),
            "records": AthenaSDKUtils.encode_pyarrow_object(batch)
        }

    def as_dict(self):
        # If _no_ partition_config is provided, we *must* return at least 1 partition
        # otherwise Athena will not know to retrieve data.
        if self.partitions is None:
            self.partitions = {'partitionId': [1]}
            # self.partitions = {
            #     'schema': pa.schema([('partitionId', pa.int32())]),
            #     'records': {
            #         'partitionId': [1]
            #     },
            # }

        return {
            "@type": "GetTableLayoutResponse",
            "catalogName": self.catalogName,
            "tableName": {'schemaName': self.databaseName, 'tableName': self.tableName},
            "partitions": self.encoded_partition_config(),
            "requestType": self.request_type
        }


class GetSplitsResponse:
    request_type = 'GET_SPLITS'

    def __init__(self, catalogName, splits) -> None:
        self.catalogName = catalogName
        self.splits = splits

    def as_dict(self):
        return {
            "@type": "GetSplitsResponse",
            "catalogName": self.catalogName,
            "splits": self.splits,
            "continuationToken": None,
            "requestType": self.request_type
        }


class ReadRecordsResponse:
    request_type = 'READ_RECORDS'

    def __init__(self, catalogName, schema, records) -> None:
        self.catalogName = catalogName
        self.schema = schema
        self.records = records

    def as_dict(self):
        return {
            "@type": "ReadRecordsResponse",
            "catalogName": self.catalogName,
            "records": {
                "aId": str(uuid4()),
                "schema": AthenaSDKUtils.encode_pyarrow_object(self.schema),
                "records": AthenaSDKUtils.encode_pyarrow_object(self.records)
            },
            "requestType": self.request_type
        }