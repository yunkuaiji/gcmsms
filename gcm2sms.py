#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  2015 广西云会计财税服务有限公司 (http://www.yunkuaiji.me)
#via Google Cloud Messaging send sms
#see http://netbizltd.com/wp/budget-sms-gateway/
"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import sys
import json
import logging
import getpass
from optparse import OptionParser

import sleekxmpp
import xml
import xml.sax.saxutils
from sleekxmpp.xmlstream import ElementBase, register_stanza_plugin
from sleekxmpp.xmlstream.matcher import MatchXPath
from sleekxmpp.xmlstream.handler import Callback
import uuid

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

SERVER = 'gcm.googleapis.com'
PORT = 5235
USERNAME = 'xxxxxx@gcm.googleapis.com'
PASSWORD = ' '
regid = 'android device reg_id '

#from sleekxmpp.plugins.xep_0199.ping import XEP_0199


#class XEP_0199_m(XEP_0199):
#    default_config = {
#        'keepalive': True,
#        'interval': 100,
#        'timeout': 10
#    }

#definition GCM  stanzas
class Gcm(ElementBase):
    namespace = 'google:mobile:data'
    name = 'gcm'
    plugin_attrib = 'gcm'
    interfaces = set('gcm')
    sub_interfaces = interfaces


class GcmMessage(ElementBase):
    namespace = ''
    name = 'message'
    interfaces = set('gcm')
    sub_interfaces = interfaces
    subitem = (Gcm,)


register_stanza_plugin(GcmMessage, Gcm)


class EchoBot(sleekxmpp.ClientXMPP):
    """
    A simple SleekXMPP bot that will echo messages it
    receives, along with a short thank you message.
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.register_handler(
            Callback('GcmMessage', MatchXPath('{%s}message/{%s}gcm' % (self.default_ns, 'google:mobile:data')),
                     self.message_callback))
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        #self.add_event_handler("Message", self.message)

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        # self.send_presence()
        # self.get_roster()

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()

    def send_gcm_message(self, message):
        msg = GcmMessage()
        msg['gcm'].xml.text = xml.sax.saxutils.escape(json.dumps(message, ensure_ascii=False))

        self.send(msg)

    # I could then access the JSON data using:

    def message_callback(self, message):
        gcm = json.loads(message.xml.find('{google:mobile:data}gcm').text)
        print gcm
        if gcm.get('message_type', False) in ('ack', 'receipt'):
            if gcm['message_type'] == 'ack':
                print "########################################################"
                print u"GCM接收信息成功！"
            if gcm.get('message_type', False) == 'receipt':
                print "########################################################"
                print gcm['data']['message_status']
                print u"GCM发送信息至手机成功！"
        if gcm.get('data', False) and gcm['data'].has_key('test'):
            print "########################################################"
            print(u"接收入GCMSMS Android app测试信息成功")
        if gcm.get('data', False) and gcm['data'].has_key('text'):
            print "########################################################"
            print gcm['data']['number']+"-"+gcm['data']['text']
            print(u"接收入GCMSMS Android app测试信息成功")

if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-t", "--to", dest="to",
                    help="JID to send the message to")
    optp.add_option("-m", "--message", dest="message",
                    help="message to send")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = USERNAME
    if opts.password is None:
        opts.password = PASSWORD
        # getpass.getpass("Password: ")
    if opts.to is None:
        opts.to = regid
    if opts.message is None:
        opts.message = {
            "to": regid,
            "message_id": uuid.uuid1().urn[9:],
            "data":
                {
                    "number": "mobile number",
                    "message": u"odoo 测试 GCMSMS 网关:sleepxmpp",
                },
            "time_to_live": 600,
            "delay_while_idle": True,
            "delivery_receipt_requested": True
        }
    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = EchoBot(opts.jid, opts.password)
    #xmpp.register_plugin('xep_0030')  # Service Discovery
    #xmpp.register_plugin('xep_0004')  # Data Forms
    #xmpp.register_plugin('xep_0060')  # PubSub
    xmpp.register_plugin('xep_0184')
    xmpp.register_plugin('xep_0198')
    xmpp.register_plugin('xep_0199')  # XMPP Ping

    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect(('gcm.googleapis.com', 5235), use_ssl=True):
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.send_gcm_message(opts.message)
        xmpp.process(block=False)
        print("Done")
    else:
        print("Unable to connect.")
