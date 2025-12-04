# Multi-Domain Intelligence Platform  
**Tier 3 High Distinction Project** – Cybersecurity ⋅ Data Science ⋅ IT Operations  

A full-stack, role-based, multi-domain analytical dashboard built with **Streamlit**, **SQLite**, **OOP architecture**, and **GROK integration** that solves real operational bottlenecks for three distinct business units.

## Project Overview  
This application delivers **three complete, interactive dashboards** in a single Streamlit multi-page web app:

1. **Cybersecurity Incident Response Dashboard** – Identifies phishing surge trends and resolution bottlenecks  
2. **Data Science Governance Dashboard** – Analyzes dataset growth, dependencies, and recommends archiving policies  
3. **IT Operations Service Desk Dashboard** – Pinpoints staff/process delays in ticket resolution  

All mandatory features are implemented:

- Secure authentication (bcrypt + SQLite)  
- Full CRUD operations across all domains  
- Clean OOP refactoring (entity models + service classes)  
- Interactive Plotly visualizations for every domain  
- AI Assistant powered by OpenAI GPT (context-aware advice in all dashboards)  
- Proper separation of concerns (models / services / database / pages)

## Final Project Structure
  
multi_domain_platform/
├── models/                  # Entity classes (OOP)
│   ├── user.py
│   ├── security_incident.py
│   ├── dataset.py
│   └── it_ticket.py
├── services/                # Business logic & coordination
│   ├── auth_manager.py
│   ├── database_manager.py
│   └── ai_assistant.py
├── database/
│   └── db.py                # SQLite connection & schema
├── pages/                   # Streamlit multi-page navigation
│   ├── 1_Login.py
│   ├── 2_Cybersecurity.py
│   ├── 3_Data_Science.py
│   ├── 4_IT_Operations.py
│   └── 5_AI_Assistant.py
├── Data/
│   └── platform.db          # Production SQLite database
app.py                       # Streamlit entry point
secrets.toml                 # OpenAI API key (gitignored)
requirements.txt
README.md