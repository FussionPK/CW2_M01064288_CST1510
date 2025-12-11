import google.generativeai as genai

class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_response(self, prompt: str) -> str:
        """Generate response from Google Gemini API"""
        response = self.model.generate_content(prompt)
        return response.text