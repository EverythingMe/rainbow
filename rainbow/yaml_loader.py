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

import yaml
import re
from rainbow.datasources.base import DataCollectionPointer


class RainbowYamlLoader(yaml.Loader):
    @staticmethod
    def yaml_pointer(loader, node):
        """
        DataSource pointer, wraps the string in a DataCollectionPointer() object

        :param loader: loader.add_constructor parameter
        :param node: loader.add_constructor parameter
        :rtype: DataCollectionPointer
        :return: File content as string
        """

        value = loader.construct_scalar(node)

        # remove implicit resolver character
        if value[0] == '$':
            value = value[1:]

        return DataCollectionPointer(value)

    @staticmethod
    def yaml_file(loader, node):
        """
        Load file content as string to YAML

        :param loader: loader.add_constructor parameter
        :param node: loader.add_constructor parameter
        :rtype: str
        :return: File content as string
        """

        value = loader.construct_scalar(node)
        with open(value) as f:
            return f.read()

    @classmethod
    def yaml_file64(cls, loader, node):
        """
        Same as yaml_file, but returns base64 encoded data

        :param loader: loader.add_constructor parameter
        :param node: loader.add_constructor parameter
        :rtype: str
        :return: File content as base64 encoded string
        """

        return cls.yaml_file(loader, node).encode('base64')

    @staticmethod
    def yaml_yaml(loader, node):
        """
        Yo dawg, we heard you like YAML...
        Same as yaml_file, but returns a yaml decoded data

        :param loader: loader.add_constructor parameter
        :param node: loader.add_constructor parameter
        :return: File content as base64 encoded string
        """
        template_path = loader.construct_scalar(node)

        if ':' in template_path:
            key, yaml_file = template_path.split(':', 1)
        else:
            yaml_file = template_path
            key = None

        with open(yaml_file) as f:
            template = RainbowYamlLoader(f).get_data()
            
        if key:
            template = template[key]
        return template


    def __init__(self, *args, **kwargs):
        self.add_constructor('!file', self.__class__.yaml_file)
        self.add_constructor('!file64', self.__class__.yaml_file64)
        self.add_constructor('!yaml', self.__class__.yaml_yaml)
        self.add_constructor('!pointer', self.__class__.yaml_pointer)
        self.add_implicit_resolver('!pointer', re.compile(r'^\$\S+'), None)

        super(RainbowYamlLoader, self).__init__(*args, **kwargs)
