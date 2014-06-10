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
            if len(template) == 1 and template.keys()[0].startswith('Rb::'):
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
