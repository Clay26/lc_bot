import logging
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceExistsError

class TableCache():
    def __init__(self, entityType):
        self.tableName = entityType.get_partition_key()
        self.tableServiceClient = None
        self.tableClient = None

        self.entityType = entityType

        self.logger = logging.getLogger('discord.TableCache')

    def initialize_table(self, connectionString):
        try:
            self.tableServiceClient = TableServiceClient.from_connection_string(conn_str=connectionString)
            self.tableClient = self.tableServiceClient.create_table(table_name=self.tableName)
            self.logger.debug(f'Created [{self.tableName}] table.')
        except ResourceExistsError:
            self.tableClient = self.tableServiceClient.get_table_client(table_name=self.tableName)
            self.logger.debug(f'Connected to [{self.tableName}] table.')
        except Exception as e:
            # Log an error message if something goes wrong
            self.logger.error(f"Failed to initialize [{self.tableName}]: {e}", exc_info=True)

    def save_entity(self, obj):
        try:
            self.logger.info(f'Trying to save entity to table [{self.tableName}]')
            self.tableClient.upsert_entity(mode=UpdateMode.MERGE, entity=obj.to_entity())
            self.logger.debug(f'Successfully saved entity to table [{self.tableName}]')
        except Exception as e:
            self.logger.error(f"Error saving to table [{self.tableName}]: {e}")

    def load_entity(self, rowKey):
        try:
            self.logger.info(f'Trying to pull from [{self.tableName}] cache.')
            data = self.tableClient.get_entity(partition_key=self.tableName, row_key=self.entityType.format_row_key(rowKey))
            self.logger.debug(f'Found row [{rowKey}] in [{self.tableName}] cache!')
            return self.entityType.from_entity(data)
        except Exception as e:
            # Log an error message if something goes wrong
            self.logger.error(f"Failed to pull [{self.tableName}] for row [{rowKey}]: {e}", exc_info=True)
