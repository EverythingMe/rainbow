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
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE =OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of DoAT

import time
import json
import itertools
import boto.cloudformation
import boto.exception


def boto_all(func, *args, **kwargs):
    """
    Iterate through all boto next_token's
    """

    ret = [func(*args, **kwargs)]

    while ret[-1].next_token:
        kwargs['next_token'] = ret[-1].next_token
        ret.append(func(*args, **kwargs))

    # flatten it by 1 level
    return list(reduce(itertools.chain, ret))


class StackStatus(str):
    pass


class StackSuccessStatus(StackStatus):
    pass


class StackFailStatus(StackStatus):
    pass


class CloudformationException(Exception):
    pass


class Cloudformation(object):
    default_region = 'us-east-1'

    def __init__(self, region=None):
        """
        :param region: AWS region
        :type region: str
        """

        self.connection = boto.cloudformation.connect_to_region(region or Cloudformation.default_region)

        if not self.connection:
            raise CloudformationException('Invalid region %s' % (region or Cloudformation.default_region,))

    @staticmethod
    def resolve_template_parameters(template, datasource_collection):
        """
        Resolve all template parameters from datasource_collection, return a dictionary of parameters
        to pass to update_stack() or create_stack() methods

        :type template: dict
        :type datasource_collection: DataSourceCollection
        :rtype: dict
        :return: parameters parameter for update_stack() or create_stack()
        """

        parameters = {}
        for parameter, parameter_definition in template.get('Parameters', {}).iteritems():
            if 'Default' in parameter_definition and not parameter in datasource_collection:
                parameter_value = parameter_definition['Default']
            else:
                parameter_value = datasource_collection.get_parameter_recursive(parameter)

                if hasattr(parameter_value, '__iter__'):
                    parameter_value = ', '.join(map(str, parameter_value))

            parameters[parameter] = parameter_value

        return parameters

    def update_stack(self, name, template, parameters):
        """
        Update CFN stack

        :param name: stack name
        :type name: str
        :param template: JSON encodeable object
        :type template: str
        :param parameters: dictionary containing key value pairs as CFN parameters
        :type parameters: dict
        """

        try:
            self.connection.update_stack(name, json.dumps(template), disable_rollback=True,
                                         parameters=parameters.items(), capabilities=['CAPABILITY_IAM'])
        except boto.exception.BotoServerError, ex:
            raise CloudformationException('error occured while updating stack %s: %s' % (name, ex.message))

    def create_stack(self, name, template, parameters):
        """
        Create CFN stack

        :param name: stack name
        :type name: str
        :param template: JSON encodeable object
        :type template: str
        :param parameters: dictionary containing key value pairs as CFN parameters
        :type parameters: dict
        """

        try:
            self.connection.create_stack(name, json.dumps(template), disable_rollback=True,
                                         parameters=parameters.items(), capabilities=['CAPABILITY_IAM'])
        except boto.exception.BotoServerError, ex:
            raise CloudformationException('error occured while creating stack %s: %s' % (name, ex.message))

    def describe_stack_events(self, name):
        """
        Describe CFN stack events

        :param name: stack name
        :type name: str
        :return: stack events
        :rtype: list of boto.cloudformation.stack.StackEvent
        """

        return boto_all(self.connection.describe_stack_events, name)

    def describe_stack(self, name):
        """
        Describe CFN stack

        :param name: stack name
        :return: stack object
        :rtype: boto.cloudformation.stack.Stack
        """

        return self.connection.describe_stacks(name)[0]

    def tail_stack_events(self, name, initial_entry=None):
        """
        This function is a wrapper around _tail_stack_events(), because a generator function doesn't run any code
        before the first iterator item is accessed (aka .next() is called).
        This function can be called without an `inital_entry` and tail the stack events from the bottom.

        Each iteration returns either:
        1. StackFailStatus object which indicates the stack creation/update failed (last iteration)
        2. StackSuccessStatus object which indicates the stack creation/update succeeded (last iteration)
        3. dictionary describing the stack event, containing the following keys: resource_type, logical_resource_id,
           physical_resource_id, resource_status, resource_status_reason

        A common usage pattern would be to call tail_stack_events('stack') prior to running update_stack() on it,
        thus creating the iterator prior to the actual beginning of the update. Then, after initiating the update
        process, for loop through the iterator receiving the generated events and status updates.

        :param name: stack name
        :type name: str
        :param initial_entry: where to start tailing from. None means to start from the last item (exclusive)
        :type initial_entry: None or int
        :return: generator object yielding stack events
        :rtype: generator
        """

        if initial_entry is None:
            return self._tail_stack_events(name, len(self.describe_stack_events(name)))
        else:
            return self._tail_stack_events(name, initial_entry)

    def _tail_stack_events(self, name, initial_entry):
        """
        See tail_stack_events()
        """

        previous_stack_events = initial_entry

        while True:
            stack = self.describe_stack(name)
            stack_events = self.describe_stack_events(name)

            if len(stack_events) > previous_stack_events:
                # iterate on all new events, at reversed order (the list is sorted from newest to oldest)
                for event in stack_events[:-previous_stack_events or None][::-1]:
                    yield {'resource_type': event.resource_type,
                           'logical_resource_id': event.logical_resource_id,
                           'physical_resource_id': event.physical_resource_id,
                           'resource_status': event.resource_status,
                           'resource_status_reason': event.resource_status_reason}

                previous_stack_events = len(stack_events)

            if stack.stack_status.endswith('_FAILED') or \
                    stack.stack_status in ('ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE'):
                yield StackFailStatus(stack.stack_status)
                break
            elif stack.stack_status.endswith('_COMPLETE'):
                yield StackSuccessStatus(stack.stack_status)
                break

            time.sleep(2)
