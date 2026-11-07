from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HostIn(BaseModel):
    """Сервер и его метрики."""

    name: str
    ip: Optional[str] = None
    status: Optional[str] = None  
    cpu_percent: Optional[float] = Field(default=None, ge=0, le=100)
    memory_percent: Optional[float] = Field(default=None, ge=0, le=100)
    disk_percent: Optional[float] = Field(default=None, ge=0, le=100)
    net_rx_bytes: Optional[int] = Field(default=None, ge=0)
    net_tx_bytes: Optional[int] = Field(default=None, ge=0)


class ContainerIn(BaseModel):
    id: str
    name: str
    image: Optional[str] = None
    status: str = "unknown"  
    ip: Optional[str] = None
    networks: list[str] = []


class NodeIn(BaseModel):
    id: str
    label: Optional[str] = None
    type: str


class LinkIn(BaseModel):
    source: str
    target: str
    type: str  # host | network | traffic
    load: Optional[float] = Field(default=None, ge=0, le=100)


class NetworkIn(BaseModel):
    nodes: list[NodeIn] = []
    links: list[LinkIn] = []


class ReportIn(BaseModel):
    schema_version: Optional[str] = None
    source_id: str
    timestamp: datetime
    host: HostIn
    containers: list[ContainerIn] = []
    network: Optional[NetworkIn] = None
