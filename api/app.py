from fastapi import FastAPI
from fastapi import Body,Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

import mcd.video as v
from mcd.camera import get_cameras
import mcd.conf as conf

app = FastAPI()


@app.get("/switch_mode")
async def switch_mode(mode:str = Query('huiji_detect'),enum=['huiji_detect','person_detect']):
    conf.current_mode = mode
    return {
        "code": 0,
        "msg":f"mode set to ${mode}"
    }

@app.get("/capture_addr")
async def get_capture_addr():
    capture_addr = conf.huiji_detect_config['camera_source'] \
                if conf.current_mode == "huiji_detect" \
                else conf.person_detect_config['camera_source']
    return {
        "code":0,
        "data":capture_addr
    }

@app.get("/combo_meals")
async def get_combo_meals():
    return {
        "code":0,
        "data":{
            "combo_meals": conf.huiji_detect_config["combo_meals"],
            "current": conf.huiji_detect_config["current_combo_meals"]
        }
    }

@app.get("/switch_combo_meals")
async def switch_combo_meals(combo_meals_id:int = Query(0, ge=0, le=1)):
    conf.huiji_detect_config["current_combo_meals"] = conf.huiji_detect_config["combo_meals"][combo_meals_id]
    # 此处需要将视频分析的结果和套餐的信息进行合并
    return {
        "code": 0,
        "msg":"switch success"
    }


@app.get("/combo_meals_analysis")
async def start_combo_meals_analysis():
    # 此处需要将视频分析的结果和套餐的信息进行合并
    return {
        "code":0,
        "data":{
            "current_combo_meals": conf.huiji_detect_config["current_combo_meals"],
            "input_video":"video_source_feed",
            "output_video":"combo_meal_detect_video_output_feed"
        }
    }

@app.get("/person_analysis")
async def get_person_analysis():
    return {
        "code":0,
        "data":{
            "input_video":"video_source_feed",
            "output_video":"person_detect_video_output_feed"
        }
    }

@app.get("/available_cameras")
async def get_available_cameras():
    return {
        "code":0,
        "data":{id:name for id,name in get_cameras()}
    }

@app.post("/capture_addr")
async def put_capture_addr(type:int = 1, capture_addr:str = Body(..., media_type="text/plain")):
    if conf.current_mode == "huiji_detect":
        conf.huiji_detect_config['camera_source'] = capture_addr
    else:
        conf.person_detect_config['camera_source'] = capture_addr

    v.start()

    return {
        "code":0,
        "data":{
            "mode":conf.current_mode,
            "capture_addr": capture_addr
        }
    }

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

@app.lifespan
async def startup_shutdown(app):
    conf.load_config()
    yield
    conf.save_config()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
