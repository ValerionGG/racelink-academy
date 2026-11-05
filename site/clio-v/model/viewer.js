const views = Object.freeze({
  'three-quarter': { dir: [1.06,.45,1.36], width:4.85, height:2.28 },
  front: { dir:[0,.014,1], width:2.68, height:2.04 },
  rear: { dir:[0,.014,-1], width:2.68, height:2.04 },
  left: { dir:[1,.003,0], width:4.68, height:2.03 },
  right: { dir:[-1,.003,0], width:4.68, height:2.03 },
  top: { dir:[0,1,.0001], width:2.60, height:4.62 },
  cabin: { dir:[.68,1.10,-.70], width:3.51, height:2.78 },
  cockpit: { interior:true }
});
const labels={ 'three-quarter':'Trois quarts avant',front:'Face avant',rear:'Arrière',left:'Profil gauche',right:'Profil droit',top:'Vue de dessus',cabin:'Habitacle ouvert',cockpit:'Poste de conduite'};
const asset=name=>new URL(name,import.meta.url).href;

export async function mountClioViewer(container, {onChange=()=>{},view='three-quarter',theme='light', labels:customLabels={}, canvasLabel='Vue 3D interactive. Flèches pour tourner, plus et moins pour zoomer.'}={}) {
  let active=Object.hasOwn(views,view)?view:'three-quarter';
  let ortho,perspective,cam,renderer,controls,scene,model,env,observer,controller,contextLost;
  let mode='poster',disposed=false,raf=0,desiredTheme=theme;
  const poster = document.createElement('img');
  poster.draggable=false;
  Object.assign(poster.style,{display:'block',width:'100%',height:'100%',objectFit:'contain'});
  function updatePoster(){poster.src=asset(active+'.webp');poster.alt=customLabels[active]||labels[active];}
  updatePoster();container.replaceChildren(poster);
  const emit=()=>{container.dataset.viewerMode=mode;container.dataset.viewerView=active;onChange({view:active,mode});};
  const paint=()=>{if(!raf && mode==='webgl')raf=requestAnimationFrame(()=>{raf=0;if(!disposed&&mode==='webgl')renderer.render(scene,cam);});};
  const rebuildProjection=()=>{
    const w=Math.max(1,container.clientWidth),h=Math.max(1,container.clientHeight),aspect=w/h;
    if(!renderer)return;
    renderer.setSize(w,h,false);
    if(active==='cockpit'){perspective.aspect=aspect;perspective.updateProjectionMatrix();}
    else{const v=views[active];const hSpan=Math.max(v.height,v.width/aspect);ortho.left=-hSpan*aspect/2;ortho.right=-ortho.left;ortho.top=hSpan/2;ortho.bottom=-ortho.top;ortho.updateProjectionMatrix();}
    paint();
  };
  const setTheme=value=>{desiredTheme=value==='dark'?'dark':'light';if(scene){scene.environmentIntensity=desiredTheme==='dark'?1.2:1;paint();}};
  function setView(id){
    if(!Object.hasOwn(views,id)||disposed)return;
    active=id;
    if(mode!=='webgl'){updatePoster();emit();return;}
    const open=id==='cabin',cockpit=id==='cockpit';
    for(const group of ['pavillon','vitrages','montants','details']){
      const item=model.getObjectByName(group);if(item)item.visible=!open && (group!=='vitrages'||!cockpit);
    }
    model.getObjectByName('Ombre').visible=!cockpit;
    cam=cockpit?perspective:ortho;
    controls.object=cam;
    if(cockpit){
      // OrbitControls rotates about a point just ahead of the driver's eyes.
      // A short radius gives a seated look-around with no collision or vehicle walking.
      const eye=[.323,1.12,-.083],target=[.249,1.044,.139];
      cam.position.set(...eye);controls.target.set(...target);cam.fov=73;cam.zoom=1;
      controls.minDistance=.21;controls.maxDistance=.29;controls.minPolarAngle=.25;controls.maxPolarAngle=Math.PI*.86;
      controls.enablePan=false;controls.enableZoom=false;
    } else {
      const v=views[id],focus=open?[0,.62,-.13]:[0,.64,0];
      cam.position.set(...v.dir).normalize().multiplyScalar(6.6);
      controls.target.set(...focus);cam.position.add(controls.target);ortho.zoom=1;
      controls.minPolarAngle=.0001;controls.maxPolarAngle=Math.PI*.491;controls.minDistance=.15;controls.maxDistance=15;
      controls.minZoom=.72;controls.maxZoom=3.2;controls.enableZoom=true;controls.enablePan=false;
    }
    rebuildProjection();controls.update();paint();emit();
  }
  function orbit(degrees=15,vertical=0) {
    if(mode!=='webgl'||disposed)return;
    const v=cam.position.clone().sub(controls.target);let radius=v.length(),az=Math.atan2(v.x,v.z)+degrees*Math.PI/180;
    const polar=Math.max(controls.minPolarAngle,Math.min(controls.maxPolarAngle,Math.acos(Math.min(1,v.y/radius))+vertical*Math.PI/180));
    v.set(Math.sin(polar)*Math.sin(az),Math.cos(polar),Math.sin(polar)*Math.cos(az)).multiplyScalar(radius);
    cam.position.copy(controls.target).add(v);controls.update();paint();
  }
  function zoom(factor=1.2){
    if(mode!=='webgl'||disposed||!Number.isFinite(factor)||factor<=0)return;
    if(active==='cockpit')cam.fov=Math.max(44,Math.min(91,cam.fov/factor));
    else cam.zoom=Math.max(controls.minZoom,Math.min(controls.maxZoom,cam.zoom*factor));
    cam.updateProjectionMatrix();paint();
  }
  const reset=()=>setView(active);
  function releaseRender(){
    cancelAnimationFrame(raf);raf=0;observer?.disconnect();controller?.abort();controls?.dispose();
    model?.traverse(obj=>{if(obj.geometry)obj.geometry.dispose();if(obj.material){for(const m of [obj.material].flat()){m.map?.dispose();m.dispose();}}});
    env?.dispose();renderer?.dispose();renderer?.domElement.remove();renderer=null;
  }
  const dispose=()=>{if(disposed)return;disposed=true;releaseRender();poster.remove();};
  function fallback(){releaseRender();mode='poster';updatePoster();container.replaceChildren(poster);emit();}
  try{
    const T=await import('../../atelier-3d/engine.mjs');
    if(disposed)return;
    renderer=new T.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});
    renderer.setClearColor(0,0);renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));
    renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.13;
    const loader=new T.GLTFLoader();loader.setMeshoptDecoder(T.MeshoptDecoder);
    const gltf=await loader.loadAsync(asset('clio-v.glb'));
    model=gltf.scene;scene=new T.Scene();scene.add(model);
    env=await gltf.parser.getDependency('texture',gltf.parser.json.extras.studioTexture);
    env.mapping=303;env.colorSpace='srgb';env.needsUpdate=true;scene.environment=env;
    perspective=gltf.cameras[0];ortho=new T.OrthographicCamera(-2,2,1,-1,.01,50);cam=ortho;
    scene.add(new T.HemisphereLight(0xf3f7ff,0xe3ded5,1.05));
    for(const [position,color,intensity] of [[[2,5,3],0xfff4e3,2.05],[[-3,3,-3],0xcae0ff,1.38],[[2,1,-3],0xffffff,.65]]){
      const light=new T.DirectionalLight(color,intensity);light.position.set(...position);scene.add(light);
    }
    const canvas=renderer.domElement;Object.assign(canvas.style,{width:'100%',height:'100%',display:'block',touchAction:'none'});
    canvas.tabIndex=0;canvas.setAttribute('aria-label',canvasLabel);
    controls=new T.OrbitControls(cam,canvas);controls.enablePan=false;controls.enableDamping=false;controls.addEventListener('change',paint);
    controller=new AbortController();
    canvas.addEventListener('keydown',event=>{
      if(event.altKey||event.ctrlKey||event.metaKey)return;
      const actions={ArrowLeft:()=>orbit(-15),ArrowRight:()=>orbit(15),ArrowUp:()=>orbit(0,-9),ArrowDown:()=>orbit(0,9),'+':()=>zoom(1.15),'=':()=>zoom(1.15),'-':()=>zoom(1/1.15),Home:reset};
      if(actions[event.key]){event.preventDefault();actions[event.key]();}
    },{signal:controller.signal});
    contextLost=event=>{event.preventDefault();fallback();};
    canvas.addEventListener('webglcontextlost',contextLost,{once:true,signal:controller.signal});
    container.replaceChildren(canvas);mode='webgl';
    observer=new ResizeObserver(rebuildProjection);observer.observe(container);setTheme(desiredTheme);setView(active);
  }catch(error){fallback();}
  return {setView,setTheme,orbit,zoom,reset,dispose};
}
