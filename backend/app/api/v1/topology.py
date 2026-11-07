from typing import Optional

from fastapi import APIRouter

from app import stubs

router = APIRouter(tags=["topology"])


@router.get("/topology")
def get_topology(host_id: Optional[int] = None, type: Optional[str] = None):
    # TODO: заменить на topology_service.build_graph(db, filters)
    nodes = stubs.TOPOLOGY["nodes"]
    links = stubs.TOPOLOGY["links"]
    if type:
        nodes = [n for n in nodes if n["type"] == type]
        ids = {n["id"] for n in nodes}
        links = [l for l in links if l["source"] in ids and l["target"] in ids]
    return {"nodes": nodes, "links": links, "generated_at": stubs.TOPOLOGY["generated_at"]}
