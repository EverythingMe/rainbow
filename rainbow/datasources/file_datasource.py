from base import DataSourceBase
from datasource_exceptions import InvalidDataSourceFormatException

__all__ = ['FileDataSource', 'File64DataSource']


class FileDataSource(DataSourceBase):
    datasource_name = 'file'

    def __init__(self, data_source):
        super(FileDataSource, self).__init__(data_source)

        if not ':' in data_source:
            raise InvalidDataSourceFormatException("FileDataSource must be in name:path_to_file format")

        name, path = data_source.split(':', 1)

        with open(path) as f:
            self.data = {name: f.read(-1)}


class File64DataSource(DataSourceBase):
    datasource_name = 'file64'

    def __init__(self, data_source):
        super(File64DataSource, self).__init__(data_source)

        if not ':' in data_source:
            raise InvalidDataSourceFormatException("File64DataSource must be in name:path_to_file format")

        name, path = data_source.split(':', 1)

        with open(path) as f:
            self.data = {name: f.read(-1).encode('base64')}
