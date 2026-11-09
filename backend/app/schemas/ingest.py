from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class HostIn(InputModel):
    name: str = Field(min_length=1, max_length=255)
    ip: str | None = Field(default=None, max_length=64)
    status: str | None = Field(default=None, min_length=1, max_length=32)
    cpu_percent: float | None = Field(default=None, ge=0, le=100)
    memory_percent: float | None = Field(default=None, ge=0, le=100)
    disk_percent: float | None = Field(default=None, ge=0, le=100)
    net_rx_bytes: int | None = Field(default=None, ge=0)
    net_tx_bytes: int | None = Field(default=None, ge=0)


class ContainerIn(InputModel):
    id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    image: str | None = Field(default=None, max_length=512)
    status: str | None = Field(default=None, min_length=1, max_length=64)
    ip: str | None = Field(default=None, max_length=64)
    networks: list[Annotated[str, Field(min_length=1, max_length=255)]] | None = None


class NodeIn(InputModel):
    id: str = Field(min_length=1, max_length=255)
    label: str | None = Field(default=None, max_length=255)
    type: str = Field(min_length=1, max_length=32)


class LinkIn(InputModel):
    source: str = Field(min_length=1, max_length=255)
    target: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=32)
    load: float | None = Field(default=None, ge=0, le=100)


class NetworkIn(InputModel):
    nodes: list[NodeIn] = Field(default_factory=list)
    links: list[LinkIn] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_topology(self):
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Идентификаторы узлов в топологии должны быть уникальными")

        known_node_ids = set(node_ids)
        for link in self.links:
            if link.source not in known_node_ids or link.target not in known_node_ids:
                raise ValueError(
                    f"Связь {link.source!r} -> {link.target!r} "
                    "ссылается на отсутствующий узел"
                )

        link_keys = [(link.source, link.target, link.type) for link in self.links]
        if len(link_keys) != len(set(link_keys)):
            raise ValueError(
                "Связи с одинаковыми концами и типом не должны повторяться"
            )

        return self


class ReportIn(InputModel):
    schema_version: str | None = Field(default=None, max_length=32)
    source_id: str = Field(min_length=1, max_length=255)
    timestamp: datetime
    host: HostIn
    containers: list[ContainerIn] = Field(default_factory=list)
    network: NetworkIn | None = None

    @model_validator(mode="after")
    def validate_container_ids(self):
        container_ids = [container.id for container in self.containers]
        if len(container_ids) != len(set(container_ids)):
            raise ValueError(
                "Идентификаторы контейнеров в отчёте должны быть уникальными"
            )
        return self
