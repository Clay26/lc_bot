from azure.data.tables import TableEntity
from typing import ClassVar, Type
from .BaseEntity import BaseEntity


class ServerEntity(BaseEntity):
    PARTITION_KEY: ClassVar[str] = "ChannelCache"
    channelId: int

    def __init__(self, guildId: int, channelId: int = 0):
        super().__init__(self.PARTITION_KEY, str(guildId))
        self.channelId = channelId

    def to_entity(self) -> dict:
        return {
            "PartitionKey": self.PartitionKey,
            "RowKey": self.RowKey,
            "ChannelId": str(self.channelId),
        }

    @classmethod
    def from_entity(cls: Type['ServerEntity'], entity: TableEntity) -> 'ServerEntity':
        obj = cls(int(entity.get('RowKey', "0")))
        obj.channelId = int(entity.get('ChannelId', "0"))
        return obj

    @classmethod
    def get_partition_key(cls) -> str:
        return cls.PARTITION_KEY
