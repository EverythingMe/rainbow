from datasource_exceptions import *


class DataCollectionPointer(str):
    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, str.__repr__(self))


class DataSourceBaseMeta(type):
    datasources = {}

    @classmethod
    def __new__(mcs, cls, name, bases, d):
        ret = type.__new__(cls, name, bases, d)
        if hasattr(ret, 'datasource_name'):
            mcs.datasources[ret.datasource_name] = ret
        return ret


class DataSourceBase(object):
    __metaclass__ = DataSourceBaseMeta

    # will be initialized to argparse.ArgumentParser command line args
    region = 'us-east-1'

    def __init__(self, data_source):
        self.data_source = data_source
        self.data = None

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

    def __repr__(self):
        return '<%s data_source=%r data=%r>' % (self.__class__.__name__, self.data_source, self.data)


class DataSourceCollection(list):
    def __init__(self, datasources):
        """
        :param datasources: list of strings containing data sources. i.e.: yaml:path/to/yaml.yaml
        :type datasources: list
        """

        l = []

        for datasource in datasources:
            try:
                source, data = datasource.split(":", 1)
            except:
                raise InvalidDataSourceFormatException(
                    "Invalid data source format %r. Data source should be \"<format>:<parameter>\"" % (datasource,))

            if not source in DataSourceBaseMeta.datasources:
                raise UnknownDataSourceException(
                    "Unknown data source %s, valid data sources are %s" %
                    (source, ", ".join(DataSourceBaseMeta.datasources.keys())))

            l.append(DataSourceBaseMeta.datasources[source](data))

        super(DataSourceCollection, self).__init__(l)

    def get_parameter_recursive(self, parameter):
        """
        See `get_parameter()` doc.
        The difference between the two functions is that this function follows pointers.

        :param parameter: parameter to look up
        :type parameter: str
        :return: `parameter` resolved (recursively)
        """

        parameter = self.get_parameter(parameter)

        if isinstance(parameter, DataCollectionPointer):
            # pointer, resolve it

            return self.get_parameter_recursive(parameter)
        elif hasattr(parameter, '__iter__'):
            # resolve iterables and convert to a list

            return [self.get_parameter_recursive(i) if isinstance(i, DataCollectionPointer) else i for i in parameter]
        else:
            # regular parameter, return as is.

            return parameter

    def get_parameter(self, parameter):
        """
        Look up `parameter` in all data sources available to the collection, returning the first match.
        This function doesn't follow pointers. You probably want `get_parameter_recursive()`

        :param parameter: parameter to look up
        :type parameter: str
        :return: `parameter` resolved
        """

        for data_source in self:
            if parameter in data_source:
                return data_source[parameter]
        else:
            raise InvalidParameterException(
                "Unable to find parameter %s in any of the data sources %r" % (parameter, self))

    def __contains__(self, item):
        try:
            self.get_parameter_recursive(item)
            return True
        except InvalidParameterException:
            return False
