import mock
import functools
from unittest import TestCase
from rainbow.datasources import DataSourceCollection
from rainbow.cloudformation import Cloudformation


__author__ = 'omrib'


def mock_boto_cloudformation_connect_to_region(region, stacks):
    return MockCloudformationConnection(region, stacks)


class DotDict(dict):
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value


class MockCloudformationConnection(object):
    def __init__(self, region, stacks):
        """
        :type region: str
        :type stacks: dict
        """

        self.region = region
        self.stacks = stacks

    # noinspection PyUnusedLocal
    def describe_stacks(self, stack_name_or_id=None, next_token=None):
        if stack_name_or_id:
            return [self.stacks[self.region][stack_name_or_id]]
        else:
            return self.stacks[self.region].values()


class MockCloudformationStack(object):
    def __init__(self, resources={}, outputs={}):
        self._resources = resources
        self._outputs = outputs

    def describe_resources(self):
        return [DotDict(logical_resource_id=key, physical_resource_id=value)
                for key, value in self._resources.iteritems()]

    @property
    def outputs(self):
        return [DotDict(key=key, value=value)
                for key, value in self._outputs.iteritems()]


class TestDataSources(TestCase):
    def setUp(self):
        Cloudformation.default_region = 'us-east-1'

        # c can override b, which can override a
        data_sources = ['cfn_resources:us-stack1',
                        'cfn_outputs:us-stack2',
                        'cfn_resources:eu-west-1:eu-stack1',
                        'cfn_outputs:eu-west-1:eu-stack2']

        stacks = {
            'us-east-1': {
                'us-stack1': MockCloudformationStack(resources={'UsResource1': 'us-stack1-UsResource1-ABCDEFGH'}),
                'us-stack2': MockCloudformationStack(outputs={'UsOutput1': 'US output'})
            },
            'eu-west-1': {
                'eu-stack1': MockCloudformationStack(resources={'EuResource1': 'eu-stack1-EuResource1-ABCDEFGH'}),
                'eu-stack2': MockCloudformationStack(outputs={'EuOutput1': 'EU output'})
            }
        }

        with mock.patch('boto.cloudformation.connect_to_region',
                        functools.partial(mock_boto_cloudformation_connect_to_region, stacks=stacks)):
            self.datasource_collection = DataSourceCollection(data_sources)

    def test_cfn_resources_implicit_region(self):
        self.assertEqual(self.datasource_collection.get_parameter_recursive('UsResource1'), 'us-stack1-UsResource1-ABCDEFGH')

    def test_cfn_outputs_implicit_region(self):
        self.assertEqual(self.datasource_collection.get_parameter_recursive('UsOutput1'), 'US output')

    def test_cfn_resources_ecplicit_region(self):
        self.assertEqual(self.datasource_collection.get_parameter_recursive('EuResource1'), 'eu-stack1-EuResource1-ABCDEFGH')

    def test_cfn_outputs_explicit_region(self):
        self.assertEqual(self.datasource_collection.get_parameter_recursive('EuOutput1'), 'EU output')
