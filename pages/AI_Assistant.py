import streamlit as st
import google.generativeai as genai


def initialize_gemini_client(api_key: str):
	# Configure Gemini with API key
	genai.configure(api_key=api_key)
	return genai.GenerativeModel('gemini-2.0-flash')


def get_ai_response(gemini_model, user_message: str, conversation_history: list) -> str:
	# Add the user message to conversation history
	conversation_history.append({
		"role": "user",
		"content": user_message
	})

	# Prepare messages for Gemini API
	messages = []
	for msg in conversation_history:
		messages.append({
			"role": "user" if msg["role"] == "user" else "model",
			"parts": [msg["content"]]
		})

	# Call Gemini API with conversation history
	chat_session = gemini_model.start_chat(history=messages[:-1])
	api_response = chat_session.send_message(
		messages[-1]["parts"][0],
		generation_config=genai.types.GenerationConfig(
			max_output_tokens=500,
			temperature=0.7
		)
	)

	# Extract assistant response
	assistant_message = api_response.text

	# Add assistant response to history
	conversation_history.append({
		"role": "assistant",
		"content": assistant_message
	})

	return assistant_message


def main():
	st.set_page_config(page_title="AI Chat", page_icon=":bar_chart:", initial_sidebar_state="expanded")
	st.title("AI Chat Assistant")

	# Check if user is logged in
	if "user" not in st.session_state:
		st.session_state["user"] = None

	if st.session_state["user"] is None:
		st.warning("Please sign in on the Login page to use the AI Chat.")
		return

	# Display current user
	st.success(f"Signed in as {st.session_state['user']['username']}")

	# Initialize conversation history in session state
	if "conversation_history" not in st.session_state:
		st.session_state["conversation_history"] = []

	# Get API key from secrets
	try:
		gemini_api_key = st.secrets["GOOGLE_API_KEY"]
	except KeyError:
		st.error("Google API key not found in secrets.toml")
		return

	# Display conversation history
	st.subheader("Messages")
	
	for message in st.session_state["conversation_history"]:
		if message["role"] == "user":
			st.write(f"**You:** {message['content']}")
		else:
			st.write(f"**Assistant:** {message['content']}")

	# Input section
	st.subheader("Send Message")
	with st.form("chat_form"):
		user_input_message = st.text_area(
			"Type your message:",
			placeholder="Ask anything...",
			height=80,
			label_visibility="collapsed"
		)
		send_message_button = st.form_submit_button("Send", use_container_width=True)

		if send_message_button:
			if user_input_message.strip() == "":
				st.warning("Please enter a message.")
			else:
				try:
					# Get Gemini client with API key from secrets
					gemini_model = initialize_gemini_client(gemini_api_key)

					# Get AI response
					with st.spinner("Thinking..."):
						ai_response_text = get_ai_response(
							gemini_model,
							user_input_message,
							st.session_state["conversation_history"]
						)

					st.rerun()
				except Exception as error_message:
					st.error(f"Error: {error_message}")

	# Clear chat button
	if len(st.session_state["conversation_history"]) > 0:
		if st.button("Clear Chat", use_container_width=True):
			st.session_state["conversation_history"] = []
			st.rerun()


if __name__ == "__main__":
	main()
