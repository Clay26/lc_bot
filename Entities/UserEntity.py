import datetime
from .BaseEntity import BaseEntity

class UserEntity(BaseEntity):
    def __init__(self, userId):
        super().__init__("UserCache", userId)
        self.numEasy = 0
        self.numMedium = 0
        self.numHard = 0
        self.longestStreak = 0
        self.currStreakStartDate = datetime.datetime.now()
        self.completedToday = False

    def to_entity(self):
        return {
            "PartitionKey": self.PartitionKey,
            "RowKey": str(self.RowKey),
            "numEasy": self.numEasy,
            "numMedium": self.numMedium,
            "numHard": self.numHard,
            "longestStreak": self.longestStreak,
            "currStreakStartDate": self.currStreakStartDate.isoformat(),  # ISO format for datetime
            "completedToday": self.completedToday
        }

    @classmethod
    def from_entity(cls, entity):
        # Convert RowKey back to integer if it was originally an integer, here assumed as a string
        user_id = entity['RowKey']
        obj = cls(user_id)
        obj.numEasy = int(entity.get('numEasy', 0))
        obj.numMedium = int(entity.get('numMedium', 0))
        obj.numHard = int(entity.get('numHard', 0))
        obj.longestStreak = int(entity.get('longestStreak', 0))
        # Parse the ISO format datetime back into a datetime object
        obj.currStreakStartDate = datetime.datetime.fromisoformat(entity.get('currStreakStartDate'))
        obj.completedToday = entity.get('completedToday', False) == 'True'
        return obj

    @classmethod
    def get_partition_key(cls):
        return "UserCache"

    @classmethod
    def format_row_key(cls, rowKey):
        return str(rowKey)

    def get_current_streak(self):
        today = datetime.datetime.now()
        if self.completedToday:
            return (today.date() - self.currStreakStartDate.date()).days + 1
        else:
            return (today.date() - self.currStreakStartDate.date()).days
