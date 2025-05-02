# 📦 box_my_domain

**box_my_domain** is a mystery box experience for domain names, powered by AI. It allows users to draw random domains, evaluate their value, and take action — such as reselling, parking for profit, or building a site using Airo. A smart agent guides users through onboarding, making domain ownership easy and fun.

---

## 🚀 Features

- 🎲 Draw a random domain name and re-roll for a new selection  
- 🧠 Evaluate domain quality using AI and multiple attributes  
- 💸 Resell domains on integrated marketplaces  
- 🅿️ Park domains to earn passive revenue  
- 🔗 Redirect domains to Airo for quick website creation  
- 🤖 Smart onboarding agent to guide users through domain setup and options  

---

## 📂 Project Structure

box_my_domain/
├── public/ # Static assets for React

├── src/ # React.js frontend source

├── server/ # FastAPI backend

├── mcp_tools/ # Domain tools & automation logic

├── README.md # This file

---

## 🛠️ Getting Started

### ⚙️ Prerequisites

- [Node.js](https://nodejs.org/) (v18+ recommended)  
- [Poetry](https://python-poetry.org/) (v1.6+)  
- [Python](https://www.python.org/downloads/) (>=3.10)  

---

## 🧩 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/box_my_domain.git
cd box_my_domain

### 2. Frontend Setup (React.js)
cd src
npm install
npm run dev  # or npm start

### 3. Backend Setup (FastAPI + Poetry)

cd ../server
poetry install
poetry shell

# Set up environment variables (via .env or export)
export GODADDY_API_KEY=your_key
export GODADDY_API_SECRET=your_secret

# Start the FastAPI server
uvicorn main:app --reload

### 4. gAI MCP Server tool Registry

