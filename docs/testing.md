# Testing

Testing helps ensure the correctness, reliability, and maintainability of the
Music Podcast Player.

## Frontend Tests

To run the frontend tests, enter the `frontend` directory and run the following.

```
npm install
npm run test
```

## Backend Tests

The backend of the Music Podcast Player is split into multiple components,
including the API service and database service. Some packages are solely 
dependencies (never run directly), and may not always include tests. Both the
API service and database service include unit and API-scoped integration tests.
(API-scoped meaning the internals of the service are not mocked, but services
reached across the network are. For instance, the API service tests mock 
responses from the database service to ensure it can handle failure cases.)

Within the package's directory (under `backend/packages`), run the following to
trigger the tests.

```
uv sync --group dev
uv run python -m pytest
```
