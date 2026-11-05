"""Inspect a self-contained RaceLink GLB without loading any geometry or third-party code."""
from collections import Counter
import json
from pathlib import Path
import struct
import sys

def inventory(path):
    p=Path(path)
    with p.open("rb") as f:
        magic,version,total=struct.unpack("<4sII",f.read(12))
        if magic!=b"glTF" or version!=2 or total!=p.stat().st_size:
            raise ValueError("Invalid GLB v2 header")
        size,kind=struct.unpack("<I4s",f.read(8))
        if kind!=b"JSON" or size>8_000_000 or size>total-20: raise ValueError("Invalid JSON chunk")
        d=json.loads(f.read(size))
    if any("uri" in x for k in ("buffers","images") for x in d.get(k,[])):
        raise ValueError("Inspect external resources separately")
    # Quantization can insert a mesh node below a parent carrying the CAD identity.
    scene=d["scenes"][d.get("scene",0)]["nodes"]
    stack=[(i,None) for i in scene]
    seen,owners,used=set(),{},[]
    while stack:
        i,owner=stack.pop()
        if type(i) is not int or i in seen or not 0<=i<len(d["nodes"]): raise ValueError("Invalid active node tree")
        seen.add(i)
        n=d["nodes"][i]; extras=n.get("extras") or {}
        if extras.get("family") and "solid" in extras:
            owner=extras["solid"]
            if owner in owners: raise ValueError("Duplicate source solid identity")
            owners[owner]=extras["family"]
        if "mesh" in n:
            if type(n["mesh"]) is not int or not 0<=n["mesh"]<len(d["meshes"]): raise ValueError("Unknown mesh reference")
            used.append(owner)
        stack.extend((j,owner) for j in n.get("children",[]))
    identified={owner for owner in used if owner is not None}
    if identified!=set(owners): raise ValueError("Empty source solid identity")
    return {"mesh_instances":len(used),"classified_solids":len(identified),
            "unclassified_instances":used.count(None),"families":dict(sorted(Counter(owners.values()).items()))}

if __name__=="__main__":
    print(json.dumps(inventory(sys.argv[1]),ensure_ascii=False,indent=2))
