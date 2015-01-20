class DataSourceBaseException(Exception):
    pass


class InvalidDataSourceFormatException(DataSourceBaseException):
    pass


class UnknownDataSourceException(DataSourceBaseException):
    pass


class InvalidParameterException(DataSourceBaseException):
    pass
