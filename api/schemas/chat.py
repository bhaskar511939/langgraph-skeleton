from pydantic import BaseModel, field_validator


class AskRequest(BaseModel):
    query:   str
    user_id: str        = "default"
    model:   str | None = None

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query cannot be empty")
        return v.strip()
