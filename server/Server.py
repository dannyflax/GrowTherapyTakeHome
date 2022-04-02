from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
api = Api(app)

# Don't count leap years for now...
kDaysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# TODO - Better error messages
kValidationErrorMessage = "Incorrect parameters."
kValidationSuccessMessage = "Success"
kApiErrorMessage = "Failed to access Wikipedia API or failed to parse response."

kWikipediaBase = "https://wikimedia.org/api/rest_v1/metrics/pageviews"

# Without a user agent, Wikipedia will block our requests.
kRequestContentHeaders = {
    'user-agent' : 'GrowTherapy (https://growtherapy.com/)'
}

def ValidateArgsNonEmpty(ArgKeys, Args):
    for key in ArgKeys:
        if Args.get(key) is None:
            return False
    return True

def AttemptCastDigit(DigitString):
    if str.isdigit(DigitString):
        return int(DigitString)
    else:
        return -1

def AttemptCastDate(DateTime):
    try:
        return datetime.strptime(
                    request.args.get("startDate"), 
                    '%m.%d.%Y'
                )
    except ValueError:
        return None

def ValidateParams(ArgValueMap, Args):
    result = {}
    if not ValidateArgsNonEmpty(ArgValueMap.keys(), Args):
        return None
    for key, value in ArgValueMap.items():
        if value is "Month":
            monthValue = AttemptCastDigit(Args.get(key))
            if monthValue <= 0 or monthValue > 12:
                return None
            result[key] = monthValue
        if value is "Year":
            yearValue = AttemptCastDigit(Args.get(key))
            if yearValue <= 0:
                return None
            result[key] = yearValue
        if value is "Date":
            dateValue = AttemptCastDate(Args.get(key))
            if dateValue is None:
                return None
            result[key] = dateValue
        if value is "String":
            result[key] = Args.get(key)
    return result

def ValidateResponse(Response):
    if Response.status_code is 200:
        try:
            Response.json()
            return True
        except RequestsJSONDecodeError:
            return False
    return False

def ExecuteQuery(query):
    return requests.get(kWikipediaBase + query, headers=kRequestContentHeaders)

def CollectResponsesFromQueries(Queries):
    results = []
    for query in Queries:
        response = ExecuteQuery(query)
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

class MainApi1Week(Resource):
    def get(self):
        paramSetup = {
            "startDate" : "Date"
        }
        paramsDict = ValidateParams(paramSetup, request.args)
        if paramsDict is None:
            return kValidationErrorMessage
        dateStrings = ComputeDatesListFromStartDate(paramsDict["startDate"], 7)
        queries = map(lambda dateString: "/top/en.wikipedia/all-access/" + dateString, dateStrings)
        responses = CollectResponsesFromQueries(queries)
        view_sums = SumViewsFromDateResponses(responses)
        return SortedResponseFromViewSums(view_sums)

class MainApi1Month(Resource):
    def get(self):
        paramSetup = {
            "month" : "Month",
            "year" : "Year"
        }
        paramsDict = ValidateParams(paramSetup, request.args)
        if paramsDict is None:
            return kValidationErrorMessage
        startDate = datetime(year=paramsDict["year"], month=paramsDict["month"], day=1)
        daysNumber = kDaysPerMonth[paramsDict["month"] - 1]
        dateStrings = ComputeDatesListFromStartDate(startDate, daysNumber)
        queries = map(lambda dateString: "/top/en.wikipedia/all-access/" + dateString, dateStrings)
        responses = CollectResponsesFromQueries(queries)
        view_sums = SumViewsFromDateResponses(responses)
        return SortedResponseFromViewSums(view_sums)

class MainApi2Week(Resource):
    def get(self):
        paramSetup = {
            "startDate" : "Date",
            "articleName" : "String"
        }
        paramsDict = ValidateParams(paramSetup, request.args)
        if paramsDict is None:
            return kValidationErrorMessage
        startDate = paramsDict["startDate"]
        articleName = paramsDict["articleName"]
        endDate = startDate + timedelta(days=6)
        response = ExecuteQuery(
            "/per-article/en.wikipedia.org/all-access/all-agents/%s/daily/%s/%s" % (articleName, PythonDateToWikiDateStringApi2(startDate), PythonDateToWikiDateStringApi2(endDate))
        )
        if not ValidateResponse(response):
            return kValidationErrorMessage
        return SumViewCountsReponse(response.json())

class MainApi2Month(Resource):
    def get(self):
        paramSetup = {
            "month" : "Month",
            "year" : "Year",
            "articleName" : "String"
        }
        paramsDict = ValidateParams(paramSetup, request.args)
        if paramsDict is None:
            return kValidationErrorMessage
        startDate = datetime(year=paramsDict["year"], month=paramsDict["month"], day=1)
        articleName = paramsDict["articleName"]
        endDate = startDate + timedelta(days=kDaysPerMonth[paramsDict["month"] - 1] - 1)
        response = ExecuteQuery(
            "/per-article/en.wikipedia.org/all-access/all-agents/%s/daily/%s/%s" % (articleName, PythonDateToWikiDateStringApi2(startDate), PythonDateToWikiDateStringApi2(endDate))
        )
        if not ValidateResponse(response):
            return kValidationErrorMessage
        return SumViewCountsReponse(response.json())

class MainApi3(Resource):
    def get(self):
        paramSetup = {
            "month" : "Month",
            "year" : "Year",
            "articleName" : "String"
        }
        paramsDict = ValidateParams(paramSetup, request.args)
        if paramsDict is None:
            return kValidationErrorMessage
        startDate = datetime(year=paramsDict["year"], month=paramsDict["month"], day=1)
        articleName = paramsDict["articleName"]
        endDate = startDate + timedelta(days=kDaysPerMonth[paramsDict["month"] - 1] - 1)
        response = ExecuteQuery(
            "/per-article/en.wikipedia.org/all-access/all-agents/%s/daily/%s/%s" % (articleName, PythonDateToWikiDateStringApi2(startDate), PythonDateToWikiDateStringApi2(endDate))
        )
        if not ValidateResponse(response):
            return kValidationErrorMessage
        return str(MaxDayFromCountsResponse(response.json()))

api.add_resource(MainApi1Week, '/main/api1/week')
api.add_resource(MainApi1Month, '/main/api1/month')
api.add_resource(MainApi2Week, '/main/api2/week')
api.add_resource(MainApi2Month, '/main/api2/month')
api.add_resource(MainApi3, '/main/api3')

if __name__ == '__main__':
    app.run() 