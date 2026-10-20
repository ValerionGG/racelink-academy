export const tracks = {
  driving: [
    {title:['Poser le regard','Look ahead','Dirigir la mirada'],query:'vision',goal:['Identifier les repères visuels et le point de sortie avant de chercher la vitesse.','Identify visual reference points and the exit before chasing speed.','Identificar referencias visuales y la salida antes de buscar velocidad.']},
    {title:['Dessiner la trajectoire','Understand the racing line','Entender la trazada'],query:'racing line',goal:['Distinguer entrée, point de corde et sortie ; comparer deux explications.','Distinguish entry, apex and exit; compare two explanations.','Distinguir entrada, vértice y salida; comparar dos explicaciones.']},
    {title:['Comprendre le freinage','Understand braking','Comprender la frenada'],query:'braking',goal:['Comprendre l’évolution de la pression et le transfert de charge dans le contexte choisi.','Understand pressure changes and weight transfer in your chosen context.','Comprender la presión y la transferencia de carga en tu contexto.']},
    {title:['Analyser un tour','Analyze a lap','Analizar una vuelta'],query:'telemetry',goal:['Relier une trace de données à une action et choisir un seul axe de progression.','Connect a data trace to an action and choose one area for improvement.','Relacionar datos con una acción y elegir un aspecto que mejorar.']}
  ],
  engineering: [
    {title:['Lire une trace','Read a trace','Leer una señal'],query:'telemetry',goal:['Identifier les axes, les unités et les principales entrées pilote.','Identify axes, units and key driver inputs.','Identificar ejes, unidades y acciones del piloto.']},
    {title:['Comprendre les pneus','Understand tires','Comprender los neumáticos'],query:'tyre',goal:['Comparer température, pression et adhérence sans confondre corrélation et cause.','Compare temperature, pressure and grip without confusing correlation with causation.','Comparar temperatura, presión y agarre sin confundir correlación y causa.']},
    {title:['Découvrir l’aérodynamique','Explore aerodynamics','Explorar la aerodinámica'],query:'aerodynamics',goal:['Distinguer appui et traînée, puis observer leurs compromis.','Distinguish downforce from drag and explore their tradeoffs.','Distinguir carga y resistencia y explorar sus compromisos.']},
    {title:['Raisonner en stratégie','Think about strategy','Pensar en estrategia'],query:'strategy',goal:['Identifier les hypothèses derrière une décision de course.','Identify the assumptions behind a race decision.','Identificar las hipótesis de una decisión de carrera.']}
  ],
  mechanics: [
    {title:['Comprendre le moteur','Understand the engine','Comprender el motor'],query:'engine',goal:['Nommer les éléments et comprendre le cycle de fonctionnement.','Name the components and understand the operating cycle.','Nombrar componentes y comprender el ciclo de funcionamiento.']},
    {title:['Découvrir les suspensions','Explore suspension','Explorar la suspensión'],query:'suspension',goal:['Relier le mouvement de la roue aux composants du train roulant.','Connect wheel motion to suspension components.','Relacionar el movimiento de la rueda con sus componentes.']},
    {title:['Comprendre les freins','Understand brakes','Comprender los frenos'],query:'brakes',goal:['Distinguer commande, friction et gestion thermique.','Distinguish control, friction and heat management.','Distinguir mando, fricción y gestión térmica.']},
    {title:['Lire un réglage','Read a setup','Leer un ajuste'],query:'setup',goal:['Identifier l’effet attendu d’un réglage et ses limites selon le véhicule.','Identify the intended effect and limits of a setup change.','Identificar el efecto esperado y los límites de un ajuste.']}
  ],
  simracing: [
    {title:['Préparer le poste','Prepare your rig','Preparar el equipo'],query:'sim racing beginner',goal:['Trouver les bases adaptées à son simulateur et à son matériel.','Find the basics for your simulator and equipment.','Encontrar los fundamentos para tu simulador y equipo.']},
    {title:['Calibrer ses commandes','Calibrate controls','Calibrar los controles'],query:'pedals',goal:['Comprendre les entrées du volant et des pédales avant d’ajuster.','Understand wheel and pedal inputs before adjusting.','Comprender entradas de volante y pedales antes de ajustar.']},
    {title:['Construire sa régularité','Build consistency','Mejorar la regularidad'],query:'racing line',goal:['Choisir des repères reproductibles et comparer plusieurs tours.','Choose repeatable reference points and compare laps.','Elegir referencias repetibles y comparar vueltas.']},
    {title:['Explorer les setups','Explore setups','Explorar reglajes'],query:'setup',goal:['Documenter une modification à la fois pour comprendre son effet.','Document one change at a time to understand its effect.','Documentar un cambio cada vez para comprender su efecto.']}
  ],
  media: [
    {title:['Anticiper l’image','Plan the shot','Planificar la imagen'],query:'motorsport photography',goal:['Observer cadrage, position et contexte de la prise de vue.','Observe framing, position and shooting context.','Observar encuadre, posición y contexto.']},
    {title:['Comprendre le mouvement','Understand motion','Comprender el movimiento'],query:'panning',goal:['Comparer les choix de vitesse et leur rendu visuel.','Compare shutter choices and their visual effects.','Comparar velocidades y efectos visuales.']},
    {title:['Filmer une séquence','Film a sequence','Filmar una secuencia'],query:'film motorsport',goal:['Décomposer une séquence en plans complémentaires.','Break a sequence into complementary shots.','Descomponer una secuencia en planos complementarios.']},
    {title:['Construire le récit','Build the story','Construir el relato'],query:'editing',goal:['Relier les images pour transmettre une intention claire.','Connect images to convey a clear intention.','Relacionar imágenes para transmitir una intención clara.']}
  ],
  business: [
    {title:['Comprendre l’écosystème','Understand the ecosystem','Comprender el ecosistema'],query:'motorsport business',goal:['Identifier les rôles des équipes, organisateurs et partenaires.','Identify teams, organizers and partners.','Identificar equipos, organizadores y socios.']},
    {title:['Définir sa proposition','Define your proposition','Definir tu propuesta'],query:'sponsorship',goal:['Comprendre ce qu’un partenariat peut apporter à chaque partie.','Understand what each party can gain from a partnership.','Comprender lo que aporta una colaboración a cada parte.']},
    {title:['Préparer un dossier','Prepare a proposal','Preparar una propuesta'],query:'sponsor proposal',goal:['Comparer la structure de plusieurs présentations et leurs preuves.','Compare the structure and evidence in different proposals.','Comparar estructuras y evidencias de propuestas.']},
    {title:['Mesurer une collaboration','Measure a partnership','Medir una colaboración'],query:'motorsport marketing',goal:['Distinguer objectifs, actions et résultats observables.','Distinguish objectives, actions and observable results.','Distinguir objetivos, acciones y resultados observables.']}
  ],
  career: [
    {title:['Explorer les métiers','Explore careers','Explorar profesiones'],query:'motorsport career',goal:['Repérer plusieurs fonctions et leurs tâches quotidiennes.','Identify different roles and daily activities.','Identificar funciones y actividades diarias.']},
    {title:['Identifier les compétences','Identify skills','Identificar competencias'],query:'race engineer',goal:['Comparer les compétences citées par plusieurs professionnels.','Compare skills mentioned by several professionals.','Comparar competencias citadas por profesionales.']},
    {title:['Construire son expérience','Build experience','Adquirir experiencia'],query:'motorsport experience',goal:['Identifier des exemples de projets et d’expériences documentées.','Identify examples of documented projects and experience.','Identificar proyectos y experiencias documentadas.']},
    {title:['Préparer sa candidature','Prepare an application','Preparar una candidatura'],query:'job motorsport',goal:['Relier ses réalisations aux attentes d’un métier précis.','Connect your achievements to a specific role.','Relacionar tus logros con una profesión concreta.']}
  ],
  fitness: [
    {title:['Comprendre les exigences','Understand the demands','Comprender las exigencias'],query:'driver fitness',goal:['Identifier les contraintes physiques propres à sa discipline.','Identify the physical demands of your discipline.','Identificar las exigencias físicas de tu disciplina.']},
    {title:['Découvrir la préparation','Explore preparation','Explorar la preparación'],query:'racing driver training',goal:['Observer les objectifs des exercices présentés par les professionnels.','Observe the goals of exercises presented by professionals.','Observar los objetivos de ejercicios presentados por profesionales.']},
    {title:['Comprendre la récupération','Understand recovery','Comprender la recuperación'],query:'recovery',goal:['Identifier ce qui relève de principes généraux ou d’un suivi individuel.','Distinguish general principles from individual guidance.','Distinguir principios generales y seguimiento individual.']},
    {title:['Structurer ses questions','Structure your questions','Organizar tus preguntas'],query:'driver preparation',goal:['Préparer les questions à discuter avec un encadrant qualifié.','Prepare questions to discuss with a qualified professional.','Preparar preguntas para un profesional cualificado.']}
  ]
};
