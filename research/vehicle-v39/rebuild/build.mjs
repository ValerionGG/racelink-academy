import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as T from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)),'build');
await fs.mkdir(root,{recursive:true});
const scene = new T.Scene();
const bank = new Map();
const groups = new Map();
const colors = {};
function paint(key,hex,metal=0,rough=.49,alpha=1) {
  colors[key]=new T.MeshStandardMaterial({name:key,color:hex,metalness:metal,roughness:rough,side:T.DoubleSide,transparent:alpha<1,opacity:alpha});
}
paint('bleu',0x235993,.57,.23); paint('noir-laque',0x212932,.32,.21);
paint('bord',0x1b2228,.08,.49); paint('pneu',0x22252b,.02,.83);
paint('gomme',0x14181c,.01,.85); paint('acier',0x818a94,.74,.26);
paint('alu',0xc9d1d8,.6,.25); paint('chrome-fume',0x76858f,.5,.32);
paint('verre',0x354953,.2,.12,.81); paint('feu',0xc72e38,.26,.25);
paint('diode',0xe5f5ff,.13,.12); paint('cuir',0x282d36,.02,.69);
paint('textile',0x545d68,.03,.88); paint('garniture',0x414b55,.06,.71);
paint('ecran',0x152e38,.15,.3); paint('trait-ecran',0x72cbe6,.05,.48);
paint('surpiqure',0x6694b4,0,.7); paint('verre-feu',0x393d47,.27,.24);
colors.diode.emissive.setHex(0xa0c4de); colors.diode.emissiveIntensity=.27;
const {sin,cos,PI,sqrt,abs,max,min}=Math;
const V=(x,y,z)=>new T.Vector3(x,y,z);
function add(gn,mat,geom,pos=[0,0,0],rot=[0,0,0],scale=[1,1,1]) {
  const g=geom.index ? geom.toNonIndexed():geom;
  for(const key of Object.keys(g.attributes)) if(!['position','normal'].includes(key))g.deleteAttribute(key);
  if(!g.attributes.normal)g.computeVertexNormals();
  g.applyMatrix4(new T.Matrix4().compose(V(...pos),new T.Quaternion().setFromEuler(new T.Euler(...rot)),V(...scale)));
  if(gn==='carrosserie'){
    const attr=g.attributes.position;
    for(let i=0;i<attr.count;i++){
      const z=attr.getZ(i),x=attr.getX(i),end=Math.max(0,Math.min(1,(Math.abs(z)-1.62)/.406));
      const retreat=.234*(Math.abs(x)/.85)**3*end*end;
      attr.setZ(i,z-Math.sign(z)*retreat);
    }
  }
  const key=gn+'|'+mat;
  if(!bank.has(key))bank.set(key,[]);
  bank.get(key).push(g);
}
function patch(gn,mat,fn,n=18,m=6) {
  const p=[],idx=[];
  for(let i=0;i<=n;i++)for(let j=0;j<=m;j++)p.push(...fn(i/n,j/m));
  for(let i=0;i<n;i++)for(let j=0;j<m;j++){let a=i*(m+1)+j,b=a+m+1;idx.push(a,b,b+1,a,b+1,a+1);}
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p,3));g.setIndex(idx);g.computeVertexNormals();add(gn,mat,g);
}
function edge(gn,mat,points,r=.006,steps=24,smooth=true) {
  const coords=points.map(p=>V(...p));const curve=smooth?new T.CatmullRomCurve3(coords):new T.CurvePath();
  if(!smooth)for(let i=1;i<coords.length;i++)curve.add(new T.LineCurve3(coords[i-1],coords[i]));
  add(gn,mat,new T.TubeGeometry(curve,steps,r,5,false));
}
function box(gn,mat,x,y,z,w,h,d,r=.01,rot=[0,0,0]) {
 add(gn,mat,new RoundedBoxGeometry(w,h,d,2,Math.min(r,w*.49,h*.49,d*.49)),[x,y,z],rot);
}
function orb(gn,mat,x,y,z,a,b,c,rot=[0,0,0]) {add(gn,mat,new T.SphereGeometry(1,20,12),[x,y,z],rot,[a,b,c]);}
function panel(gn,mat,points){const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(points.flat(),3));const ids=[];for(let i=1;i<points.length-1;i++)ids.push(0,i,i+1);g.setIndex(ids);g.computeVertexNormals();add(gn,mat,g);}
function at(z,marks){
 if(z<=marks[0][0])return marks[0][1];
 let i=1;while(i<marks.length-1 && z>marks[i][0])i++;
 const [a,l]=marks[i-1],[b,h]=marks[i],t=min(1,(z-a)/(b-a)),prior=marks[max(0,i-2)],next=marks[min(i+1,marks.length-1)];
 const slopeL=(h-prior[1])/(b-prior[0]), slopeH=(next[1]-l)/(next[0]-a);
 return (2*t**3-3*t*t+1)*l + (t**3-2*t*t+t)*(b-a)*slopeL +(-2*t**3+3*t*t)*h +(t**3-t*t)*(b-a)*slopeH;
}
const width=z=>at(z,[[-2.026,.791],[-1.97,.812],[-1.82,.837],[-1.55,.855],[-1.25,.861],[-.86,.853],[-.05,.849],[.66,.851],[1.15,.861],[1.53,.848],[1.78,.847],[1.96,.836],[2.026,.812]]);
const belt=z=>at(z,[[-2.026,.823],[-1.87,.962],[-1.64,1.035],[-1.28,1.024],[-.7,.980],[.15,.936],[.84,.907],[1.32,.866],[1.78,.810],[2.026,.734]]);
const wheelZ=[-1.3895,1.1935];
function base(z){let y=at(z,[[-2.026,.324],[-1.84,.265],[-.9,.212],[.9,.212],[1.76,.245],[2.026,.245]]);for(const wz of wheelZ){let d=abs(z-wz);if(d<.327)y=max(y,.306+sqrt(.327**2-d*d));}return y;}
function sideX(z,y) {const u=max(0,min(1,(y-.22)/(belt(z)-.22)));return width(z)-.047*(1-u)**3-.018*Math.exp(-((u-.48)**2)/.015)+.008*Math.exp(-((u-.8)**2)/.009)-.026*u**8;}
const lerp=(a,b,t)=>a+(b-a)*t;
for(const s of [-1,1]){
  patch('carrosserie','bleu',(u,v)=>{let z=lerp(-2.026,2.026,u),y=lerp(base(z),belt(z),v);return [s*sideX(z,y),y,z];},216,14);
  // Return the panel inward to the wheel wells. The opening itself stays empty.
  patch('carrosserie','bord',(u,v)=>{let z=lerp(-2.026,2.026,u),y=base(z);return [s*(sideX(z,y)-.076*v),y-.006*v,z];},216,1);
  for(const wz of wheelZ){
    const line=[];
    for(let j=0;j<=28;j++){let a=PI*j/28, z=wz+.332*cos(a), y=.308+.333*sin(a);line.push([s*(sideX(z,y)+.001),y,z]);}
    edge('carrosserie','bleu',line,.008,35);
  }
  const stripe=[[.232,-.991],[.224,-.84],[.224,.71],[.236,.87]];
  edge('carrosserie','noir-laque',stripe.map(([y,z])=>[s*sideX(z,y),y,z]),.018);
  const press=[[.445,-1.03],[.405,-.83],[.390,-.12],[.432,.48],[.52,.79]];
  edge('carrosserie','bleu',press.map(([y,z])=>[s*(sideX(z,y)+.004),y,z]),.009);
  for(const line of [[[.945,.72],[.81,.77],[.66,.78],[.43,.735],[.28,.657],[.251,.59],[.251,-.23],[.28,-.34],[.58,-.36],[.92,-.40]],[[.248,-.36],[.256,-.79],[.375,-.947],[.542,-1.014],[.764,-1.332],[.958,-1.50]]]){
    const seam=new T.CatmullRomCurve3(line.map(([y,z])=>V(0,y,z)));
    const path=seam.getPoints(60).map(({y,z})=>[s*(sideX(z,y)+.0037),y,z]);
    edge('carrosserie','bord',path,.0034,75);
  }
  let z=-.21,y=.876;orb('carrosserie','bleu',s*(sideX(z,y)+.006),y,z,.022,.018,.071);
  edge('carrosserie','chrome-fume',[[s*.839,.866,-.263],[s*.851,.868,-.23],[s*.843,.867,-.168]],.004);
}
// Surface across the hood and the rear hatch shoulder, leaving the cabin hollow.
function cap(za,zb,hump){patch('carrosserie','bleu',(u,v)=>{let z=lerp(za,zb,u),a=v*2-1,w=sideX(z,belt(z));return [w*a,belt(z)+hump(z)*(1-a*a)+.009*(1-a*a)*cos(a*PI*2),z];},45,30);}
cap(.81,2.026,z=>at(z,[[.81,.047],[1.2,.058],[1.65,.048],[2.026,.011]]));cap(-2.026,-1.65,z=>.041);
for(const s of [-1,1])edge('carrosserie','bord',[[s*.642,.939,.831],[s*.677,.920,1.04],[s*.666,.89,1.29],[s*.616,.856,1.53],[s*.527,.809,1.785]],.0032,32);
function end(sgn,u,v){const z=sgn*2.026, a=u*2-1;return [a*sideX(z,lerp(base(z),belt(z),v)),lerp(base(z),belt(z)+.008*(1-a*a),v),z-sgn*.010*a*a*(1-v)];}
for(const h of [-1,1])patch('carrosserie','bleu',(u,v)=>end(h,u,v),36,15);
// Cabin glass and pillars sit on a curved belt that rises toward the tail.
function roofY(z){return at(z,[[-1.29,1.342],[-1.09,1.403],[-.75,1.43],[-.42,1.44],[-.10,1.423],[.19,1.369]]);}
function roofW(z){return at(z,[[-1.29,.527],[-1.07,.555],[-.70,.56],[-.15,.554],[.19,.534]]);}
patch('pavillon','bleu',(u,v)=>{let z=lerp(-1.28,.16,u),a=v*2-1;return [a*roofW(z),roofY(z)-.039*a*a,z+.015*(1-a*a)];},46,30);
for(const s of [-1,1])edge('pavillon','bleu',Array.from({length:18},(_,i)=>{let z=lerp(-1.28,.16,i/17);return [s*roofW(z),roofY(z)-.04,z];}),.027);
function screen(front,u,v){let a=2*u-1, z=front?lerp(.875-.073*a*a,.19-.024*a*a,v):lerp(-1.81+.13*a*a,-1.29+.05*a*a,v);
 const y=front?lerp(.963-.031*a*a,1.369-.045*a*a,v):lerp(1.043-.035*a*a,1.342-.046*a*a,v);
 const w=front?lerp(.772,.535,v):lerp(.723,.532,v);
 return [a*w,y+.011*sin(PI*v)*(1-a*a),z];}
for(const front of [true,false]){
 patch('vitrages','verre',(u,v)=>screen(front,u,v),22,15);
 for(const u of [0,1])edge('montants','bleu',Array.from({length:6},(_,i)=>screen(front,u,i/5)),front?.032:.060);
 for(const v of [0,1])edge('vitrages','bord',Array.from({length:17},(_,i)=>screen(front,i/16,v)),.012);
}
function sideWindow(s,lower,upper,u,v){
 const bottom=lerp(lower[0],lower[1],u),top=lerp(upper[0],upper[1],u),z=lerp(bottom,top,v);
 const low=belt(bottom)+.014,high=roofY(max(-1.28,min(.19,top)))-.076;
 return [s*(lerp(sideX(bottom,low)-.014, roofW(max(-1.28,min(.19,top)))+.012,v)+.009*sin(PI*v)),lerp(low,high,v),z];
}
for(const s of [-1,1]){
 for(const [low,high] of [[[.798,-.36],[.146,-.411]],[[-.407,-1.34],[-.448,-1.005]]]){
  const win=(u,v)=>sideWindow(s,low,high,u,v);
  patch('vitrages','verre',win,22,12);
  for(const v of [0,1])edge('montants',v?'bord':'chrome-fume',Array.from({length:13},(_,i)=>win(i/12,v)),v?.012:.008);
  for(const u of [0,1])edge('montants','bord',Array.from({length:8},(_,i)=>win(u,i/7)),.015);
 }
 patch('montants','noir-laque',(u,v)=>sideWindow(s,[-.36,-.411],[-.411,-.452],u,v),3,12);
 patch('montants','bleu',(u,v)=>sideWindow(s,[-1.34,-1.69],[-1.005,-1.255],u,v),9,14);
 edge('montants','bord',[[s*.761,1.119,-1.302],[s*.735,1.16,-1.269],[s*.711,1.19,-1.244]],.010,12);
 edge('carrosserie','bord',[[s*.799,.971,.69],[s*.863,.97,.652],[s*.915,1.007,.67]],.019);
 orb('carrosserie','noir-laque',s*.91,1.027,.67,.08,.046,.108);
 orb('carrosserie','bleu',s*.914,1.043,.675,.082,.036,.108);
 orb('carrosserie','chrome-fume',s*.92,1.028,.584,.064,.028,.011);
}
box('pavillon','noir-laque',0,1.355,-1.315,1.08,.044,.15,.022,[-.12,0,0]);
orb('pavillon','bleu',0,1.431,-.99,.024,.039,.076,[.26,0,0]);
for(const a of [[-.66,-.03,.042],[.02,.65,.012]]) edge('details','bord',[[a[0],.977,.847],[lerp(a[0],a[1],.35),.982,.85-a[2]],[a[1],.982,.824-a[2]]],.006);
edge('details','bord',[[0,1.092,-1.76],[.19,1.096,-1.749],[.35,1.092,-1.731]],.009);
// Curved fascia panels use individual x positions on the rounded nose rather than flat decals.
function frontZ(x,y){const a=abs(x);return 2.036-.22*(a/.85)**3+.012*(y-.55);}
function rearZ(x,y){const a=abs(x);return -2.040+.265*(a/.85)**3+.04*(y-.57);}
function face(gn,mat,poly,front=true,offset=0){
 let fn=front?frontZ:rearZ;
 // An outline curved to the face with a centered vertex gives a gently crowned panel.
 const mid=poly.reduce((p,v)=>[p[0]+v[0]/poly.length,p[1]+v[1]/poly.length],[0,0]);
 for(let i=0;i<poly.length;i++){
   const a=poly[i],b=poly[(i+1)%poly.length];
   patch(gn,mat,(u,v)=>{const x=lerp(mid[0],lerp(a[0],b[0],u),v),y=lerp(mid[1],lerp(a[1],b[1],u),v);return [x,y,fn(x,y)+offset];},8,8);
 }
}
function fasciaLine(mat,coords,r,front=true,off=.005){const fn=front?frontZ:rearZ;edge('face',mat,coords.map(([x,y])=>[x,y,fn(x,y)+(front?off:-off)]),r,20,false);}
face('face','noir-laque',[[-.71,.72],[-.47,.745],[0,.754],[.47,.745],[.71,.72],[.48,.614],[.21,.591],[0,.59],[-.21,.591],[-.48,.614]]);
face('face','bord',[[-.72,.525],[-.56,.544],[.56,.544],[.72,.525],[.66,.284],[.47,.268],[-.47,.268],[-.66,.284]]);
for(let i=0;i<6;i++)fasciaLine('chrome-fume',[[-.615,.302+i*.038],[-.35,.299+i*.039],[0,.297+i*.039],[.35,.299+i*.039],[.615,.302+i*.038]],.0036);
for(let i=-7;i<=7;i++){const x=i*.071;for(let j=0;j<3;j++){const y=.637+j*.036;if(abs(x)+.026>.47+(y-.637)*2)continue;fasciaLine('chrome-fume',[[x-.019,y],[x,y+.014],[x+.018,y],[x,y-.014],[x-.019,y]],.0038);}}
for(const s of [-1,1]){
 const mirror=arr=>arr.map(([x,y])=>[s*x,y]);
 face('face','verre-feu',mirror([[.452,.745],[.61,.78],[.754,.805],[.814,.80],[.798,.761],[.713,.712],[.55,.701]]),true,.010);
 fasciaLine('diode',mirror([[.47,.743],[.615,.763],[.731,.782],[.792,.787]]),.009,true,.021);
 face('face','noir-laque',mirror([[.693,.681],[.767,.714],[.805,.693],[.756,.448],[.684,.372],[.646,.391]]),true,.010);
 face('face','diode',mirror([[.768,.686],[.788,.701],[.759,.508],[.696,.412],[.665,.395],[.727,.524]]),true,.026);
 fasciaLine('acier',mirror([[.105,.407],[.34,.404],[.579,.423],[.677,.479]]),.013,true,.029);
 face('face','verre-feu',mirror([[.25,.865],[.48,.892],[.682,.944],[.814,.967],[.8,.891],[.697,.829],[.48,.83],[.355,.833]]),false,-.017);
 fasciaLine('feu',mirror([[.28,.854],[.47,.871],[.65,.906],[.783,.939],[.77,.902],[.681,.858],[.593,.853]]),.016,false,.029);
}
face('face','bord',[[-.60,.452],[-.46,.485],[.46,.485],[.60,.452],[.57,.313],[-.57,.313]],false,-.014);
for(const s of [-1,1])fasciaLine('feu',[[s*.63,.43],[s*.692,.444],[s*.739,.46]],.011,false,.019);
// The lamp carries around the rear quarter into the flank and frames the hatch.
for(const s of [-1,1]){
 const sideLamp=[[s*.73,.908,-1.884],[s*.789,.954,-1.807],[s*.835,.958,-1.65],[s*.829,.927,-1.585],[s*.816,.857,-1.691],[s*.761,.844,-1.868]];
 panel('face','verre-feu',sideLamp);
 edge('face','feu',[[s*.773,.891,-1.849],[s*.81,.912,-1.785],[s*.843,.936,-1.64]],.011,20);
}
const capLine=[[-.615,.883],[-.589,.797],[-.521,.704],[-.448,.654],[0,.64],[.448,.654],[.521,.704],[.589,.797],[.615,.883]];
fasciaLine('bord',capLine,.0037,false,.005);
const fill=[];for(let i=0;i<=32;i++){
 const y=.821+.072*cos(i*PI/16),z=-1.344+.071*sin(i*PI/16);
 fill.push([-(sideX(z,y)+.0037),y,z]);
}
edge('carrosserie','bord',fill,.0032,36);
for(const front of [true,false]){
 let y=front?.693:.807,w=front?.057:.04,h=front?.085:.055;
 fasciaLine('alu',[[0,y+h],[w,y],[0,y-h],[-w,y],[0,y+h]],.008,front,.025);
 fasciaLine('acier',[[.004,y+h*.75],[w*.73,y],[-.002,y-h*.76],[-w*.72,y],[.004,y+h*.75]],.0025,front,.026);
}
box('face','bord',0,.438,2.053,.395,.09,.012,.01);
box('face','alu',0,.438,2.062,.375,.073,.008,.006);
box('face','alu',0,.543,-2.047,.39,.072,.009,.005);
// Spaced lettering describes the model visible on the hatch and the exhibition plate.
const glyphs=[
  [[.88,.89],[.58,1],[.23,.97],[.03,.73],[0,.26],[.23,.02],[.62,0],[.9,.14]],
  [[.05,1],[.05,.04],[.87,.04]],
  [[.44,1],[.44,.04]],
  [[.4,1],[.15,.91],[0,.71],[0,.24],[.21,.035],[.65,0],[.89,.18],[.91,.74],[.73,.95],[.4,1]]
];
for(const [front,cy,cz,scale,mat] of [[true,.438,2.068,.032,'bord'],[false,.737,-2.045,.027,'alu']]){
  for(const [i,points] of glyphs.entries()){
    const x=(i-1.5)*scale*1.55;
    edge('face',mat,points.map(([u,v])=>[(front?1:-1)*(x+(u-.45)*scale),cy+(v-.5)*scale,cz]),scale*.058,14,false);
  }
}
// Tires and diamond-cut split-spoke alloys. All four share identical dimensions.
for(const z of wheelZ)for(const s of [-1,1]){
 let xc=.754*s, yc=.306;
 const profile=[[.206,-.071],[.241,-.093],[.285,-.093],[.301,-.077],[.309,-.052],[.309,.054],[.303,.075],[.288,.088],[.262,.098],[.224,.098],[.205,.082],[.205,-.071]].map(p=>new T.Vector2(...p));
 add('roues','pneu',new T.LatheGeometry(profile,72),[xc,yc,z],[0,0,PI*.5]);
 const cyl=(mat,r,l,x)=>add('roues',mat,new T.CylinderGeometry(r,r,l,48),[x,yc,z],[0,0,PI*.5]);
 const rim=s*.853;
 cyl('gomme',.206,.008,s*.807);cyl('acier',.163,.009,s*.817);cyl('garniture',.106,.01,s*.828);
 const circ=(radius,r,mat,x)=>add('roues',mat,new T.TorusGeometry(radius,r,7,64),[x,yc,z],[0,PI/2,0]);
 circ(.211,.008,'alu',rim);circ(.204,.008,'noir-laque',rim);circ(.233,.0025,'gomme',s*.852);circ(.271,.0018,'gomme',s*.849);
 function wheelPoint(r,a,x){return [x,yc+cos(a)*r,z+sin(a)*r]}
 for(let i=0;i<5;i++){
  const a=2*PI*i/5;
  for(const sign of [-1,1]){
   const verts=[[.054,a-.16],[.128,a+sign*.105-.052],[.198,a+sign*.23-.082],[.202,a+sign*.23+.093],[.127,a+sign*.105+.083],[.062,a+.17]];
   panel('roues','noir-laque',verts.map(([r,t])=>wheelPoint(r,t,rim+s*.003)));
   panel('roues','alu',[[.063,a-.06],[.127,a+sign*.1-.025],[.202,a+sign*.24-.045],[.202,a+sign*.24+.012],[.128,a+sign*.1+.035]].map(([r,t])=>wheelPoint(r,t,rim+s*.005)));
  }
  const b=wheelPoint(.042,a,rim+s*.009);orb('roues','acier',...b,.007,.009,.009);
 }
 cyl('noir-laque',.039,.015,rim+s*.004);
 const loop=[[0,.022],[.013,0],[0,-.022],[-.013,0],[0,.022]].map(([u,v])=>[rim+s*.013,yc+v,z+u]);
 edge('roues','alu',loop,.0018,12,false);
}
box('habitacle','bord',0,.24,-.23,1.45,.058,2.89,.027);
box('habitacle','cuir',0,.53,-1.48,1.31,.065,.54,.027);
for(const s of [-1,1]){
 // Low interior panels remain visible in the roof-off view.
 box('habitacle','garniture',s*.776,.651,-.225,.043,.459,1.98,.019);
 edge('habitacle','cuir',[[s*.744,.815,.698],[s*.741,.803,.4],[s*.741,.758,-.134],[s*.741,.747,-.31]],.026);
 edge('habitacle','chrome-fume',[[s*.741,.784,.464],[s*.734,.805,.388],[s*.734,.8,.313]],.008);
 edgesSeat(s*.355,.048);
}
function edgesSeat(x,z){
 box('habitacle','cuir',x,.489,z,.526,.135,.512,.062);
 box('habitacle','textile',x,.551,z,.372,.065,.448,.03);
 for(const side of [-1,1])orb('habitacle','cuir',x+side*.222,.544,z,.058,.072,.233);
 const back=[-.15,0,0];
 box('habitacle','cuir',x,.777,z-.233,.502,.498,.12,.058,back);
 box('habitacle','textile',x,.79,z-.17,.354,.434,.065,.032,back);
 for(const side of [-1,1]){
  orb('habitacle','cuir',x+side*.206,.796,z-.171,.055,.234,.075,back);
  edge('habitacle','surpiqure',[[x+side*.147,.612,z-.115],[x+side*.154,.789,z-.119],[x+side*.124,.957,z-.151]],.0028);
  box('habitacle','acier',x+side*.071,1.026,z-.259,.012,.105,.012,.003);
 }
 box('habitacle','cuir',x,1.083,z-.27,.251,.168,.129,.041,[-.13,0,0]);
}
box('habitacle','cuir',0,.495,-.917,1.378,.161,.465,.064);
box('habitacle','textile',0,.555,-.932,1.234,.062,.36,.025);
box('habitacle','cuir',0,.767,-1.176,1.344,.471,.14,.055,[-.18,0,0]);
for(const x of [-.428,0,.428]){
 box('habitacle','textile',x,.759,-1.106,.371,.371,.058,.026,[-.16,0,0]);
 box('habitacle','cuir',x,1.055,-1.229,x===0?.193:.235,.133,.109,.036,[-.13,0,0]);
}
box('habitacle','garniture',0,.358,.088,.216,.167,.87,.049);
box('habitacle','cuir',0,.506,-.107,.18,.097,.299,.042);
box('habitacle','bord',0,.45,.278,.159,.024,.194,.011);
edge('habitacle','acier',[[0,.469,.264],[0,.549,.261],[0,.592,.284]],.012,12);
orb('habitacle','cuir',0,.595,.279,.032,.031,.041);
const dashCross=(u,v)=>{let x=lerp(-.76,.76,u), q=lerp(0,PI*2,v);return[x,.821+.102*cos(q)-.027*(x/.76)**2,.702+.155*sin(q)-.045*(x/.76)**2];};
patch('habitacle','garniture',dashCross,36,32);
box('habitacle','bord',0,.75,.755,1.46,.32,.244,.07);
box('habitacle','bord',-.438,.67,.682,.56,.193,.17,.039);
box('habitacle','garniture',0,.903,.756,1.47,.058,.23,.02);
edge('habitacle','chrome-fume',[[-.66,.70,.592],[-.42,.713,.594],[-.21,.713,.594]],.0026);
edge('habitacle','acier',[[-.71,.835,.548],[-.47,.849,.536],[-.185,.851,.541],[.1,.852,.541],[.53,.859,.521],[.70,.842,.53]],.0055,38);
const dashFaceZ=.555;
for(const x of [-.643,-.361,.622]){
 box('habitacle','noir-laque',x,.825,dashFaceZ,.112,.043,.027,.012);
 for(let i=0;i<3;i++)box('habitacle','chrome-fume',x,.813+i*.01,dashFaceZ-.016,.093,.0025,.004,.001);
}
box('habitacle','bord',.353,.905,.619,.354,.13,.11,.047);
box('habitacle','ecran',.353,.895,.56,.294,.089,.012,.005);
for(const x of [.268,.437]){
 const list=[];for(let i=0;i<18;i++){const a=lerp(-1.95,1.95,i/17);list.push([x+.031*sin(a),.891+.031*cos(a),.551]);}
 edge('habitacle','trait-ecran',list,.0025,18);
  for(let i=0;i<8;i++){const a=lerp(-1.95,1.95,i/7);edge('habitacle','acier',[[x+.023*sin(a),.891+.023*cos(a),.548],[x+.027*sin(a),.891+.027*cos(a),.548]],.0012,2,false);}
}
box('habitacle','noir-laque',-.04,.878,.52,.173,.235,.032,.016,[-.08,0,0]);
box('habitacle','ecran',-.04,.881,.50,.145,.202,.012,.005,[-.08,0,0]);
for(const line of [[[-.106,.904],[-.077,.916],[-.047,.893],[-.019,.900],[.017,.88]],[[-.11,.853],[-.06,.853],[-.047,.878],[-.021,.876],[.011,.913]]])
 edge('habitacle','trait-ecran',line.map(([x,y])=>[x,y,.489-(y-.87)*.08]),.0028,16,false);
for(let k=0;k<4;k++)box('habitacle','chrome-fume',-.09+k*.032,.799,.491,.014,.007,.002,.001);
for(let k=0;k<3;k++)box('habitacle','chrome-fume',-.076+k*.046,.966,.482,.021,.002,.002,.0005);
for(let k=0;k<5;k++)box('habitacle','bord',-.13+k*.045,.756,.538,.038,.015,.014,.006);
panel('habitacle','feu',[[-.052,.753,.524],[-.046,.763,.524],[-.040,.753,.524]]);
for(const x of [-.113,-.049,.014])add('habitacle','acier',new T.CylinderGeometry(.014,.016,.016,16),[x,.71,.535],[PI/2,0,0]);
for(const x of [-.113,-.049,.014])orb('habitacle','bord',x,.71,.523,.011,.011,.004);
// Flat-bottom three-spoke wheel and stalks, viewed from the real driving side in France.
const sw=[.355,.816,.398],wheelTilt=.22;
function SW(u,v,off=0){return [sw[0]+u,sw[1]+v,sw[2]+v*wheelTilt+off];}
const ring=[];for(let i=0;i<=54;i++){const a=2*PI*i/54;ring.push(SW(.162*sin(a),max(-.143,.161*cos(a))));}
edge('habitacle','cuir',ring,.017,75);
for(const poly of [[[-.14,.043],[-.058,.041],[-.023,.013],[-.064,-.015],[-.139,.003]],[[.14,.043],[.058,.041],[.023,.013],[.064,-.015],[.139,.003]],[[-.052,-.019],[-.014,-.128],[.023,-.135],[.047,-.025]]])panel('habitacle','acier',poly.map(([u,v])=>SW(u,v,-.004)));
orb('habitacle','cuir',...sw,.083,.064,.041);
edge('habitacle','alu',[[0,.017],[.011,0],[0,-.017],[-.011,0],[0,.017]].map(([u,v])=>SW(u,v,-.042)),.002,12,false);
for(const s of [-1,1])edge('habitacle','bord',[SW(s*.052,.012,.05),SW(s*.166,.047,.072),SW(s*.206,.054,.071)],.009);
box('habitacle','bord',0,1.253,.343,.17,.056,.033,.015);
for(const [key,parts] of bank){
 const [gn,name]=key.split('|');if(!groups.has(gn)){const group=new T.Group();group.name=gn;groups.set(gn,group);scene.add(group);}
 const merged=mergeGeometries(parts,false);const mesh=new T.Mesh(merged,colors[name]);mesh.name=gn+'_'+name;groups.get(gn).add(mesh);
}
const groundMaterial = new T.MeshBasicMaterial({name:'ombre',color:0xffffff,transparent:true,depthWrite:false});
const ground = new T.Mesh(new T.PlaneGeometry(2.8,5.75),groundMaterial);
ground.rotation.x=-PI/2;ground.position.y=-.008;ground.name='Ombre';scene.add(ground);
const camera=new T.PerspectiveCamera(64,1,.015,60);camera.name='CameraHabitacle';scene.add(camera);
globalThis.FileReader=class {readAsArrayBuffer(blob){blob.arrayBuffer().then(value=>{this.result=value;this.onloadend?.();});}};
const binary=await new GLTFExporter().parseAsync(scene,{binary:true});
await fs.writeFile(path.join(root,'clio-raw.glb'),new Uint8Array(binary));
console.log('Exported',binary.byteLength,'bytes',bank.size,'material groups');
