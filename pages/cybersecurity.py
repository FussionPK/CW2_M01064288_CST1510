import json
from datetime import date, datetime, time
from typing import Optional

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


def load_incident_dataframe(db: DbManagerService) -> pd.DataFrame:
	incident_rows = db.list_incidents()
	if not incident_rows:
		return pd.DataFrame()
	df = pd.DataFrame(incident_rows)
	for column in ["detected_at", "first_response_at", "resolved_at"]:
		if column in df.columns:
			df[column] = pd.to_datetime(df[column], errors="coerce")
	return df


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
			st.warning("Configure GOOGLE_API_KEY in secrets.toml to enable AI-driven insights.")
		else:
			st.warning("Configure XAI_API_KEY in secrets.toml to enable AI-driven insights.")
		return None

	try:
		return AIService(api_key, provider=provider)
	except Exception as error:
		st.error(f"AI setup error: {error}")
		return None


def render_ai_advice(df: pd.DataFrame) -> None:
	if df.empty:
		st.info("Add incidents to unlock AI analysis.")
		return
	ai_service = build_ai_service()
	if ai_service is None:
		return

	latest_backlog = df[df["status"].isin(["Open", "Investigating", "Monitoring"])]
	phishing_backlog = latest_backlog[latest_backlog["category"].str.contains("phishing", case=False, na=False)]
	daily_counts = (
		df.assign(detected_day=df["detected_at"].dt.date)
		.groupby(["detected_day", "category"], dropna=False)
		.size()
		.reset_index(name="daily_total")
	)
	insight_payload = {
		"total_incidents": int(df.shape[0]),
		"active_backlog": int(latest_backlog.shape[0]),
		"phishing_backlog": int(phishing_backlog.shape[0]),
		"trend_sample": daily_counts.tail(10).to_dict(orient="records"),
	}
	prompt = (
		"You are the SOC lead. Using the structured JSON below, summarise the phishing trend and "
		"what the response team should prioritise next. Keep it under 120 words."
		f"\nJSON: {json.dumps(insight_payload, default=str)}"
	)
	with st.spinner("Generating analyst recommendation..."):
		recommendation = ai_service.generate_response(prompt)
	st.write(recommendation)


def main() -> None:
	st.set_page_config(page_title="Cybersecurity Dashboard", page_icon=":bar_chart:", initial_sidebar_state="expanded")
	st.title("Cybersecurity Incident Response")
	st.caption("Monitor phishing surges and response bottlenecks in real-time.")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	database_manager_service = get_db_manager()

	if st.session_state["user"] is None:
		st.warning("Please sign in on the Login page to record or triage incidents.")
	else:
		st.success(f"Signed in as {st.session_state['user']['username']}")

	incidents_df = load_incident_dataframe(database_manager_service)

	st.subheader("Threat Monitoring Overview")
	if incidents_df.empty:
		st.info("No incidents recorded yet. Add one below to start tracking trends.")
	else:
		open_incidents = incidents_df[~incidents_df["status"].isin(["Resolved", "Closed", "Contained"])]
		phishing_incidents = incidents_df[incidents_df["category"].str.contains("phishing", case=False, na=False)]
		critical_backlog = open_incidents[open_incidents["severity"].isin(["Critical", "High"])]

		col1, col2, col3 = st.columns(3)
		col1.metric("Active Incidents", int(open_incidents.shape[0]))
		col2.metric("Phishing Backlog", int(phishing_incidents[phishing_incidents["status"].isin(["Open", "Investigating"])] .shape[0]))
		avg_resolve = incidents_df["time_to_resolve_hours"].replace(0, pd.NA).dropna()
		col3.metric("Avg Resolution (hrs)", f"{avg_resolve.mean():.1f}" if not avg_resolve.empty else "n/a")

		df_trend = (
			incidents_df.dropna(subset=["detected_at"])
			.assign(detected_day=incidents_df["detected_at"].dt.date)
			.groupby(["detected_day", "category"], dropna=False)
			.size()
			.reset_index(name="incident_count")
		)
		if not df_trend.empty:
			trend_fig = px.line(
				df_trend,
				x="detected_day",
				y="incident_count",
				color="category",
				title="Incident Volume by Category",
				markers=True,
			)
			trend_fig.update_layout(margin=dict(t=60, l=0, r=0, b=0))
			st.plotly_chart(trend_fig, use_container_width=True)

		severity_breakdown = incidents_df.groupby(["severity", "status"]).size().reset_index(name="total")
		if not severity_breakdown.empty:
			backlog_fig = px.bar(
				severity_breakdown,
				x="severity",
				y="total",
				color="status",
				title="Resolution Bottleneck by Severity",
				labels={"total": "Incidents"},
			)
			backlog_fig.update_layout(margin=dict(t=60, l=0, r=0, b=0))
			st.plotly_chart(backlog_fig, use_container_width=True)

		st.markdown("**Open Critical Queue**")
		st.dataframe(
			critical_backlog[[
				"title",
				"category",
				"severity",
				"status",
				"assigned_to",
				"detected_at",
				"time_to_first_response_hours",
				"time_to_resolve_hours",
			]],
			hide_index=True,
		)

	st.subheader("Analyst Recommendation")
	render_ai_advice(incidents_df)

	st.subheader("Log New Incident")
	with st.form("incident_form", clear_on_submit=True):
		incident_title = st.text_input("Title", help="Short summary visible in queues")
		incident_description = st.text_area("Description", height=120)
		incident_category = st.selectbox("Category", ["Phishing", "Credential Abuse", "Insider", "Malware", "Other"])
		incident_threat_vector = st.text_input("Threat Vector", value="Email Link")
		incident_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
		incident_status = st.selectbox("Status", ["Open", "Investigating", "Monitoring", "Contained", "Resolved", "Closed"])
		reported_by = st.text_input("Reported By", value="SOC")
		assigned_to = st.text_input("Assigned To", value="Jamie Fox")

		detected_date = st.date_input("Detected Date", value=date.today())
		detected_time = st.time_input("Detected Time", value=time(9, 0))
		response_date = st.date_input("First Response Date", value=date.today())
		response_time = st.time_input("First Response Time", value=time(9, 30))
		resolved_date = st.date_input("Resolved Date", value=date.today())
		resolved_time = st.time_input("Resolved Time", value=time(17, 0))

		business_impact = st.text_input("Business Impact", value="")

		save_incident = st.form_submit_button("Save Incident", use_container_width=True)

		if save_incident:
			if incident_title.strip() == "" or incident_description.strip() == "":
				st.warning("Title and description are required.")
			else:
				detected_iso = parse_datetime(detected_date, detected_time)
				response_iso = parse_datetime(response_date, response_time)
				resolved_iso = parse_datetime(resolved_date, resolved_time) if incident_status in {"Resolved", "Closed", "Contained"} else None

				time_to_first_response = hours_between(detected_iso, response_iso)
				time_to_resolve = hours_between(detected_iso, resolved_iso)

				database_manager_service.add_incident(
					incident_title,
					incident_description,
					incident_category,
					incident_threat_vector,
					incident_severity,
					incident_status,
					reported_by,
					assigned_to,
					detected_iso,
					response_iso,
					resolved_iso,
					time_to_first_response,
					time_to_resolve,
					business_impact,
				)
				st.success("Incident saved successfully. Refreshing analytics...")
				st.rerun()

	st.subheader("CSV Upload (Bulk Ingest)")
	csv_file_upload = st.file_uploader("Upload enriched incident CSV", type="csv", key="cybersecurity_csv")
	if csv_file_upload is not None and st.button("Process CSV Upload", key="cybersecurity_csv_button"):
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
