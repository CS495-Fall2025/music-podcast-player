# Testing
Testing ensures to us that, in all possible scenarios, the app functions as intended. This will allow us release the app to real users in a fully functional state, as well as increase maintainability.

## Unit Testing
Unit testing has been, and will continue to be, implemented in the frontend and backend of the project. 

## Integration Testing
Integration testing has been, and will continue to be, implemented in the backend. We will also be implementing integration testing to the frontend in the coming semester.

## User Testing
User testing will be conducted in the coming semester.

## Running the frontend tests
Within the frontend directory, run the following commands:
`npm install`
`npm run test`

## Running the backend tests
Within the backend directory, run the following commands:
`python -m venv test_venv`
(Linux, MacOS) `source test_venv/bin/activate`
(Windows) `.\test_venv\bin\Activate.ps1`
`pip install dev_requirements.txt`
`python -m pytest`