from pydantic import BaseModel

class GetMediaPathParams(BaseModel):
    id_post: int
    channel: str