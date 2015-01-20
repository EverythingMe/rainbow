#
# Copyright 2014 DoAT. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY DoAT ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL DoAT OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of DoAT

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
        