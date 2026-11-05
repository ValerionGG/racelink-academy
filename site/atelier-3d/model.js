import {
  ACESFilmicToneMapping, Scene, OrthographicCamera, WebGLRenderer, Box3, Vector3,
  HemisphereLight, DirectionalLight, Spherical, GLTFLoader, OrbitControls, MeshoptDecoder
} from './engine.mjs';

const directions = {
  perspective: [-3.1, 3.05, -5.5],
  side: [0, 0, -1],
  top: [0, 1, -.001]
};
const explodedOffset = {
  chassis:[0,0,0], habitacle:[0,.62,0], berceau:[.65,.22,0],
  impact:[0,0,0], roues:[0,0,-.9], suspension:[0,.13,-.44],
  freinage:[-.4,.5,.3], fixations:[0,.93,.1]
};

export async function createWorkshop(container, accessibleName, onLoss) {
  const canvas = document.createElement('canvas');
  canvas.tabIndex = 0;
  canvas.setAttribute('aria-label', accessibleName);
  const renderer = new WebGLRenderer({canvas, alpha:true, antialias:true, powerPreference:'low-power'});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.toneMapping = ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.16;
  let model;
  try {
    const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
    model = (await loader.loadAsync(new URL('./sgt01.glb', import.meta.url).href)).scene;
  } catch (error) {
    renderer.dispose();
    throw error;
  }
  const scene = new Scene();
  scene.add(model, new HemisphereLight(0xf5f8ff, 0xb5babf, 2.3));
  for (const [x,y,z,power] of [[-3,6,-4,3.3],[4,3,2,1.65]]) {
    const light = new DirectionalLight(0xffffff,power);
    light.position.set(x,y,z);
    scene.add(light);
  }
  const solids = [];
  model.updateMatrixWorld(true);
  model.traverse(object => {
    if (!Number.isInteger(object.userData.solid)) return;
    const bounds = new Box3().setFromObject(object);
    solids.push({object, group:object.userData.family, index:object.userData.solid,
      initial:object.position.clone(), center:bounds.getCenter(new Vector3()), bounds});
  });
  if (solids.length!==271) {
    renderer.dispose();
    throw new Error('Incomplete SGT01 assembly');
  }
  const camera = new OrthographicCamera(-2,2,1,-1,.01,100);
  container.append(canvas);
  const controls = new OrbitControls(camera,canvas);
  controls.enablePan = false;
  controls.enableDamping = false;
  controls.minZoom = .35;
  controls.maxZoom = 16;
  let pickedFamily='all', pickedPiece=null, separated=false;
  let currentBounds = new Box3(), frame=0, disposed=false;

  function render() {
    if (frame || disposed) return;
    frame=requestAnimationFrame(() => {frame=0; if (!disposed) renderer.render(scene,camera);});
  }
  controls.addEventListener('change',render);

  function frameBounds(direction=null) {
    if (currentBounds.isEmpty()) return;
    const center=currentBounds.getCenter(new Vector3());
    const eye=direction ? new Vector3(...direction).normalize() :
      camera.position.clone().sub(controls.target).normalize();
    if (eye.lengthSq()<.1) eye.set(...directions.perspective).normalize();
    const size=currentBounds.getSize(new Vector3()).length() || .01;
    controls.target.copy(center);
    camera.position.copy(center).addScaledVector(eye,Math.max(2,size*2));
    camera.lookAt(center);
    camera.updateMatrixWorld(true);
    const right=new Vector3().setFromMatrixColumn(camera.matrixWorld,0);
    const up=new Vector3().setFromMatrixColumn(camera.matrixWorld,1);
    const projection=new Box3().makeEmpty();
    // Use the individual solid boxes. A bounding box around an oblique assembly can
    // include a great deal of empty space, especially when a small part is isolated.
    for (const {object,bounds,initial} of solids) {
      if (!object.visible) continue;
      const delta=object.position.clone().sub(initial);
      for (const x of [bounds.min.x,bounds.max.x])
        for (const y of [bounds.min.y,bounds.max.y])
          for (const z of [bounds.min.z,bounds.max.z]) {
            const p=new Vector3(x,y,z).add(delta).sub(center);
            projection.expandByPoint(new Vector3(p.dot(right),p.dot(up),0));
          }
    }
    const mid=projection.getCenter(new Vector3());
    camera.position.addScaledVector(right,mid.x).addScaledVector(up,mid.y);
    controls.target.addScaledVector(right,mid.x).addScaledVector(up,mid.y);
    const {width,height}=container.getBoundingClientRect();
    const aspect=width/Math.max(1,height);
    const extent=projection.getSize(new Vector3());
    const half=Math.max(extent.y/2,extent.x/(2*aspect),.002)*1.22;
    camera.left=-half*aspect;
    camera.right=half*aspect;
    camera.top=half;
    camera.bottom=-half;
    camera.zoom=1;
    camera.updateProjectionMatrix();
    controls.update();
    render();
  }
  function apply() {
    const shown=solids.filter(({group,index}) => (pickedFamily==='all' || group===pickedFamily) && (pickedPiece===null || pickedPiece===index));
    const initialBox=new Box3();
    shown.forEach(({bounds})=>initialBox.union(bounds));
    const center=initialBox.getCenter(new Vector3());
    currentBounds.makeEmpty();
    for (const solid of solids) {
      const {object,initial,group,index}=solid;
      object.visible=(pickedFamily==='all'||group===pickedFamily) && (pickedPiece===null||index===pickedPiece);
      object.position.copy(initial);
      if (!object.visible) continue;
      const shift=new Vector3();
      if (separated && pickedPiece===null) {
        if (pickedFamily==='all') {
          shift.fromArray(explodedOffset[group]);
          if (group==='impact') shift.x=solid.center.x < 1 ? -.55 : .55;
        } else {
          shift.copy(solid.center).sub(center).multiplyScalar(.55);
        }
      }
      object.position.add(shift);
      currentBounds.union(solid.bounds.clone().translate(shift));
    }
    frameBounds();
  }
  function zoom(factor) {
    camera.zoom=Math.max(controls.minZoom,Math.min(controls.maxZoom,camera.zoom*factor));
    camera.updateProjectionMatrix();
    render();
  }
  function keydown(event) {
    const step=.12;
    if (event.key==='+' || event.key==='=') {event.preventDefault();zoom(1.22);return;}
    if (event.key==='-') {event.preventDefault();zoom(1/1.22);return;}
    if (!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home'].includes(event.key)) return;
    event.preventDefault();
    if (event.key==='Home') {frameBounds(directions.perspective);return;}
    const offset=camera.position.clone().sub(controls.target);
    const orbit=new Spherical().setFromVector3(offset);
    if (event.key==='ArrowLeft') orbit.theta-=step;
    if (event.key==='ArrowRight') orbit.theta+=step;
    if (event.key==='ArrowUp') orbit.phi-=step;
    if (event.key==='ArrowDown') orbit.phi+=step;
    orbit.makeSafe();
    camera.position.copy(controls.target).add(offset.setFromSpherical(orbit));
    controls.update();
    render();
  }
  canvas.addEventListener('keydown',keydown);
  function loss(event) {event.preventDefault();onLoss();}
  canvas.addEventListener('webglcontextlost',loss);
  const observer=new ResizeObserver(() => {
    const {width,height}=container.getBoundingClientRect();
    renderer.setSize(Math.max(1,width),Math.max(1,height),false);
    frameBounds();
  });
  observer.observe(container);
  apply();
  frameBounds(directions.perspective);
  return {
    select(family,piece,exploded=false) {pickedFamily=family;pickedPiece=piece;separated=exploded;apply();},
    angle(key) {frameBounds(directions[key] || directions.perspective);},
    fit() {frameBounds();},
    focus() {canvas.focus({preventScroll:true});},
    zoom,
    dispose() {
      disposed=true;cancelAnimationFrame(frame);observer.disconnect();
      canvas.removeEventListener('webglcontextlost',loss);
      canvas.removeEventListener('keydown',keydown);
      controls.dispose();
      model.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose();}});
      renderer.dispose();canvas.remove();
    }
  };
}
