# CstoreStudio Architecture Rules

## 1. Separation of Concerns
- **UI Application (`services/ui-app`)**: This is a Next.js application. It MUST NOT contain any direct database connections, queries, or SDKs (like `boto3` or AWS SDK for DynamoDB). 
- **AI Agent Backend (`services/ai-agent`)**: This is a FastAPI backend containing an MCP (Model Context Protocol) Server. All database interactions (DynamoDB/LocalStack) MUST happen here.

## 2. Tool & API Usage
- When working on UI components, **make sure to use our MCP server tools** or the exposed FastAPI endpoints (e.g., `/tickets`, `/vendors`, `/tickets/{id}/transition`) for data fetching and mutations. 
- Do NOT generate code that tries to query DynamoDB directly from the frontend.

## 3. Tech Stack Context
- Database: DynamoDB (LocalStack via `http://localhost:4566`)
- Frontend: Next.js 15, TailwindCSS, React Server Actions / API Routes for middle-layer forwarding
- Backend AI: Python, FastAPI, LangGraph, LiteLLM
