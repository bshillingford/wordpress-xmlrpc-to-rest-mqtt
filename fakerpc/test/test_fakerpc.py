from unittest import TestCase
import unittest
from fakerpc.fakerpc import xmlrpc, new_post_helper
import paho.mqtt.client as mqtt
import random


__author__ = 'brendan'


class TestFakeRpc(TestCase):
    def test_GET(self):
        title = "GET http://httpbin.org/get?hello=a"
        body = ""
        summary, = new_post_helper(title, body)

        self.assertIn('hello', summary, 'expect "hello": "a" in result')
        self.assertTrue(summary.startswith("200"), 'expect 200 HTTP status code')

    def test_POST(self):
        title = "POST http://httpbin.org/post"
        body = "{Testing 123 data here.}"
        summary, = new_post_helper(title, body)

        self.assertIn(body, summary, "expect POST data to be in response")

    def test_MQTT(self):
        hostname = "iot.eclipse.org"
        topic = "unit/test/xmlrpc_2_mqtt"
        title = "MQTT-pub mqtt://{}/{}?qos=1&retain=true".format(hostname, topic)
        body = "Testing 123 'this is a test.' %d." % random.randint(0, 1000)
        summary, = new_post_helper(title, body)
        print summary

        called = [False]
        def on_message(client, userdata, msg):
            print msg, "***"
            self.assertEqual(body, msg.payload, 'MQTT payload')
            self.assertEqual(topic, msg.topic, 'MQTT topic')
            self.assertFalse(called[0], "expect to be called only once")
            called[0] = True

        mqttc = mqtt.Client()
        mqttc.on_connect = lambda client, userdata, flags, rc: client.subscribe(topic)
        mqttc.on_message = on_message
        mqttc.connect(hostname)
        for i in range(20):
            mqttc.loop(timeout=1)
            if called[0]:
                break
        self.assertTrue(called[0], "expect to be called only once")

if __name__ == "__main__":
    unittest.main()
