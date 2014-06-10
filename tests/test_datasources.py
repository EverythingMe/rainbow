from unittest import TestCase
from rainbow.datasources import *
from rainbow.datasources.datasource_exceptions import *

__author__ = 'omrib'


class TestDataSources(TestCase):
    def setUp(self):
        # c can override b, which can override a
        data_sources = ['file64:e_str:datasources/e.file64',
                        'file:d_str:datasources/d.file',
                        'yaml:c:datasources/nested.yaml',
                        'yaml:datasources/b.yaml',
                        'yaml:datasources/a.yaml']

        self.datasource_collection = DataSourceCollection(data_sources)

    def test_non_exist_parameter(self):
        self.assertRaises(InvalidParameterException, self.datasource_collection.get_parameter_recursive, 'test')

    def test_pointer(self):
        self.assertEqual(
            self.datasource_collection.get_parameter_recursive('a_ptr'),
            self.datasource_collection.get_parameter_recursive('b_list')
        )

        self.assertEqual(
            self.datasource_collection.get_parameter_recursive('b_ptr'),
            self.datasource_collection.get_parameter_recursive('a_list')
        )

        self.assertEqual(
            self.datasource_collection.get_parameter_recursive('c_ptr'),
            self.datasource_collection.get_parameter_recursive('a_list')
        )

    def test_string(self):
        self.assertEqual(
            self.datasource_collection.get_parameter_recursive('a_str'),
            'foobar'
        )

        self.assertEqual(
            self.datasource_collection.get_parameter_recursive('b_str'),
            'a B string'
        )

        with open('datasources/d.file') as f:
            self.assertEqual(
                self.datasource_collection.get_parameter_recursive('d_str'),
                f.read()
            )

        with open('datasources/e.file64') as f:
            self.assertEqual(
                self.datasource_collection.get_parameter_recursive('e_str'),
                f.read().encode('base64')
            )

    def test_list(self):
        self.assertEqual(
            self.datasource_collection.get_parameter_recursive('a_list'),
            'item1, item2, item3, item4'
        )

        self.assertEqual(
            self.datasource_collection.get_parameter_recursive('b_list'),
            '1, 2, 3'
        )

    def test_override(self):
        self.assertEqual(
            self.datasource_collection.get_parameter_recursive('shared'),
            'from c'
        )
