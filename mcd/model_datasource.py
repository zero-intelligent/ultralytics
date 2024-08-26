from pydantic import BaseModel, Field

class ModeDataSource(BaseModel):
    mode: str = Field(default="huiji_detect", enum=["huiji_detect", "person_detect"])
    data_source_type: str = Field(default="camera", enum=["camera", "video_file"])
    data_source: str = Field(..., min_length=1, description="数据源不能为空")