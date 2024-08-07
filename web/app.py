from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse,StreamingResponse
import mcd.video as v

app = FastAPI()

# 存储全局信息
global_store = {
    "capture_addr": 0
}

@app.get("/capture_addr")
async def get_capture_addr():
    return global_store['capture_addr']


@app.get("/available_cameras")
async def get_available_cameras():
    return v.get_available_cameras()

@app.post("/capture_addr")
async def put_capture_addr(request: Request, response: Response):
    global_store['capture_addr'] = request.json()['capture_addr']
    return {"capture_addr": global_store['capture_addr']}

def pad_frames(frames_generator):
    for frame in frames_generator:
        yield (b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get('/video_source_feed')
async def video_source_feed(request: Request, response: Response):
    source = global_store['capture_addr']
    return StreamingResponse(pad_frames(v.capture_frames(source)), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/video_output_feed')
async def video_output_feed(request: Request, response: Response):
    source = global_store['capture_addr']
    return StreamingResponse(pad_frames(v.analyze_frames(source)), media_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
