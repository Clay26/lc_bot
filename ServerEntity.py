from BaseEntity import BaseEntity

class ServerEntity(BaseEntity):
    partitionKey = "ChannelCache"

    def __init__(self, guildId):
        super().__init__(self.partitionKey, guildId)
        self.channelId = None

    def to_enttiy(self):
        return {
            "PartitionKey": self.PartitionKey,
            "RowKey": self.RowKey,
            "ChannelId": self.channelId,
        }

    @classmethod
    def from_entity(cls, entity):
        obj = cls(entity['RowKey'])
        obj.channelId = entity.get('ChannelId', None)
        return obj

    @classmethod
    def get_partition_key(cls):
        return self.partitionKey
