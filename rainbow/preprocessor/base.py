import copy
from preprocessor_exceptions import *


class PreprocessorBase(object):
    functions = {}

    @classmethod
    def expose(cls, name):
        """
        Decorator function to expose a function as a preprocessor function

        Example usage:
            @PreprocessorBase.expose('MyAwesomeFunction')
            def myfunc(preprocessor, parameter):
                return '[%s]' % (parameter,)


        Given the following template (YAML):
            key: value
            key2: {'Rb::MyAwesomeFunction': 'a great value'}

        The preprocessor will return:
            {'key': 'value',
             'key2': '[a great value]'}
        """

        def decorator(f):
            cls.functions[name] = f
            return f

        return decorator


class Preprocessor(object):
    def __init__(self, datasource_collection, region):
        self.datasource_collection = datasource_collection
        self.region = region

    def process(self, template):
        """
        Go through template, look for {'Rb::FunctionName': <parameters>} dictionaries, calling the Rainbow function
        FunctionName to process them.

        :type template: dict
        :param template: input dictionary
        :return: a copy of the template dictionary with all the Rb:: function calls processed
        """

        template = copy.deepcopy(template)

        if isinstance(template, dict):
            if len(template) == 1 and type(template.keys()[0]) is str and template.keys()[0].startswith('Rb::'):
                k, v = template.items()[0]
                if k.startswith('Rb::'):
                    function = k[4:]
                    if not function in PreprocessorBase.functions:
                        raise InvalidPreprocessorFunctionException(
                            'Rainbow Function (Rb::) %s not found in %r' % (function,
                                                                            PreprocessorBase.functions.keys(),))
                    else:
                        return PreprocessorBase.functions[function](self, v)
            else:
                for k, v in template.iteritems():
                    template[k] = self.process(v)

        return template
