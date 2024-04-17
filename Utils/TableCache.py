import logging
from typing import Type, TypeVar, Generic, Optional, Dict, Any
from azure.data.tables import TableServiceClient, UpdateMode, TableClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from Entities import BaseEntity

E = TypeVar('E', bound='BaseEntity')


class TableCache(Generic[E]):
    tableName: str
    tableServiceClient: Optional[TableServiceClient]
    tableClient: Optional[TableClient]
    localCache: Dict[str, Any]
    entityType: Type[E]
    logger: logging.Logger

    def __init__(self, entityType: Type[E]):
        self.tableName = entityType.get_partition_key()
        self.tableServiceClient = None
        self.tableClient = None

        self.localCache = {}

        self.entityType = entityType

        self.logger = logging.getLogger('discord.TableCache')

    def initialize_table(self, connectionString: str):
        try:
            self.tableServiceClient = TableServiceClient.from_connection_string(conn_str=connectionString)
            self.tableClient = self.tableServiceClient.create_table(table_name=self.tableName)
            self.logger.info(f'Created [{self.tableName}] table.')
        except ResourceExistsError:
            self.tableClient = self.tableServiceClient.get_table_client(table_name=self.tableName)
            self.logger.info(f'Connected to [{self.tableName}] table.')
        except Exception as e:
            # Log an error message if something goes wrong
            self.logger.error(f"Failed to initialize [{self.tableName}]: {e}", exc_info=True)

    def save_entity(self, obj: E):
        try:
            self.logger.debug(f'Trying to save entity to table [{self.tableName}]')
            self.tableClient.upsert_entity(mode=UpdateMode.MERGE, entity=obj.to_entity())
            self.logger.info(f'Successfully saved entity to table [{self.tableName}]')

            self.save_to_local_cache(obj)
        except Exception as e:
            self.logger.error(f"Error saving to table [{self.tableName}]: {e}")

    def load_entity(self, rowKey: any) -> Optional[E]:
        localEntity = self.load_from_local_cache(str(rowKey))
        if localEntity is not None:
            self.logger.info(f'Found row [{rowKey}] in local [{self.tableName}] cache!')
            return localEntity
        else:
            self.logger.info(f'Row [{rowKey}] not found in local [{self.tableName}] cache!')

        try:
            self.logger.debug(f'Trying to pull from [{self.tableName}] cache.')
            data = self.tableClient.get_entity(partition_key=self.tableName, row_key=str(rowKey))
            self.logger.info(f'Found row [{rowKey}] in [{self.tableName}] cache!')

            entity = self.entityType.from_entity(data)
            self.save_to_local_cache(entity)
            return entity
        except ResourceNotFoundError:
            self.logger.info(f'Row [{rowKey}] does not exit in [{self.tableName}].')
            return None
        except Exception as e:
            # Log an error message if something goes wrong
            self.logger.error(f"Failed to pull [{self.tableName}] for row [{rowKey}]: {e}", exc_info=True)
            return None

    def save_to_local_cache(self, obj: E):
        self.logger.debug('Saving to local cache.')
        self.localCache[str(obj.RowKey)] = obj

    def load_from_local_cache(self, rowKey: str) -> Optional[E]:
        self.logger.debug('Loading from local cache.')
        localEntity = self.localCache.get(rowKey, None)
        return localEntity
