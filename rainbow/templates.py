import copy
from rainbow.yaml_loader import RainbowYamlLoader


def is_cfn_magic(d):
    """
    Given dict `d`, determine if it uses CFN magic (Fn:: functions or Ref)
    This function is used for deep merging CFN templates, we don't treat CFN magic as a regular dictionary
    for merging purposes.

    :rtype: bool
    :param d: dictionary to check
    :return: true if the dictionary uses CFN magic, false if not
    """

    if len(d) != 1:
        return False

    k = d.keys()[0]

    if k == 'Ref' or k.startswith('Fn::') or k.startswith('Rb::'):
        return True

    return False


def cfn_deep_merge(a, b):
    """
    Deep merge two CFN templates, treating CFN magics (see `is_cfn_magic` for more information) as non-mergeable
    Prefers b over a

    :rtype: dict
    :param a: first dictionary
    :param b: second dictionary (overrides a)
    :return: a new dictionary which is a merge of a and b
    """

    # if a and b are dictionaries and both of them aren't cfn magic, merge them
    if isinstance(a, dict) and isinstance(b, dict) and not (is_cfn_magic(a) or is_cfn_magic(b)):
        # we're modifying and returning a, so start off with a copy
        a = copy.deepcopy(a)

        # merge two dictionaries
        for k in b:
            if k in a:
                a[k] = cfn_deep_merge(a[k], b[k])
            else:
                a[k] = copy.deepcopy(b[k])

        return a
    else:
        return copy.deepcopy(b)


class TemplateLoader(object):
    @staticmethod
    def load_templates(templates):
        """
        Load & merge templates

        :param templates: list of template paths (strings)
        :type templates: list
        :return: merged template
        :rtype: dict
        """

        template = {}
        for template_path in templates:
            with open(template_path) as f:
                template = cfn_deep_merge(template, RainbowYamlLoader(f).get_data())

        return template
