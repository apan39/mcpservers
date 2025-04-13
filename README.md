# MCP Servers Demo

This repository contains example implementations of MCP (Model Context Protocol) servers in both Python and TypeScript. Each server provides similar functionality with example tools and resources.

## Project Structure

```
.
├── docker-compose.yml
├── python/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py
└── typescript/
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    └── src/
        └── server.ts
```

## Running Locally

### Python Server

1. Create a virtual environment and install dependencies:

```bash
cd python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the server:

```bash
uvicorn server:app --host 0.0.0.0 --port 3000
```

The Python server will be available at `http://localhost:3000`.

### TypeScript Server

1. Install dependencies:

```bash
cd typescript
npm install
```

2. Build and run the server:

```bash
npm run build
npm start
```

The TypeScript server will be available at `http://localhost:3001`.

### Running with Docker Compose

To run both servers simultaneously using Docker:

```bash
docker compose up --build
```

## Deploying to Coolify

1. Fork this repository to your GitHub account.

2. In your Coolify dashboard:

   - Create a new service
   - Choose "Docker Compose"
   - Connect your forked repository
   - Configure the following environment variables if needed:
     - `PYTHON_MCP_PORT=3000`
     - `TYPESCRIPT_MCP_PORT=3001`

3. Deploy the service.

## Available Endpoints

Both servers provide the following endpoints:

- `/sse` - Server-Sent Events endpoint for MCP communication
- `/messages` - Endpoint for receiving MCP messages

## Available Tools and Resources

Both servers implement:

### Tools

- `add-numbers` - Adds two numbers together
- `string-operations` - Performs string operations (uppercase, lowercase, reverse)

### Resources

- `greeting://{name}` - Returns a personalized greeting

## Testing the Servers

You can test these servers using:

1. The MCP Inspector tool
2. Claude Desktop (by installing the servers)
3. Any MCP-compatible client

## License

MIT
