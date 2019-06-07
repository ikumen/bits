import backend
import json

from .. import TestCase, make_headers, assert_valid_response

class TestBitRoutes(TestCase):

    def test_should_return_json_list_of_bits(self, app, client):
        resp = client.get('/api/bits', headers=make_headers())

        assert_valid_response(resp)
        #print(json.loads(resp.get_data(as_text=True)))