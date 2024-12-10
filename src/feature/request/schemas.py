from pydantic import BaseModel

class GetMediaPathParams(BaseModel):
    id_post: int
    channel: str

class SendPost(BaseModel):
    channel: str
    text: str
    id_post: int