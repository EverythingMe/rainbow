from unittest import TestCase
from rainbow.yaml_loader import RainbowYamlLoader

__author__ = 'omrib'


class TestPreprocessor(TestCase):
    def setUp(self):
        with open('yamlfile/base.yaml') as f:
            self.yamlfile = RainbowYamlLoader(f).get_data()

    def test_yaml_file(self):
        with open('yamlfile/includeme.file') as f:
            self.assertEqual(
                self.yamlfile['included_file'],
                f.read()
            )

    def test_yaml_file64(self):
        with open('yamlfile/includeme.file64') as f:
            self.assertEqual(
                self.yamlfile['included_file64'],
                f.read().encode('base64')
            )

    def test_yaml_yaml(self):
        with open('yamlfile/includeme.yaml') as f:
            self.assertEqual(
                self.yamlfile['included_yaml'],
                RainbowYamlLoader(f).get_data()
            )
