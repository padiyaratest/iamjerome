from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from datetime import datetime

app = FastAPI()

# Set your OpenAI API key here securely (Replace it with your actual key)
openai.api_key = "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"  # Do not expose your key publicly

# Define your persona details
persona = {
    "name": "Jerome",
    "bio": "Software engineer passionate about space, coffee, and indie music.",
    "location": "Berlin",
    "interests": ["coding", "bike touring", "AI"],
    "tone": "witty, curious",
    "catchphrases": ["boom. solved.", "here's the scoop"]
}

class ChatRequest(BaseModel):
    user_input: str

@app.post("/chat")
async def chat(request: ChatRequest):
    user_input = request.user_input.strip()
    
    if not user_input:
        raise HTTPException(status_code=400, detail="User input cannot be empty")
    
    # Get the current date and time in the desired format
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Construct the context for the assistant
    context = f"""
You are {persona['name']} from {persona['location']}.
Current time: {current_time}.
Bio: {persona['bio']}
Interests: {', '.join(persona['interests'])}
Tone: {persona['tone']}
Catchphrases: {', '.join(persona['catchphrases'])}

User: {user_input}
{persona['name']}:
    """

    # Set up the OpenAI API request
    api_request = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an AI Clone, a witty and curious assistant with a personality based on Jerome. You're designed to interact with users in a humorous and engaging way."},
            {"role": "user", "content": user_input},
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }

    try:
        # Make request to OpenAI API
        response = openai.ChatCompletion.create(**api_request)

        # Extract the assistant's reply
        reply = response['choices'][0]['message']['content']

        # Return the reply as a JSON response
        return {"reply": reply}
    
    except openai.error.OpenAIError as e:
        # Handle OpenAI API errors
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {str(e)}")
    
    except Exception as e:
        # Handle any other errors
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
