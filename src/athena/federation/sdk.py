from abc import ABC, abstractmethod

import athena.federation.models as models


class AthenaFederationSDK(ABC):
    """
    AthenaFederationSDK is a Python implmementation of the Athena Federated Query SDK.

    All the methods in this class must be implemented for an AWS Lambda function to be able to
    serve as a Data Connector for Athena.

    The "catalog name" is defined in Athena when you create a data connector and passed to the Lambda function
    in all requests.
    "Schema" is interchangeable with database.
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def PingRequest(self) -> models.PingResponse:
        """
        Return metadata about the data connector. 

        This is used by Athena to verify the Lambda function is accessible.
        """
        raise NotImplementedError

    @abstractmethod
    def ListSchemasRequest(self) -> models.ListSchemasResponse:
        """List different available databases for your connector"""
        raise NotImplementedError

    @abstractmethod
    def ListTablesRequest(self) -> models.ListTablesResponse:
        """List available tables in the database"""
        raise NotImplementedError

    @abstractmethod
    def GetTableRequest(self) -> models.GetTableResponse:
        """Get Table metadata"""
        raise NotImplementedError

    @abstractmethod
    def GetTableLayoutRequest(self) -> models.GetTableLayoutResponse:
        """I forget the difference between TableLayout and Splits, but for now we just return a default response."""
        raise NotImplementedError

    @abstractmethod
    def GetSplitsRequest(self) -> models.GetSplitsResponse:
        """The splits don't matter to Athena, it's mostly hints to pass on to ReadRecordsRequest"""
        raise NotImplementedError

    @abstractmethod
    def ReadRecordsRequest(self) -> models.ReadRecordsResponse:
        """The actual data!"""
        raise NotImplementedError