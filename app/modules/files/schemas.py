from pydantic import BaseModel


class FileCreate(BaseModel):
    workspace_id: str
    channel_id: str
    message_id: str | None = None
    filename: str
    filepath: str
    filetype: str
    size: int
    uploader_id: str


class FileCreateRead(BaseModel):
    file_id: str


class FileUpdate(BaseModel):
    workspace_id: str | None = None
    channel_id: str | None = None
    message_id: str | None = None
