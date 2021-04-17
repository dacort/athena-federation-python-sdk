from abc import ABC, abstractmethod

import athena.federation.models as models


class AthenaFederationSDK(ABC):
    @abstractmethod
    def __init__(self, event) -> None:
        self.event = event

    @abstractmethod
    def PingRequest(self) -> models.PingResponse:
        """Basic ping request that returns metadata about this connector"""
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