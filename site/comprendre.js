// Interactive car schematic: each system opens the matching tutorials of the library.
const query = new URLSearchParams(location.search);
const ui = ['en', 'es'].includes(query.get('ui')) ? query.get('ui') : 'fr';
const t = (fr, en, es) => ({fr, en, es})[ui];
const $ = selector => document.querySelector(selector);
const count = new Intl.NumberFormat(ui);

// Same order as the numbers drawn in car-anatomy.svg.
const SYSTEMS = {
  engine: ['Transforme le carburant en mouvement. Une perte de puissance, un bruit nouveau ou le voyant moteur méritent un contrôle.', 'Turns fuel into motion. Lost power, a new noise or the engine light deserve a check.', 'Convierte el combustible en movimiento. Una pérdida de potencia, un ruido nuevo o el testigo del motor merecen una revisión.'],
  lubrication: ['L’huile protège les pièces du moteur en mouvement. Le niveau se contrôle régulièrement et la vidange suit le carnet d’entretien.', 'Oil protects the moving parts of the engine. Check the level regularly and follow the service schedule for changes.', 'El aceite protege las piezas móviles del motor. Comprueba el nivel con regularidad y sigue el plan de mantenimiento.'],
  cooling: ['Le radiateur et le liquide évacuent la chaleur du moteur. Une température qui grimpe impose de s’arrêter.', 'The radiator and coolant carry heat away from the engine. A rising temperature means stop.', 'El radiador y el líquido evacúan el calor del motor. Si la temperatura sube, hay que parar.'],
  intake: ['Amène au moteur un air filtré. Un filtre encrassé fait perdre de la performance.', 'Feeds the engine with filtered air. A clogged filter costs performance.', 'Lleva al motor aire filtrado. Un filtro sucio resta rendimiento.'],
  ignition: ['Bougies d’allumage en essence, de préchauffage en diesel : elles assurent le bon démarrage et la combustion.', 'Spark plugs on petrol engines, glow plugs on diesels: they ensure starting and clean combustion.', 'Bujías de encendido en gasolina y de precalentamiento en diésel: aseguran el arranque y la combustión.'],
  fuel: ['Le réservoir, la pompe et le filtre amènent le carburant au moteur. Le bon carburant se lit sur la trappe.', 'The tank, pump and filter bring fuel to the engine. The right fuel is shown on the filler flap.', 'El depósito, la bomba y el filtro llevan el combustible al motor. El combustible correcto se indica en la tapa.'],
  transmission: ['La boîte et les transmissions envoient la force du moteur aux roues.', 'The gearbox and driveshafts send engine power to the wheels.', 'La caja de cambios y las transmisiones llevan la fuerza del motor a las ruedas.'],
  electrical: ['La batterie, les fusibles et le circuit alimentent toute la voiture. C’est souvent la première piste quand elle ne démarre plus.', 'The battery, fuses and wiring power the whole car. Often the first thing to check when it will not start.', 'La batería, los fusibles y el circuito alimentan todo el coche. Suele ser lo primero que revisar si no arranca.'],
  electronics: ['Calculateurs, capteurs et menus surveillent la voiture. Une valise de diagnostic lit les codes défaut.', 'Control units, sensors and menus monitor the car. A diagnostic tool reads the fault codes.', 'Centralitas, sensores y menús supervisan el coche. Una herramienta de diagnóstico lee los códigos de avería.'],
  visibility: ['Voir et être vu : éclairage, essuie-glaces et filtre d’habitacle.', 'See and be seen: lights, wipers and the cabin filter.', 'Ver y ser visto: iluminación, limpiaparabrisas y filtro de habitáculo.'],
  steering: ['Relie le volant aux roues avant. Un jeu ou un volant de travers se contrôle rapidement.', 'Connects the steering wheel to the front wheels. Play or an off-centre wheel should be checked soon.', 'Une el volante con las ruedas delanteras. Una holgura o un volante torcido deben revisarse pronto.'],
  braking: ['Plaquettes, disques et liquide arrêtent la voiture. C’est un organe de sécurité : en cas de doute, passe par un professionnel.', 'Pads, discs and fluid stop the car. It is a safety system: if in doubt, see a professional.', 'Pastillas, discos y líquido detienen el coche. Es un sistema de seguridad: ante la duda, acude a un profesional.'],
  suspension: ['Amortisseurs, ressorts et bras gardent les roues au sol et le confort à bord.', 'Dampers, springs and arms keep the wheels on the road and the ride comfortable.', 'Amortiguadores, muelles y brazos mantienen las ruedas en el suelo y el confort a bordo.'],
  wheels_tires: ['Seul contact avec la route. La pression et l’usure se contrôlent à froid.', 'The only contact with the road. Check pressure and wear when cold.', 'El único contacto con la carretera. La presión y el desgaste se comprueban en frío.'],
  body: ['La structure qui protège les occupants, et tout ce qui s’y fixe.', 'The structure that protects occupants, and everything attached to it.', 'La estructura que protege a los ocupantes y todo lo que se fija a ella.'],
};
const ORDER = Object.keys(SYSTEMS);

if (ui !== 'fr') {
  const copy = {
    kick: t('', 'Understand', 'Entender'),
    title: t('', 'Your car, system by system.', 'Tu coche, sistema por sistema.'),
    lead: t('', 'Touch part of the diagram to learn what it does, then open the tutorials about it.', 'Toca una parte del esquema para saber para qué sirve y abre los tutoriales.'),
    note: t('', 'Simplified diagram of a front-engine combustion car. Actual locations vary by model: always check your owner’s manual.', 'Esquema simplificado de un coche térmico con motor delantero. La ubicación real varía según el modelo: consulta siempre tu manual.'),
  };
  document.querySelectorAll('[data-t]').forEach(node => { node.textContent = copy[node.dataset.t]; });
  document.documentElement.lang = ui;
}

const json = url => fetch(url).then(response => (response.ok ? response.json() : null)).catch(() => null);
const [svg, taxonomy, counts] = await Promise.all([
  fetch('./car-anatomy.svg').then(response => response.text()),
  json('./automotive-taxonomy.json'),
  json('./catalog/anatomy-counts.json'),
]);
$('#car').innerHTML = svg;

const label = (group, id) => {
  const entry = taxonomy?.[group]?.find(item => item.id === id);
  return entry?.label?.[ui] || entry?.label?.fr || id;
};
const howMany = (group, id) => counts?.[group]?.[id]?.[ui === 'fr' ? 1 : 0] || 0;
const library = filter => `./?browse=1&${filter}${ui === 'fr' ? '&language=fr' : `&ui=${ui}`}`;
const inLanguage = ui === 'fr' ? ' en français' : '';

function select(id, remember) {
  document.querySelectorAll('#car [data-system]').forEach(node => node.classList.toggle('on', node.dataset.system === id));
  document.querySelectorAll('[data-pick]').forEach(node => node.setAttribute('aria-pressed', String(node.dataset.pick === id)));
  const total = howMany('systems', id);
  const tasks = (taxonomy?.tasks || []).filter(task => task.system === id && howMany('tasks', task.id) > 0)
    .sort((a, b) => howMany('tasks', b.id) - howMany('tasks', a.id)).slice(0, 6);
  const action = total ? `${t('Voir les', 'See the', 'Ver los')} ${count.format(total)} ${t('tutos', 'tutorials', 'tutoriales')}${inLanguage}` : t('Voir les tutos', 'See the tutorials', 'Ver los tutoriales');
  $('#panel').innerHTML = `<p class="ca-kick">${String(ORDER.indexOf(id) + 1).padStart(2, '0')} / ${ORDER.length}</p>
    <h2>${label('systems', id)}</h2>
    <p>${t(...SYSTEMS[id])}</p>
    <a class="ca-cta" href="${library(`system=${id}`)}">${action}</a>
    ${tasks.length ? `<ul>${tasks.map(task => `<li><a href="${library(`task=${task.id}`)}"><span>${label('tasks', task.id)}</span><small>${count.format(howMany('tasks', task.id))}</small></a></li>`).join('')}</ul>` : ''}`;
  if (remember) {
    const url = new URL(location.href);
    url.searchParams.set('systeme', id);
    history.replaceState(null, '', url);
  }
}

$('#systems').innerHTML = ORDER.map((id, index) => `<button type="button" data-pick="${id}" aria-pressed="false"><b>${index + 1}</b>${label('systems', id)}</button>`).join('');
$('#systems').addEventListener('click', event => {
  const button = event.target.closest('[data-pick]');
  if (button) select(button.dataset.pick, true);
});
$('#car').addEventListener('click', event => {
  const part = event.target.closest('[data-system]');
  if (part) select(part.dataset.system, true);
});
select(SYSTEMS[query.get('systeme')] ? query.get('systeme') : 'engine', false);
