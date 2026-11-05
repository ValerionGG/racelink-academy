export const code = new URLSearchParams(location.search).get('ui');
export const language = code==='es' ? 'es' : code==='en' ? 'en' : 'fr';
export const t = (fr,en,es) => ({fr,en,es})[language];

export const text = {
  other:t('Autre véhicule à explorer sur le site de son équipe','Explore another vehicle on its team’s website','Explora otro vehículo en el sitio de su equipo'),
  back:t('Bibliothèque','Library','Biblioteca'),workshop:t('Atelier 3D','3D workshop','Taller 3D'),
  intro:t('Explorez le châssis de ce prototype à partir des plans de Team Wikispeed. Choisissez un ensemble pour voir ses pièces de près.','Explore this prototype chassis using Team Wikispeed’s design. Choose an assembly to inspect its parts.','Explora el chasis de este prototipo a partir de los planos de Team Wikispeed. Elige un conjunto para observar sus piezas.'),
  start:t('Manipuler en 3D','Open interactive 3D','Manipular en 3D'),explode:t('Vue éclatée','Exploded view','Vista de despiece'),angle:t('Point de vue','Viewpoint','Punto de vista'),
  quarter:t('Trois quarts','Three-quarter','Tres cuartos'),side:t('Profil','Side','Perfil'),top:t('Dessus','Top','Desde arriba'),fit:t('Recadrer','Fit view','Encuadrar'),
  choose:t('Explorer les pièces','Explore the parts','Explorar las piezas'),family:t('Ensemble','Assembly','Conjunto'),part:t('Pièce','Part','Pieza'),all:t('Vue d’ensemble','Overview','Vista general'),
  inventory:t('Voir l’inventaire','View inventory','Ver inventario'),source:t('Origine du modèle','Model source','Origen del modelo'),
  credits:t('Plans de Team Wikispeed, convertis et publiés par Matt Maier sur Open Source Ecology. RaceLink a adapté la géométrie pour le web et ajouté les couleurs, les regroupements et le rendu. La vue éclatée montre les pièces à distance pour faciliter leur lecture.','Team Wikispeed’s drawings were converted and published by Matt Maier on Open Source Ecology. RaceLink adapted the geometry for the web and added colours, groupings and renders. The exploded view moves parts apart for inspection.','Matt Maier convirtió y publicó los planos de Team Wikispeed en Open Source Ecology. RaceLink adaptó la geometría para la web y añadió colores, agrupaciones y renders. La vista de despiece separa las piezas para facilitar su observación.'),
  plans:t('Plans de l’équipe ↗','Team drawings ↗','Planos del equipo ↗'),download:t('Télécharger le modèle 3D','Download 3D model','Descargar el modelo 3D'),licenses:t('Crédits et licences','Credits and licences','Créditos y licencias'),
  initial:t('Plan de l’équipe, exporté en mars 2012.','Team design, exported in March 2012.','Plano del equipo, exportado en marzo de 2012.'),
  loading:t('Chargement de la géométrie…','Loading geometry…','Cargando la geometría…'),
  ready:t('Glissez pour tourner, pincez pour zoomer. Au clavier, utilisez les flèches et les touches + et −.','Drag to rotate, pinch to zoom. Use the arrow keys and + or − on a keyboard.','Arrastra para girar y pellizca para ampliar. Con teclado usa las flechas y las teclas + y −.'),
  fallback:t('3D interactive indisponible. Les vues fixes des ensembles et l’inventaire restent accessibles.','Interactive 3D is unavailable. Browse the assembly images and the inventory.','La vista 3D interactiva no está disponible. Puedes consultar las imágenes y el inventario.'),
  solid:t('volume','solid','sólido'),solids:t('volumes','solids','sólidos'),families:t('ensembles','assemblies','conjuntos'),
  pieceAll:t('Toutes les pièces','All parts','Todas las piezas'),unknown:t('Volume sans nom','Unnamed solid','Sólido sin nombre'),
  close:t('Vue de la pièce isolée','Isolated part view','Vista de la pieza aislada'),geometry:t('Nom dans la CAO','CAD source name','Nombre en el archivo CAD'),
  overview:t('Châssis assemblé','Assembled chassis','Chasis montado'),
  description:t('Les deux modules de suspension du côté passager sont dessinés dans cet assemblage. Le moteur est représenté uniquement par son berceau.','This assembly depicts the two passenger-side suspension modules. The engine is represented by its cradle only.','Este conjunto representa los dos módulos de suspensión del lado del pasajero. Del motor se muestra únicamente su soporte.'),
  unnamed:t('Ce volume appartient à l’ensemble sélectionné. Le fichier de CAO ne lui attribue pas de nom individuel.','This solid belongs to the selected assembly. The CAD file does not give it an individual name.','Este sólido pertenece al conjunto seleccionado. El archivo CAD no le asigna un nombre individual.'),
  inGroup:t('Ensemble d’origine','Original assembly','Conjunto de origen'), loadingFailure:t('Réessayer la 3D','Retry 3D','Reintentar la vista 3D'),
  canvas:t('Modèle 3D interactif. Flèches pour tourner, + et − pour zoomer.','Interactive model. Arrow keys rotate, + and − zoom.','Modelo interactivo. Las flechas giran y + o − acercan o alejan.'),
  zoomIn:t('Rapprocher','Zoom in','Acercar'),zoomOut:t('Éloigner','Zoom out','Alejar'),
  viewOf:t('Rendu de la CAO','CAD rendering','Vista del archivo CAD')
};

export const families = {
  chassis:[t('Châssis et plancher','Chassis and floor','Chasis y suelo'),88,
    t('Les longerons et les traverses entourent la plaque de plancher. Les cordons de soudure figurent eux aussi dans le fichier.','Longitudinal rails and crossmembers surround the floor plate. The source also includes the welds.','Los largueros y travesaños rodean la chapa del suelo. El archivo también incluye los cordones de soldadura.')],
  habitacle:[t('Cadres supérieurs','Upper frames','Bastidores superiores'),20,
    t('Ces tubes forment le cadre de l’habitacle et le support supérieur du module de carrosserie.','These tubes form the cabin frame and the upper mounting frame for the body module.','Estos tubos forman el bastidor del habitáculo y el soporte superior del módulo de carrocería.')],
  berceau:[t('Berceau moteur','Engine cradle','Soporte del motor'),12,
    t('Le berceau en tubes carrés se loge à l’arrière du châssis. On distingue ses traverses en isolant cet ensemble.','The square-tube cradle sits at the rear of the chassis. Isolate it to see its crossmembers.','Este soporte de tubo cuadrado está en la parte trasera del chasis. Aísla el conjunto para ver sus travesaños.')],
  impact:[t('Structures de choc','Crash structures','Estructuras de impacto'),6,
    t('Le plan distingue une structure à l’avant et une à l’arrière. La vue éclatée les écarte du châssis.','The drawing identifies separate front and rear crash structures. The exploded overview moves them away from the chassis.','El plano distingue una estructura delantera y otra trasera. La vista de despiece las separa del chasis.')],
  roues:[t('Roues et pneus','Wheels and tyres','Ruedas y neumáticos'),6,
    t('Deux roues du côté passager figurent dans le plan. Les pneus Ecopia EP100 et les jantes Motegi SP10 sont identifiés dans la CAO.','The design shows two passenger-side wheels. The CAD names Ecopia EP100 tyres and Motegi SP10 rims.','El plano muestra dos ruedas del lado del pasajero. El CAD identifica los neumáticos Ecopia EP100 y las llantas Motegi SP10.')],
  suspension:[t('Suspension et moyeux','Suspension and hubs','Suspensión y bujes'),108,
    t('Observez les ressorts, les supports de jambe, les rotules et les moyeux des deux modules dessinés.','Inspect the springs, strut mounts, ball joints and hubs of the two modelled corners.','Observa los muelles, soportes, rótulas y bujes de los dos módulos representados.')],
  freinage:[t('Freinage','Braking system','Sistema de frenado'),15,
    t('Les disques et étriers se trouvent près des roues. La platine avant regroupe la pédale, le servofrein, le maître-cylindre et des éléments ABS.','The discs and calipers sit by the wheels. The front plate groups the pedal, booster, master cylinder and ABS components.','Los discos y las pinzas están junto a las ruedas. La placa delantera reúne el pedal, el servofreno, el cilindro maestro y elementos del ABS.')],
  fixations:[t('Fixations du cadre','Frame fasteners','Fijaciones del bastidor'),16,
    t('Quatre assemblages de fixation sont représentés aux angles du cadre supérieur. Leurs vis, écrous et rondelles peuvent être isolés.','Four fastener assemblies are shown at the upper frame corners. Inspect their bolts, nuts and washers individually.','Hay cuatro conjuntos de fijación en las esquinas del bastidor superior. Se pueden aislar sus tornillos, tuercas y arandelas.')]
};

const names=[
  [/Bridgestone/,t('Pneu Ecopia EP100','Ecopia EP100 tyre','Neumático Ecopia EP100')],
  [/Motegi/,t('Jante Motegi SP10','Motegi SP10 rim','Llanta Motegi SP10')],
  [/Front_10_3_inch_Rotors/,t('Disque de frein','Brake disc','Disco de freno')],
  [/front_caliper/,t('Étrier de frein','Brake caliper','Pinza de freno')],
  [/pedal_housing/i,t('Support de pédale','Pedal housing','Alojamiento del pedal')],
  [/pedal_to_Brake/i,t('Liaison pédale–servofrein','Pedal-to-booster coupling','Acople del pedal al servofreno')],
  [/brake_pedal$/i,t('Pédale de frein','Brake pedal','Pedal de freno')],
  [/plunger/i,t('Plongeur','Plunger','Émbolo')],
  [/Brake_Booster/i,t('Servofrein','Brake booster','Servofreno')],
  [/brake_fluid/i,t('Réservoir de liquide de frein','Brake fluid reservoir','Depósito de líquido de frenos')],
  [/Master_Cylinder/i,t('Maître-cylindre','Master cylinder','Cilindro maestro')],
  [/ABS_module/i,t('Module ABS','ABS module','Módulo ABS')],
  [/^Spring_05/,t('Ressort de suspension','Suspension spring','Muelle de suspensión')],
  [/floor_plate/,t('Plaque de plancher','Floor plate','Chapa del suelo')],
  [/weld/,t('Cordon de soudure','Weld','Cordón de soldadura')],
  [/Tie_Rod/i,t('Biellette de direction','Tie rod','Tirante de dirección')],
  [/knuckle/i,t('Porte-fusée','Steering knuckle','Mangueta')],
  [/Hub_Carrier/i,t('Porte-moyeu','Hub carrier','Portabuje')],
  [/strut_top_mount/i,t('Support supérieur de jambe','Upper strut mount','Soporte superior del puntal')]
];
export const partName = source => names.find(([pattern])=>pattern.test(source))?.[1] ||
  (source ? source.replace(/_/g,' ').replace(/\s+/g,' ').trim() : text.unknown);
