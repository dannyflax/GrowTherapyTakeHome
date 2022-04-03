import unittest

import sys
sys.path.insert(1, '../')

from ServerValidation import ValidateNode, kStringObject, kIntObject, kYearStringObject, kMonthStringObject, kDateStringObject
from Server import Api1Week, Api1Month, Api2Week, Api2Month, Api3

kErrorResponseFormat = {
    "object_type" : "dict",
    "required_keys" : ["error"]
}

kSuccessResponseFormat = {
    "object_type" : "dict",
    "required_keys" : ["payload"]
}

kMockApi1SuccessPayloadWeek = [
    {'article': 'Main_Page', 'views': 48177160}, 
    {'article': 'Special:Search', 'views': 9644296}, 
    {'article': 'Bridgerton', 'views': 2735520}, 
    {'article': 'Wonder_Woman_1984', 'views': 2107456}
]

kMockApi1SuccessPayloadMonth = [
    {'article': 'Main_Page', 'views': 192708640}, 
    {'article': 'Special:Search', 'views': 38577184}, 
    {'article': 'Bridgerton', 'views': 10942080}, 
    {'article': 'Wonder_Woman_1984', 'views': 8429824}
]

kMockApi2SuccessPayload = 59591621

kMockApi3SuccessPayload = "2021-12-04 00:00:00"

kMockValidWeeksParams = {
    "startDate" : "5.29.2020",
    "articleName" : "Main_Page"
}

kMockInvalidWeeksParams = {
    "startDate" : "WRONG_DATE",
    "articleName" : 12345
}

kMockValidMonthsParams = {
    "month" : "12",
    "year" : "2020",
    "articleName" : "Main_Page"
}

kMockInvalidMonthsParams = {
    "month" : "-39",
    "year" : "asdfsda",
    "articleName" : 1234
}

kMockDataForApi1 = {
  "items": [
    {
      "project": "en.wikipedia",
      "access": "all-access",
      "year": "2020",
      "month": "12",
      "day": "29",
      "articles": [
        {
          "article": "Main_Page",
          "views": 6022145,
          "rank": 1
        },
        {
          "article": "Special:Search",
          "views": 1205537,
          "rank": 2
        },
        {
          "article": "Bridgerton",
          "views": 341940,
          "rank": 3
        },
        {
          "article": "Wonder_Woman_1984",
          "views": 263432,
          "rank": 4
        }
      ]
    }
  ]
}

kMockDataForApi2Api3 = {
  "items": [
    {
      "project": "en.wikipedia",
      "article": "Main_Page",
      "granularity": "daily",
      "timestamp": "2021120100",
      "access": "all-access",
      "agent": "all-agents",
      "views": 12442109
    },
    {
      "project": "en.wikipedia",
      "article": "Main_Page",
      "granularity": "daily",
      "timestamp": "2021120200",
      "access": "all-access",
      "agent": "all-agents",
      "views": 11651980
    },
    {
      "project": "en.wikipedia",
      "article": "Main_Page",
      "granularity": "daily",
      "timestamp": "2021120300",
      "access": "all-access",
      "agent": "all-agents",
      "views": 10599348
    },
    {
      "project": "en.wikipedia",
      "article": "Main_Page",
      "granularity": "daily",
      "timestamp": "2021120400",
      "access": "all-access",
      "agent": "all-agents",
      "views": 12824514
    },
    {
      "project": "en.wikipedia",
      "article": "Main_Page",
      "granularity": "daily",
      "timestamp": "2021120500",
      "access": "all-access",
      "agent": "all-agents",
      "views": 12073670
    }
  ]
}


kMockInvalidDataForApi1 = {
  "ite222ms": [
    {
      "project": "en.wikipedia",
      "access": "all-access",
      "year": "2020",
      "month": "12",
      "day": "29",
      "articles": [
        {
          "article": "Main_Page",
          "views": 6022145,
          "rank": 1
        },
        {
          "article": "Special:Search",
          "views": 1205537,
          "rank": 2
        },
        {
          "article": "Bridgerton",
          "views": 341940,
          "rank": 3
        },
        {
          "article": "Wonder_Woman_1984",
          "views": 263432,
          "rank": 4
        }
      ]
    }
  ]
}

kMockInvalidDataForApi2Api3 = {
  "ite222ms": [
    {
      "project": "en.wikipedia",
      "article": "Main_Page",
      "granularity": "daily",
      "timestamp": "2021120100",
      "access": "all-access",
      "agent": "all-agents",
      "views": 12442109
    },
    {
      "project": "en.wikipedia",
      "article": "Main_Page",
      "granularity": "daily",
      "timestamp": "2021120200",
      "access": "all-access",
      "agent": "all-agents",
      "views": 11651980
    },
    {
      "project": "en.wikipedia",
      "article": "Main_Page",
      "granularity": "daily",
      "timestamp": "2021120300",
      "access": "all-access",
      "agent": "all-agents",
      "views": 10599348
    },
    {
      "project": "en.wikipedia",
      "article": "Main_Page",
      "granularity": "daily",
      "timestamp": "2021120400",
      "access": "all-access",
      "agent": "all-agents",
      "views": 12824514
    },
    {
      "project": "en.wikipedia",
      "article": "Main_Page",
      "granularity": "daily",
      "timestamp": "2021120500",
      "access": "all-access",
      "agent": "all-agents",
      "views": 12073670
    }
  ]
}

class MockResponse:
    __attrs__ = ['status_code', 'data']

    def __init__(self, Data, StatusCode):
        self.status_code = StatusCode
        self.data = Data

    def json(self):
        return self.data

class MockQueryExecutor():
    def execute(self, query):
        if query.startswith("/top/en.wikipedia/all-access/"):
            return MockResponse(kMockDataForApi1, 200)
        if query.startswith("/per-article/en.wikipedia.org/all-access/"):
            return MockResponse(kMockDataForApi2Api3, 200)

class MockBadResponseQueryExecutor():
    def execute(self, query):
        if query.startswith("/top/en.wikipedia/all-access/"):
            return MockResponse(kMockInvalidDataForApi1, 200)
        if query.startswith("/per-article/en.wikipedia.org/all-access/"):
            return MockResponse(kMockInvalidDataForApi2Api3, 200)

class TestServerValidation(unittest.TestCase):
    def assertResultMatchesFormat(self, Result, Format):
        validationResult = ValidateNode(Result, Format)
        self.assertTrue(validationResult[0], validationResult[1])

    def testApi1WeekSuccess(self):
        result = Api1Week(MockQueryExecutor(), kMockValidWeeksParams)
        self.assertResultMatchesFormat(result, kSuccessResponseFormat)
        self.assertEqual(result["payload"], kMockApi1SuccessPayloadWeek)

    def testApi1WeekFail(self):
        result = Api1Week(MockQueryExecutor(), kMockInvalidWeeksParams)
        self.assertResultMatchesFormat(result, kErrorResponseFormat)

    def testApi1WeekBadResponse(self):
        result = Api1Week(MockBadResponseQueryExecutor(), kMockValidWeeksParams)
        self.assertResultMatchesFormat(result, kErrorResponseFormat)


    def testApi1MonthSuccess(self):
        result = Api1Month(MockQueryExecutor(), kMockValidMonthsParams)
        self.assertResultMatchesFormat(result, kSuccessResponseFormat)
        self.assertEqual(result["payload"], kMockApi1SuccessPayloadMonth)

    def testApi1MonthFail(self):
        result = Api1Month(MockQueryExecutor(), kMockInvalidMonthsParams)
        self.assertResultMatchesFormat(result, kErrorResponseFormat)

    def testApi1MonthBadResponse(self):
        result = Api1Month(MockBadResponseQueryExecutor(), kMockValidMonthsParams)
        self.assertResultMatchesFormat(result, kErrorResponseFormat)


    def testApi2WeekSuccess(self):
        result = Api2Week(MockQueryExecutor(), kMockValidWeeksParams)
        self.assertResultMatchesFormat(result, kSuccessResponseFormat)
        self.assertEqual(result["payload"], kMockApi2SuccessPayload)

    def testApi2WeekFail(self):
        result = Api2Week(MockQueryExecutor(), kMockInvalidWeeksParams)
        self.assertResultMatchesFormat(result, kErrorResponseFormat)

    def testApi2WeekBadResponse(self):
        result = Api2Week(MockBadResponseQueryExecutor(), kMockValidWeeksParams)
        self.assertResultMatchesFormat(result, kErrorResponseFormat)


    def testApi2MonthSuccess(self):
        result = Api2Month(MockQueryExecutor(), kMockValidMonthsParams)
        self.assertResultMatchesFormat(result, kSuccessResponseFormat)
        self.assertEqual(result["payload"], kMockApi2SuccessPayload)

    def testApi2MonthFail(self):
        result = Api2Month(MockQueryExecutor(), kMockInvalidMonthsParams)
        self.assertResultMatchesFormat(result, kErrorResponseFormat)

    def testApi2MonthBadResponse(self):
        result = Api2Month(MockBadResponseQueryExecutor(), kMockValidMonthsParams)
        self.assertResultMatchesFormat(result, kErrorResponseFormat)


    def testApi3Success(self):
        result = Api3(MockQueryExecutor(), kMockValidMonthsParams)
        self.assertResultMatchesFormat(result, kSuccessResponseFormat)
        self.assertEqual(result["payload"], kMockApi3SuccessPayload)

    def testApi3Fail(self):
        result = Api3(MockQueryExecutor(), kMockInvalidMonthsParams)
        self.assertResultMatchesFormat(result, kErrorResponseFormat)

    def testApi3BadResponse(self):
        result = Api3(MockBadResponseQueryExecutor(), kMockValidMonthsParams)
        self.assertResultMatchesFormat(result, kErrorResponseFormat)
