from fastapi import FastAPI, Depends, Request, Response
from fastapi.responses import JSONResponse
import uuid

app = FastAPI()

SESSION_COOKIE_NAME = "session_id"

# Simulate a session store (in-memory for this example)
session_store = {}


def get_or_create_session_id(request: Request, response: Response) -> str:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id or session_id not in session_store:
        # Generate a new session ID and create a session
        session_id = str(uuid.uuid4())  # Create a unique session ID
        session_store[session_id] = {"user": "Anonymous User"}
        response.set_cookie(key=SESSION_COOKIE_NAME, value=session_id)
    return session_id

@app.get("/profile")
async def profile(session_id: str = Depends(get_or_create_session_id)):
    user_data = session_store[session_id]
    return {"profile": user_data}

@app.post("/logout")
async def logout(response: Response, session_id: str = Depends(get_or_create_session_id)):
    if session_id and session_id in session_store:
        del session_store[session_id]
        response.delete_cookie(SESSION_COOKIE_NAME)
        return {"message": "Logged out"}
    else:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})


@app.get("/capture_addr")
async def get_capture_addr(request: Request, response: Response):
    session_id = get_or_create_session_id(request,response)
    return session_store[session_id]['capture_addr']


@app.post("/capture_addr")
async def put_capture_addr(request: Request, response: Response):
    session_id = get_or_create_session_id(request,response)
    session_store[session_id]['capture_addr'] = request.json()['capture_addr']
    return {"profile": session_store[session_id]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
