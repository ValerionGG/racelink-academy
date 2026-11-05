// Each station has its own source-dated coverage. Never rewrite a user's search.
export const clioDossier = './clio-5-2025.html';
const clean = s=>String(s||'').toLowerCase().normalize('NFD').replace(/\p{M}/gu,'').replace(/[^a-z0-9]+/g,' ').trim();
export function resolveClioDossier(query, filters={}) {
  let s=clean(query).replace(/\bclio(?=[5v]\b)/g,'clio ');
  const trims={generation:['sce65','tce90','ecog100','dci100'],evolution:['sce65','tce90','ecog100','dci100','etech145'],techno:['ecog100','tce90','etech145'],'esprit-alpine':['tce90','etech145']};
  let trim='',motor='';
  for(const name of Object.keys(trims)){const re=new RegExp('\\b'+name.replace('-',' ')+'\\b');if(re.test(s)){if(trim)return null;trim=name;s=s.replace(re,' ')}}
  const motors={sce65:/\bsce\s?65\b/,tce90:/\btce\s?90\b/,ecog100:/\beco\s?g\s?100\b/,dci100:/\b(?:blue\s+)?dci\s?100\b/,etech145:/\b(?:e\s?tech\s*(?:full\s+hybrid\s*)?|full hybrid\s+e\s?tech\s*)145\b/};
  for(const [id,re] of Object.entries(motors)){if(re.test(s)){if(motor)return null;motor=id;s=s.replace(re,' ')}}
  if(trim&&motor&&!trims[trim].includes(motor))return null;
  const q=s.trim().split(/\s+/).filter(Boolean);
  const model=clean(filters.model),gen=clean(filters.generation),year=String(filters.year||'');
  if(filters.make && clean(filters.make)!=='renault' || model && model!=='clio' || gen&&!['5','v','clio v','clio 5','clio v phase 2'].includes(gen) || year&&year!=='2025')return false;
  if(filters.engine || filters.fuel_type || filters.body_type || filters.spec || filters.task || filters.category || filters.platform || filters.language || filters.content_format || filters.level || filters.domain || filters.duration || filters.transcript || filters.license || (filters.format && filters.format!=='all')) return false;
  const allowed=new Set('renault clio 5 v phase 2 2025 de la en du voir voiture interieur exterieur habitacle cockpit 3d atlas fiche modele'.split(' '));
  if(q.some(token=>!allowed.has(token)))return false;
  const hasCar=q.includes('clio')||model==='clio', hasYear=q.includes('2025')||year==='2025';
  if(!hasCar||!hasYear)return null;
  const p=new URLSearchParams();if(trim)p.set('finition',trim);if(motor)p.set('moteur',motor);
  const inside=q.some(x=>['interieur','cockpit','habitacle'].includes(x));let anchor='';
  if(q.includes('3d')){p.set('vue',inside?'cockpit':'three-quarter');anchor='#atelier'}
  else if(inside){p.set('photo','cockpit');anchor='#photos'}
  else if(trim||motor)anchor='#versions';
  return clioDossier+(p.size?'?'+p:'')+anchor;
}
export const showClioDossier=(query,filters)=>Boolean(resolveClioDossier(query,filters));
