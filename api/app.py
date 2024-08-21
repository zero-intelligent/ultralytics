import os
from pathlib import Path
import aiofiles
from fastapi import FastAPI, File, Form, HTTPException, Request,Response, UploadFile
from fastapi import Body,Query
from fastapi.staticfiles import StaticFiles
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
    taocan_id: int
    data_file_source:str
    data_file_target:str



app = FastAPI()
app.mount("/video_files", StaticFiles(directory="uploads"), name="uploads")
app.mount("/analysis_video_output", StaticFiles(directory=video_srv.model_result_save_dir), name="analysis_video_output")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://pinda.cn","http://127.0.0.1:8000"],
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
    configSetting.taocan_id = conf.huiji_detect_config["current_taocan_id"]

    if conf.current_mode == 'huiji_detect':
        configSetting.camera_type=0
        configSetting.camera_local = conf.huiji_detect_config["camera_source"]
        configSetting.camera_url = ""
        configSetting.data_type = conf.huiji_detect_config.get('data_source_type')
        configSetting.data_file_source = "/video_files/" + os.path.basename(conf.huiji_detect_config.get('video_file')) if conf.huiji_detect_config.get('video_file') else ''
        configSetting.data_file_target = "/analysis_video_output/" + os.path.basename(conf.huiji_detect_config.get('video_model_output_file')) if conf.huiji_detect_config.get('video_model_output_file') else ''
        

    if conf.current_mode == 'person_detect':
        configSetting.camera_type = 0
        configSetting.camera_local = conf.person_detect_config["camera_source"]
        configSetting.camera_url = ""
        configSetting.data_type = conf.person_detect_config.get('data_source_type')
        configSetting.data_file_source = "/video_files/" + os.path.basename(conf.person_detect_config.get('video_file')) if conf.person_detect_config.get('video_file') else ''
        configSetting.data_file_target = "/analysis_video_output/" + os.path.basename(conf.person_detect_config.get('video_model_output_file')) if conf.person_detect_config.get('video_model_output_file') else ''

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
        "msg":f"mode swit to {mode}"
    }

class ModeDataSourceRequest(BaseModel):
    mode: str = Field(default="huiji_detect", enum=["huiji_detect", "person_detect"])
    data_source_type: str = Field(default="camera", enum=["camera", "video_file"])
    data_source: str = Field(..., min_length=1, description="数据源不能为空")

@app.post("/mode_datasource")
async def set_mode_datasource(request: ModeDataSourceRequest):
    conf.current_mode = request.mode
    def update_datasource(detect_config):
        detect_config['data_source_type'] = request.data_source_type
        if request.data_source_type == 'camera':
            if detect_config['camera_source'] != request.data_source:
                detect_config['camera_source'] = request.data_source
                video_srv.huiji_detect_frames()
        else:
            if detect_config['video_file'] != request.data_source:
                detect_config['video_file'] = request.data_source
                video_srv.analysis_video_file()

    if request.mode == "huiji_detect":
        update_datasource(conf.huiji_detect_config)
    else:
        update_datasource(conf.person_detect_config)

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
    conf.huiji_detect_config["current_taocan_id"] = taocan_id
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

@app.get("/do_set_type")
async def do_set_type():
    conf.current_mode = "huiji_detect"
    conf.huiji_detect_config['data_source_type'] = "video_file"
    conf.huiji_detect_config['data_source'] = "/Users/chenyuyun/Documents/GitHub/ultralytics/api/demo.mp4"
    video_srv.analysis_video_file()
    return {
        "code":0
    }

@app.get("/switch_data_type")
async def switch_data_type(type:str):
    # conf.current_mode = "huiji_detect"
    # conf.huiji_detect_config['data_source_type'] = "video_file"
    # conf.huiji_detect_config['data_source'] = "/Users/chenyuyun/Documents/GitHub/ultralytics/api/demo.mp4"
    # video_srv.analysis_video_file()
    return {
        "code":0
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
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



@app.post('/bunchs_upload')
async def buncks_upload_file(
        identifier: str = Form(..., description="文件唯一标识符"),
        current: str = Form(..., description="文件分片序号（初值为1）"),
        total: str = Form(..., description="总分片数量"),
        name: str = Form(..., description="文件名"),
        file: UploadFile = File(..., description="文件")
):
    """文件分片上传"""
    UPLOAD_FILE_PATH = "uploads"
    current = current.zfill(3)
    total   = str(total-1).zfill(3)
    path = Path(UPLOAD_FILE_PATH, identifier)
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = Path(path, f'{identifier}_{current}')
    if not os.path.exists(file_name):
        async with aiofiles.open(file_name, 'wb') as f:
            await f.write(await file.read())

    if current == total:
        await merge_chunks(identifier, name)

    return {"code": 200, "data": {
        'chunk': f'{identifier}_{current}'}}




async def merge_chunks(identifier, name):

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

    # 上传完成后，更新文件信息
    await set_mode_datasource(ModeDataSourceRequest(
        mode = conf.current_mode,
        data_source_type = "video_file",
        data_source = output_file
    ))



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
