from rainbow.cloudformation import Cloudformation
from base import DataSourceBase

__all__ = ['CfnOutputsDataSource', 'CfnResourcesDataSource', 'CfnParametersDataSource']


class CfnDataSourceBase(DataSourceBase):
    def __init__(self, data_source):
        super(CfnDataSourceBase, self).__init__(data_source)

        stack_name = data_source
        region = Cloudformation.default_region

        if ':' in data_source:
            region, stack_name = data_source.split(':', 1)

        cfn_connection = Cloudformation(region)
        if not cfn_connection:
            raise Exception('Invalid region %r' % (region,))

        self.stack = cfn_connection.describe_stack(stack_name)


class CfnOutputsDataSource(CfnDataSourceBase):
    datasource_name = 'cfn_outputs'

    def __init__(self, data_source):
        super(CfnOutputsDataSource, self).__init__(data_source)

        self.data = {i.key: i.value for i in self.stack.outputs}


class CfnResourcesDataSource(CfnDataSourceBase):
    datasource_name = 'cfn_resources'

    def __init__(self, data_source):
        super(CfnResourcesDataSource, self).__init__(data_source)

        self.data = {r.logical_resource_id: r.physical_resource_id for r in self.stack.describe_resources()}


class CfnParametersDataSource(CfnDataSourceBase):
    datasource_name = 'cfn_parameters'

    def __init__(self, data_source):
        super(CfnParametersDataSource, self).__init__(data_source)
        
        self.data = {p.key: p.value for p in self.stack.parameters}
        
