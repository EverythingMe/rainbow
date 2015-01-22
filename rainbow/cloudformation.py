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
    # this is from http://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_Stack.html
    # boto.cloudformation.stack.StackEvent.valid_states doesn't have the full list.
    VALID_STACK_STATUSES = ['CREATE_IN_PROGRESS', 'CREATE_FAILED', 'CREATE_COMPLETE', 'ROLLBACK_IN_PROGRESS',
                            'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'DELETE_IN_PROGRESS', 'DELETE_FAILED',
                            'DELETE_COMPLETE', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
                            'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_IN_PROGRESS', 'UPDATE_ROLLBACK_FAILED',
                            'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE']

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
                    parameter_value = ','.join(map(str, parameter_value))

            parameters[parameter] = parameter_value

        # All template parameters are converted to strings and stripped
        # I couldn't find any documentation for this, but I have tested it myself:
        # template.yaml:
        #     Parameters:
        #       StringParameter:
        #         Type: String
        #       NumberParameter:
        #         Type: Number
        #       CommaDelimitedParameter:
        #         Type: CommaDelimitedList
        #     Resources:
        #       Eip:
        #         Type: AWS::EC2::EIP
        #
        # parameters.yaml:
        #     CommaDelimitedParameter: ["a", " b", "c ", " d "]
        #     StringParameter: "       \n     string that starts and ends with a new line       \n          "
        #     NumberParameter: 10
        #
        # creation:
        #     rainbow -d yaml:parameters.yaml test template.yaml
        #
        # test:
        #     >>> import boto.cloudformation
        #     >>> cfn = boto.cloudformation.connect_to_region('us-east-1')
        #     >>> stack = cfn.describe_stacks('test')[0]
        #     >>> stack.parameters
        #     [Parameter:"StringParameter"="string that starts and ends with a new line",
        #      Parameter:"CommaDelimitedParameter"="a,b,c,d", Parameter:"NumberParameter"="10"]
        return {k: str(v).strip() for k, v in parameters.iteritems()}

    def stack_exists(self, name):
        """
        Check if a CFN stack exists

        :param name: stack name
        :return: True/False
        :rtype: bool
        """

        # conserve bandwidth (and API calls) by not listing any stacks in DELETE_COMPLETE state
        active_stacks = boto_all(self.connection.list_stacks, [state for state in Cloudformation.VALID_STACK_STATUSES
                                                               if state != 'DELETE_COMPLETE'])
        return name in [stack.stack_name for stack in active_stacks if stack.stack_status]

    def update_stack(self, name, template, parameters):
        """
        Update CFN stack

        :param name: stack name
        :type name: str
        :param template: JSON encodeable object
        :type template: str
        :param parameters: dictionary containing key value pairs as CFN parameters
        :type parameters: dict
        :rtype: bool
        :return: False if there aren't any updates to be performed, True if no exception has been thrown.
        """

        try:
            self.connection.update_stack(name, json.dumps(template), disable_rollback=True,
                                         parameters=parameters.items(), capabilities=['CAPABILITY_IAM'])
        except boto.exception.BotoServerError, ex:
            if ex.message == 'No updates are to be performed.':
                # this is not really an error, but there aren't any updates.
                return False
            else:
                raise CloudformationException('error occured while updating stack %s: %s' % (name, ex.message))
        else:
            return True

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
        elif initial_entry < 0:
            return self._tail_stack_events(name, len(self.describe_stack_events(name)) + initial_entry)
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
                           'resource_status_reason': event.resource_status_reason,
                           'timestamp': event.timestamp}

                previous_stack_events = len(stack_events)

            if stack.stack_status.endswith('_FAILED') or \
                    stack.stack_status in ('ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE'):
                yield StackFailStatus(stack.stack_status)
                break
            elif stack.stack_status.endswith('_COMPLETE'):
                yield StackSuccessStatus(stack.stack_status)
                break

            time.sleep(2)
