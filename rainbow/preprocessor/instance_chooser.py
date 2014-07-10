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

from base import PreprocessorBase
from preprocessor_exceptions import PreprocessorBaseException
from rainbow.datasources.base import DataCollectionPointer


regions_instances = {
    'us-east-1': ['m3.large', 'm3.2xlarge', 'm1.small', 'c1.medium', 'cg1.4xlarge', 't1.micro', 'cr1.8xlarge',
                  'c3.2xlarge', 'c3.xlarge', 'm1.large', 'hs1.8xlarge', 'c3.8xlarge', 'c3.4xlarge', 'hi1.4xlarge',
                  'i2.8xlarge', 'c1.xlarge', 'm2.2xlarge', 'g2.2xlarge', 'm2.xlarge', 'm1.medium', 'i2.xlarge',
                  'm3.medium', 'cc2.8xlarge', 'i2.2xlarge', 'c3.large', 'i2.4xlarge', 'm1.xlarge', 'm2.4xlarge',
                  'm3.xlarge'],
    'ap-northeast-1': ['m3.large', 'm3.2xlarge', 'm1.small', 'c1.medium', 't1.micro', 'cr1.8xlarge', 'c3.2xlarge',
                       'c3.xlarge', 'm1.large', 'hs1.8xlarge', 'c3.8xlarge', 'c3.4xlarge', 'hi1.4xlarge', 'i2.8xlarge',
                       'c1.xlarge', 'm2.2xlarge', 'g2.2xlarge', 'm2.xlarge', 'm1.medium', 'i2.xlarge', 'm3.medium',
                       'cc2.8xlarge', 'i2.2xlarge', 'c3.large', 'i2.4xlarge', 'm1.xlarge', 'm2.4xlarge', 'm3.xlarge'],
    'eu-west-1': ['m3.large', 'm3.2xlarge', 'm1.small', 'c1.medium', 'cg1.4xlarge', 't1.micro', 'cr1.8xlarge',
                  'c3.2xlarge', 'c3.xlarge', 'm1.large', 'hs1.8xlarge', 'c3.8xlarge', 'c3.4xlarge', 'hi1.4xlarge',
                  'i2.8xlarge', 'c1.xlarge', 'm2.2xlarge', 'g2.2xlarge', 'm2.xlarge', 'm1.medium', 'i2.xlarge',
                  'm3.medium', 'cc2.8xlarge', 'i2.2xlarge', 'c3.large', 'i2.4xlarge', 'm1.xlarge', 'm2.4xlarge',
                  'm3.xlarge'],
    'ap-southeast-1': ['m3.large', 'm3.2xlarge', 'm1.small', 'c1.medium', 't1.micro', 'c3.2xlarge', 'c3.xlarge',
                       'm1.large', 'hs1.8xlarge', 'c3.8xlarge', 'c3.4xlarge', 'i2.8xlarge', 'c1.xlarge', 'm2.2xlarge',
                       'm2.xlarge', 'm1.medium', 'i2.xlarge', 'm3.medium', 'i2.2xlarge', 'c3.large', 'i2.4xlarge',
                       'm1.xlarge', 'm2.4xlarge', 'm3.xlarge'],
    'ap-southeast-2': ['m3.large', 'm3.2xlarge', 'm1.small', 'c1.medium', 't1.micro', 'c3.2xlarge', 'c3.xlarge',
                       'm1.large', 'hs1.8xlarge', 'c3.8xlarge', 'c3.4xlarge', 'i2.8xlarge', 'c1.xlarge', 'm2.2xlarge',
                       'm2.xlarge', 'm1.medium', 'i2.xlarge', 'm3.medium', 'i2.2xlarge', 'c3.large', 'i2.4xlarge',
                       'm1.xlarge', 'm2.4xlarge', 'm3.xlarge'],
    'us-west-2': ['m3.large', 'm3.2xlarge', 'm1.small', 'c1.medium', 't1.micro', 'cr1.8xlarge', 'c3.2xlarge',
                  'c3.xlarge', 'm1.large', 'hs1.8xlarge', 'c3.8xlarge', 'c3.4xlarge', 'hi1.4xlarge', 'i2.8xlarge',
                  'c1.xlarge', 'm2.2xlarge', 'g2.2xlarge', 'm2.xlarge', 'm1.medium', 'i2.xlarge', 'm3.medium',
                  'cc2.8xlarge', 'i2.2xlarge', 'c3.large', 'i2.4xlarge', 'm1.xlarge', 'm2.4xlarge', 'm3.xlarge'],
    'us-west-1': ['m3.large', 'm3.2xlarge', 'm1.small', 'c1.medium', 't1.micro', 'c3.2xlarge', 'c3.xlarge', 'm1.large',
                  'c3.8xlarge', 'c3.4xlarge', 'i2.8xlarge', 'c1.xlarge', 'm2.2xlarge', 'g2.2xlarge', 'm2.xlarge',
                  'm1.medium', 'i2.xlarge', 'm3.medium', 'i2.2xlarge', 'c3.large', 'i2.4xlarge', 'm1.xlarge',
                  'm2.4xlarge', 'm3.xlarge'],
    'sa-east-1': ['m3.large', 'm3.2xlarge', 'm1.small', 'c1.medium', 't1.micro', 'm1.large', 'c1.xlarge', 'm2.2xlarge',
                  'm2.xlarge', 'm1.medium', 'm3.medium', 'm1.xlarge', 'm2.4xlarge', 'm3.xlarge']
}


class InvalidInstanceException(PreprocessorBaseException):
    pass


@PreprocessorBase.expose('InstanceChooser')
def instance_chooser(preprocessor, instance_types):
    """
    Rb::InstanceChooser
        Choose the first valid instance (for the current region).
        For example, if a certain region doesn't support the c3 instances family, you can specify 'c3.large'
        with a fallback to 'c1.medium'. The function returns the first instance type that's available on that region.
    Example usage:
        {'Rb::InstanceChooser': ['c3.large', 'c1.medium']}
    On a region that supports c3.large, 'c3.large' will be returned
    On a region that doesn't, 'c1.medium' will be returned

    :param preprocessor: Preprocessor instance processing the function
    :type preprocessor: Preprocessor
    :param instance_types: list of instance types to choose from
    :type instance_types: list
    :rtype: str
    """

    if isinstance(instance_types, DataCollectionPointer):
        instance_types = preprocessor.datasource_collection.get_parameter_recursive(instance_types)

    if not hasattr(instance_types, '__iter__'):
        raise InvalidInstanceException('Instance types should be an iterable (a list)')

    # resolve pointers if relevant
    for i, v in enumerate(instance_types):
        if isinstance(v, DataCollectionPointer):
            instance_types[i] = preprocessor.datasource_collection.get_parameter_recursive(str(v))

    available_instance_types = [instance_type for instance_type in instance_types
                                if instance_type in regions_instances[preprocessor.region]]

    if not available_instance_types:
        raise InvalidInstanceException(
            "Unable to find a suitable instance type for region %s out of %r. Available instances: %r" %
            (preprocessor.region, instance_types, regions_instances[preprocessor.region]))
    else:
        return available_instance_types[0]
