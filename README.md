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
* **LLM:** Gemini 3.1 Pro (via LiteLLM gateway).
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
│   ├── ai-agent/         # LangGraph + Gemini Agentic Service
│   └── mcp-server/       # Model Context Protocol (MCP) Tools for AWS/DB
├── infrastructure/
│   ├── localstack/       # S3 & DynamoDB initialization scripts
│   └── terraform/        # EKS & AWS Resource definitions
├── build.gradle.kts      # Monorepo management
└── docker-compose.yml    # Full local environment
```

---

## 🚦 Getting Started (Local Development)

### 1. Initialize Infrastructure
Ensure Docker is running and launch the emulated AWS stack:
```bash
docker-compose up -d
# This starts LocalStack, DynamoDB, S3, and Prometheus.
```

### 2. Seed the Database
Initialize your roles (Admin, Manager, Owner, Vendor) and dummy vendors:
```bash
python scripts/seed_db.py
```

### 3. Run the Studio
Use the Gradle wrapper to boot the full stack:
```bash
./gradlew bootRun
```
* **Manager Portal:** `localhost:3000/portal/manager` (manager/manager)
* **Owner Portal:** `localhost:3000/portal/owner` (owner/owner)
* **Admin Trace:** `localhost:3000/portal/admin` (admin/admin)

---

## 📊 Observability & Trust
Because the system is autonomous, we use **Langfuse** to provide a "Full Trace" of every agent's thought process. You can see the **Internal Monologue** of the Auditor Agent when it decides whether to trust a vendor's bid or flag it for human review.

