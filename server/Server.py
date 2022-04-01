from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# TODO - Better error messages
kValidationErrorMessage = "Incorrect parameters."
kValidationSuccessMessage = "Success"

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

class MainApi1Week(Resource):
    def get(self):
        paramSetup = {
            "startDate" : "Date"
        }
        paramsDict = ValidateParams(paramSetup, request.args)
        if paramsDict is None:
            return kValidationErrorMessage
        return kValidationSuccessMessage

class MainApi1Month(Resource):
    def get(self):
        paramSetup = {
            "month" : "Month",
            "year" : "Year"
        }
        paramsDict = ValidateParams(paramSetup, request.args)
        if paramsDict is None:
            return kValidationErrorMessage
        return kValidationSuccessMessage

class MainApi2Week(Resource):
    def get(self):
        paramSetup = {
            "startDate" : "Date",
            "articleName" : "String"
        }
        paramsDict = ValidateParams(paramSetup, request.args)
        if paramsDict is None:
            return kValidationErrorMessage
        print(paramsDict)
        return kValidationSuccessMessage

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
        print(paramsDict)
        return kValidationSuccessMessage

class MainApi3(Resource):
    def get(self):
        paramSetup = {
            "articleName" : "String"
        }
        paramsDict = ValidateParams(paramSetup, request.args)
        if paramsDict is None:
            return kValidationErrorMessage
        return kValidationSuccessMessage

api.add_resource(MainApi1Week, '/main/api1/week')
api.add_resource(MainApi1Month, '/main/api1/month')
api.add_resource(MainApi2Week, '/main/api2/week')
api.add_resource(MainApi2Month, '/main/api2/month')
api.add_resource(MainApi3, '/main/api3')

if __name__ == '__main__':
    app.run() 