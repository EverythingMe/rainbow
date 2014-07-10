from unittest import TestCase
from rainbow.datasources import DataSourceCollection
from rainbow.preprocessor import Preprocessor
from rainbow.preprocessor.preprocessor_exceptions import InvalidPreprocessorFunctionException
from rainbow.preprocessor.instance_chooser import InvalidInstanceException
from rainbow.yaml_loader import RainbowYamlLoader
from rainbow.cloudformation import Cloudformation
from rainbow.templates import TemplateLoader

__author__ = 'omrib'


class TestCloudformation(TestCase):
    def setUp(self):
        data_sources = ['yaml:c:datasources/nested.yaml',
                        'yaml:datasources/b.yaml',
                        'yaml:datasources/a.yaml']

        self.datasource_collection = DataSourceCollection(data_sources)
        self.preprocessor = Preprocessor(self.datasource_collection, 'us-east-1')

    def test_resolve_template_parameters(self):
        template = TemplateLoader.load_templates(['templates/simpletemplate.yaml'])
        parameters = Cloudformation.resolve_template_parameters(template, self.datasource_collection)

        self.assertEqual(parameters['a_list'], 'item1, item2, item3, item4')
        self.assertEqual(parameters['b_list'], '1, 2, 3')

    def test_invalid_function(self):
        self.assertRaises(InvalidPreprocessorFunctionException, self.preprocessor.process, {'Rb::NoSuchFunction': ''})
