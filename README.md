# Encrypted-Chat-Application
A real-time chat platform built with FastAPI and WebSockets, featuring secure authentication and encrypted message storage.
This project demonstrates how modern applications can combine scalability, security, and real-time communication.

## 🛠️ Tech Stack

Backend: FastAPI (Python), WebSockets

Database: SQLite + SQLAlchemy ORM

Security: JWT Authentication, Fernet Encryption (cryptography)

Auth & Hashing: Passlib (bcrypt), Python-JOSE (JWT)

Frontend: Minimal HTML/JS client for chatting

Deployment Ready: Can be hosted on Render / Heroku / AWS

## 🚧 Project Progress

✅ Phase 1: User auth (register/login), JWT tokens

✅ Phase 2: Real-time chat rooms with WebSockets

✅ Phase 3: Encrypted persistence (messages stored as ciphertext, decrypted on retrieval)

🔜 Phase 4: Deployment (make it accessible to friends online)

🔜 Phase 5: Extra features (file sharing, notifications, polished UI)


## ⚡ Quickstart
1) git clone https://github.com/<your-username>/Encrypted-Chat-Application.git
2) cd Encrypted-Chat-Application
3) pip install -r requirements.txt
4) uvicorn app.main:app --reload
5) Swagger Docs → http://127.0.0.1:8000/docs
6) Web Client → http://127.0.0.1:8000/client

## 🎯 Scope & Use Cases

1) Learning Project – shows knowledge of authentication, cryptography, and real-time systems.

2) Secure Messaging Prototype – encrypted chat with history.

3) Portfolio Ready – demonstrates backend skills, API design, and security awareness.

4) Scalable Foundation – could be extended into a full end-to-end encrypted messaging platform.

