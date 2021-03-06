from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime, timedelta
from enum import Enum
import requests
import ServerValidation

app = Flask(__name__)
api = Api(app)

# Don't count leap years for now...
kDaysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

kValidationSuccessMessage = "Success"
kApiErrorMessage = "Failed to access Wikipedia API or response is in non-json format."

kWikipediaBase = "https://wikimedia.org/api/rest_v1/metrics/pageviews"

# Without a user agent, Wikipedia will block our requests.
kRequestContentHeaders = {
    'user-agent' : 'GrowTherapy (https://growtherapy.com/)'
}

kFormatViewsNode = {
                      "object_type" : "dict",
                      "required_keys" : ["project", "article", "granularity", "timestamp", "access", "agent", "views"],
                      "key_values" : {
                        "project" : ServerValidation.kStringObject, 
                        "article" : ServerValidation.kStringObject, 
                        "granularity" : ServerValidation.kStringObject, 
                        "timestamp" : ServerValidation.kStringObject, 
                        "access" : ServerValidation.kStringObject, 
                        "agent" : ServerValidation.kStringObject, 
                        "views" : ServerValidation.kIntObject
                      }
                    }

kViewsResponseFormat = {
  "object_type" : "dict",
  "required_keys" : ["items"],
  "key_values" : {
     "items" : {
                "object_type" : "array",
                "valid_types" : [kFormatViewsNode]
                }
  }
}

kArticleObjectFormat = {
    "object_type" : "dict",
    "required_keys" : ["article", "views"],
    "key_values" : {
        "article" : ServerValidation.kStringObject,
        "views" : ServerValidation.kIntObject,
    }
}

kArticlesResponseFormat = {
    "object_type" : "dict",
    "required_keys" : ["articles"],
        "key_values" : {
            "articles" : {
              "object_type" : "array",
              "required_values" : [kArticleObjectFormat],
              "required_keys" : [kArticleObjectFormat]
            }
        }
}

kArticlesItemsResponseFormat = {
  "object_type" : "dict",
  "required_keys" : ["items"],
  "key_values" : {
     "items" : {
                "object_type" : "array",
                "required_values" : [kArticlesResponseFormat],
                "valid_types" : [kArticlesResponseFormat]
                }
  }
}

kArticlesListResponseFormat = {
    "object_type" : "array",
    "required_values" : [kArticlesItemsResponseFormat],
    "valid_types" : [kArticlesItemsResponseFormat]
}

class WikiRequestsQueryExecutor:
    def execute(self, query):
        return requests.get(kWikipediaBase + query, headers=kRequestContentHeaders)

def ValidateArgsNonEmpty(ArgKeys, Args):
    for key in ArgKeys:
        if Args.get(key) is None:
            return False
    return True

def CreateValidatorFromParams(Params):
    return {
        "object_type" : "dict",
        "required_keys" : list(Params.keys()),
        "key_values" : Params
    }

def CastAndValidateParams(Args, ArgValueMap):
    validator = CreateValidatorFromParams(ArgValueMap)
    validationResult = ServerValidation.ValidateNode(Args, validator)
    if not validationResult[0]:
        return (False, validationResult[1])
    if not ValidateArgsNonEmpty(ArgValueMap.keys(), Args):
        return (False, "Required args empty after validation")
    result = {}
    for key, value in ArgValueMap.items():
        if value["object_type"] is "month_string":
            monthValue = ServerValidation.AttemptCastDigit(Args.get(key))
            if monthValue[1] <= 0 or monthValue[1] > 12:
                return (False, "Failed to cast month string after validation")
            result[key] = monthValue[1]
        if value["object_type"] is "year_string":
            yearValue = ServerValidation.AttemptCastDigit(Args.get(key))
            if yearValue[1] <= 0:
                return (False, "Failed to cast year string after validation")
            result[key] = yearValue[1]
        if value["object_type"] is "date_string":
            dateValue = ServerValidation.AttemptCastDate(Args.get(key))
            if not dateValue[0]:
                return (False, "Failed to cast date string after validation")
            result[key] = dateValue[1]
        if value["object_type"] is "string":
            result[key] = Args.get(key)
    return (True, result)

def ValidateResponse(Response):
    if Response.status_code is 200:
        try:
            Response.json()
            return True
        except RequestsJSONDecodeError:
            return False
    return False

def CollectResponsesFromQueries(Queries, Executor):
    results = []
    for query in Queries:
        response = Executor.execute(query)
        if ValidateResponse(response):
            results.append(response.json())
    return results

def PythonDateToWikiDateString(PythonDate):
    return PythonDate.strftime("%Y/%m/%d")

def PythonDateToWikiDateStringApi2(PythonDate):
    return PythonDate.strftime("%Y%m%d")

def ComputeDatesListFromStartDate(StartDate, AdditionalDays):
    dates = []
    for i in range(0, AdditionalDays + 1):
        dates.append(PythonDateToWikiDateString(StartDate + timedelta(days=i)))
    return dates

def SumViewsFromDateResponses(DateResponses):
    viewsMap = {}
    for dateResponse in DateResponses:
        for articleData in dateResponse["items"][0]["articles"]:
            article = articleData["article"]
            if not article in viewsMap:
                viewsMap[article] = 0
            viewsMap[article] = viewsMap[article] + int(articleData["views"])
    return viewsMap

def SortedResponseFromViewSums(ViewSums):
    sorted_keys = sorted(ViewSums, key=ViewSums.get, reverse=True)
    results = []
    for key in sorted_keys:
        results.append({
            "article" : key,
            "views" : ViewSums[key]
        })
    return results

def SumViewCountsReponse(ViewCountsResponse):
    sum = 0
    for item in ViewCountsResponse["items"]:
        sum = sum + item["views"]
    return sum

def MaxDayFromCountsResponse(ViewCountsResponse):
    max = 0
    maxDate = None
    for item in ViewCountsResponse["items"]:
        if item["views"] > max:
            max = item["views"]
            maxDate = item["timestamp"]
    return datetime.strptime(
        maxDate, 
        '%Y%m%d%M'
    )

def WrapSuccessResponse(Response):
    return {"payload" : Response}

def WrapErrorResponse(Error):
    return {"error" : Error}

# Api1Week - Top Pages By Week
#
# Calculates the most viewed pages in a given week.
#
# Params:
#   startDate - The start date for the week. Will count this day and the 6 following.
#
# Payload Example: 
# 
# [
#     {'article': 'Main_Page', 'views': 48177160}, 
#     {'article': 'Special:Search', 'views': 9644296}, 
#     {'article': 'Bridgerton', 'views': 2735520}, 
#     {'article': 'Wonder_Woman_1984', 'views': 2107456}
# ]
#  

class MainApi1Week(Resource):
    def get(self):
        return Api1Week(WikiRequestsQueryExecutor(), request.args)

def Api1Week(Executor, Args):
    paramSetup = {
        "startDate" : ServerValidation.kDateStringObject
    }
    paramsResult = CastAndValidateParams(Args, paramSetup)
    if not paramsResult[0]:
        return WrapErrorResponse("Incorrect Parameters - %s" % paramsResult[1])
    paramsDict = paramsResult[1]
    dateStrings = ComputeDatesListFromStartDate(paramsDict["startDate"], 7)
    queries = map(lambda dateString: "/top/en.wikipedia/all-access/" + dateString, dateStrings)
    responses = CollectResponsesFromQueries(queries, Executor)
    validationResult = ServerValidation.ValidateNode(responses, kArticlesListResponseFormat)
    if not validationResult[0]:
        return WrapErrorResponse("Failed to parse response: %s" % validationResult[1])
    view_sums = SumViewsFromDateResponses(responses)
    return WrapSuccessResponse(SortedResponseFromViewSums(view_sums))

# Api1Month - Top Pages By Month
#
# Calculates the most viewed pages in a given calendar month and year. Does not account for leap years.
#
# Params:
#   month - The desired month
#   year - The desired year
#
# Payload Example: 
# 
# [
#     {'article': 'Main_Page', 'views': 48177160}, 
#     {'article': 'Special:Search', 'views': 9644296}, 
#     {'article': 'Bridgerton', 'views': 2735520}, 
#     {'article': 'Wonder_Woman_1984', 'views': 2107456}
# ]
#  

class MainApi1Month(Resource):
    def get(self):
        return Api1Month(WikiRequestsQueryExecutor(), request.args)

def Api1Month(Executor, Args):
    paramSetup = {
        "month" : ServerValidation.kMonthStringObject,
        "year" : ServerValidation.kYearStringObject
    }
    paramsResult = CastAndValidateParams(Args, paramSetup)
    if not paramsResult[0]:
        return WrapErrorResponse("Incorrect Parameters - %s" % paramsResult[1])
    paramsDict = paramsResult[1]
    startDate = datetime(year=paramsDict["year"], month=paramsDict["month"], day=1)
    daysNumber = kDaysPerMonth[paramsDict["month"] - 1]
    dateStrings = ComputeDatesListFromStartDate(startDate, daysNumber)
    queries = map(lambda dateString: "/top/en.wikipedia/all-access/" + dateString, dateStrings)
    responses = CollectResponsesFromQueries(queries, Executor)
    validationResult = ServerValidation.ValidateNode(responses, kArticlesListResponseFormat)
    if not validationResult[0]:
        return WrapErrorResponse("Failed to parse response: %s" % validationResult[1])
    view_sums = SumViewsFromDateResponses(responses)
    return WrapSuccessResponse(SortedResponseFromViewSums(view_sums))

# Api2Week - View Count by Week
#
# Calculates total number of views an article had in a given week.
#
# Params:
#   startDate - The start date for the week. Will count this day and the 6 following.
#   articleName - The desired article name
#
# Payload Example: 
#
#   59591621
#  
class MainApi2Week(Resource):
    def get(self):
        return Api2Week(WikiRequestsQueryExecutor(), request.args)

def Api2Week(Executor, Args):
    paramSetup = {
        "startDate" : ServerValidation.kDateStringObject,
        "articleName" : ServerValidation.kStringObject
    }
    paramsResult = CastAndValidateParams(Args, paramSetup)
    if not paramsResult[0]:
        return WrapErrorResponse("Incorrect Parameters - %s" % paramsResult[1])
    paramsDict = paramsResult[1]
    startDate = paramsDict["startDate"]
    articleName = paramsDict["articleName"]
    endDate = startDate + timedelta(days=6)
    response = Executor.execute(
        "/per-article/en.wikipedia.org/all-access/all-agents/%s/daily/%s/%s" % (articleName, PythonDateToWikiDateStringApi2(startDate), PythonDateToWikiDateStringApi2(endDate))
    )
    if not ValidateResponse(response):
        return WrapErrorResponse(kApiErrorMessage)
    validationResult = ServerValidation.ValidateNode(response.json(), kViewsResponseFormat)
    if not validationResult[0]:
        return WrapErrorResponse("Failed to parse response: %s" % validationResult[1])
    return WrapSuccessResponse(SumViewCountsReponse(response.json()))

# Api2Month - View Count by Month
#
# Calculates total number of views an article had in a given month and calendar year.
#
# Params:
#   month - The desired month
#   year - The desired year
#   articleName - The desired article name
#
# Payload Example: 
#
#   59591621
#  
class MainApi2Month(Resource):
    def get(self):
        return Api2Month(WikiRequestsQueryExecutor(), request.args)

def Api2Month(Executor, Args):
        paramSetup = {
            "month" : ServerValidation.kMonthStringObject,
            "year" : ServerValidation.kYearStringObject,
            "articleName" : ServerValidation.kStringObject
        }
        paramsResult = CastAndValidateParams(Args, paramSetup)
        if not paramsResult[0]:
            return WrapErrorResponse("Incorrect Parameters - %s" % paramsResult[1])
        paramsDict = paramsResult[1]
        startDate = datetime(year=paramsDict["year"], month=paramsDict["month"], day=1)
        articleName = paramsDict["articleName"]
        endDate = startDate + timedelta(days=kDaysPerMonth[paramsDict["month"] - 1] - 1)
        response = Executor.execute(
            "/per-article/en.wikipedia.org/all-access/all-agents/%s/daily/%s/%s" % (articleName, PythonDateToWikiDateStringApi2(startDate), PythonDateToWikiDateStringApi2(endDate))
        )
        if not ValidateResponse(response):
            return WrapErrorResponse(kApiErrorMessage)
        validationResult = ServerValidation.ValidateNode(response.json(), kViewsResponseFormat)
        if not validationResult[0]:
            return WrapErrorResponse("Failed to parse response: %s" % validationResult[1])
        return WrapSuccessResponse(SumViewCountsReponse(response.json()))

# Api3 - Date with most page views
#
# Given a month and year, returns the calendar date with the most page views.
#
# Params:
#   month - The desired month
#   year - The desired year
#   articleName - The desired article name
#
# Payload Example: 
#
#   "2021-12-04 00:00:00"
#  
class MainApi3(Resource):
    def get(self):
        return Api3(WikiRequestsQueryExecutor(), request.args)

def Api3(Executor, Args):
    paramSetup = {
        "month" : ServerValidation.kMonthStringObject,
        "year" : ServerValidation.kYearStringObject,
        "articleName" : ServerValidation.kStringObject
    }
    paramsResult = CastAndValidateParams(Args, paramSetup)
    if not paramsResult[0]:
        return WrapErrorResponse("Incorrect Parameters - %s" % paramsResult[1])
    paramsDict = paramsResult[1]
    startDate = datetime(year=paramsDict["year"], month=paramsDict["month"], day=1)
    articleName = paramsDict["articleName"]
    endDate = startDate + timedelta(days=kDaysPerMonth[paramsDict["month"] - 1] - 1)
    response = Executor.execute(
        "/per-article/en.wikipedia.org/all-access/all-agents/%s/daily/%s/%s" % (articleName, PythonDateToWikiDateStringApi2(startDate), PythonDateToWikiDateStringApi2(endDate))
    )
    if not ValidateResponse(response):
        return WrapErrorResponse(kApiErrorMessage)
    validationResult = ServerValidation.ValidateNode(response.json(), kViewsResponseFormat)
    if not validationResult[0]:
        return WrapErrorResponse("Failed to parse response: %s" % validationResult[1])
    return WrapSuccessResponse(str(MaxDayFromCountsResponse(response.json())))

api.add_resource(MainApi1Week, '/main/api1/week')
api.add_resource(MainApi1Month, '/main/api1/month')
api.add_resource(MainApi2Week, '/main/api2/week')
api.add_resource(MainApi2Month, '/main/api2/month')
api.add_resource(MainApi3, '/main/api3')

if __name__ == '__main__':
    app.run() 