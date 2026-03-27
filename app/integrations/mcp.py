from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    name: str
    transport: str = "stdio"
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)


class MCPToolDescriptor(BaseModel):
    server_name: str
    tool_name: str
    description: str
    input_schema: dict = Field(default_factory=dict)

