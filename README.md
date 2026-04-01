# 🏪 CstoreStudio: The Autonomous Maintenance Engine

**CstoreStudio** is a high-end, multi-agentic platform designed to automate the entire lifecycle of C-store repairs—from the moment a pump leaks to the final payment dispatch. Built for a 2026 production environment, it replaces manual phone tag and "truck roll" guesswork with a self-reasoning agentic mesh.

---

## 🧠 The Agentic Philosophy
Unlike traditional workflow apps, CstoreStudio treats the **Human as an Exception**. The core is a **Supervisor-Auditor** pattern powered by **Gemini 3.1 Pro** and **LangGraph**, where agents negotiate with vendors and audit visual repairs autonomously.

### The Multi-Agent Mesh:
* **The Supervisor (Orchestrator):** The high-level "Project Manager" that routes the ticket through its state machine.
* **The Triage Agent (Vision):** Uses Gemini 3.1 Pro to analyze video/photos of broken assets to provide instant "AI Diagnosis" and ballpark cost estimates.
* **The Market Agent (Procurement):** Connects to the Vendor Database via **MCP**, invites bids, and ranks them based on cost, rating, and proximity.
* **The Auditor Agent (The Watchdog):** Cross-references vendor bids against AI estimates and performs "Before/After" visual verification of the repair.

---

## 🚀 Technical Stack
* **LLM:** (via LiteLLM gateway).
* **Orchestration:** LangGraph (Stateful Multi-Agent workflows).
* **Tooling:** **Model Context Protocol (MCP)** for decoupled access to AWS and local databases.
* **Frontend:** Next.js 15 (App Router) with Role-Based Access Control (RBAC).
* **Backend:** FastAPI (Python 3.11+) & Gradle (Kotlin DSL) Monorepo management.
* **Infrastructure:** EKS (Production), LocalStack (Local Dev), S3, DynamoDB.
* **Observability:** Prometheus, Grafana, and Langfuse (for agentic tracing).

---

## 🛠️ The Business Workflow

| Step | Actor | Action |
| :--- | :--- | :--- |
| **1. Intake** | **Manager** | Uploads a 10s video/photo + note. AI Triage runs instantly. |
| **2. Bidding** | **Market Agent** | Ticket enters "Awaiting Bids." Vendors submit actual prices. |
| **3. Audit** | **Auditor Agent** | Compares bids vs. AI estimate. Flags high-risk discrepancies. |
| **4. Approval** | **Owner** | Reviews the "Bid Comparison" dashboard and clicks **Approve**. |
| **5. Fix** | **Vendor** | Completes repair and uploads a **Completion Photo + Invoice**. |
| **6. Validate** | **Manager** | Validates the physical fix via the portal. |
| **7. Close** | **Owner** | Clicks **Dispatch Payment**. Ticket moves to **CLOSED**. |

---

## 📁 Project Structure (Gradle Monorepo)
```text
CstoreStudio/
├── services/
│   ├── ui-app/           # Next.js 15 Frontend (Portals for Manager/Owner/Vendor)
│   ├── ai-agent/         # LangGraph + Gemini Service (Includes seed_db.py)
│   └── mcp-server/       # Model Context Protocol (MCP) Tools for AWS/DB
├── infrastructure/
│   ├── localstack/       # S3 & DynamoDB initialization scripts
│   └── terraform/        # EKS & AWS Resource definitions
├── build.gradle.kts      # Monorepo management
└── docker-compose.yml    # Full local environment
```

---

## 🚦 Getting Started (Local Development)

### 1. Start the Environment
The most reliable way to launch the stack is using the provided management script. This command handles container builds, waits for LocalStack services to be `ACTIVE`, and executes the initial database seed.

Ensure Docker Desktop is running, then run:
```bash
./manage.sh up
```

### 2. Seed the Database (Manual/Repeatable)
To reseed the database at any time:
```bash
./manage.sh seed
```

### 3. Restart or Tear Down
```bash
./manage.sh restart   # Full restart (down + up + seed)
./manage.sh down      # Stop and remove all containers and volumes
```

### 4. Access the Portals
* **Manager Portal:** http://localhost:3000/portal/manager (manager/manager)
* **Owner Portal:** http://localhost:3000/portal/owner (owner/owner)
* **Admin Trace:** http://localhost:3000/portal/admin (admin/admin)
* **Prometheus:** http://localhost:9090
* **Grafana:** http://localhost:3001

---

## 📝 API Quick Reference

### Create Ticket (POST /tickets)
```http
POST /tickets
{
	"media_url": "http://localhost:4566/fake.jpg",
	"category": "GAS",
	"manager_note": "Test note",
	"store_id": "ST-101",
	"asset_id": "A-001"
}
```
Returns: `{ "ticket_id": "...", "status": "OPEN" }`

---

---

## 📊 Observability & Trust
Because the system is autonomous, we use **Langfuse** to provide a "Full Trace" of every agent's thought process. You can see the **Internal Monologue** of the Auditor Agent when it decides whether to trust a vendor's bid or flag it for human review.

System Health Report:

Checks if all 4 Portals (Manager, Owner, Vendor, Admin) are returning 200 OK.

Verifies that LocalStack S3 and DynamoDB are synced.

Checks the latency of the model Triage call.

Outputs a 'Ready for Production' summary in Markdown.