import json
import os
import time
from fastapi import APIRouter, FastAPI, File, HTTPException, Request,Response, UploadFile, WebSocket, WebSocketDisconnect
from fastapi import Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from mcd.resp import ok
from mcd.logger import log
from mcd.camera import get_cameras
from mcd import conf,video_srv
from mcd.domain_entities import DataSourceType, ModeDataSource,Mode
from mcd.event import config_changed_event,result_frame_arrive_event


app = FastAPI()
router = APIRouter(prefix="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], //"http://pinda.cn","http://pinda.org.cn","http://127.0.0.1:8000","http://127.0.0.1:8001" 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@router.get("/demo_huiji")
async def demo(mode:Mode = Query(default=Mode.HUIJI)):
    video_srv.update_datasource(ModeDataSource(
        mode = Mode(mode),
        data_source_type = "camera",
        data_source = "0"
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

@router.get("/demo_person")
async def demo_person():
    return await demo(mode=Mode.PERSON)


@router.get("/config_sse")
async def get_config():
    async def config_stream():
        while True:
            await config_changed_event.wait()  # 等待新消息
            config_changed_event.clear()  # 清除事件，等待下次设置
            config = get_config()
            event = f"data: {json.dumps(config,ensure_ascii=False)}\n\n"
            log.info(f"SSE push event：{event}")
            yield event

    return StreamingResponse(config_stream(), media_type="text/event-stream")

@router.websocket("/config_ws")
async def websocket_endpoint(websocket: WebSocket):
    log.info("websocket_endpoint enter")
    await websocket.accept()
    log.info("websocket_endpoint accepted")
    try:
        while True:
            await config_changed_event.wait()  # 等待新消息
            config_changed_event.clear()  # 清除事件，等待下次设置
            config = get_config()
            log.info(f"websocket push json {config}")
            # data = await websocket.receive_text()
            await websocket.send_json(config)
            log.info("websocket pushed")
    except WebSocketDisconnect:
        log.error("Client disconnected")
        
        
        
        

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
        
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Example</title>
    </head>
    <body>
        <h1>WebSocket Example</h1>
        <button onclick="connectWebSocket()">Connect WebSocket</button>
        <button onclick="sendMessage()">Send Message</button>
        <ul id='messages'>
        </ul>
        <script>
            var websocket;
            function connectWebSocket() {
                websocket = new WebSocket("ws://8.140.49.13:6789/ws");
                websocket.onmessage = function(event) {
                    var messages = document.getElementById('messages');
                    var message = document.createElement('li');
                    var content = document.createTextNode(event.data);
                    message.appendChild(content);
                    messages.appendChild(message);
                };
            }
            function sendMessage() {
                websocket.send("Hello from client");
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)


def get_config():
    # assure enum type
    conf.current_mode =  Mode(conf.current_mode)
    
    config = {
        "mode": conf.current_mode.value,
        "running_state": video_srv.VideoState.running_state.value,
        "frame_rate": int(video_srv.VideoState.frame_rate),
        "camera_type": 0,
        "camera_local": conf.current_detect_config()["camera_source"],
        "camera_url": "",
        "data_type": conf.current_detect_config()['data_source_type'],
        "video_source": f"video_source_feed",
        "video_target": f"video_output_feed",
    }
    
    if conf.current_mode == Mode.HUIJI:
        result_state,results = video_srv.get_huiji_detect_items(video_srv.current_taocan_check_result)
        config['current_taocan_result'] = [r.model_dump() for r in results]
        config['total_taocan_result_state'] = result_state
        config["taocan_id"] = conf.current_detect_config()["current_taocan_id"]
    else:
        config['current_person_result'] =  video_srv.get_current_person_detect_result()
    return config

@router.get("/get_config")
async def config():
    data = get_config()
    log.info(f"get_config: {data}")
    return ok(data)


@router.get("/switch_mode")
async def switch_mode(mode:Mode = Query(default=Mode.HUIJI)):
    switch_ok = video_srv.swith_mode(mode)
    if switch_ok:
        return ok(msg=f"mode swit to {conf.current_mode}")
    else:
        return ok(msg=f"mode has been {conf.current_mode}")
    

@router.post("/mode_datasource")
async def set_mode_datasource(request: ModeDataSource):
    detect_config = conf.current_detect_config()
    if conf.current_mode == request.mode \
       and detect_config['data_source_type'] == request.data_source_type \
       and conf.data_source() == request.data_source:
        return ok(msg=f"mode_datasource same,no changed")
        
    video_srv.update_datasource(request)
    return ok(msg=f"mode_datasource changed to:{conf.current_mode}:{conf.current_detect_config()['data_source_type']}:{conf.data_source()}")

@router.get("/mode_datasource")
async def get_mode_datasource():
    return ok({
            "mode": conf.current_mode,
            "data_source_type": conf.current_detect_config()['data_source_type'],
            "data_source": conf.data_source()
        })

@router.get("/taocans")
async def get_taocans():
    return ok({
            "taocans": conf.huiji_detect_config["taocans"],
            "current_taocan_id": conf.huiji_detect_config["current_taocan_id"]
        })

@router.get("/switch_taocan")
async def switch_taocan(taocan_id:int = Query(ge=0, le=1)):
    if conf.huiji_detect_config["current_taocan_id"] == taocan_id:
        return ok(msg=f"taocan_id had {taocan_id}")
    conf.huiji_detect_config["current_taocan_id"] = taocan_id
    config_changed_event.set()
    # 此处需要将视频分析的结果和套餐的信息进行合并
    return ok(msg=f"switch success to {taocan_id}")


@router.get("/available_cameras")
async def get_available_cameras():
    return ok(data = {id:name for id,name in get_cameras()})

@router.get('/huiji_video_taocan_detect_result')
async def sync_huiji_video_events():
    if not video_srv.current_taocan_check_result:
        return ok(data = {},msg="当前没有检测结果")
    taocan_id = conf.huiji_detect_config['current_taocan_id']
    taocan =  conf.huiji_detect_config['taocan'][taocan_id]
    return ok({
            "taocan_id": taocan_id,
            "taocan_name":taocan['name'],
            "items": video_srv.get_detect_items(video_srv.current_taocan_check_result)
        })


@router.get('/video_source_feed')
async def video_source_feed():
    def queue_to_generator():
        while True:
            item = video_srv.video_frame_queue.get()
            # log.info('=====  sending source frame....')
            yield pub_and_pad(item)
            
    return StreamingResponse(queue_to_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

latest_frame = None

def pub_and_pad(r):
    global latest_frame
    latest_frame = r['tracked_frame']
    result_frame_arrive_event.set()  # 设置事件，通知订阅者
    return (b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + r['orig_frame'] + b'\r\n')


@router.get('/video_output_feed')
async def video_output_feed():
    # 从检测流中获取最新的输出结果侦
    async def get_latest_frame_generator():
        while True:
            await result_frame_arrive_event.wait()  # 等待新消息
            result_frame_arrive_event.clear()  # 清除事件，等待下次设置
            # log.info('=====  sending output frame....')
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
   
    return StreamingResponse(get_latest_frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")


@router.post('/single_upload')
async def single_upload_file(file: UploadFile = File(...)):
    try:
        # 读取文件内容
        file_content = await file.read()
        # 处理文件（例如，保存到磁盘）
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads",exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_content)
         # 上传完成后，更新文件信息
        video_srv.update_datasource(ModeDataSource(
            mode = Mode(conf.current_mode),
            data_source_type = DataSourceType.VIDEO_FILE,
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
    log.info(f"{request.method} {request.url}")
    start = time.time()
    response = await call_next(request)
    respons_text = response.json() if hasattr(response,'json') else ''
    log.info(f"{request.method} {request.url} response: {response.status_code} {respons_text},rts:{time.time()-start:.2f}s")
    return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    conf.load_config()
    video_srv.run_detect_loop()
    yield
    conf.save_config()

app.router.lifespan_context = lifespan
app.include_router(router)

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6789, log_level="info")

if __name__ == "__main__":
    main()
