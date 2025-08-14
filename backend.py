# backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import uvicorn

# Create FastAPI app
app = FastAPI(title="Finance Chatbot Backend")

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class UserProfile(BaseModel):
    name: str
    age: int
    income: float
    risk: str

class ChatRequest(BaseModel):
    prompt: str
    profile: UserProfile

# --- Core Logic ---
def generate_response(prompt: str, profile: dict) -> str:
    p = prompt.lower()
    name = profile.get("name") or "Friend"
    if "tax" in p or "taxes" in p:
        return (
            f"{name}, here’s a quick tax tip: keep organized records, claim eligible deductions, "
            "use tax-advantaged accounts where available, and consider consulting a tax professional."
        )
    if "save" in p or "savings" in p or "emergency" in p:
        return (
            f"{name}, aim for 3–6 months of essential expenses as an emergency fund. "
            "Automate saving 10–20% of income and adjust for your goals."
        )
    if "invest" in p or "investment" in p or "portfolio" in p:
        risk = profile.get("risk", "Medium")
        if risk == "Low":
            return "Low risk: diversified bonds, fixed-income funds, or conservative allocation funds."
        if risk == "High":
            return "High risk: diversified equity/index funds, dollar-cost averaging, and emerging markets."
        return "Medium risk: balanced portfolio of equities and fixed-income."
    return "I can help with savings, taxes, and investments. Try asking about a savings plan or tax tips."

# --- API Endpoint ---
@app.post("/chat")
def chat_endpoint(data: ChatRequest) -> Dict:
    answer = generate_response(data.prompt, data.profile.dict())
    return {"response": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
