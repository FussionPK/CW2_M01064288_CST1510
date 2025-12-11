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

## Final Project Description

The multi-domain platform is a Streamlit-based web application that combines cybersecurity monitoring, data science tools, IT operations ticketing, and an AI assistant into one secure, multi-page interface. The project is organized as follows: the root folder contains app.py (the main Streamlit entry point), requirements.txt, a git-ignored secrets.toml for the OpenAI API key, and a README.md. Inside, the models directory holds object-oriented entity classes (user.py, security_incident.py, dataset.py, and it_ticket.py), the services directory contains the core business logic (auth_manager.py for authentication, database_manager.py for database operations, and ai_assistant.py for AI features), the database directory has db.py which manages the SQLite connection and schema, the pages directory includes the individual Streamlit pages (1_Login.py, 2_Cybersecurity.py, 3_Data_Science.py, 4_IT_Operations.py, and 5_AI_Assistant.py), and the Data directory stores the actual production SQLite database file platform.db.