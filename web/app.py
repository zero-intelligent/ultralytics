from fastapi import FastAPI, Depends, Request, Response
from fastapi.responses import JSONResponse,StreamingResponse
import cv2
import uvicorn
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

def generate_frames(source=0):
    cap = cv2.VideoCapture(source)  # 捕获摄像头输入，0 表示默认摄像头
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 处理帧的地方，示例中我们将帧转换为灰度
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 编码帧为JPEG格式
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # 使用 yield 生成帧数据流
        yield (b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.get('/video_feed')
async def video_feed(request: Request, response: Response):
    session_id = get_or_create_session_id(request,response)
    source = session_store[session_id]['capture_addr'] or 0
    return StreamingResponse(generate_frames(source), media_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
