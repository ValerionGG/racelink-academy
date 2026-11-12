import {renderOfficialSystems} from './repere.js';
const $=s=>document.querySelector(s),base=new URL('.',import.meta.url),photoBase=new URL('photos/',base);
const price=n=>new Intl.NumberFormat('fr-FR',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(n);
const date=s=>new Intl.DateTimeFormat('fr-FR',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(s+'T12:00:00Z'));
const make=(tag,txt,cls)=>{const n=document.createElement(tag);if(txt!=null)n.textContent=txt;if(cls)n.className=cls;return n};
const href=(s,u)=>{const n=make('a',s);n.href=u;return n};
const pressed=(el,v)=>el.setAttribute('aria-pressed',String(v));
const params=new URLSearchParams(location.search);
function store(k,v){const u=new URL(location.href);if(v)u.searchParams.set(k,v);else u.searchParams.delete(k);history.replaceState(null,'',u)}
const req=async url=>{const r=await fetch(new URL(url,base));if(!r.ok)throw Error('Données indisponibles');return r.json()};
const pinMap={
 'clio-hero.webp':[[80,62,'Signature avant','La face avant et ses feux ont changé lors du restylage.',4],[51,76,'Roue avant','Retrouvez les jantes illustrées pour chaque finition.',24]],
 'clio-rear.webp':[[23,60,'Hayon','Renault donne aussi la hauteur du véhicule hayon ouvert.',18]],
 'clio-cockpit.webp':[[37,41,'Instrumentation','Comparez les écrans et les compteurs selon la finition.',10],[69,40,'Écran central','Cet exemplaire illustre le poste de conduite esprit Alpine.',15],[65,77,'Sélecteur de vitesses','Le levier visible ici est celui de cet exemplaire à boîte manuelle.',17]],
 'clio-engine.webp':[[55,54,'Sous le capot','Cette photo montre un exemplaire hybride 1.6 E-Tech. Pour identifier votre moteur, consultez ses documents.',25]]
};
let brochure='https://cdn.group.renault.com/ren/fr/product-plans/clio-ph2/Brochure_Clio_mai_2025.pdf.asset.pdf/b560ce39fc.pdf';
async function gallery(){
 const photos=await req('photos/photos.json'), film=$('#film'), main=$('#main-photo'), box=$('#lightbox');
 const short=['Avant','Arrière','Habitacle','En 2025','Moteur','Face avant'];
 const id=p=>p.src.replace(/^clio-|\.webp$/g,'');
 const open=i=>{const p=photos[i];main.src=new URL(p.src,photoBase);main.alt=p.alt;main.width=p.width;main.height=p.height;$('#photo-title').textContent=p.title;$('#photo-caption').textContent=p.caption+' · '+date(p.date);$('#photo-credit').href=new URL('credits.html#'+id(p),photoBase);
 $('#photo-n').textContent=String(i+1).padStart(2,'0');$('#pin-info').hidden=true;
 [...film.children].forEach((b,j)=>pressed(b,i===j));$('#pins').replaceChildren();
 (pinMap[p.src]||[]).forEach(([x,y,label,info,page],j)=>{const b=make('button'),n=make('span',String(j+1));b.className='pin';b.setAttribute('aria-label','Repère '+(j+1)+' : '+label);pressed(b,false);b.style.left=x+'%';b.style.top=y+'%';b.append(n);b.onclick=()=>{const off=b.getAttribute('aria-pressed')==='true';[...$('#pins').children].forEach(k=>pressed(k,false));$('#pin-info').hidden=off;if(off)return;pressed(b,true);$('#pin-info').replaceChildren(make('strong',label+' · '),document.createTextNode(info+' '),href('Renault, p. '+page+' ↗',brochure+'#page='+page))};$('#pins').append(b)});
 $('#expand').onclick=()=>{$('#large-photo').src=main.src;$('#large-photo').alt=p.alt;$('#large-caption').textContent=p.title+' · '+p.author+' · '+p.license;box.showModal()};$('#expand').hidden=false;
 };
 photos.forEach((p,i)=>{const b=make('button'),img=make('img');img.alt='';img.loading='lazy';img.src=new URL(p.src,photoBase);b.title=p.title;b.setAttribute('aria-label',p.title);b.append(img,make('span',short[i]||p.title));b.onclick=()=>{open(i);store('photo',id(p))};film.append(b)});
 open(Math.max(0,photos.findIndex(p=>id(p)===params.get('photo'))));$('#closebox').onclick=()=>box.close();box.onclick=e=>{if(e.target===box)box.close()};
}
async function versions(){const d=await req('renault.json'), rail=$('#trims'),select=$('#engine');brochure=d.sources.brochure;
 renderOfficialSystems($('#systemes'),d);
 const engines=new Map(d.engines.map(e=>[e.id,e])), trims=new Map(d.trims.map(t=>[t.id,t]));let selected;
 const showEngine=(remember=false)=>{const e=engines.get(select.value),t=selected,dl=$('#engine-spec');if(!e)return;dl.replaceChildren();
 for(const [k,v] of [['Énergie',e.fuel],['Boîte',e.gearbox],['Prix TTC au 01/07/25',price(t.engines[e.id])],['Cylindrée',new Intl.NumberFormat('fr-FR').format(e.capacity_cm3)+' cm³'],['Coffre (norme VDA)',e.boot_dm3_vda+' dm³']]){const g=make('div');g.append(make('dt',k),make('dd',v));dl.append(g)}
 if(remember){store('finition',t.id);store('moteur',e.id)}};
 const pick=(id,prefer,remember)=>{const t=trims.get(id);selected=t;$('#trim-name').textContent=t.label;[...rail.children].forEach(b=>pressed(b,b.value===id));select.replaceChildren();for(const eid of Object.keys(t.engines)){const o=make('option',engines.get(eid).label);o.value=eid;select.append(o)}
 select.value=Object.hasOwn(t.engines,prefer)?prefer:Object.keys(t.engines)[0];showEngine(remember);const eq=$('#equipment');eq.replaceChildren();
 for(const [k,list] of [['Équipements de série · exemples',t.standard_examples],['En option · exemples',t.options]]){const block=make('div');block.append(make('h4',k));if(list.length){const ul=make('ul');list.forEach(v=>ul.append(make('li',v)));block.append(ul)}else{block.append(make('p','Détail non précisé dans le comparatif des finitions.','fine'))}eq.append(block)}
 const s=$('#trim-sources');s.replaceChildren(href('Tarif Renault · p. 6 ↗',d.sources.tariff),href('Fiche moteur ↗',ePage(select.value)));if(t.cockpit_page)s.append(href('Voir la finition · p. '+t.cockpit_page+' ↗',brochure+'#page='+t.cockpit_page));
 };
 const ePage=id=>id==='etech145'?d.sources.engine_detail:d.sources.engine_thermal;
 d.trims.forEach(t=>{const b=make('button');b.value=t.id;b.append(make('span',t.label),make('small',Object.keys(t.engines).length+' moteurs'));b.onclick=()=>pick(t.id,select.value,true);rail.append(b)});select.onchange=()=>pick(selected.id,select.value,true);
 const requested=params.get('moteur'),candidates=d.trims.filter(t=>Object.hasOwn(t.engines,requested));let initial=trims.has(params.get('finition'))?params.get('finition'):'evolution';
 if(!params.has('finition')&&candidates.length){initial=candidates[0].id;const note=make('p',engines.get(requested).label+' au tarif : '+candidates.map(t=>t.label).join(', ')+'.','fine');rail.before(note);note.classList.add('motor-note')}
 pick(initial,requested,false);
 const table=make('table'),h=table.createTHead().insertRow();['Finition','Motorisation','TTC'].forEach(k=>{const th=make('th',k);th.scope='col';h.append(th)});const bod=table.createTBody();d.trims.forEach(t=>Object.entries(t.engines).forEach(([id,p])=>{const row=bod.insertRow();[t.label,engines.get(id).label,price(p)].forEach(v=>row.append(make('td',v)))}));const wrap=make('div',null,'table-scroll');wrap.append(table);$('#matrix').append(wrap,make('p',d.price_scope),href('Consulter le document Renault ↗',d.sources.tariff));
 const tech=$('#technical'),dim=d.dimensions_mm;tech.append(make('h3','Encombrement'),make('p',`Longueur : ${dim.length} mm · Largeur rétroviseurs rabattus : ${dim.width_folded_mirrors} mm, ouverts : ${dim.width_open_mirrors} mm · Hauteur : ${dim.height} mm, hayon ouvert : ${dim.height_with_boot_open} mm · Empattement : ${dim.wheelbase} mm.`),href('Dessins cotés de face, de dos, de profil et de dessus ↗',d.sources.dimensions),make('h3','Nuancier illustré'),make('p','Ces six teintes sont illustrées pour la techno avec pack look. Les pastilles ci-dessous sont indicatives.'));
 const swatches=make('ul',null,'swatches');d.colours.forEach((c,i)=>{const li=make('li'),sw=make('i');sw.style.backgroundColor=['#eeede6','#5f6162','#262827','#305d86','#b3b6b0','#db6f30'][i];li.append(sw,c);swatches.append(li)});tech.append(swatches,href('Voir les peintures Renault en photo ↗',d.sources.colours),make('h3','Gammes spécifiques'),make('p','Auto-école : '+d.special_versions.auto_ecole.map(s=>engines.get(s).label).join(', ')+'. Utilitaire evolution réversible : '+d.special_versions.utilitaire_evolution_reversible.map(s=>engines.get(s).label).join(', ')+'.'),href('Consulter le tarif Renault ↗',d.sources.commercial),make('p',d.sixth_gen_note),href('Annonce de la sixième génération ↗',d.sources.sixth_gen));
 d.date_editions.forEach((x,i)=>{const a=make('article');a.append(make('p','ÉDITION RENAULT  /  0'+(i+1),'eyebrow'),make('h3',date(x.from)+' – '+date(x.to)),href('Lire la notice ↗',x.guide),href('PDF ↗',x.pdf));if(x.id==='13326')a.append(href('Tutoriels Renault ↗','https://www.user-manual.renault.com/fr/notice/13326/videos'));$('#manuals').append(a)});
}
gallery().catch(()=>{$('#photo-caption').textContent='Photographie de la phase 2. Consultez les crédits pour retrouver les autres vues.'});
versions().catch(()=>{$('#trim-name').textContent='Consulter la documentation Renault';$('#equipment').append(href('Brochure Renault ↗',brochure))});
