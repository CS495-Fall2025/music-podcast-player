FROM python:3.13-alpine

WORKDIR /app

# Install dependancies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy in the app source directory
COPY app /app/app

# Expose the port for the backend
EXPOSE 5000

# Tell flask to host on 0.0.0.0 and what module the app is in
ENV FLASK_APP=app.app:create_app
ENV FLASK_RUN_HOST=0.0.0.0

# Run the backend
CMD ["python3", "-m", "flask", "run"]
