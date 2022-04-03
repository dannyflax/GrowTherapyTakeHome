# Library for validating JSON dictionaries.
#
# Usage:
#
# 1. Setup a format spec. This will be a python dict object, more details below.
# 2. Call ServerValidation.ValidateNode() on an array or dictionary parsed from JSON, passing in the spec you made in step 1.
# 3. ValidateNode returns a tuple. 
#    The first element is a boolean specifying whether or not the object passed validation.
#    The second element is the reason validation failed, if applicable..
#
# Format Specs:
# 
# Each object in the schema is represented by a json dictionary, of the following format:
# { 
#   "object_type" : "#OBJECT_TYPE",
#   "#ADDITIONAL_OBJECT_SETTINGS" : "..."
#  }
#
# You can specify the following object types:
#
#   string:
#     
#     The only rule here is that these objects must be castable to a string.
#     There are no additional settings to specify for this object.
#
#   month_string:
#     
#     This object must be a string as specified above, and must contain an integer value between 1 and 12.
#     There are no additional settings to specify for this object.
#
#   year_string:
#     
#     This object must be a string as specified above, and must contain an integer value greater than 0.
#     There are no additional settings to specify for this object.
#
#   date_string:
#     
#     This object must be a string as specified above, and must adhere to the following format:
#        "m.d.Y"
#         - m is one or two digits representing the month
#         - d is one or two digits representing the date
#         - Y is four digits represeting the year
#        e.g. "12.29.1995"
#
#     There are no additional settings to specify for this object.
#
#   int:
#    
#     The only rule here is that these objects must be castable to an int.
#     There are no additional settings to specify for this object.
#
#   array:
#
#     This object must be castable to a python list.
#
#     The following additional settings can be applied:
#
#       required_values
#       
#         List specifying the exact object types, in-order, that must be present in the array.
#         If one or more of these objects isn't present at the location specified, validation will fail..
#
#         Example:
#       
        # {
        #    "object_type" : "array",
        #    "required_values" : [kStringObject, kIntObject, kDateStringObject] 
        # }       
#
#         The following list will pass:
#      
#         ["string", 123, "5.15.2019"]
#
#         The following lists will fail:
#
#         ["only_two_objects", 123]
#         ["string", "not_an_int", "5.15.2019"]
#         ["string", 123, "Invalid_Date"]
#
#       valid_types
#
#         List specifying the object types that can exist in the list.
#         If an object appears in the list that does not match one of these types, validation will fail.
#         
#         Example:
#       
#         {
#            "object_type" : "array",
#            "valid_types" : [kIntObject, kDateStringObject] 
#         }       
#
#         The following lists will pass:
#      
#         [123, "5.15.2019"]
#         ["5.15.2019"]
#         [123, 542]
#         []
#
#         The following lists will fail:
#
#         ["not_a_date", 123]
#         [123, 345, [23, 342]]
#        
#   dict:
#
#     This object must be castable to a python dict.
#     The following additional settings can be applied:
#
#       required_keys
#       
#         List of strings specifying the keys required for the object to be considered valid.
#         The exact value of the objects at these keys is not important.
#
#         Example:
#       
#         {
#            "object_type" : "dict",
#            "required_keys" : ["key1", "key2", "key3"] 
#         }       
#
#         The following dicts will pass:
#      
#         {"key1" : 123, "key2" : [1, 2, 3], "key3" : "12.29.1995"}
#         {"key1" : 123, "key2" : [1, 2, 3], "key3" : "12.29.1995", "key5" : "whatever"}
#
#         The following dicts will fail:
# 
#         {"key1" : 123, "key2" : [1, 2, 3], "key5" : "whatever"}
#         {}
#
#       key_values
#
#         NOTE: This setting will only be applied if required_keys is applied as well.   
#      
#         Dictionary specifying the required object type for any set of required keys.
#         If the value for any key listed does not match, validation will fail.
#         
#         Example:
#       
#         {
#            "object_type" : "array",
#            "required_keys" : ["key1", "key2", "key3"],
#            "key_values" : {
#              "key1" : kStringObject,
#              "key3" : kDateStringObject 
#            }
#         }    
#   
#         The following dicts will pass:
#      
#         {"key1" : "string", "key2" : [1, 2, 3], "key3" : "12.29.1995"}
#         {"key1" : "string", "key2" : 256, "key3" : "12.29.1995", "key5" : "whatever"}
#
#         The following dicts will fail:
# 
#         {"key1" : 123, "key2" : [1, 2, 3], "key3" : "not_a_date"}
#         {"key1" : "string", "key2" : 256, "key3" : ["abc", "123"]}
#   

from datetime import datetime, timedelta

kMonthStringObject = {"object_type" : "month_string"}
kDateStringObject = {"object_type" : "date_string"}
kYearStringObject = {"object_type" : "year_string"}
kStringObject = {"object_type" : "string"}
kIntObject = {"object_type" : "int"}     

def AttemptCastDigit(DigitString):
    if str.isdigit(DigitString):
        return (True, int(DigitString))
    else:
        return (False, -1)

def AttemptCastDate(DateTime):
    try:
        return (
            True,
            datetime.strptime(
                DateTime, 
                '%m.%d.%Y'
                )
            )
    except ValueError as e:
        return (False, str(e))

def ValidateNode(Node, FormatNode):
    if not isinstance(FormatNode, dict) or not "object_type" in FormatNode:
        return (False, "Invalid Spec - Spec must start with a dict with a key 'object_type'.")
    object_type = FormatNode["object_type"]
    if object_type is "month_string":
        if not isinstance(Node, str):
            return (False, "Expected string but got %s" % str(Node))
        monthValue = AttemptCastDigit(Node)
        if not monthValue[0]:
            return (False, "Cannot parse string as month: %s" % monthValue[1])
        if monthValue[1] <= 0 or monthValue[1] > 12:
            return (False, "Month string must be between 1 and 12.")
        return (True, None)
    if object_type is "year_string":
        if not isinstance(Node, str):
            return (False, "Expected string but got %s" % str(Node))
        yearValue = AttemptCastDigit(Node)
        if not yearValue[0]:
            return (False, "Cannot parse string as year: %s" % yearValue[1])
        if yearValue <= 0:
            return (False, "Year string must be greater than 0.")
        return (True, None)
    if object_type is "date_string":
        if not isinstance(Node, str):
            return (False, "Expected string but got %s" % str(Node))
        dateValue = AttemptCastDate(Node)
        if not dateValue[0]:
            return (False, dateValue[1])
        return (True, None)
    if object_type is "string":
        if not isinstance(Node, str):
            return (False, "Expected string but got %s" % str(Node))
        return (True, None)
    if object_type is "int":
        if not isinstance(Node, int):
            return (False, "Expected int but got %s" % str(Node))
        return (True, None)
    if object_type is "array":
        if not isinstance(Node, list):
            return (False, "Expected array but got %s" % str(Node))
        if "required_values" in FormatNode:
            required_values = FormatNode["required_values"]
            if not isinstance(required_values, list):
                return (False, "Invalid Spec - Expected required_values to be a list, but got %s" % str(required_values))
            if len(required_values) > len(Node):
                return (
                    False, 
                    "Expected array to have %i values but array only had %i - %s" 
                    % (len(required_values), len(Node), str(Node))
                )
            for x in range(0, len(required_values)):
                resp = ValidateNode(Node[x], required_values[x])
                if not resp[0]:
                    return (
                        False, 
                        resp[1]
                    )
        if "valid_types" in FormatNode:
            valid_types = FormatNode["valid_types"]
            if not isinstance(valid_types, list):
                return (False, "Invalid Spec - Expected valid_types to be a list, but got %s" % str(valid_types))
            for value in Node:
                value_valid = False
                for valid_type in valid_types:
                    resp = ValidateNode(value, valid_type)
                    if resp[0]:
                        value_valid = True
                        break
                if not value_valid:
                    return (False, "Value %s not a part of any valid types." % str(value))
        return (True, None)
    if object_type is "dict":
        if not isinstance(Node, dict):
            return (False, "Expected dict but got %s" % str(Node))
        if "required_keys" in FormatNode:
            required_keys = FormatNode["required_keys"]
            if not isinstance(required_keys, list):
                return (False, "Invalid Spec - Expected required_keys to be a list, but got %s" % str(required_keys))
            for key in required_keys:
                if not key in Node:
                    return (False, "Required key %s missing from dict %s" % (key, str(Node)))
            if "key_values" in FormatNode:
                key_values = FormatNode["key_values"]
                if not isinstance(key_values, dict):
                    return (False, "Invalid Spec - Expected key_values to be a dict, but got %s" % str(dict))
                for key in Node:
                    if key in key_values:
                        resp = ValidateNode(Node[key], key_values[key])
                        if not resp[0]:
                            return (False, resp[1])
        return (True, None)

            