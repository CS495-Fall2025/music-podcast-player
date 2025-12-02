# Database Model

## tracks

id INTEGER PRIMARY KEY
name CHAR(255) NOT NULL
artist INTEGER KEY -> artists
duration INTEGER (in seconds)
