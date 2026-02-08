# Backend Environment and Secrets

## Environment Variables

### Allowed Origins (CORS)
`RSS_PLAYER_ALLOWED_ORIGINS`

A comma separated list of URLs to allow through CORS. (A browser protection that
prevents websites not on the list of URLs from accessing our backend on behalf of the
user.)

If using for local development, use `http://localhost:5173`.

## Secrets

### Podcast Index Key and Secret
`RSS_PLAYER_PODCAST_INDEX_KEY`, `RSS_PLAYER_PODCAST_INDEX_SECRET`

The key and secret obtained from the Podcast Index. These can be obtained
[here](https://api.podcastindex.org/signup).

### Database Connection
`RSS_PLAYER_DATABASE_CONNECTION`

The connection URL for our database. In the form
`dialect+driver://username:password@host:port/database`. To use the Postgres instance in
Docker, use `postgres://postgres:dev-db-password@database/postgres`. See SQLAlchemy's
[documentation](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) for
more details.

## AWS Deployment Secret Route Variables

In order to protect our secrets, we store them as encrypted strings in AWS' parameter
store. Since the secrets used will differ between development and production, the routes
for these need to be set when the app is deployed to AWS. Additionally, because the 
secrets are fetched from these routes, the variables under "Secrets" do not need to be
set.

```
SSM_ROUTE_PODCAST_INDEX_KEY
SSM_ROUTE_PODCAST_INDEX_SECRET
SSM_ROUTE_DATABASE_CONNECTION
```
