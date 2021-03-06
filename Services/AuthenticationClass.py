#!/usr/bin/python3


import requests
import base64
import json
import platform
import datetime


class Authentication:

    url = 'https://api.syncplicity.com/oauth/token'
    login_data = 'grant_type=client_credentials'

    def __init__(self):
        if platform.system() == 'Windows':
            path_to_file = '.\Services\ConfigurationFile'
        else:
            path_to_file = 'Services/ConfigurationFile'
        with open(path_to_file, 'r', newline=None) as Credentials_File:
            self.Credentials = json.load(Credentials_File)

        self.AppKey = self.Credentials['App Key']
        self.AppSecret = self.Credentials['App Secret']
        self.AppToken = self.Credentials['Application Token']
        # auth_time_buffer is a number in seconds. It is used to calculate auth_time_to_live.
        # We decrease the auth server reported token lifetime (expires_in) by this buffer time.
        # This way there is always enough time to renew a token
        # regardless of network latency, clock skew between this machine and the auth server, etc.
        self.auth_time_buffer = 100

        if self.AppSecret == "":
            raise ValueError('Missing App Secret! Please enter App Secret in configuration file')
        if self.AppToken == "":
            raise ValueError('Missing Application Token! Please enter Application Token in configuration file')

        self.OAuthBasic = base64.b64encode((self.AppKey + ":" + self.AppSecret).encode('ascii')).decode('utf8')
        self.login_headers = {'Authorization': 'Basic %s' % self.OAuthBasic, 'Sync-App-Token': '%s' % self.AppToken,
                              'Content-Type': 'application/x-www-form-urlencoded'}

        # request = requests.post(self.url, data=self.login_data, headers=self.login_headers,
        #                         proxies={"http":"http://127.0.0.1:PORT", "https": "http://127.0.0.1:PORT"},
        #                         verify=r'PATH\TO\CERTIFICATE')
        request = requests.post(self.url, data=self.login_data, headers=self.login_headers)

        if request.status_code != 200:
            raise ValueError(
                'Failed to complete authentication, received error code %s %s' % (request.status_code, request.reason))
                
        self.auth_timestamp = int(datetime.datetime.now().timestamp())
        json_data = json.loads(request.content.decode('utf8'))
        self.AccessToken = json_data["access_token"]
        self.Company_ID = json_data["user_company_id"]
        self.AuthenticatedUserId = json_data["user_id"]
        self.expires_in = json_data["expires_in"]
        self.auth_time_to_live = int(self.expires_in) - int(self.auth_time_buffer)
