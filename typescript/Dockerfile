FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Build TypeScript code
RUN npm run build

RUN npx playwright install --with-deps

# Expose port for SSE server
EXPOSE 3001

# Start the server
CMD ["npm", "start"]