import yaml
import re
from rainbow.datasources.base import DataCollectionPointer


class RainbowYamlLoader(yaml.Loader):
    @staticmethod
    def yaml_pointer(loader, node):
        """
        DataSource pointer, wraps the string in a DataCollectionPointer() object

        :param loader: loader.add_constructor parameter
        :param node: loader.add_constructor parameter
        :rtype: DataCollectionPointer
        :return: File content as string
        """

        value = loader.construct_scalar(node)

        # remove implicit resolver character
        if value[0] == '$':
            value = value[1:]

        return DataCollectionPointer(value)

    @staticmethod
    def yaml_file(loader, node):
        """
        Load file content as string to YAML

        :param loader: loader.add_constructor parameter
        :param node: loader.add_constructor parameter
        :rtype: str
        :return: File content as string
        """

        value = loader.construct_scalar(node)
        with open(value) as f:
            return f.read()

    @classmethod
    def yaml_file64(cls, loader, node):
        """
        Same as yaml_file, but returns base64 encoded data

        :param loader: loader.add_constructor parameter
        :param node: loader.add_constructor parameter
        :rtype: str
        :return: File content as base64 encoded string
        """

        return cls.yaml_file(loader, node).encode('base64')

    @staticmethod
    def yaml_yaml(loader, node):
        """
        Yo dawg, we heard you like YAML...
        Same as yaml_file, but returns a yaml decoded data

        :param loader: loader.add_constructor parameter
        :param node: loader.add_constructor parameter
        :return: File content as base64 encoded string
        """
        template_path = loader.construct_scalar(node)

        if ':' in template_path:
            key, yaml_file = template_path.split(':', 1)
        else:
            yaml_file = template_path
            key = None

        with open(yaml_file) as f:
            template = RainbowYamlLoader(f).get_data()
            
        if key:
            template = template[key]
        return template


    def __init__(self, *args, **kwargs):
        self.add_constructor('!file', self.__class__.yaml_file)
        self.add_constructor('!file64', self.__class__.yaml_file64)
        self.add_constructor('!yaml', self.__class__.yaml_yaml)
        self.add_constructor('!pointer', self.__class__.yaml_pointer)
        self.add_implicit_resolver('!pointer', re.compile(r'^\$\S+'), None)

        super(RainbowYamlLoader, self).__init__(*args, **kwargs)
