from azure.data.tables import TableEntity
from abc import ABC, abstractmethod
from typing import Type


class BaseEntity(ABC):
    PartitionKey: str
    RowKey: str

    def __init__(self, partitionKey: str, rowKey: str):
        self.PartitionKey = partitionKey
        self.RowKey = rowKey

    @abstractmethod
    def to_entity(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_entity(cls: Type['BaseEntity'], entity: TableEntity) -> 'BaseEntity':
        pass

    @classmethod
    @abstractmethod
    def get_partition_key(cls) -> str:
        pass
