import http
import json
from unittest import TestCase
import auth
from auth import AuthError

AUDIENCE = "coffee-shop-api-id"

AUTH0_DOMAIN = "sw-ark.eu.auth0.com"
CLIENT_ID = "AXZyXNVKFfJ4ak6Tgs1buK0ZHuafGf7H"
TD_UN_HY_J_Z = "s0PAy7M_CPBLslXk_qdXuDlIaBMsDttt-wWYA0o3EvY4ljO7nhy4TdUN3Hy-j19z"
EXPIRED_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNra3RjcXFPczVsSHBvQW0wY2lCbyJ9' \
                '.' \
                'eyJpc3MiOiJodHRwczovL3N3LWFyay5ldS5hdXRoMC5jb20vIiwic3ViIjoiQVhaeVhOVktGZko0YWs2VGdzMWJ1SzBaSHVhZkdmN0hAY2xpZW50cyIsImF1ZCI6ImNvZmZlZS1zaG9wLWFwaS1pZCIsImlhdCI6MTU5Njg0OTQ1NSwiZXhwIjoxNTk2OTM1ODU1LCJhenAiOiJBWFp5WE5WS0ZmSjRhazZUZ3MxYnVLMFpIdWFmR2Y3SCIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyIsInBlcm1pc3Npb25zIjpbXX0' \
                '.' \
                'mwWNQ_kie9hFn_h2QtNJeZ7LEfuIuub1J2yCrlxFg8H3Xk-T-nMaOhgBpO4UcuHy-_1a_Mlb8ZFLpfKO3ausqzsAlbhbmPomq9DRbgMJqWbZ2ArPG7nVuyVx2difI-CUh0nXZ-FpshkcavB9r-dx-XDA_6Xq2JJd3jB_3DqSqEIVxj_rY7FHwBm0IEMpo9tMfaC5mgmcorUZGqUIjPd36gi65AvXqEzKbs9A2pYKOBqvihiREOaIr-7oy8UYZDD8Za3zXgcK75l5vqwxpQRtzWFG6PYg9DWhAGUIvlN1vSHIGXDzUTPJOEMupKM2ig-lft6Ui7LDONrRc0ihMdjteQ'


class AuthTestCase(TestCase):

    def test_decodeValidToken_tokenPayloadReturned(self):
        token = get_valid_token()
        payload = auth.verify_decode_jwt(token)
        self.assertIsNotNone(payload)
        for k in ['iss', 'sub', 'aud', 'azp', 'gty', 'permissions']:
            self.assertIn(k, payload)

    def test_decodeInvalidToken_thenAuthError(self):
        with self.assertRaises(AuthError) as context:
            auth.verify_decode_jwt('invalidtoken')
        self.assertEqual(context.exception.error['code'], 'invalid_token')
        self.assertEqual(context.exception.error['description'], 'Incorrect token provided.')
        self.assertEqual(context.exception.status_code, 400)

    def test_decodeExpiredToken_thenAuthError(self):
        with self.assertRaises(AuthError) as context:
            auth.verify_decode_jwt(EXPIRED_TOKEN)
        self.assertEqual(context.exception.error['code'], 'token_expired')
        self.assertEqual(context.exception.error['description'], 'Token expired.')
        self.assertEqual(context.exception.status_code, 401)

    def test_checkUnAuthorizedPermission_thenAuthError(self):
        with self.assertRaises(AuthError) as context:
            auth.check_permissions("edit:7amada", {"permissions": []})
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.error['code'], 'unauthorized_action')
        self.assertEqual(context.exception.error['description'], 'Action is not authorized')

    def test_authorizedPermission_theTrueReturned(self):
        result = auth.check_permissions("edit:user", {"permissions": ["edit:user"]})
        self.assertEqual(result, True)


def get_valid_token():
    conn = http.client.HTTPSConnection(AUTH0_DOMAIN)

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": TD_UN_HY_J_Z,
        "audience": AUDIENCE, "grant_type": "client_credentials"
    }

    headers = {'content-type': "application/json"}

    conn.request("POST", "/oauth/token", json.dumps(payload), headers)

    res = conn.getresponse()
    data = res.read()
    token_obj = json.loads(data)
    return token_obj['access_token']
