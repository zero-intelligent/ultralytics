from fastapi import FastAPI
from fastapi import Body
from fastapi.responses import StreamingResponse
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
    return {k:f'Camera {k}' for k in v.get_available_cameras()}

@app.post("/capture_addr")
async def put_capture_addr(capture_addr:str = Body(..., media_type="text/plain")):
    global_store['capture_addr'] = capture_addr
    return {"capture_addr": capture_addr}

def pad_frame(frame):
    return (b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get('/video_source_feed')
async def video_source_feed():
    source = global_store['capture_addr']
    return StreamingResponse(v.capture_frames(source,pad_frame), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/person_detect_video_output_feed')
async def person_detect_video_output_feed():
    source = global_store['capture_addr']
    return StreamingResponse(v.detect_person_frames(source,pad_frame), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/mcd_package_detect_video_output_feed')
async def mcd_package_detect_video_output_feed():
    source = global_store['capture_addr']
    return StreamingResponse(v.detect_mcd_packages_frames(source,pad_frame), media_type='multipart/x-mixed-replace; boundary=frame')



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
