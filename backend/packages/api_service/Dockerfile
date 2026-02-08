FROM python:3.13-alpine

WORKDIR /app

# For psycopg2
RUN apk add postgresql-dev gcc python3-dev musl-dev

# Install dependencies first for better caching
RUN pip3 install pip-tools
COPY pyproject.toml ./
RUN pip-compile pyproject.toml
RUN pip3 uninstall -y pip-tools
RUN pip3 install -r requirements.txt

# Copy in the src directory
COPY src ./src

# Install the backend as a package
RUN pip3 install .

# Copy migrations and alembic config after package install
#COPY migrations ./migrations
#COPY alembic.ini ./

# Expose the port for the backend
EXPOSE 5000

# Configure the environment
ENV FLASK_APP=rss_music_api_service:create_app
ENV FLASK_RUN_HOST=0.0.0.0
#ENV ALLOWED_ORIGINS=http://localhost:5173

# Run the backend
CMD ["python3", "-m", "flask", "run"]
