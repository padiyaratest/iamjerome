from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from datetime import datetime
import openai
import json

app = FastAPI()

# Securely set your API key (avoid hardcoding in real deployment)
openai.api_key = "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"

# Persona details
persona = {
    "name": "Jerome",
    "bio": "Software engineer passionate about space, coffee, and indie music.",
    "location": "Berlin",
    "interests": ["coding", "bike touring", "AI"],
    "tone": "witty, curious",
    "catchphrases": ["boom. solved.", "here's the scoop"]
}


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            user_input = await websocket.receive_text()

            if not user_input.strip():
                await websocket.send_text("Let's not ghost each other—type something!")
                continue

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Inject persona details into the prompt
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

            full_system_prompt = (
                "You are an AI Clone, a witty and curious assistant with a personality based on Jerome. "
                "You're designed to interact with users in a humorous and engaging way.\n\n"
                f"{context.strip()}"
            )

            api_request = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": user_input},
                ],
                "max_tokens": 150,
                "temperature": 0.7
            }

            response = openai.ChatCompletion.create(**api_request)
            reply = response['choices'][0]['message']['content']
            await websocket.send_text(reply)

    except WebSocketDisconnect:
        print("Client disconnected")
