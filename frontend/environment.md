# Frontend Environment

## Environment (Build) Variables

## Backend URL

`VITE_BACKEND_URL`

The URL the frontend can expect to be the backend. For local development, use
`http://localhost:5000`. For a cloud deployment, don't set this - we will fetch this
from a `config.json` file, described below.

### Include Development Features

`VITE_INCLUDE_DEV_FEATURES`

Whether the frontend should include pages that are used strictly for development.
For instance, a page allowing a user to send a Boost to an arbitrary lightning address.
Set this to `no` unless you specifically need one of these features, in which case set
it to `yes`. Always set to `no` in a production build.

### Block Lightning Payments

`VITE_BLOCK_LIGHTNING_PAYMENTS`

Prevents the frontend from making lightning payments and instead prints them to the
console. Useful for testing features involving lightning payments without actually
making them. Set to `yes` to use, `no` otherwise, including in production.

### Lightning Recipient Override

`VITE_LIGHTNING_RECIPIENT_OVERRIDE`

Forces all lightning payments made to the frontend to go to the wallet address specified
here. Leave this blank to not use this feature (including in production). This is
helpful to test the app's ability to send lightning payments with correct metadata.

## Config

Used for variables that can change without rebuilding the frontend. If `config.json` is
present in the frontend's top level build directory, it will override the values of some
environment variables.

Example for local development:

```json
{
  "backendUrl": "http://localhost:5000"
}
```

### Backend URL

`backendUrl`

The URL the frontend can expect to be the backend. For local development, use
`http://localhost:5000`.
