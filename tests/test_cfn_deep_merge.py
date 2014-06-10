from unittest import TestCase
from rainbow.yaml_loader import RainbowYamlLoader
from rainbow.templates import cfn_deep_merge

__author__ = 'omrib'


class TestCfnDeepMerge(TestCase):
    def setUp(self):
        with open('cfn_deep_merge/a.yaml') as a, \
                open('cfn_deep_merge/b.yaml') as b, \
                open('cfn_deep_merge/c.yaml') as c:
            self.a = RainbowYamlLoader(a).get_data()
            self.b = RainbowYamlLoader(b).get_data()
            self.c = RainbowYamlLoader(c).get_data()

    def test_cfn_deep_merge(self):
        a_b_merged = cfn_deep_merge(self.a, self.b)
        self.assertDictEqual(self.c, a_b_merged)
