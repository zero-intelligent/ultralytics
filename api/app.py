import asyncio
import copy
from fastapi import FastAPI, Response
from fastapi import Body,Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware


import mcd.video as video_srv
from mcd.camera import get_cameras
import mcd.conf as conf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://pinda.cn"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def index():
    html_content = """
    <html>
    <head>
    <title>Camera Stream</title>
    </head>
    <body>
    <h1>Camera Stream</h1>
    <table>
        <tr>
            <td><img src="/huiji_video_source_feed" width="1024" height="768" /></td>
            <td><img src="/huiji_video_output_feed" width="1024" height="768" /></td>
        </tr>
    </table>
    </body>
    </html>
    """

    return Response(content=html_content, media_type="text/html")


@app.get("/switch_mode")
async def switch_mode(mode:str = Query('huiji_detect'),enum=['huiji_detect','person_detect']):
    if conf.current_mode == mode:
        return {
            "code": 0,
            "msg":f"mode has been {mode}"
        }
    
    conf.current_mode = mode
    return {
        "code": 0,
        "msg":f"mode swit to ${mode}"
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
            "current_combo_meals_id": conf.huiji_detect_config["current_combo_meals_id"]
        }
    }

@app.get("/switch_combo_meal")
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
            "input_video":"huiji_video_source_feed",
            "output_video":"huiji_video_output_feed"
        }
    }

@app.get("/person_analysis")
async def get_person_analysis():
    return {
        "code":0,
        "data":{
            "input_video":"person_video_source_feed",
            "output_video":"person_video_output_feed"
        }
    }

@app.get("/available_cameras")
async def get_available_cameras():
    return {
        "code":0,
        "data":{id:name for id,name in get_cameras()}
    }

@app.post("/capture_addr")
async def put_capture_addr(capture_addr:str = Body(..., media_type="text/plain")):
    if conf.current_mode == "huiji_detect" and conf.huiji_detect_config['camera_source'] == capture_addr \
    or conf.current_mode == "person_detect" and conf.person_detect_config['camera_source'] == capture_addr:
        return {
            "code":0,
            "data":{
                "mode":conf.current_mode,
                "capture_addr": capture_addr
            },
            "msg":f'camera has been {capture_addr},not changed'
        }

    if conf.current_mode == "huiji_detect":
        conf.huiji_detect_config['camera_source'] = capture_addr
    else:
        conf.person_detect_config['camera_source'] = capture_addr

    return {
        "code":0,
        "data":{
            "mode":conf.current_mode,
            "capture_addr": capture_addr
        }
    }

def pad_frame(frame):
    return (b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.get('/huiji_video_source_feed')
async def huiji_video_source_feed():
    img_stream = (pad_frame(r[0]) for r in video_srv.huiji_detect_frames())
    return StreamingResponse(img_stream, media_type="multipart/x-mixed-replace; boundary=frame")


@app.get('/huiji_video_taocan_detect_result')
async def sync_huiji_video_events():
    if not video_srv.current_taocan_check_result:
        return {
            "code":1,
            "data":{
                "input_video": "person_video_source_feed",
                "output_video": "person_video_output_feed"
            },
            "msg":"当前没有检测结果"
        }
    taocan_id = conf.huiji_detect_config['current_combo_meals_id']
    taocan =  conf.huiji_detect_config['combo_meals'][taocan_id]
    return {
        "code":0,
        "data":{
            "taocan_id": taocan_id,
            "taocan_name":taocan['name'],
            "items": video_srv.get_detect_items(video_srv.current_taocan_check_result)
        }
    }

@app.get('/huiji_video_events')
async def async_huiji_video_events():
    event_stream = (video_srv.get_detect_items(v[2]) for v in video_srv.huiji_detect_frames() if video_srv.changed(v[2]))
    return StreamingResponse(event_stream, media_type="text/json")

@app.get('/huiji_video_output_feed')
async def huiji_video_output_feed():
    img_stream = (pad_frame(v[1]) for v in video_srv.huiji_detect_frames())
    return StreamingResponse(img_stream, media_type="multipart/x-mixed-replace; boundary=frame")


@app.get('/person_video_source_feed')
async def person_video_source_feed():
    img_stream = (pad_frame(v[0]) for v in video_srv.person_detect_frames())
    return StreamingResponse(img_stream, media_type="multipart/x-mixed-replace; boundary=frame")

@app.get('/person_video_output_feed')
async def person_detect_video_output_feed():
    img_stream = (pad_frame(v[1]) for v in video_srv.person_detect_frames())
    return StreamingResponse(img_stream, media_type="multipart/x-mixed-replace; boundary=frame")


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    conf.load_config()
    yield
    conf.save_config()

app.router.lifespan_context = lifespan


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6789, log_level="info")
