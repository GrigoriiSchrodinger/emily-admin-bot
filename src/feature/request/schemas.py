from pydantic import BaseModel

class GetMediaPathParams(BaseModel):
    id_post: int
    channel: str

class SendPost(BaseModel):
    channel: str
    text: str
    id_post: int


class DetailByChannelIdPost(BaseModel):
    channel: str
    id_post: int


class DetailByChannelIdPostResponse(BaseModel):
    content: str
    channel: str
    id_post: int
    outlinks: list[str]
