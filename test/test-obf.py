import unittest

import obf, json

class TestObfuscator(unittest.TestCase):

    simple_json = {
        "key1": "value1",
        "list1": ["listvalue1", 123, "listvalue3"],
        "list2": ["listvalue1", 123, "listvalue3", ["sublistvalue1", "sublistvalue2"]],
        "object1": {
            "key1": "value1",
            "list1": ["listvalue1", 123, "listvalue3"],
            "list2": ["listvalue1", 123, "listvalue3", ["sublistvalue1", "sublistvalue2"]],
            "list3": ["listvalue1", {"key1": "value1", "key2": "value2"}, "listvalue3"]
        },
        "key2": "value2"

    }

    def setUp(self):
        self.o=obf.obf.obfuscator()
        self.simple_json_string=json.dumps(self.simple_json)    # obfuscator actually works on JSON strings, not dicts

    def test_basic_text_encoding_with_blocked_words(self):
        self.o.blockedwords = ['example', 'but', 'unused', 'blocked', 'words']
        e=self.o.encode_text("hello world example words")
        self.assertEqual(e,"hello world RESTRICTIONS ASSOILS")

    def test_basic_text_encoding(self):
        e=self.o.encode_text("hello world")
        self.assertEqual(e,"SPRIGHTFUL HAPPENINGS")

    def test_email_address(self):
        # specific email address obfuscation functionality only works when you are trying to obfuscate particular words
        # so we need to set some specific blocked words
        self.o.blockedwords=['example','but','unused','blocked','words']
        e=self.o.encode_text('bob.roberts@emailaddress.com')
        self.assertEqual(e,"DREAMING.DISORDERS@PARLAYS.com")
        self.o.excluded_domains.append('emailaddress')
        e = self.o.encode_text('bob.roberts@emailaddress.com')
        self.assertEqual(e, "DREAMING.DISORDERS@emailaddress.com")


    def test_json_encoding(self):
        keys_to_encode = {'key1', "list1", "list2", "list3"}
        o_simple_json = self.o.encode_json(self.simple_json_string, keys_to_encode)
        self.assertEqual(o_simple_json['key1'],"VIBISTS1")
        self.assertEqual(o_simple_json['key2'], "value2")
        self.assertEqual(o_simple_json['list1'],["PLANKS1",123,"PLANKS3"])
        self.assertEqual(o_simple_json['object1']['key1'],"VIBISTS1")
        self.assertEqual(o_simple_json['object1']['list2'], ['PLANKS1', 123, 'PLANKS3', ['PIONS1', 'PIONS2']])
        self.assertEqual(o_simple_json['object1']['list3'][1], {"key1": "VIBISTS1", "key2": "value2"})

if __name__ == '__main__':
    unittest.main()