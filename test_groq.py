from groq import Groq
from dotenv import load_dotenv
import os

# Load the API key from .env file
load_dotenv()

# Connect to Groq
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Send a test message to LLaMA 3.3 70B
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are an expert SEO content writer."
        },
        {
            "role": "user",
            "content": "Write one sentence about why SEO content marketing matters for SaaS startups."
        }
    ],
    temperature=0.7,
    max_tokens=100
)

# Print the response
print("✅ Groq API connected successfully!")
print("---")
print(response.choices[0].message.content)