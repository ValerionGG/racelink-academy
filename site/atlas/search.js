// Vehicle identity is exact; this index never guesses a generation or engine.
export const clean = value => String(value || '').toLowerCase().normalize('NFD').replace(/\p{M}/gu, '').replace(/\+/g,' plus ').replace(/([a-z])([0-9])/g, '$1 $2').replace(/[^a-z0-9]+/g, ' ').replace(/\bhybride\b/g,'hybrid').trim();
const romans = {i:'1',ii:'2',iii:'3',iv:'4',v:'5',vi:'6'};
const words = value => clean(value).split(/\s+/).filter(Boolean);
const phrase = (text, value) => (` ${text} `).includes(` ${clean(value)} `);
const remove = (text, value) => (` ${text} `).replace(` ${clean(value)} `, ' ').trim();
const empty = v => v === '' || v === undefined || v === null || v === 'all';
const incompatible = ['platform','language','content_format','level','domain','duration','transcript','license','task','category','spec','body_type'];
export const fuelTest = (engine, value) => {
  const f=clean(engine.fuel), q=clean(value);
  if (/hybrid|hybride/.test(q)) return /hybrid/.test(f);
  if (/electri|ev\b/.test(q)) return /electri/.test(f);
  if (/diesel|gazole/.test(q)) return /diesel/.test(f);
  if (/gpl/.test(q)) return /gpl/.test(f);
  return f.includes(q);
};
export function matchCars(models, query='', filters={}, {allowEmpty=false}={}) {
  if (incompatible.some(k=>!empty(filters[k])) || !empty(filters.format)) return [];
  return models.flatMap(model=>{
    let q=clean(query), trim=null, motor=null;
    if(model.id==='citroen-c3-iv')q=q.replace(/\be\s+c\s+3\b|\bec\s+3\b/g,'c 3 electrique');
    if(model.id==='peugeot-208-ii')q=q.replace(/\be\s+208\b/g,'208 electrique');
    if (!empty(filters.make)&&clean(filters.make)!==clean(model.make)) return [];
    if (!empty(filters.model)&&![model.model,...(model.aliases||[])].some(s=>clean(s)===clean(filters.model))) return [];
    if (!empty(filters.year)&&String(filters.year)!==String(model.year)) return [];
    if (!empty(filters.generation)) {
      const g=clean(filters.generation), n=romans[clean(model.generation)]||clean(model.generation);
      if (![clean(model.generation),n,clean(model.model+' '+model.generation),clean(model.model+' '+n),clean(model.model+' '+model.generation+' '+model.phase)].includes(g)) return [];
    }
    const identity=phrase(q,model.make)||phrase(q,model.model)||(model.aliases||[]).some(s=>phrase(q,s))||!empty(filters.model)||!empty(filters.make);
    if (!identity&&!(allowEmpty&&!q)) return [];
    // A phase introduction date is not the requested dossier year. Numeric model
    // names such as 2008 are removed before interpreting the remaining years.
    const withoutModel=remove(q,model.model);
    if(words(withoutModel).some(w=>/^20\d{2}$/.test(w)&&w!==String(model.year)))return [];
    const phase=q.match(/\bphase\s+(\d+)\b/);
    if(phase){if(phase[1]!==clean(model.phase).match(/\bphase\s+(\d+)\b/)?.[1])return [];q=q.replace(phase[0],' ').trim();}
    for (const item of [...(model.trims||[])].sort((a,b)=>b.label.length-a.label.length)) {
      if (phrase(q,item.label)) { if(trim) return []; trim=item; q=remove(q,item.label); }
    }
    for (const item of [...(model.engines||[])].sort((a,b)=>b.label.length-a.label.length)) {
      const aliases=[item.label,...(item.aliases||[]),item.label.replace(/full hybrid /i,''),item.label.replace(/^Blue /i,'')].map(s=>model.id==='citroen-c3-iv'?clean(s).replace(/\be\s+c\s+3\b|\bec\s+3\b/g,'c 3 electrique'):s);
      const found=aliases.find(s=>phrase(q,s));
      if(found) { if(motor) return []; motor=item; q=remove(q,found); }
    }
    if (!empty(filters.engine)) {
      const found=model.engines.find(e=>[e.id,e.label,...(e.aliases||[])].some(s=>clean(s)===clean(filters.engine)));
      if (!found || motor&&motor.id!==found.id) return []; motor=found;
    }
    if (trim&&motor&&!trim.engines.includes(motor.id)) return [];
    const requestedFuel=words(q).filter(w=>['hybrid','electrique','electric','diesel','gazole','gpl','essence'].includes(w));
    if(!empty(filters.fuel_type))requestedFuel.push(filters.fuel_type);
    if(requestedFuel.length) {
      const eligible=(motor?[motor]:model.engines).filter(e=>(!trim||trim.engines.includes(e.id))&&requestedFuel.every(f=>fuelTest(e,f)));
      if(!eligible.length) return [];
      if(!motor)motor=eligible[0];
      if(!trim)trim=model.trims.find(t=>t.engines.includes(motor.id));
    }
    // Strip identity phrases so the 3 in C3 cannot authorize generation III.
    for(const name of [...(model.aliases||[]),model.make+' '+model.model,model.model,model.make].sort((a,b)=>b.length-a.length))if(phrase(q,name))q=remove(q,name);
    const allowed=new Set(words('je veux une un ma mon pour de la en du voir voiture interieur exterieur habitacle cockpit 3d atlas fiche modele versions finitions hybrid electrique electric diesel gazole gpl essence '+model.generation+' '+(romans[clean(model.generation)]||'')+' '+model.year));
    if(words(q).some(w=>!allowed.has(w))) return [];
    const inside=words(q).some(w=>['interieur','habitacle','cockpit'].includes(w));
    return [{model,trim:trim?.id||'',motor:motor?.id||'',fuel:requestedFuel.join(' + '),view:words(q).includes('3d')?'3d':inside?'habitacle':'exterieur'}];
  });
}
export function carHref(match, base='./vehicules.html') {
  const p=new URLSearchParams({voiture:match.model.id,annee:String(match.model.year)});
  if(match.view&&match.view!=='exterieur')p.set('vue',match.view);
  if(match.trim)p.set('finition',match.trim);
  if(match.motor)p.set('moteur',match.motor);
  if(match.fuel)p.set('energie',match.fuel);
  return base+'?'+p;
}
