# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
from mozsvc.config import get_configurator
from mozsvc.plugin import load_and_register


def includeme(config):
    config.include("cornice")
    config.include("mozsvc")
    config.include("pyramid_whoauth")
    config.scan("tokenserver.views")
    # initializes the backend
    load_and_register("tokenserver", config)


def main(global_config, **settings):
    config = get_configurator(global_config, **settings)
    config.include(includeme)
    return config.make_wsgi_app()