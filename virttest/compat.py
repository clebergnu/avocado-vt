import argparse

from avocado.core.settings import settings


def is_registering_settings_required():
    """Checks the characteristics of the Avocado settings API.

    And signals if the explicit registration of options is required, along
    with other API details that should be followed.

    The heuristic used here is to check for methods that are only present
    in the new API, and should be "safe enough".

    TODO: remove this once support for Avocado releases before 81.0,
    including 69.x LTS is dropped.
    """
    return (hasattr(settings, 'add_argparser_to_option') and
            hasattr(settings, 'register_option') and
            hasattr(settings, 'as_json'))


if is_registering_settings_required():
    def get_opt(opt, name):
        """
        Compatibility handler for options in either argparse.Namespace or dict

        :param opt: either an argpase.Namespace instance or a dict
        :param name: the name of the attribute or key
        """
        return opt.get(name)


    def set_opt(opt, name, value):
        """
        Compatibility handler for options in either argparse.Namespace or dict

        :param opt: either an argpase.Namespace instance or a dict
        :param name: the name of the attribute or key
        :param value: the value to be set
        """
        opt[name] = value
else:
    def get_opt(opt, name):
        if isinstance(opt, argparse.Namespace):
            return getattr(opt, name, None)
        else:
            return opt.get(name)


    def set_opt(opt, name, value):
        if isinstance(opt, argparse.Namespace):
            setattr(opt, name, value)
        else:
            opt[name] = value