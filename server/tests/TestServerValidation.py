import unittest

import sys
sys.path.insert(1, '../')

from ServerValidation import ValidateNode, kStringObject, kIntObject, kYearStringObject, kMonthStringObject

class TestServerValidation(unittest.TestCase):
    def assertResultAndErrorStart(self, ValidationObject, ExpectedResult, ExpectedErrorStart):
        self.assertEqual(ValidationObject[0], ExpectedResult)
        self.assertTrue(ValidationObject[1].startswith(ExpectedErrorStart), "%s doesn't start with %s" % (ValidationObject[1], ExpectedErrorStart))

    def test_invalid_spec(self):
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

if __name__ == '__main__':
    unittest.main()