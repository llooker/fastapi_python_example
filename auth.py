import urllib
import base64
import json
import time
import binascii
import os
from hashlib import sha1
import six
import six.moves.urllib as urllib

import hmac

import configparser
import looker_sdk

CONFIG_FILE = 'config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILE)


user_data = {
     'user_1':{
         'external_user_id':"pythonruss@example.com"
        ,'first_name':"Russ"
        ,'last_name':"Python"
        ,'permissions':[
            "access_data",
            "see_looks",
            "see_user_dashboards",
            "see_lookml_dashboards",
            "download_with_limit"
        ]
        ,'models':['thelook']
        ,'access_filters':{}
        ,'user_attributes':{'my_attribute':'my_value'}
        ,'group_ids':[1,2]
        ,'external_group_id':None
     }
    ,'user_2':{
         'external_user_id':"mrbean@example.com"
        ,'first_name':"Mr"
        ,'last_name':"Bean"
        ,'permissions':[
            "access_data",
            "see_looks",
            "see_user_dashboards",
            "see_lookml_dashboards",
            "download_with_limit",
            "schedule_look_emails",
            "schedule_external_look_emails",
            "create_alerts",
            "see_drill_overlay",
            "save_content",
            "embed_browse_spaces",
            "schedule_look_emails",
            "send_to_sftp",
            "send_to_s3",
            "send_outgoing_webhook",
            "send_to_integration",
            "download_without_limit",
            "explore",
            "see_sql"
        ]
        ,'models':['thelook']
        ,'access_filters':{}
        ,'user_attributes':{'my_attribute':'my_value'}
        ,'group_ids':[1,2]
        ,'external_group_id':None
    }
}



class Looker:
  def __init__(self, host, secret):
    self.secret = secret
    self.host = host
  def __str__(self):
    return f'host: {self.host} \n secret: {self.secret}'


class User:
  def __init__(self, external_user_id=None, first_name=None, last_name=None,
               permissions=[], models=[], group_ids=[], external_group_id=None,
               user_attributes={}, access_filters={}):
    self.external_user_id = external_user_id
    self.first_name = first_name
    self.last_name = last_name
    self.permissions = permissions
    self.models = models
    self.access_filters = access_filters
    self.user_attributes = user_attributes
    self.group_ids = group_ids
    self.external_group_id = external_group_id

class UserJsonify:
  def __init__(self, external_user_id=None, first_name=None, last_name=None,
               permissions=[], models=[], group_ids=[], external_group_id=None,
               user_attributes={}, access_filters={}):
    self.external_user_id = json.dumps(external_user_id)
    self.first_name = json.dumps(first_name)
    self.last_name = json.dumps(last_name)
    self.permissions = json.dumps(permissions)
    self.models = json.dumps(models)
    self.access_filters = json.dumps(access_filters)
    self.user_attributes = json.dumps(user_attributes)
    self.group_ids = json.dumps(group_ids)
    self.external_group_id = json.dumps(external_group_id)


class URL:
  def __init__(self, looker, user, session_length, embed_url, force_logout_login=False):
    self.looker = looker
    self.user = user
    embed_url = urllib.parse.unquote(embed_url)
    self.path = '/login/embed/' + urllib.parse.quote_plus(embed_url)
    self.session_length = json.dumps(session_length)
    self.force_logout_login = json.dumps(force_logout_login)

  def set_time(self):
    self.time = json.dumps(int(time.time()))

  def set_nonce(self):
    def to_ascii(s):
      """Compatibility function for converting between Python 2.7 and 3 calls"""
      if isinstance(s, six.text_type):
        return s
      elif isinstance(s, six.binary_type):
        return "".join(map(chr, map(ord, s.decode(encoding='UTF-8'))))
      return s
    self.nonce = json.dumps(to_ascii(binascii.hexlify(os.urandom(16))))

  def sign(self):
    #  Do not change the order of these
    string_to_sign = "\n".join([self.looker.host,
                                self.path,
                                self.nonce,
                                self.time,
                                self.session_length,
                                self.user.external_user_id,
                                self.user.permissions,
                                self.user.models,
                                self.user.group_ids,
                                self.user.external_group_id,
                                self.user.user_attributes,
                                self.user.access_filters])

    signer = hmac.new(bytearray(self.looker.secret, 'UTF-8'), string_to_sign.encode('UTF-8'), sha1)
    self.signature = base64.b64encode(signer.digest())

  def to_string(self):
    self.set_time()
    self.set_nonce()
    self.sign()
    params = {
              'nonce':               self.nonce,
              'time':                self.time,
              'session_length':      self.session_length,
              'external_user_id':    self.user.external_user_id,
              'permissions':         self.user.permissions,
              'models':              self.user.models,
              'group_ids':           self.user.group_ids,
              'external_group_id':   self.user.external_group_id,
              'user_attributes':     self.user.user_attributes,
              'access_filters':      self.user.access_filters,
              'signature':           self.signature,
              'first_name':          self.user.first_name,
              'last_name':           self.user.last_name,
              'force_logout_login':  self.force_logout_login}
    query_string = '&'.join(["%s=%s" % (key, urllib.parse.quote_plus(val)) for key, val in params.items()])
    return "%s%s?%s" % (self.looker.host, self.path, query_string)


def generateUrlLocally(src:str="",userToken=""):
  looker = Looker(config['embed']['EMBED_HOST'], config['embed']['SECRET'])
  user = UserJsonify(**user_data[userToken])
  url = URL(looker, user, 1500, src, force_logout_login=True)
  return "https://" + url.to_string()


looker = looker_sdk.init40(config_file=CONFIG_FILE,section='api')

def urlFromLookerAPI(src:str="",userToken:str=""):
    user = User(**user_data[userToken])
    return looker.create_sso_embed_url({
            "target_url": f"https://{config['embed']['EMBED_HOST']}{src}",
            "session_length": 1500,
            "force_logout_login": False,
            "external_user_id": user.external_user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "permissions": user.permissions,
            "models": user.models,
            "group_ids": user.group_ids,
            "external_group_id": user.external_group_id,
            "user_attributes": user.user_attributes,
            })
