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


def namespace_to_section_key(namespace, section_size=1):
    """Converts an namespace into a section and key pair.

    A namespace in the new Avocado settings module consists of a dot
    separated components words, of which some may be mapped to a
    configuration file section, and some to a configuration file
    key under such a section.  For example:

    [major.minor]
    key = value

    Would be mapped to a "major.minor.key" namespace.  In the
    configuration dictionary, a user would look for "major.minor.key".
    Because we need to revert the process, and obtain the section name
    and key name from the namespace, it's necessary to give the
    size of components for the section, and the key is assumed to be
    the rest.
    """
    components = namespace.split('.', section_size)
    key = components.pop()
    section = '.'.join(components)
    return section, key


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

    def set_opt_from_settings(opt, namespace, section_size=1, **kwargs):
        """No-op, default values are set at settings.register_option()."""
        pass


    def get_settings_value(section, key, **kwargs):
        namespace = '%s.%s' % (section, key)
        return settings.as_dict().get(namespace)
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


    def set_opt_from_settings(opt, namespace, section_size=1, **kwargs):
        """Sets option default value from the configuration file."""
        section, key = namespace_to_section_key(namespace, section_size)
        value = settings.get_value(section, key, **kwargs)
        set_opt(opt, namespace, value)


    def get_settings_value(section, key, **kwargs):
        settings.get_value(section, key, **kwargs)
