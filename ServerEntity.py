from BaseEntity import BaseEntity

class ServerEntity(BaseEntity):
    def __init__(self, guildId, channelId=0):
        super().__init__("ChannelCache", guildId)
        self.channelId = channelId

    def to_entity(self):
        return {
            "PartitionKey": self.PartitionKey,
            "RowKey": str(self.RowKey),
            "ChannelId": str(self.channelId),
        }

    @classmethod
    def from_entity(cls, entity):
        obj = cls(int(entity.get('RowKey', "0")))
        obj.channelId = int(entity.get('ChannelId', "0"))
        return obj

    @classmethod
    def get_partition_key(cls):
        return "ChannelCache"

    @classmethod
    def format_row_key(cls, rowKey):
        return str(rowKey)
