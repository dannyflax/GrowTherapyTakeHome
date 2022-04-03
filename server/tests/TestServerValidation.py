import unittest

import sys
sys.path.insert(1, '../')

from ServerValidation import ValidateNode, kStringObject, kIntObject, kYearStringObject, kMonthStringObject, kDateStringObject

class TestServerValidation(unittest.TestCase):
    def assertResultAndErrorStart(self, ValidationObject, ExpectedResult, ExpectedErrorStart):
        self.assertEqual(ValidationObject[0], ExpectedResult)
        if ExpectedErrorStart is not None:
            self.assertTrue(ValidationObject[1].startswith(ExpectedErrorStart), "%s doesn't start with %s" % (ValidationObject[1], ExpectedErrorStart))

    def testInvalidSpec(self):
        invalid_spec_1 = 123
        invalid_spec_2 = {
          "object_type" : "array",
          "required_values" : kStringObject
        }
        invalid_spec_3 = {
          "object_type" : "array",
          "valid_types" : kIntObject
        }
        invalid_spec_4 = {
          "object_type" : "dict",
          "required_keys" : 123
        }
        invalid_spec_5 = {
          "object_type" : "dict",
          "required_keys" : ["key1"],
          "key_values" : [kIntObject]
        }
        self.assertResultAndErrorStart(ValidateNode({}, invalid_spec_1), False, "Invalid Spec - Spec must start with a dict with a key")
        self.assertResultAndErrorStart(ValidateNode([123], invalid_spec_2), False, "Invalid Spec - Expected required_values to be a list")
        self.assertResultAndErrorStart(ValidateNode([123], invalid_spec_3), False, "Invalid Spec - Expected valid_types to be a list")
        self.assertResultAndErrorStart(ValidateNode({}, invalid_spec_4), False, "Invalid Spec - Expected required_keys to be a list")
        self.assertResultAndErrorStart(ValidateNode({"key1" : 123}, invalid_spec_5), False, "Invalid Spec - Expected key_values to be a dict")

    def testArrayNoSettings(self):
        spec = {
          "object_type" : "array" 
        }  
        self.assertResultAndErrorStart(ValidateNode([], spec), True, None)
        self.assertResultAndErrorStart(ValidateNode([123], spec), True, None)
        self.assertResultAndErrorStart(ValidateNode(["123", 123], spec), True, None)
        self.assertResultAndErrorStart(ValidateNode(["123", "123", [1, 2, 3]], spec), True, None)
        self.assertResultAndErrorStart(ValidateNode(123, spec), False, None)
        self.assertResultAndErrorStart(ValidateNode({}, spec), False, None)

    def testArrayRequiredValues(self):
        spec = {
           "object_type" : "array",
           "required_values" : [kStringObject, kIntObject, kDateStringObject] 
        }
        self.assertResultAndErrorStart(ValidateNode(["string", 123, "5.15.2019"], spec), True, None)

        self.assertResultAndErrorStart(ValidateNode(["only_two_objects", 123], spec), False, None)
        self.assertResultAndErrorStart(ValidateNode(["string", "not_an_int", "5.15.2019"], spec), False, None)
        self.assertResultAndErrorStart(ValidateNode(["string", 123, "Invalid_Date"], spec), False, None)

    def testArrayValidTypes(self):
        spec = {
          "object_type" : "array",
          "valid_types" : [kIntObject, kDateStringObject] 
        }

        self.assertResultAndErrorStart(ValidateNode([123, "5.15.2019"], spec), True, None)
        self.assertResultAndErrorStart(ValidateNode(["5.15.2019"], spec), True, None)
        self.assertResultAndErrorStart(ValidateNode([123, 542], spec), True, None)
        self.assertResultAndErrorStart(ValidateNode([], spec), True, None)

        self.assertResultAndErrorStart(ValidateNode(["not_a_date", 123], spec), False, None)
        self.assertResultAndErrorStart(ValidateNode([123, 345, [23, 342]], spec), False, None)

    def testDictNoSettings(self):
        spec = {
          "object_type" : "dict" 
        }
        self.assertResultAndErrorStart(ValidateNode({}, spec), True, None)
        self.assertResultAndErrorStart(ValidateNode({"key" : 123}, spec), True, None)
        self.assertResultAndErrorStart(ValidateNode({"key1" : 123, "key2" : [123, 23]}, spec), True, None)
        
        self.assertResultAndErrorStart(ValidateNode(123, spec), False, None)
        self.assertResultAndErrorStart(ValidateNode([], spec), False, None)

    def testDictKeyValues(self):
        spec = {
           "object_type" : "dict",
           "required_keys" : ["key1", "key2", "key3"],
            "key_values" : {
             "key1" : kStringObject,
             "key3" : kDateStringObject 
           }
        }

        self.assertResultAndErrorStart(ValidateNode({"key1" : "string", "key2" : [1, 2, 3], "key3" : "12.29.1995"}, spec), True, None)
        self.assertResultAndErrorStart(ValidateNode({"key1" : "string", "key2" : 256, "key3" : "12.29.1995", "key5" : "whatever"}, spec), True, None)

        self.assertResultAndErrorStart(ValidateNode({"key1" : 123, "key2" : [1, 2, 3], "key3" : "not_a_date"}, spec), False, None)
        self.assertResultAndErrorStart(ValidateNode({"key1" : "string", "key2" : 256, "key3" : ["abc", "123"]}, spec), False, None)

    def testDictRequiredKeys(self):
        spec = {
           "object_type" : "dict",
           "required_keys" : ["key1", "key2", "key3"] 
        }

        self.assertResultAndErrorStart(ValidateNode({"key1" : 123, "key2" : [1, 2, 3], "key3" : "12.29.1995"}, spec), True, None)
        self.assertResultAndErrorStart(ValidateNode( {"key1" : 123, "key2" : [1, 2, 3], "key3" : "12.29.1995", "key5" : "whatever"}, spec), True, None)

        self.assertResultAndErrorStart(ValidateNode({"key1" : 123, "key2" : [1, 2, 3], "key5" : "whatever"}, spec), False, None)
        self.assertResultAndErrorStart(ValidateNode({}, spec), False, None)
    
if __name__ == '__main__':
    unittest.main()