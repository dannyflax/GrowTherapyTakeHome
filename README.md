# GrowTherapyTakeHome

## What's this?

Wrapper API around the Wikipedia pageviews API.

Built using Python3 and Flask.

API specifics in comments under server/Server.py.

This project consists of 3 parts:
1. API wrapper, in Server.py
2. Framework for parsing JSON payloads, in ServerValidation.py
3. Unit tests for both, under server/tests

## Running Instructions

First, make sure you have python3 installed.

Then, from the server/ directory run the following command to install the necessary frameworks:

```
python3 -m pip install -r requirements.txt --user
```
You only need to do this once.

Now you can run the server with the following command:

```
python3 Server.py
```

And unit tests with these commands:

```
cd tests
python -m unittest TestServerValidation
python -m unittest TestServer
```

## Future Improvements

This repo has the following todo's that could help in the future:
1. Add a good .gitignore - I'm aware there are some compiled python files in here, I just didn't have the time to properly get rid of them.
2. Unit testing non-critical methods within Server.py.
3. Create a client to demonstrate the working API.
4. Adhere better to python naming standards - My python is a bit rusty, so I might have botched the naming conventions here.
