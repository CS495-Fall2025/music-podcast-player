FROM node:24-alpine

WORKDIR /app

# Install packages inside container so node_modules is independent.
COPY package.json ./
COPY package-lock.json ./

RUN npm install

# Copy the rest of the project.
COPY . .

# Expose the port for accessing the frontend.
EXPOSE 5173

# Run the frontend.
# "dev-docker" is just "dev", but listening on 0.0.0.0 (we can't access it if its on
# localhost).
CMD ["npm", "run", "dev-docker"]
