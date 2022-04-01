from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime

app = Flask(__name__)
api = Api(app)

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

class MainApi1Week(Resource):
    def get(self):
        if not ValidateArgsNonEmpty(["startDate"], request.args):
            return kValidationErrorMessage
        potentialDate = AttemptCastDate(request.args.get("month"))
        if potentialDate is None:
            return kValidationErrorMessage
        return kValidationSuccessMessage

class MainApi1Month(Resource):
    def get(self):
        if not ValidateArgsNonEmpty(["month"], request.args):
            return kValidationErrorMessage
        month = AttemptCastDigit(request.args.get("month"))
        if month <= 0 or month > 12:
            return kValidationSuccessMessage

api.add_resource(MainApi1Week, '/main/api1/week')
api.add_resource(MainApi1Month, '/main/api1/month')

if __name__ == '__main__':
    app.run() 