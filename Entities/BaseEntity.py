from abc import ABC, abstractmethod

class BaseEntity(ABC):
    def __init__(self, partitionKey, rowKey):
        self.PartitionKey = partitionKey
        self.RowKey = rowKey

    @abstractmethod
    def to_entity(self):
        pass

    @abstractmethod
    def from_entity(cls, entity):
        pass

    @abstractmethod
    def get_partition_key(cls, entity):
        pass

    @classmethod
    def format_row_key(cls, rowKey):
        return rowKey
