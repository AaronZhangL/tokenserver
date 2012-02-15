# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
from webtest import TestApp
import unittest
import json
import os

from tokenserver import main
from vep import DummyVerifier
from mozsvc.util import CatchErrors

here = os.path.dirname(__file__)


class TestService(unittest.TestCase):

    def setUp(self):

        global_config = {'__file__': os.path.join(here, 'test.ini'),
                         'here': here}

        settings = {'pyramid.includes': 'pyramid_debugtoolbar',
                    'pyramid.debug_authorization': 'false',
                    'pyramid.default_locale_name': 'en',
                    'pyramid.reload_templates': 'true',
                    'pyramid.debug_notfound': 'false',
                    'pyramid.debug_templates': 'true',
                    'mako.directories': 'cornice:templates',
                    'pyramid.debug_routematch': 'false'}

        app = CatchErrors(main(global_config, **settings))
        self.app = TestApp(app)
        self.verifier = DummyVerifier

        def urlopen(url, data): # NOQA
            class response(object):
                @staticmethod
                def read():
                    key = DummyVerifier.fetch_public_key("browserid.org")
                    return json.dumps({"public-key": key})
            return response

        self.verifier.urlopen = urlopen

    def _getassertion(self):
        email = 'tarek@mozilla.com'
        url = 'http://tokenserver.services.mozilla.com'
        return self.verifier.make_assertion(email, url)

    def test_unknown_app(self):
        headers = {'Authorization': 'Browser-ID %s' % self._getassertion()}
        resp = self.app.get('/1.0/xXx/token', headers=headers, status=404)
        self.assertTrue('errors' in resp.json)

    def test_no_auth(self):
        self.app.get('/1.0/sync/2.1', status=401)

    def test_valid_app(self):
        headers = {'Authorization': 'Browser-ID %s' % self._getassertion()}
        res = self.app.get('/1.0/sync/2.1', headers=headers)
        self.assertEqual(res.json['service_entry'], 'http://example.com')