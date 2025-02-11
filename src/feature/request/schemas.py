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
    new_content: str | None

class DetailBySeed(BaseModel):
    seed: str

class DetailBySeedResponse(BaseModel):
    content: str
    channel: str
    id_post: int
    outlinks: list[str]
    new_content: str | None
    media_resolution: bool

class ToggleMediaResolution(BaseModel):
    seed: str

class ToggleMediaResolutionResponse(BaseModel):
    media_resolution: bool
