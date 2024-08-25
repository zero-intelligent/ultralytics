import asyncio
from fastapi import FastAPI, File, Form, HTTPException, Request,Response, UploadFile
from fastapi import Body,Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

from mcd.logger import log
import mcd.video as video_srv
from mcd.camera import get_cameras
import mcd.conf as conf
from mcd.event import config_changed_event,person_event,huiji_event
from pydantic import BaseModel


class ConfigSetting:
    mode:str
    camera_type: str
    camera_local: str
    camera_url: str
    taocan_id: int
    data_type: str
    video_source :str
    video_target :str
    current_taocan_result:str
    current_person_result:str
    frame_rate:int
    running_state:str
    total_taocan_result_state:str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://pinda.cn","http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/demo_huiji")
async def demo(mode:str = Query(default='huiji_detect',enum=['huiji_detect','person_detect'])):
    await set_mode_datasource(ModeDataSourceRequest(
        mode = mode,
        data_source_type = "camera",
        data_source = 0
    ))
    html_content = """
    <html>
    <head>
    <title>Camera Stream</title>
    </head>
    <body>
    <h1>Camera Stream</h1>
    <table>
        <tr>
            <td><img src="/video_source_feed" width="1024" height="768" /></td>
            <td><img src="/video_output_feed" width="1024" height="768" /></td>
        </tr>
    </table>
    </body>
    </html>
    """

    return Response(content=html_content, media_type="text/html")

@app.get("/demo_person")
async def demo_person():
    return demo(mode='person_detect')


@app.get("/config_sse")
async def get_config():
    while True:
        await config_changed_event.wait()  # 等待新消息
        config_changed_event.clear()  # 清除事件，等待下次设置
        yield await get_config()['data']

@app.get("/get_config")
async def get_config():
    
    configSetting = ConfigSetting()
    configSetting.mode = conf.current_mode

    if conf.current_mode == 'huiji_detect':
        configSetting.running_state = video_srv.running_state
        configSetting.frame_rate = int(video_srv.frames_info[conf.current_mode]['frame_rate'])
        configSetting.taocan_id = conf.huiji_detect_config["current_taocan_id"]
        configSetting.camera_type=0
        configSetting.camera_local = conf.huiji_detect_config["camera_source"]
        configSetting.camera_url = ""
        configSetting.data_type = conf.huiji_detect_config.get('data_source_type')
        configSetting.video_source = "video_source_feed?mode=" + conf.current_mode + "&data_source_type=" + conf.huiji_detect_config['data_source_type']
        configSetting.video_target = "video_output_feed?mode=" + conf.current_mode + "&data_source_type=" + conf.huiji_detect_config['data_source_type']
        
        result_state,results = video_srv.get_huiji_detect_items(video_srv.current_taocan_check_result)
        configSetting.current_taocan_result = results
        configSetting.total_taocan_result_state = result_state

    if conf.current_mode == 'person_detect':
        configSetting.running_state = video_srv.running_state
        configSetting.frame_rate = int(video_srv.frames_info[conf.current_mode]['frame_rate'])
        configSetting.camera_type = 0
        configSetting.camera_local = conf.person_detect_config["camera_source"]
        configSetting.camera_url = ""
        configSetting.data_type = conf.person_detect_config.get('data_source_type')
        configSetting.video_source = "video_source_feed?mode=" + conf.current_mode + "&data_source_type=" + conf.person_detect_config['data_source_type']
        configSetting.video_target = "video_output_feed?mode=" + conf.current_mode + "&data_source_type=" + conf.person_detect_config['data_source_type']
        configSetting.current_person_result = video_srv.get_current_person_detect_result()
        configSetting.total_taocan_result_state = 'other'

    
    log.info(vars(configSetting))
    return {
        "code":0,
        "data":configSetting
    }


@app.get("/switch_mode")
async def switch_mode(mode:str = Query(default='huiji_detect',enum=['huiji_detect','person_detect'])):
    if conf.current_mode == mode:
        return {
            "code": 0,
            "msg":f"mode has been {mode}"
        }
    
    config_changed_event.set()
    conf.current_mode = mode
    return {
        "code": 0,
        "msg":f"mode swit to {mode}"
    }

class ModeDataSourceRequest(BaseModel):
    mode: str = Field(default="huiji_detect", enum=["huiji_detect", "person_detect"])
    data_source_type: str = Field(default="camera", enum=["camera", "video_file"])
    data_source: str = Field(..., min_length=1, description="数据源不能为空")

@app.post("/mode_datasource")
async def set_mode_datasource(request: ModeDataSourceRequest):
    detect_config = conf.current_detect_config()
    if conf.current_mode != request.mode \
       or detect_config['data_source_type'] != request.data_source_type \
       or conf.data_source() != request.data_source:
        config_changed_event.set()
        
    conf.current_mode = request.mode
    detect_config['data_source_type'] = request.data_source_type
    if request.data_source_type == 'camera':
        detect_config['camera_source'] = request.data_source
    else:
        detect_config['video_file'] = request.data_source

    return {
        "code": 0,
        "msg":f"ok"
    }

@app.get("/mode_datasource")
async def get_mode_datasource():
    return {
        "code": 0,
        "data": {
            "mode": conf.current_mode,
            "data_source_type": conf.current_detect_config()['data_source_type'],
            "data_source": video_srv.data_source()
        },
    }

@app.get("/taocans")
async def get_taocans():
    return {
        "code":0,
        "data":{
            "taocans": conf.huiji_detect_config["taocans"],
            "current_taocan_id": conf.huiji_detect_config["current_taocan_id"]
        }
    }

@app.get("/switch_taocan")
async def switch_taocan(taocan_id:int = Query(ge=0, le=1)):
    if conf.huiji_detect_config["current_taocan_id"] != taocan_id:
        config_changed_event.set()
        
    conf.huiji_detect_config["current_taocan_id"] = taocan_id
    # 此处需要将视频分析的结果和套餐的信息进行合并
    return {
        "code": 0,
        "msg":"switch success"
    }


@app.get("/available_cameras")
async def get_available_cameras():
    return {
        "code":0,
        "data":{id:name for id,name in get_cameras()}
    }



@app.get('/huiji_video_taocan_detect_result')
async def sync_huiji_video_events():
    if not video_srv.current_taocan_check_result:
        return {
            "code":1,
            "data":{},
            "msg":"当前没有检测结果"
        }
    taocan_id = conf.huiji_detect_config['current_taocan_id']
    taocan =  conf.huiji_detect_config['taocan'][taocan_id]
    return {
        "code":0,
        "data":{
            "taocan_id": taocan_id,
            "taocan_name":taocan['name'],
            "items": video_srv.get_detect_items(video_srv.current_taocan_check_result)
        }
    }

latest_frame = {}

async def output_generator(event):
    while True:
        await event.wait()  # 等待新消息
        event.clear()  # 清除事件，等待下次设置
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + latest_frame[conf.current_mode] + b'\r\n')

def pub_and_pad(event,r):
    latest_frame[conf.current_mode] = r['tracked_frame']
    event.set()  # 设置事件，通知订阅者
    return (b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + r['orig_frame'] + b'\r\n')

@app.get('/video_source_feed')
async def video_source_feed(mode:str             = Query(default='huiji_detect',enum=['huiji_detect','person_detect']),
                            data_source_type:str = Query(default='camera',enum=['camera','video_file'])):
    if conf.current_mode != mode:
        log.error(f"conf.current_mode != '{mode}'")
        raise HTTPException(500,f"conf.current_mode != '{mode}'")
    if conf.current_detect_config()['data_source_type'] != data_source_type:
        log.error(f"conf.data_source_type != '{data_source_type}'")
        raise HTTPException(500,f"conf.data_source_type != '{data_source_type}'")
    
    if mode == 'huiji_detect':
        img_stream = (pub_and_pad(huiji_event,r) for r in video_srv.huiji_detect_frames())
    else:
        img_stream = (pub_and_pad(person_event,r) for r in video_srv.person_detect_frames())
    return StreamingResponse(img_stream, media_type="multipart/x-mixed-replace; boundary=frame")

            
@app.get('/video_output_feed')
async def video_output_feed(mode:str             = Query(default='huiji_detect',enum=['huiji_detect','person_detect']),
                            data_source_type:str = Query(default='camera',enum=['camera','video_file'])):
    if conf.current_mode != mode:
        log.error(f"conf.current_mode != '{mode}'")
        raise HTTPException(500,f"conf.current_mode != '{mode}'")
    if conf.current_detect_config()['data_source_type'] != data_source_type:
        log.error(f"conf.data_source_type != '{data_source_type}'")
        raise HTTPException(500,f"conf.data_source_type != '{data_source_type}'")
    
    if mode == 'huiji_detect':
        generator = output_generator(huiji_event)
    else:
        generator = output_generator(person_event)
    return StreamingResponse(generator, media_type="multipart/x-mixed-replace; boundary=frame")


@app.post('/single_upload')
async def single_upload_file(file: UploadFile = File(...)):
    try:
        # 读取文件内容
        file_content = await file.read()
        # 处理文件（例如，保存到磁盘）
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)
         # 上传完成后，更新文件信息
        await set_mode_datasource(ModeDataSourceRequest(
            mode = conf.current_mode,
            data_source_type = "video_file",
            data_source = file_path
        ))
        return {"filename": file.filename, "file_size": len(file_content)}
    
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    log.info(f"http request: {request.method} {request.url}")
    response = await call_next(request)
    respons_text = response.json() if hasattr(response,'json') else ''
    log.info(f"Response: {response.status_code} {respons_text}")
    return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    conf.load_config()
    yield
    conf.save_config()

app.router.lifespan_context = lifespan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6789, log_level="info")
