import json
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

from database.db import DatabaseConnection
from services.ai_assistant import AIService
from services.database_manager import DbManagerService


def get_services() -> DbManagerService:
	database_connection = DatabaseConnection()
	database_connection.initialize()
	return DbManagerService(database_connection)


def build_cybersecurity_snapshot(db: DbManagerService) -> Dict:
	incidents = pd.DataFrame(db.list_incidents())
	if incidents.empty:
		return {"message": "No incident data available."}
	incidents["detected_at"] = pd.to_datetime(incidents["detected_at"], errors="coerce")
	open_incidents = incidents[~incidents["status"].isin(["Resolved", "Closed", "Contained"])]
	phishing_open = open_incidents[incidents["category"].str.contains("phishing", case=False, na=False)]
	severity_backlog = (
		open_incidents.groupby("severity", dropna=False).size().reset_index(name="open_total")
		.sort_values("open_total", ascending=False)
		.to_dict(orient="records")
	)
	return {
		"total_incidents": int(incidents.shape[0]),
		"open_incidents": int(open_incidents.shape[0]),
		"open_phishing": int(phishing_open.shape[0]),
		"severity_backlog": severity_backlog,
	}


def build_data_science_snapshot(db: DbManagerService) -> Dict:
	datasets = pd.DataFrame(db.list_datasets())
	if datasets.empty:
		return {"message": "No dataset catalog entries yet."}
	datasets["size_mb"] = pd.to_numeric(datasets["size_mb"], errors="coerce")
	datasets["row_count"] = pd.to_numeric(datasets["row_count"], errors="coerce")
	department_summary = (
		datasets.groupby("owner_department", dropna=False)["size_mb"].sum().reset_index().to_dict(orient="records")
	)
	heavy = datasets.sort_values("size_mb", ascending=False).head(5)[
		datasets.columns.intersection(["name", "owner_department", "size_mb", "status"])
	].to_dict(orient="records")
	return {
		"total_datasets": int(datasets.shape[0]),
		"total_storage_mb": float(datasets["size_mb"].sum()),
		"department_storage": department_summary,
		"top_consumers": heavy,
	}


def build_it_snapshot(db: DbManagerService) -> Dict:
	tickets = pd.DataFrame(db.list_tickets())
	if tickets.empty:
		return {"message": "No ticket data available."}
	tickets["waiting_stage_hours"] = pd.to_numeric(tickets["waiting_stage_hours"], errors="coerce")
	tickets["time_to_resolve_hours"] = pd.to_numeric(tickets["time_to_resolve_hours"], errors="coerce")
	stage_wait = (
		tickets.groupby("stage", dropna=False)["waiting_stage_hours"].mean().reset_index().sort_values("waiting_stage_hours", ascending=False)
		.to_dict(orient="records")
	)
	technician_load = (
		tickets.groupby("assigned_to", dropna=False)["time_to_resolve_hours"].mean().reset_index().sort_values("time_to_resolve_hours", ascending=False)
		.to_dict(orient="records")
	)
	return {
		"open_tickets": int(tickets[tickets["status"].isin(["Open", "In Progress", "Waiting for User", "Waiting for Vendor"])].shape[0]),
		"stage_wait": stage_wait,
		"technician_resolution": technician_load,
	}


DOMAIN_BUILDERS = {
	"Cybersecurity": build_cybersecurity_snapshot,
	"Data Science": build_data_science_snapshot,
	"IT Operations": build_it_snapshot,
}


def build_context_snapshot(db: DbManagerService, domain: str) -> Dict:
	if domain == "General":
		return {"message": "User requested a general assistant response."}
	return DOMAIN_BUILDERS[domain](db)


def build_ai_service() -> Optional[AIService]:
	provider = "google"
	try:
		provider = st.secrets["AI_PROVIDER"].lower()
	except KeyError:
		provider = "google"

	key_name = "GOOGLE_API_KEY" if provider == "google" else "XAI_API_KEY"
	try:
		api_key = st.secrets[key_name]
	except KeyError:
		if provider == "google":
			st.error("Google API key not found in secrets.toml")
		else:
			st.error("xAI API key not found in secrets.toml")
		return None

	try:
		return AIService(api_key, provider=provider)
	except Exception as error:
		st.error(f"AI setup error: {error}")
		return None


def main() -> None:
	st.set_page_config(page_title="AI Assistant", page_icon=":bar_chart:", initial_sidebar_state="expanded")
	st.title("AI Assistant")
	st.caption("Context-aware advisor pulling live operational data.")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	if st.session_state["user"] is None:
		st.warning("Please sign in on the Login page to use the AI Assistant.")
		return

	st.success(f"Signed in as {st.session_state['user']['username']}")

	if "conversation_history" not in st.session_state:
		st.session_state["conversation_history"] = []

	ai_service = build_ai_service()
	if ai_service is None:
		return

	db_service = get_services()
	selected_domain = st.selectbox("Domain Context", ["Cybersecurity", "Data Science", "IT Operations", "General"])
	context_snapshot = build_context_snapshot(db_service, selected_domain)

	with st.expander("Current Context Snapshot", expanded=False):
		st.json(context_snapshot)

	st.subheader("Dialogue")
	for message in st.session_state["conversation_history"]:
		if message["role"] == "user":
			st.write(f"**You:** {message['content']}")
		else:
			st.write(f"**Assistant:** {message['content']}")

	with st.form("chat_form"):
		user_input_message = st.text_area("Type your message", placeholder="Ask the assistant for guidance...", height=80)
		submit_message = st.form_submit_button("Send", use_container_width=True)

		if submit_message:
			if user_input_message.strip() == "":
				st.warning("Please enter a message.")
			else:
				conversation_transcript = "\n".join([
					f"User: {m['content']}" if m["role"] == "user" else f"Assistant: {m['content']}"
					for m in st.session_state["conversation_history"]
				])
				prompt = (
					"You are an embedded assistant supporting the {domain} team. "
					"Base your answer on the operational snapshot JSON and the conversation so far."
					"Be concise and actionable.".format(domain=selected_domain)
				)
				payload = {
					"snapshot": context_snapshot,
					"conversation": conversation_transcript,
					"user_message": user_input_message,
				}
				with st.spinner("Thinking..."):
					response_text = ai_service.generate_response(f"{prompt}\nDATA: {json.dumps(payload, default=str)}")

				st.session_state["conversation_history"].append({"role": "user", "content": user_input_message})
				st.session_state["conversation_history"].append({"role": "assistant", "content": response_text})
				st.rerun()

	if st.session_state["conversation_history"]:
		if st.button("Clear Chat", use_container_width=True):
			st.session_state["conversation_history"] = []
			st.rerun()


if __name__ == "__main__":
	main()
