from pathlib import Path
import base64
from fastapi import FastAPI,Depends,HTTPException,UploadFile,File,Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select
import httpx
from .database import Base,engine,get_db
from .models import User,History
from pydantic import BaseModel

# Base.metadata.create_all(engine)
# app=FastAPI(title="Sahayak AI")
# OLLAMA="http://127.0.0.1:11434/api/chat"
# MODEL="llama3.2:1b"
# VISION_MODEL="moondream"

class UserCreate(BaseModel):
    name:str
    phone:str|None=None
    assistance_type:str|None=None
class Chat(BaseModel):
    user_id:int
    message:str

PRODUCTS=[
("♿","Manual Wheelchair","Mobility","₹3,999"),
("🦽","Electric Wheelchair","Mobility","₹48,000"),
("🦻","Hearing Aid","Hearing","₹13,990"),
("🦻","Rechargeable Hearing Aid","Hearing","₹71,990"),
("🔎","Low Vision Magnifier","Vision","₹1,999"),
("👓","Smart Assistive Glasses","Vision","₹5,300"),
("🥽","Smart Audio Glasses","Vision","₹2,799"),
("🦯","Smart Cane","Vision","Ask seller"),
("⠿","Braille Device","Vision","Ask seller"),
("🗣️","Communication Aid","Communication","Ask seller")
]

@app.get("/api/status")
async def status():
    try:
        async with httpx.AsyncClient(timeout=2) as c:
            r=await c.get("http://127.0.0.1:11434/api/tags")
            return {"online":r.status_code==200,"model":MODEL}
    except: return {"online":False,"model":MODEL}

@app.get("/api/products")
def products():
    return [{"icon":a,"name":b,"category":c,"price":d} for a,b,c,d in PRODUCTS]

@app.post("/api/user")
def user(x:UserCreate,db:Session=Depends(get_db)):
    u=User(**x.model_dump());db.add(u);db.commit();db.refresh(u)
    return {"user_id":u.id}

@app.post("/api/chat")
async def chat(x:Chat,db:Session=Depends(get_db)):
    if not db.get(User,x.user_id): raise HTTPException(404,"User not found")
    try:
        async with httpx.AsyncClient(timeout=90) as c:
            r=await c.post(OLLAMA,json={"model":MODEL,"stream":False,"messages":[
                {"role":"system","content":"You are Sahayak AI. Understand Hindi, Hinglish and English. Give simple helpful answers. Help with accessibility and assistive technology. For medical questions give general information and advise a professional."},
                {"role":"user","content":x.message}]})
            r.raise_for_status();answer=r.json()["message"]["content"].strip()
    except:
        raise HTTPException(503,"Local AI offline. Run: ollama pull llama3.2:3b and make sure Ollama is running.")
    db.add(History(user_id=x.user_id,question=x.message,answer=answer));db.commit()
    return {"answer":answer}

@app.post("/api/vision")
async def vision(image: UploadFile = File(...), question: str = Form("Describe this image in simple language and tell me anything useful for accessibility.")):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(400,"Please upload an image file.")
    try:
        raw=await image.read()
        if len(raw)>8*1024*1024:
            raise HTTPException(413,"Image is too large. Please use an image smaller than 8 MB.")
        encoded=base64.b64encode(raw).decode("utf-8")
        async with httpx.AsyncClient(timeout=120) as c:
            r=await c.post(OLLAMA,json={"model":VISION_MODEL,"stream":False,"messages":[
                {"role":"system","content":"You are Sahayak AI Visual Assistant. Describe images clearly and simply for people with disabilities. Focus on objects, people, signs, text, obstacles, entrances, doors, stairs, vehicles and other accessibility-relevant details. Never claim certainty when the image is unclear. Do not provide medical diagnosis."},
                {"role":"user","content":question,"images":[encoded]}
            ]})
            r.raise_for_status()
            data=r.json()
            answer=data.get("message",{}).get("content","").strip()
            if not answer: raise HTTPException(502,"Vision model returned an empty answer.")
            return {"answer":answer,"model":VISION_MODEL}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(503,"AI Vision is unavailable. Run: ollama pull moondream and make sure Ollama is running.")

@app.get("/api/history/{uid}")
def history(uid:int,db:Session=Depends(get_db)):
    rows=db.scalars(select(History).where(History.user_id==uid).order_by(History.created_at.desc())).all()
    return [{"question":r.question,"answer":r.answer} for r in rows]

app.mount("/",StaticFiles(directory=str(Path(__file__).parent.parent/"frontend"),html=True),name="frontend")
