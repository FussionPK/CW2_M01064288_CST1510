from datetime import date, datetime, time
from typing import Optional

import json
import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import DatabaseConnection
from services.ai_assistant import AIService
from services.database_manager import DbManagerService


def get_db_manager() -> DbManagerService:
	database_connection = DatabaseConnection()
	database_connection.initialize()
	return DbManagerService(database_connection)


def load_ticket_dataframe(db: DbManagerService) -> pd.DataFrame:
	rows = db.list_tickets()
	if not rows:
		return pd.DataFrame()
	df = pd.DataFrame(rows)
	for column in ["time_to_resolve_hours", "waiting_stage_hours", "customer_satisfaction"]:
		df[column] = pd.to_numeric(df[column], errors="coerce")
	for column in ["created_at", "updated_at", "resolved_at"]:
		if column in df.columns:
			df[column] = pd.to_datetime(df[column], errors="coerce")
	return df


def parse_datetime(selected_date: date, selected_time: time) -> Optional[str]:
	if selected_date is None or selected_time is None:
		return None
	combined = datetime.combine(selected_date, selected_time)
	return combined.isoformat()


def hours_between(start_iso: Optional[str], end_iso: Optional[str]) -> float:
	if start_iso is None or end_iso is None:
		return 0.0
	start_dt = datetime.fromisoformat(start_iso)
	end_dt = datetime.fromisoformat(end_iso)
	if end_dt <= start_dt:
		return 0.0
	return round((end_dt - start_dt).total_seconds() / 3600, 2)


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
			st.warning("Add GOOGLE_API_KEY to secrets.toml to unlock AI coaching.")
		else:
			st.warning("Add XAI_API_KEY to secrets.toml to unlock AI coaching.")
		return None

	try:
		return AIService(api_key, provider=provider)
	except Exception as error:
		st.error(f"AI setup error: {error}")
		return None


def render_operational_ai(df: pd.DataFrame) -> None:
	if df.empty:
		st.info("Log tickets to enable AI service recommendations.")
		return
	ai_service = build_ai_service()
	if ai_service is None:
		return

	stage_wait = (
		df.groupby("stage", dropna=False)["waiting_stage_hours"].mean().reset_index()
		.sort_values("waiting_stage_hours", ascending=False)
	)
	technician_health = (
		df.groupby("assigned_to", dropna=False)
		.agg({"time_to_resolve_hours": "mean", "customer_satisfaction": "mean"})
		.sort_values("time_to_resolve_hours", ascending=False)
		.reset_index()
	)
	backlog = df[df["status"].isin(["Open", "In Progress", "Waiting for User", "Waiting for Vendor"])]
	insight_payload = {
		"worst_stage": stage_wait.head(3).to_dict(orient="records"),
		"technician_health": technician_health.head(3).to_dict(orient="records"),
		"backlog_size": int(backlog.shape[0]),
	}
	prompt = (
		"You are the IT service desk manager. Provide a short action plan (<=120 words) prioritising "
		"stage improvements and coaching needs based on the JSON metrics."
		f"\nJSON: {json.dumps(insight_payload, default=str)}"
	)
	with st.spinner("Generating service desk recommendation..."):
		recommendation = ai_service.generate_response(prompt)
	st.write(recommendation)


def main() -> None:
	st.set_page_config(page_title="IT Operations Dashboard", page_icon=":bar_chart:", initial_sidebar_state="expanded")
	st.title("IT Service Desk Performance")
	st.caption("Spot staff anomalies and stage bottlenecks driving slow resolutions.")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	database_manager_service = get_db_manager()

	if st.session_state["user"] is None:
		st.info("Sign in on the Login page to update tickets.")
	else:
		st.success(f"Signed in as {st.session_state['user']['username']}")

	tickets_df = load_ticket_dataframe(database_manager_service)

	st.subheader("Performance Overview")
	if tickets_df.empty:
		st.info("No tickets recorded yet. Add one below to analyse performance.")
	else:
		open_tickets = tickets_df[tickets_df["status"].isin(["Open", "In Progress", "Waiting for User", "Waiting for Vendor"])]
		resolved_tickets = tickets_df[tickets_df["time_to_resolve_hours"].notna() & (tickets_df["time_to_resolve_hours"] > 0)]
		long_wait_stage = (
			tickets_df.groupby("stage", dropna=False)["waiting_stage_hours"].mean().reset_index()
			.sort_values("waiting_stage_hours", ascending=False)
		)
		poorest_stage = long_wait_stage.iloc[0] if not long_wait_stage.empty else None
		technician_backlog = (
			tickets_df.groupby("assigned_to", dropna=False)
			.agg(active_open=("status", lambda s: (s.isin(["Open", "In Progress", "Waiting for User", "Waiting for Vendor"]).sum())),
				avg_resolution=("time_to_resolve_hours", "mean"))
			.reset_index()
			.sort_values("active_open", ascending=False)
		)
		worst_technician = technician_backlog.iloc[0] if not technician_backlog.empty else None

		col1, col2, col3 = st.columns(3)
		col1.metric("Open Tickets", int(open_tickets.shape[0]))
		col2.metric("Avg Resolution (hrs)", f"{resolved_tickets['time_to_resolve_hours'].mean():.1f}" if not resolved_tickets.empty else "n/a")
		col3.metric("Bottleneck Stage", poorest_stage["stage"] if poorest_stage is not None else "n/a", delta=f"{poorest_stage['waiting_stage_hours']:.1f} hrs wait" if poorest_stage is not None else None)

		stage_wait_chart = px.bar(
			long_wait_stage,
			x="stage",
			y="waiting_stage_hours",
			title="Average Waiting Time by Stage (hrs)",
			labels={"waiting_stage_hours": "Avg Waiting Hours", "stage": "Stage"},
			text_auto=".1f",
		)
		stage_wait_chart.update_layout(margin=dict(t=60, l=0, r=0, b=0))
		st.plotly_chart(stage_wait_chart, use_container_width=True)

		tech_resolution = (
			tickets_df.groupby("assigned_to", dropna=False)["time_to_resolve_hours"].mean().reset_index()
			.sort_values("time_to_resolve_hours", ascending=False)
		)
		if not tech_resolution.empty:
			tech_fig = px.bar(
				tech_resolution,
				x="assigned_to",
				y="time_to_resolve_hours",
				title="Average Resolution Time by Technician",
				labels={"time_to_resolve_hours": "Hours", "assigned_to": "Technician"},
				text_auto=".1f",
			)
			tech_fig.update_layout(margin=dict(t=60, l=0, r=0, b=0))
			st.plotly_chart(tech_fig, use_container_width=True)

		st.markdown("**Active Backlog Detail**")
		st.dataframe(
			open_tickets[[
				"title",
				"stage",
				"status",
				"priority",
				"assigned_to",
				"waiting_stage_hours",
				"time_to_resolve_hours",
				"customer_satisfaction",
			]],
			hide_index=True,
		)

	st.subheader("AI Service Desk Recommendation")
	render_operational_ai(tickets_df)

	st.subheader("Create Ticket")
	with st.form("ticket_form", clear_on_submit=True):
		ticket_title = st.text_input("Title")
		ticket_description = st.text_area("Description", height=120)
		ticket_status = st.selectbox("Status", ["Open", "In Progress", "Waiting for User", "Waiting for Vendor", "Resolved", "Closed"])
		ticket_stage = st.selectbox("Process Stage", ["Intake", "Investigation", "Waiting for User", "Waiting for Vendor", "Fulfillment", "Major Incident"])
		ticket_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
		ticket_assigned_to = st.text_input("Assigned To", value="Morgan Lee")
		ticket_channel = st.selectbox("Channel", ["Portal", "Phone", "Email", "Chat"])
		customer_satisfaction = st.slider("Customer Satisfaction", min_value=0, max_value=100, value=80, step=5)

		created_date = st.date_input("Created Date", value=date.today())
		created_time = st.time_input("Created Time", value=time(8, 0))
		updated_date = st.date_input("Last Update Date", value=date.today())
		updated_time = st.time_input("Last Update Time", value=time(12, 0))
		resolved_date = st.date_input("Resolved Date", value=date.today())
		resolved_time = st.time_input("Resolved Time", value=time(17, 0))

		waiting_hours = st.number_input("Waiting Time in Stage (hrs)", min_value=0.0, value=4.0, step=0.5)

		save_ticket = st.form_submit_button("Save Ticket", use_container_width=True)

		if save_ticket:
			if ticket_title.strip() == "" or ticket_description.strip() == "":
				st.warning("Title and description are required.")
			else:
				created_iso = parse_datetime(created_date, created_time)
				updated_iso = parse_datetime(updated_date, updated_time)
				resolved_iso = parse_datetime(resolved_date, resolved_time) if ticket_status in {"Resolved", "Closed"} else None
				time_to_resolve = hours_between(created_iso, resolved_iso)

				database_manager_service.add_ticket(
					ticket_title,
					ticket_description,
					ticket_status,
					ticket_stage,
					ticket_priority,
					created_iso,
					updated_iso,
					resolved_iso,
					ticket_assigned_to,
					time_to_resolve,
					waiting_hours,
					int(customer_satisfaction),
					ticket_channel,
				)
				st.success("Ticket saved successfully. Refreshing analytics...")
				st.rerun()

	st.subheader("CSV Upload (Ticket Intake)")
	csv_file_upload = st.file_uploader("Upload ticket export", type="csv", key="it_ops_csv")
	if csv_file_upload is not None and st.button("Process CSV Upload", key="it_ops_csv_button"):
		try:
			csv_dataframe = pd.read_csv(csv_file_upload)
			filename_text = csv_file_upload.name
			row_count_number = len(csv_dataframe)
			column_names_text = ",".join(csv_dataframe.columns.tolist())
			upload_date_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			data_json_text = csv_dataframe.to_json(orient="records")

			database_manager_service.add_csv_data(filename_text, row_count_number, column_names_text, upload_date_text, data_json_text)
			st.success(f"CSV file '{filename_text}' staged successfully with {row_count_number} rows.")
			st.dataframe(csv_dataframe.head(10))
		except Exception as error:
			st.error(f"Error processing CSV: {error}")

	st.subheader("Staged CSV Files")
	all_csv_uploads = database_manager_service.list_csv_data()
	if not all_csv_uploads:
		st.info("No staged CSV uploads yet.")
	else:
		st.dataframe(pd.DataFrame(all_csv_uploads), hide_index=True)


if __name__ == "__main__":
	main()
