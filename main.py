from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import openai
from datetime import datetime

app = FastAPI()

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up template rendering
templates = Jinja2Templates(directory="templates")

# OpenAI API key
openai.api_key = "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"

# Persona
persona = {
    "name": "Jerome",
    "bio": "Software engineer passionate about space, coffee, and indie music.",
    "location": "Berlin",
    "interests": ["coding", "bike touring", "AI"],
    "tone": "witty, curious",
    "catchphrases": ["boom. solved.", "here's the scoop"]
}


@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": user_input},
                ],
                max_tokens=150,
                temperature=0.7
            )

            reply = response['choices'][0]['message']['content']
            await websocket.send_text(reply)

    except WebSocketDisconnect:
        print("Client disconnected")
