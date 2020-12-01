from avocado.core.nrunner import Runnable
from avocado.core.plugin_interfaces import Resolver
from avocado.core.resolver import (ReferenceResolution,
                                   ReferenceResolutionResult)
from avocado.core.settings import settings

from .. import loader


class VTResolver(Resolver):

    name = 'vt'
    description = 'Test resolver for Avocado-VT tests'

    @staticmethod
    def _test_factory_to_runnable(test_factory):
        klass, params = test_factory
        url = params.get('name')
        vt_params = params.get('vt_params')

        # Flatten the vt_params, discarding the attributes that are not
        # scalars, and will not be used in the context of nrunner
        for key in ('_name_map_file', '_short_name_map_file', 'dep'):
            if key in vt_params:
                del(vt_params[key])

        return Runnable('avocado-vt', url, **vt_params)

    @staticmethod
    def resolve(reference):
        config = settings.as_dict()
        vt_loader = loader.VirtTestLoader(config, {})
        suite = vt_loader.discover(reference)
        runnables = [VTResolver._test_factory_to_runnable(_) for _ in suite]
        if runnables:
            return ReferenceResolution(reference,
                                       ReferenceResolutionResult.SUCCESS,
                                       runnables)
        else:
            return ReferenceResolution(reference,
                                       ReferenceResolutionResult.NOTFOUND)
