import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
default_key = os.getenv("OPENAI_API_KEY")

def generate_resume_bullets(prompt, api_key=None):
    try:
        client = OpenAI(api_key=api_key or default_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional resume writer."},
                {"role": "user", "content": f"Write 3 resume bullet points for: {prompt}"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("🔴 OPENAI ERROR:", e)
        return f"Error: {e}"