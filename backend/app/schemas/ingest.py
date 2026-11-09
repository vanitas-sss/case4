from datetime import datetime

from pydantic import BaseModel, Field


class HostIn(BaseModel):
    name: str
    ip: str | None = None
    status: str | None = None
    cpu_percent: float | None = Field(default=None, ge=0, le=100)
    memory_percent: float | None = Field(default=None, ge=0, le=100)
    disk_percent: float | None = Field(default=None, ge=0, le=100)
    net_rx_bytes: int | None = Field(default=None, ge=0)
    net_tx_bytes: int | None = Field(default=None, ge=0)


class ContainerIn(BaseModel):
    id: str
    name: str
    image: str | None = None
    status: str = "unknown"
    ip: str | None = None
    networks: list[str] = Field(default_factory=list)


class NodeIn(BaseModel):
    id: str
    label: str | None = None
    type: str


class LinkIn(BaseModel):
    source: str
    target: str
    type: str  
    load: float | None = Field(default=None, ge=0, le=100)


class NetworkIn(BaseModel):
    nodes: list[NodeIn] = Field(default_factory=list)
    links: list[LinkIn] = Field(default_factory=list)


class ReportIn(BaseModel):
    schema_version: str | None = None
    source_id: str
    timestamp: datetime
    host: HostIn
    containers: list[ContainerIn] = Field(default_factory=list)
    network: NetworkIn | None = None
