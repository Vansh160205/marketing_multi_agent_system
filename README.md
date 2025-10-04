Of course. Here is a professional `README.md` file for your GitHub repository, created by synthesizing the information from your project files and the provided documentation.

-----

# Marketing Multi-Agent System

[](https://www.google.com/search?q=https://github.com/your-username/marketing-multi-agent-system/actions)
[](https://www.google.com/search?q=https://codecov.io/gh/your-username/marketing-multi-agent-system)
[](https://opensource.org/licenses/MIT)

This repository contains the source code for a sophisticated, AI-driven Marketing Multi-Agent System. [cite\_start]The system is designed to automate and optimize lead management and campaign execution through the collaboration of three specialized agents[cite: 15].

[cite\_start]The architecture is built on a robust, asynchronous Python framework using FastAPI[cite: 16, 65]. [cite\_start]All inter-agent communication is facilitated by a central Model Context Protocol (MCP) Server that implements the JSON-RPC 2.0 protocol over both HTTP and WebSocket transport layers[cite: 17]. [cite\_start]A key feature is the adaptive memory architecture, which leverages a polyglot persistence strategy (PostgreSQL, Redis, Neo4j) to enable agents to learn from interactions and improve over time[cite: 18, 38].

-----

### \#\# System Architecture

The system follows a centralized, agent-based architecture where all data access and communication are brokered by the MCP Server. Agents interact with a unified Memory System, which abstracts the underlying polyglot database layer.

```mermaid
graph TD
    %% Define Nodes
    Client["Client Applications<br/>Marketing Team Interface"]
    MCPServer["MCP Server - FastAPI<br/>JSON-RPC 2.0 over HTTP/WS"]
    Triage["Lead Triage Agent"]
    Engage["Engagement Agent"]
    Optimize["Campaign Optimization Agent"]
    MemoryHub["Memory Systems"]
    Redis[(Redis<br/>Short-term Memory)]
    Postgres[(PostgreSQL<br/>Long-term Memory)]
    Neo4j[(Neo4j<br/>Episodic & Semantic)]

    %% Define Connections
    Client -- HTTPS --> MCPServer
    MCPServer --> Triage
    MCPServer --> Engage
    MCPServer --> Optimize
    Triage --> MemoryHub
    Engage --> MemoryHub
    Optimize --> MemoryHub
    MemoryHub --> Redis
    MemoryHub --> Postgres
    MemoryHub --> Neo4j

    %% Define Styles
    classDef client fill:#e0f7fa,stroke:#4dd0e1,stroke-width:2px,color:#006064
    classDef server fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef agent fill:#f3e5f5,stroke:#ab47bc,stroke-width:2px,color:#4a148c
    classDef memory_hub fill:#e8f5e9,stroke:#66bb6a,stroke-width:2px,color:#1b5e20
    classDef database fill:#fffde7,stroke:#fdd835,stroke-width:2px,color:#f57f17

    %% Apply Styles
    class Client client
    class MCPServer server
    class Triage,Engage,Optimize agent
    class MemoryHub memory_hub
    class Redis,Postgres,Neo4j database
```

-----

### \#\# Core Features

  * [cite\_start]**Multi-Agent System**: Features three specialized agents for Lead Triage, Engagement, and Campaign Optimization[cite: 15].
  * [cite\_start]**Adaptive Memory**: A four-tiered memory system allows agents to learn from interactions[cite: 18].
      * [cite\_start]**Short-Term (Redis)**: For fast, conversational context[cite: 38].
      * [cite\_start]**Long-Term (PostgreSQL)**: For durable storage of customer history and preferences[cite: 38].
      * [cite\_start]**Episodic & Semantic (Neo4j)**: For storing successful problem-resolution patterns and domain knowledge as a graph[cite: 38].
  * [cite\_start]**Centralized API**: A single, secure MCP Server built with FastAPI manages all data access and communication using the JSON-RPC 2.0 protocol[cite: 29, 30].
  * [cite\_start]**Asynchronous by Design**: Built entirely on Python's `asyncio` for high-concurrency and performance in I/O-bound tasks[cite: 63, 64, 65, 66].
  * [cite\_start]**Production-Ready**: Designed for production with Kubernetes manifests, security protocols, and a robust testing and monitoring strategy[cite: 19].

-----

### \#\# Tech Stack

  * **Backend**: Python 3.10+, FastAPI
  * **Databases**: PostgreSQL, Redis, Neo4j
  * **Communication**: JSON-RPC 2.0, WebSockets
  * **Async**: `asyncio`, `asyncpg`, `redis-py[async]`
  * **Testing**: Pytest, `pytest-asyncio`
  * **Deployment**: Docker, Kubernetes

-----

### \#\# Setup and Installation

Follow these steps to get the project running locally.

**1. Clone the Repository**

```bash
git clone https://github.com/your-username/marketing-multi-agent-system.git
cd marketing-multi-agent-system
```

**2. Create and Activate Virtual Environment**

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

**3. Install Dependencies**

```bash
pip install -r requirements.txt
```

**4. Install Project in Editable Mode**
This step is crucial for making the `src` layout work correctly.

```bash
pip install -e .
```

**5. Configure Environment Variables**
Create a `.env` file in the project root by copying the example below. Fill in your actual credentials.

```env
# .env file
APP_NAME="Marketing Multi-Agent System"
DEBUG=True
API_KEY="your-super-secret-and-long-api-key"

# MCP Server
MCP_HOST="localhost"
MCP_PORT=8000

# Databases
POSTGRES_URL="postgresql+asyncpg://postgres:your_pg_password@localhost:5432/marketing"
REDIS_URL="redis://localhost:6379"
NEO4J_URL="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your_neo4j_password"

# Memory Settings
SHORT_TERM_MEMORY_SIZE=100
SHORT_TERM_MEMORY_TTL=3600
```

**6. Start External Services (Docker)**
Make sure Docker is running, then start the required databases.

```bash
docker run -d --name postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=your_pg_password -e POSTGRES_DB=marketing -p 5432:5432 postgres:14
docker run -d --name neo4j -e NEO4J_AUTH=neo4j/your_neo4j_password -p 7687:7687 -p 7474:7474 neo4j:5
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

**7. Initialize the Database**
Run the setup script to create the necessary tables and indexes.

```bash
python -m src.database.init_db
```

-----

### \#\# Usage

**1. Start the MCP Server**
Open a terminal and run the following command. Keep this server running.

```bash
python -m src.mcp.server
```

**2. Run the Demo Workflow**
In a new terminal, run the main demo script to see the agents in action.

```bash
python -m main
```

**3. Run the Test Suite**
To verify the entire system is working correctly, run the full test suite.

```bash
pytest
```

-----

### \#\# API

[cite\_start]The system exposes a single JSON-RPC 2.0 endpoint at `/rpc`[cite: 78]. [cite\_start]All requests must include an API key in the `X-API-KEY` header[cite: 141].

**Example Request (`curl`)**:

```bash
curl -X POST http://localhost:8000/rpc \
-H "Content-Type: application/json" \
-H "X-API-KEY: your-super-secret-and-long-api-key" \
-d '{
    "jsonrpc": "2.0",
    "method": "get_lead_data",
    "params": {"lead_id": 1},
    "id": "1"
}'
```

---
### **Roadmap and Future Work**

This project provides a solid foundation, but several enhancements are planned to make it fully production-ready, based on the initial code review.

#### **Immediate Priorities (Production Hardening)**
* [cite_start]**Replace Simulated Logic**: The current `EngagementAgent` and `CampaignOptimizationAgent` use `random` to simulate outcomes and metrics[cite: 2]. The next step is to integrate with real-world APIs for email delivery (e.g., SendGrid) and analytics.
* **Enhance Observability**: Implement structured logging across all agents and services. [cite_start]While a `/metrics` endpoint is planned [cite: 407, 419][cite_start], the code needs to be fully instrumented with the `prometheus-client` to track RPC latency and agent performance[cite: 406, 425].
* **Improve Agent Intelligence**:
    * [cite_start]Replace the simplistic, hard-coded scoring logic in the `LeadTriageAgent` with a configurable or ML-driven model[cite: 2].
    * [cite_start]Upgrade the keyword-based matching in the `EpisodicMemory` to use vector embeddings and cosine similarity for more accurate results[cite: 2].

#### **Future Enhancements**
* [cite_start]**Resilience**: Implement retry logic with exponential backoff in the `MCPClient` to handle transient network failures gracefully[cite: 2].
* [cite_start]**Performance**: Address the potential race condition in `Short-TermMemory` by using Redis transactions or Lua scripting to ensure atomic operations[cite: 2].
* [cite_start]**Load Testing**: Execute the planned load testing scenarios using Locust to validate system performance under a 10x load increase and ensure latency targets are met[cite: 381, 384].

---
### License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
