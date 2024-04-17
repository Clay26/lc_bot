import datetime
from azure.data.tables import TableEntity
from typing import ClassVar, Type, Optional
from .BaseEntity import BaseEntity


class UserEntity(BaseEntity):
    PARTITION_KEY: ClassVar[str] = "UserCache"
    userId: int
    numEasy: int
    numMedium: int
    numHard: int
    longestStreak: int
    currStreakStartDate: Optional[datetime.datetime] = None
    completedToday: bool

    def __init__(self, userId: str):
        super().__init__(self.PARTITION_KEY, str(userId))
        self.id = userId
        self.numEasy = 0
        self.numMedium = 0
        self.numHard = 0
        self.longestStreak = 0
        self.currStreakStartDate = None
        self.completedToday = False

    def to_entity(self) -> dict:
        currStreakStartDataStr = (self.currStreakStartDate.isoformat() if self.currStreakStartDate else "None")

        return {
            "PartitionKey": self.PartitionKey,
            "RowKey": str(self.RowKey),
            "numEasy": self.numEasy,
            "numMedium": self.numMedium,
            "numHard": self.numHard,
            "longestStreak": self.longestStreak,
            "currStreakStartDate": currStreakStartDataStr,  # ISO format for datetime
            "completedToday": self.completedToday
        }

    @classmethod
    def from_entity(cls: Type['UserEntity'], entity: TableEntity) -> 'UserEntity':
        user_id = entity['RowKey']
        obj = cls(user_id)
        obj.numEasy = int(entity.get('numEasy', 0))
        obj.numMedium = int(entity.get('numMedium', 0))
        obj.numHard = int(entity.get('numHard', 0))
        obj.longestStreak = int(entity.get('longestStreak', 0))
        obj.completedToday = entity.get('completedToday', False)

        currStreakStartDateData = entity['currStreakStartDate']
        if currStreakStartDateData == "None":
            currStreakStartDate = None
        else:
            currStreakStartDate = datetime.datetime.fromisoformat(currStreakStartDateData)
        obj.currStreakStartDate = currStreakStartDate
        return obj

    @classmethod
    def get_partition_key(cls) -> str:
        return cls.PARTITION_KEY

    def get_current_streak(self) -> int:
        if (self.currStreakStartDate is None):
            return 0

        utc = datetime.timezone.utc
        now = datetime.datetime.now(utc)
        time = datetime.time(hour=11, minute=00, tzinfo=utc)

        nextRelease = datetime.datetime.combine(now.date(), time)

        if now > nextRelease:
            # Before 11 AM UTC, use yesterday as latest release
            nextRelease = nextRelease + datetime.timedelta(days=1)

        latestRelease = nextRelease - datetime.timedelta(days=1)

        todayBonus = (0 if self.completedToday else -1)

        return (latestRelease.date() - self.currStreakStartDate.date()).days + 1 + todayBonus
