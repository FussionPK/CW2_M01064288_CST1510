from datetime import date, datetime
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


def load_dataset_dataframe(db: DbManagerService) -> pd.DataFrame:
	rows = db.list_datasets()
	if not rows:
		return pd.DataFrame()
	df = pd.DataFrame(rows)
	numeric_columns = ["row_count", "size_mb", "quality_score"]
	for column in numeric_columns:
		df[column] = pd.to_numeric(df[column], errors="coerce")
	if "last_accessed" in df.columns:
		df["last_accessed"] = pd.to_datetime(df["last_accessed"], errors="coerce")
	if "updated_at" in df.columns:
		df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")
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
			st.warning("Provide GOOGLE_API_KEY in secrets.toml to enable AI governance guidance.")
		else:
			st.warning("Provide XAI_API_KEY in secrets.toml to enable AI governance guidance.")
		return None

	try:
		return AIService(api_key, provider=provider)
	except Exception as error:
		st.error(f"AI setup error: {error}")
		return None


def render_governance_ai(df: pd.DataFrame) -> None:
	if df.empty:
		st.info("Add datasets to analyse governance health.")
		return
	ai_service = build_ai_service()
	if ai_service is None:
		return

	stale_datasets = df[df["status"].str.contains("inactive", case=False, na=False)]
	heavy_datasets = df[df["size_mb"] >= 25]
	department_summary = (
		df.groupby("owner_department", dropna=False)
		.agg({"size_mb": "sum", "row_count": "sum", "quality_score": "mean"})
		.reset_index()
	)
	insight_payload = {
		"inactive_count": int(stale_datasets.shape[0]),
		"heavy_datasets": heavy_datasets.sort_values("size_mb", ascending=False).head(5).to_dict(orient="records"),
		"department_summary": department_summary.to_dict(orient="records"),
	}
	prompt = (
		"You are a data governance lead. Recommend archival and quality actions based on the JSON summary. "
		"Keep the response under 120 words and be specific about departments or datasets that need attention."
		f"\nJSON: {json.dumps(insight_payload, default=str)}"
	)
	with st.spinner("Generating governance actions..."):
		recommendation = ai_service.generate_response(prompt)
	st.write(recommendation)


def parse_float(value: str) -> float:
	try:
		return round(float(value), 2)
	except (TypeError, ValueError):
		return 0.0


def parse_int(value: str) -> int:
	try:
		return int(value)
	except (TypeError, ValueError):
		return 0


def main() -> None:
	st.set_page_config(page_title="Data Science Dashboard", page_icon=":bar_chart:", initial_sidebar_state="expanded")
	st.title("Data Science Governance")
	st.caption("Audit dataset growth, storage consumption, and quality signals.")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	database_manager_service = get_db_manager()

	if st.session_state["user"] is None:
		st.info("Sign in on the Login page to manage datasets.")
	else:
		st.success(f"Signed in as {st.session_state['user']['username']}")

	datasets_df = load_dataset_dataframe(database_manager_service)

	st.subheader("Resource Consumption Overview")
	if datasets_df.empty:
		st.info("No datasets recorded yet. Add one below to analyse storage and quality.")
	else:
		total_storage = datasets_df["size_mb"].sum()
		total_row_count = datasets_df["row_count"].sum()
		heavy_datasets = datasets_df[datasets_df["size_mb"] >= 25]

		col1, col2, col3 = st.columns(3)
		col1.metric("Total Storage (GB)", f"{total_storage / 1024:.2f}")
		col2.metric("Rows Managed", f"{total_row_count:,}")
		col3.metric("Large Datasets", int(heavy_datasets.shape[0]))

		department_breakdown = (
			datasets_df.groupby("owner_department", dropna=False)["size_mb"].sum().reset_index()
		)
		if not department_breakdown.empty:
			dept_fig = px.bar(
				department_breakdown,
				x="owner_department",
				y="size_mb",
				title="Storage Footprint by Department (MB)",
				labels={"owner_department": "Department", "size_mb": "Size (MB)"},
				text_auto=".0f",
			)
			dept_fig.update_layout(margin=dict(t=60, l=0, r=0, b=0))
			st.plotly_chart(dept_fig, use_container_width=True)

		growth_trend = (
			datasets_df.dropna(subset=["updated_at"])
			.assign(updated_month=datasets_df["updated_at"].dt.to_period("M").dt.to_timestamp())
			.groupby(["updated_month", "owner_department"], dropna=False)["size_mb"].sum()
			.reset_index()
		)
		if not growth_trend.empty:
			trend_fig = px.line(
				growth_trend,
				x="updated_month",
				y="size_mb",
				color="owner_department",
				title="Dataset Growth Trend",
				markers=True,
			)
			trend_fig.update_layout(margin=dict(t=60, l=0, r=0, b=0))
			st.plotly_chart(trend_fig, use_container_width=True)

		st.markdown("**Top Resource Consumers**")
		st.dataframe(
			datasets_df.sort_values("size_mb", ascending=False)[
				[
					"name",
					"owner_department",
					"data_source",
					"row_count",
					"size_mb",
					"quality_score",
					"status",
				]
			].head(10),
			hide_index=True,
		)

	st.subheader("AI Governance Recommendation")
	render_governance_ai(datasets_df)

	st.subheader("Add Dataset")
	with st.form("dataset_form", clear_on_submit=True):
		col_left, col_right = st.columns(2)
		with col_left:
			dataset_name = st.text_input("Name")
			dataset_owner_department = st.selectbox(
				"Owner Department",
				["Security", "Data Science", "IT Operations", "Finance", "HR", "Other"],
			)
			dataset_source = st.text_input("Data Source", value="S3")
			dataset_row_count = st.text_input("Row Count", value="100000")
			dataset_size = st.text_input("Size (MB)", value="5.0")
		with col_right:
			dataset_quality = st.slider("Quality Score", min_value=0.0, max_value=1.0, value=0.8, step=0.05)
			dataset_retention = st.text_input("Retention Policy", value="Archive after 12 months")
			dataset_status = st.selectbox("Status", ["Active", "Inactive", "Archived"])
			last_accessed = st.date_input("Last Accessed", value=datetime.today().date())
			updated_at = st.date_input("Last Refreshed", value=datetime.today().date())

		dataset_description = st.text_area("Description", height=120)
		created_at = st.date_input("Created On", value=datetime.today().date())

		save_dataset = st.form_submit_button("Save Dataset", use_container_width=True)

		if save_dataset:
			if dataset_name.strip() == "":
				st.warning("Dataset name is required.")
			else:
				database_manager_service.add_dataset(
					dataset_name,
					dataset_description,
					dataset_owner_department,
					dataset_source,
					parse_int(dataset_row_count),
					parse_float(dataset_size),
					float(dataset_quality),
					dataset_retention,
					dataset_status,
					last_accessed.isoformat(),
					created_at.isoformat(),
					updated_at.isoformat(),
				)
				st.success("Dataset saved successfully. Refreshing insights...")
				st.rerun()

	st.subheader("CSV Upload (Catalog Staging)")
	csv_file_upload = st.file_uploader("Upload dataset catalog extract", type="csv", key="dataset_csv")
	if csv_file_upload is not None and st.button("Process CSV Upload", key="dataset_csv_button"):
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
