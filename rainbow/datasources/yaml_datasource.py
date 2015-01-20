from base import DataSourceBase
from rainbow.yaml_loader import RainbowYamlLoader

__all__ = ['YamlDataSource']


class YamlDataSource(DataSourceBase):
    datasource_name = 'yaml'

    def __init__(self, data_source):
        # data_source can be path/to/file.yaml or Key:path/to/file.yaml
        # this lets you use one yaml file for multiple purposes
        if ':' in data_source:
            key, yaml_file = data_source.split(':', 1)
        else:
            yaml_file = data_source
            key = None

        super(YamlDataSource, self).__init__(data_source)

        with open(yaml_file) as f:
            self.data = RainbowYamlLoader(f).get_data()

        if key:
            self.data = self.data[key]
