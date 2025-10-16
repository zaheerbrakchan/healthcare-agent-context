# 🧠 Healthcare Agent System — Large Context Handling in Agentic Systems

### 🚀 Built for Lyzr Hiring Hackathon 2025

---

## 📖 Problem Statement

LLMs have limited context windows — once exceeded, they lose track of earlier information, leading to *context rotting*.  
In multi-turn, multi-agent systems (like AI assistants or workflow agents), this creates major reliability issues — especially when handling large tool outputs or long conversations.

The goal of this project was to **design and build a system capable of retaining and reasoning over large contexts**, even when total memory exceeds the model’s limit.

---

## 💡 My Approach

I built a **multi-agent healthcare system** with two intelligent agents:

1. 🩺 **Appointment Agent** – Handles appointment bookings and slot retrievals  
2. 🧾 **Pre-assessment Agent** – Gathers patient pre-assessment details before the appointment  

Both agents are connected through a **Shared Context Memory Layer**, allowing them to exchange relevant context seamlessly.

---

## ⚙️ Key Features

### 🧩 1. Large Tool Output Handling
When fetching available slots for a department (e.g., *Dental*), the API might return huge data — potentially exceeding LLM context size.  
To handle this, I implemented:
- **Chunked context processing**: Slots are segmented and summarized intelligently.  
- **Context persistence**: Relevant data is stored and recalled instead of re-fed entirely.  
- **Adaptive truncation**: The system respects model-specific token limits dynamically.

### 🔁 2. Shared Context Between Agents
Information gathered by one agent (e.g., booked appointment details) is automatically available to the other agent.  
This ensures:
- Consistency between agent conversations  
- Reduced repetition for the user  
- Context continuity across multi-turn interactions  

### 🧠 3. Adaptive Model Context Management
The system automatically adjusts how much historical context to retain based on the **model’s token window** (e.g., GPT-4-Turbo vs GPT-3.5).  
This keeps responses efficient and relevant.

---

## 🏗️ Architecture Overview

```
├── backend/
│   ├── agents/
│   │   ├── appointment_agent/
│   │   ├── preassessment_agent/
│   │   ├── shared_context.py      ← Shared context manager
│   │
│   ├── services/
│   │   ├── llm_service.py         ← Handles model calls & context window control
│   │   ├── vector_db.py           ← Vector-based memory storage (couldn't complete: will use in future )
│   │   ├── retrieval.py           ← Fetches and filters relevant past context((couldn't complete: will use in future ))
│   │
│   ├── tools/
│   │   ├── appointment/           ← Appointment APIs & helpers
│   │   ├── preassessment/         ← Pre-assessment tools
│   │
│   ├── routers/
│   │   ├── appointment_agent_router.py
│   │   ├── preassessment_agent_router.py
│   │
│   ├── main.py                    ← FastAPI entry point
│   ├── db.py                      ← Database & config
│   └── requirements.txt
```

---

## ⚙️ Tech Stack

- **FastAPI** — Backend framework  
- **OpenAI API** — LLM inference  
- **PostgreSQL (Supabase)** — Context storage  
- **LangChain / custom memory logic** — Context chunking & retrieval  
- **Railway** — Deployment platform  

---

## 🧩 How It Solves the Challenge

| Challenge | My Solution |
|------------|--------------|
| LLM context window limit | Dynamic token-aware context management |
| Multi-turn context loss | Shared context layer across agents |
| Tool outputs too large | Chunked slot handling and summarization |
| Scalability | Vector-based retrieval for long conversations |
| Efficiency | Minimized redundant LLM calls |

---

## 💭 Thought Process

My design thinking was focused on **context efficiency and modularity**:
- Treat each agent as a *reasoning unit* with its own memory.
- Introduce a *shared memory bus* for cross-agent information.
- Control token usage proactively instead of reactively truncating history.
- Make the system modular enough to plug in new agents or tools easily.

---

## 🔗 Demo & Deployment

🚀 **Live Demo:**  https://www.youtube.com/watch?v=uP_ahcpJuKM
💻

---

## ✨ Future Improvements
- Integrate **persistent long-term memory** (vector search for full context recall)  
- Add **temporal context weighting** (recent info prioritized)  
- Extend to **multi-specialty agent collaboration** (e.g., lab, billing, etc.)

---

## 👨‍💻 Author

**Zaheer Brakchan**  
*AI Engineer & Problem Solver*  

