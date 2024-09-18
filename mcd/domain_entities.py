from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

    
class Mode(Enum):
    HUIJI = "huiji_detect"
    PERSON = "person_detect"

class DataSourceType(Enum):
    CAMERA = "camera"
    VIDEO_FILE = "video_file"
    
class RunningState(Enum):
    READY = "ready"
    LOADING = "loading"
    RUNNING = "running"
    FINISHED = "finished"
    
    
class ModeDataSource(BaseModel):
    mode: Mode = Field(default=Mode.HUIJI)
    data_source_type: DataSourceType = Field(default=DataSourceType.CAMERA)
    data_source: str = Field(..., min_length=1, description="数据源不能为空")
    
    class Config:
        use_enum_values = True  # This ensures that enum values are serialized as their underlying values

    
class TancanResult(BaseModel):
    id:int = Field(default=0, description="id必须>0")
    name:Optional[str] = Field(default="",description="名称不能为空")
    count:Optional[int] = Field(default=None, description="食物数量")
    real_count:Optional[int] = Field(default=None,ge=0, description="实际数量")
    lack_item:Optional[bool] = Field(default=None, description="是否欠缺食物")
    lack_count:Optional[bool] = Field(default=None, description="食物数量是否缺少")
    is_in_taocan:bool = Field(default=True, description="是否在套餐内")
    
    
