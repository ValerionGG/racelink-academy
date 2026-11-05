"""Build the compact GLB, including an original studio reflection and contact shadow."""
import io
import json
import struct
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image
project = Path(__file__).resolve().parent
here = project / "build"
(here / "deliver").mkdir(parents=True, exist_ok=True)
packed = here / "clio-packed.glb"
subprocess.run(["node", str(project/"node_modules/gltfpack/cli.js"), "-i", str(here/"clio-raw.glb"), "-o", str(packed), "-cc", "-kv", "-kn", "-km"], check=True)
buf = packed.read_bytes()
n, = struct.unpack_from("<I", buf, 12)
doc = json.loads(buf[20:20+n])
data = bytearray(buf[28+n:])
def image_blob(im, name):
    stream = io.BytesIO()
    im.save(stream,format="PNG",optimize=True)
    content = stream.getvalue()
    while len(data)%4: data.append(0)
    idx = len(doc["bufferViews"])
    doc["bufferViews"].append({"buffer":0,"byteOffset":len(data),"byteLength":len(content)})
    data.extend(content)
    images = doc.setdefault("images",[])
    images.append({"name":name,"bufferView":idx,"mimeType":"image/png"})
    textures = doc.setdefault("textures",[])
    textures.append({"source":len(images)-1})
    return len(textures)-1
x,y=np.meshgrid(np.linspace(-1,1,360),np.linspace(-1,1,640))
a= .33*np.exp(-((x/.73)**4+(y/.71)**4)*2)+.15*np.exp(-((x/.74)**2+(y/.75)**2)*2)
for xc in (-.53,.53):
    for zc in (-.42,.48):
        a+=.30*np.exp(-((x-xc)/.12)**2-((y-zc)/.06)**2)
shadow=np.zeros((640,360,4),np.uint8)
shadow[:,:,:3]=[19,25,31]
shadow[:,:,3]=(np.clip(a,0,.82)*255).astype(np.uint8)
st=image_blob(Image.fromarray(shadow),"Ombre diffuse")
mat=next(m for m in doc['materials'] if m['name']=='ombre')
mat['pbrMetallicRoughness']['baseColorTexture']={'index':st}
mat['alphaMode']='BLEND'
# Rectangular studio reflectors on an equirectangular panorama.
u,v=np.meshgrid(np.linspace(0,1,512),np.linspace(0,1,256))
lum= .14+.14*np.exp(-((v-.54)/.18)**2)+.30*(1-v)
for cx,cy,rx,ry,strength in [(.16,.24,.16,.055,.9),(.64,.36,.19,.025,.88),(.91,.47,.048,.20,.73),(.4,.43,.08,.12,.57)]:
    dx=np.minimum(abs(u-cx),1-abs(u-cx))
    lum+=strength*np.exp(-((dx/rx)**6+((v-cy)/ry)**6))
rgb=np.uint8(np.clip(lum[:,:,None]*np.array([.96,.99,1.]),0,1)*255)
et=image_blob(Image.fromarray(rgb),"Réflexions de studio")
doc.setdefault('extras',{})['studioTexture']=et
doc['asset']['copyright']='RaceLink Academy. Reconstitution géométrique pédagogique de la Clio V phase 2. Dessin indépendant.'
doc['buffers'][0]['byteLength']=len(data)
j=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode()
j+=b' '*(-len(j)%4);data.extend(b'\0'*(-len(data)%4))
result=struct.pack('<4sII',b'glTF',2,28+len(j)+len(data))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(data),b'BIN\0')+data
(here/'deliver/clio-v.glb').write_bytes(result)
print('Mesh file bytes',len(result),'primitives',sum(len(m['primitives']) for m in doc['meshes']),'cameras',len(doc.get('cameras',[])))
