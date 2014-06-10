from unittest import TestCase
from rainbow.datasources import DataSourceCollection
from rainbow.preprocessor import Preprocessor
from rainbow.preprocessor.preprocessor_exceptions import InvalidPreprocessorFunctionException
from rainbow.preprocessor.instance_chooser import InvalidInstanceException
from rainbow.yaml_loader import RainbowYamlLoader

__author__ = 'omrib'


class TestPreprocessor(TestCase):
    def setUp(self):
        # c can override b, which can override a
        data_sources = ['yaml:c:datasources/nested.yaml',
                        'yaml:datasources/b.yaml',
                        'yaml:datasources/a.yaml']

        self.datasource_collection = DataSourceCollection(data_sources)
        self.preprocessor = Preprocessor(self.datasource_collection, 'us-east-1')

    def test_instance_chooser(self):
        with open('preprocessor/instance_chooser1.yaml') as instance_chooser1, \
                open('preprocessor/instance_chooser2.yaml') as instance_chooser2, \
                open('preprocessor/instance_chooser3.yaml') as instance_chooser3:
            template = RainbowYamlLoader(instance_chooser1).get_data()
            template2 = RainbowYamlLoader(instance_chooser2).get_data()
            template3 = RainbowYamlLoader(instance_chooser3).get_data()

        processed = self.preprocessor.process(template)
        self.assertEqual(processed['Resources']['Properties']['InstanceType'], 'c1.xlarge')

        processed2 = self.preprocessor.process(template2)
        self.assertEqual(processed2['Resources']['Properties']['InstanceType'], 'c3.large')

        self.assertRaises(InvalidInstanceException, self.preprocessor.process, template3)

    def test_invalid_function(self):
        self.assertRaises(InvalidPreprocessorFunctionException, self.preprocessor.process, {'Rb::NoSuchFunction': ''})