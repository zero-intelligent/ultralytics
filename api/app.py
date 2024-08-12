from fastapi import FastAPI
from fastapi import Body
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

import mcd.video as v
from mcd.camera import get_cameras
from mcd.combo_meals import combo_meals,current_combo_meals

app = FastAPI()

# 存储全局信息
global_store = {
    "capture_addr": 0
}

@app.get("/capture_addr")
async def get_capture_addr():
    return global_store['capture_addr']

@app.get("/combo_meals")
async def get_combo_meals():
    return {
        "combo_meals": combo_meals,
        "current": current_combo_meals
    }

@app.get("/combo_meals_analysis")
async def get_combo_meals_analysis():
    # 此处需要将视频分析的结果和套餐的信息进行合并
    return {
        "current_combo_meals": current_combo_meals,
        "input_video":"video_source_feed",
        "output_video":"combo_meal_detect_video_output_feed"
    }


@app.get("/person_analysis")
async def get_person_analysis():
    # 此处需要将视频分析的结果和套餐的信息进行合并
    return {
        "input_video":"video_source_feed",
        "output_video":"person_detect_video_output_feed"
    }

@app.get("/available_cameras")
async def get_available_cameras():
    return {id:name for id,name in get_cameras()}

@app.post("/capture_addr")
async def put_capture_addr(type:int = 1, capture_addr:str = Body(..., media_type="text/plain")):
    global_store['capture_addr'] = capture_addr
    if type == 1:
        v.start_combo_meal_detect(global_store['capture_addr'])
    else:
        v.detect_person_frames(global_store['capture_addr'])
    return {"capture_addr": capture_addr,"type":type}

def pad_frame(frame):
    return (b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.get('/video_source_feed')
async def video_source_feed():
    event_generator = v.stream_generator('source_frame',pad_frame)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get('/combo_meal_detect_video_events')
async def mcd_combo_meal_detect_video_events():

    event_generator = v.stream_generator('combo_meal_result_detected')
    return StreamingResponse(event_generator(), media_type='text/event-stream')

@app.get('/combo_meal_detect_video_output_feed')
async def mcd_combo_meal_detect_video_output_feed():

    event_generator = v.stream_generator('model_result_img_detected')
    return StreamingResponse(event_generator(), media_type='multipart/x-mixed-replace; boundary=frame')


@app.get('/person_detect_video_output_feed')
async def person_detect_video_output_feed():
    event_generator = v.stream_generator('model_result_img_detected')
    return StreamingResponse(event_generator(), media_type='multipart/x-mixed-replace; boundary=frame')


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"code": 1, "msg": str(exc)}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": 2, "msg": str(exc.detail)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"code": 3, "msg": str(exc)}
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
