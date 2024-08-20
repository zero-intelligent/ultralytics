import os
from fastapi import FastAPI, HTTPException, Response
from fastapi import Body,Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

from fastapi.middleware.cors import CORSMiddleware


import mcd.video as video_srv
from mcd.camera import get_cameras
import mcd.conf as conf
from pydantic import BaseModel

class CameraSetting(BaseModel):
    type: str
    local: str
    url: str

class ConfigSetting:
    model:str
    camera_type: str
    camera_local: str
    camera_url: str
    taocan_id: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://pinda.cn"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/demo_huiji")
async def demo_huiji():
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

@app.get("/demo_person")
async def demo_person():
    html_content = """
    <html>
    <head>
    <title>Camera Stream</title>
    </head>
    <body>
    <h1>Camera Stream</h1>
    <table>
        <tr>
            <td><img src="/person_video_source_feed" width="1024" height="768" /></td>
            <td><img src="/person_video_output_feed" width="1024" height="768" /></td>
        </tr>
    </table>
    </body>
    </html>
    """

    return Response(content=html_content, media_type="text/html")


@app.get("/get_config")
async def get_config():
    configSetting = ConfigSetting()
    configSetting.model = conf.current_mode
    print(conf.huiji_detect_config)
    configSetting.taocan_id = conf.huiji_detect_config["current_taocan_id"]["id"]

    if conf.current_mode == 'huiji_detect':
        configSetting.camera_type=0
        configSetting.camera_local = conf.huiji_detect_config["camera_source"]
        configSetting.camera_url = ""
        configSetting.data_type = "camera"

    if conf.current_mode == 'person_detect':
        configSetting.camera_type = 0
        configSetting.camera_local = conf.person_detect_config["camera_source"]
        configSetting.camera_url = ""
        configSetting.data_type = "camera"

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
    
    conf.current_mode = mode
    return {
        "code": 0,
        "msg":f"mode swit to ${mode}"
    }

class ModeDataSourceRequest(BaseModel):
    mode: str = Field(default="huiji_detect", enum=["huiji_detect", "person_detect"])
    data_source_type: str = Field(default="camera", enum=["camera", "video_file"])
    data_source: str = Field(..., min_length=1, description="数据源不能为空")

@app.post("/mode_datasource")
async def set_mode_datasource(request: ModeDataSourceRequest):
    conf.current_mode = request.mode
    if request.mode == "huiji_detect":
        conf.huiji_detect_config['data_source_type'] = request.data_source_type
        if conf.huiji_detect_config['data_source'] != request.data_source:
            conf.huiji_detect_config['data_source'] = request.data_source
            video_srv.analysis_video_file()
    else:
        conf.person_detect_config['data_source_type'] = request.data_source_type
        if conf.person_detect_config['data_source'] != request.data_source:
            conf.person_detect_config['data_source'] = request.data_source
            video_srv.analysis_video_file()

    return {
        "code": 0,
        "msg":f"ok"
    }

@app.get("/mode_datasource")
async def get_mode_datasource():
    data_source_type = 'camera'
    data_source = '0'

    if conf.current_mode == "huiji_detect":
        data_source_type = conf.huiji_detect_config['data_source_type']
        data_source = conf.huiji_detect_config['camera_source'] if data_source_type == 'camera' else conf.huiji_detect_config['video_file']
    else:
        data_source_type = conf.person_detect_config['data_source_type']
        data_source = conf.person_detect_config['camera_source'] if data_source_type == 'camera' else conf.person_detect_config['video_file']
    
    return {
        "code": 0,
        "data": {
            "mode": conf.current_mode,
            "data_source_type": data_source_type,
            "data_source": data_source
        },
    }

# 扩展名到 MIME 类型的映射
MIME_TYPES = {
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    ".webm": "video/webm",
    ".mkv": "video/x-matroska",
}

@app.get("/video_model_output_file")
async def get_video_model_output_file():
    video_file = conf.huiji_detect_config.get('video_model_output_file')
    if not video_file or not os.path.exists(video_file):
        raise HTTPException(status_code=400, detail="未找到输出文件")
    
    file_name, file_extension = os.path.splitext(os.path.basename(video_file))
    # 获取文件扩展名
    file_extension = os.path.splitext(video_file)[1].lower()

    # 获取对应的 MIME 类型
    media_type = MIME_TYPES.get(file_extension)

    if not media_type:
        raise HTTPException(status_code=400, detail="Unsupported video format")

    if not os.path.exists(video_file):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=video_file,
        media_type=media_type,
        filename=os.path.basename(video_file)
    )

@app.get("/capture_addr")
async def get_capture_addr():
    capture_addr = conf.huiji_detect_config['camera_source'] \
                if conf.current_mode == "huiji_detect" \
                else conf.person_detect_config['camera_source']
    return {
        "code":0,
        "data":capture_addr
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
async def switch_taocan(taocan_id:int = Query(0, ge=0, le=1)):
    conf.huiji_detect_config["current_taocan_id"] = conf.huiji_detect_config["taocans"][taocan_id]
    # 此处需要将视频分析的结果和套餐的信息进行合并
    return {
        "code": 0,
        "msg":"switch success"
    }


@app.get("/taocan_analysis")
async def start_taocan_analysis():
    # 先启动视频捕获
    if not video_srv.current_taocan_check_result:
        next(video_srv.huiji_detect_frames())
    if video_srv.current_taocan_check_result is None:
        raise Exception('启动huji检测失败！')
    result = video_srv.get_detect_items(video_srv.current_taocan_check_result)

    return {
        "code":0,
        "data":{
            "current_taocan_result": result,
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

@app.put("/video_input_file")
async def put_video_file(capture_addr:str = Body(..., media_type="text/plain")):
    return {
        "code":0,
        "data":{
            "mode":conf.current_mode,
            "capture_addr": capture_addr
        }
    }

@app.get("/video_input_file")
async def get_video_file(capture_addr:str = Body(..., media_type="text/plain")):
    return {
        "code":0,
        "data":{
            "mode":conf.current_mode,
            "capture_addr": capture_addr
        }
    }

@app.get("/video_model_output_file")
async def get_video_model_output_file(capture_addr:str = Body(..., media_type="text/plain")):
    return {
        "code":0,
        "data":{
            "mode":conf.current_mode,
            "capture_addr": capture_addr
        }
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



@app.post('/upload')
async def upload_file(
        identifier: str = Form(..., description="文件唯一标识符"),
        current: str = Form(..., description="文件分片序号（初值为1）"),
        total: str = Form(..., description="总分片数量"),
        name: str = Form(..., description="文件名"),
        file: UploadFile = File(..., description="文件")
):
    """文件分片上传"""
    UPLOAD_FILE_PATH = "uploads"
    current = current.zfill(3)
    total   = total.zfill(3)
    path = Path(UPLOAD_FILE_PATH, identifier)
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = Path(path, f'{identifier}_{current}')
    if not os.path.exists(file_name):
        async with aiofiles.open(file_name, 'wb') as f:
            await f.write(await file.read())

    if current == total:
        merge_chunks(identifier, name)

    return {"code": 200, "data": {
        'chunk': f'{identifier}_{current}'}}




def merge_chunks(identifier, name):

    UPLOAD_FILE_PATH = "uploads/" + identifier

    chunk_files = sorted(os.listdir(UPLOAD_FILE_PATH)) # 获取所有分片文件
    print(chunk_files)
    output_file = f'{UPLOAD_FILE_PATH}/{name}' # 定义合并后的文件路径

    with open(output_file, 'wb') as output:
        for chunk_file in chunk_files:
            with open(f'{UPLOAD_FILE_PATH}/{chunk_file}', 'rb') as chunk:
                output.write(chunk.read()) # 将分片内容写入合并后的文件

    # 删除所有分片文件
    # for chunk_file in chunk_files:
    #     os.remove(f'{UPLOAD_FILE_PATH}/{chunk_file}')

    print('File saved successfully')


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
