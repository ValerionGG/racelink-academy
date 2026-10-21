"""Conservative automotive indexing from video titles, using only the standard library.

Extracted mentions are search aids, never vehicle compatibility or maintenance advice.
No model year, engine, generation or fuel is supplied from external vehicle knowledge.
"""
import re
import unicodedata

VERSION = "1.0.2"


def fold(value):
    text = "".join(c for c in unicodedata.normalize("NFKD", str(value or ""))
                   if not unicodedata.combining(c)).lower()
    return text.translate(str.maketrans({"ł": "l", "ß": "ss", "’": "'"}))


def entry(id_, fr, en, es, **extra):
    return {"id": id_, "label": {"fr": fr, "en": en, "es": es}, **extra}


TASKS = [
    entry("oil_change", "Vidange moteur", "Engine oil change", "Cambio de aceite", system="lubrication"),
    entry("oil_filter", "Filtre à huile", "Oil filter", "Filtro de aceite", system="lubrication"),
    entry("oil_spec", "Grade et norme d’huile", "Oil grade and specification", "Grado y norma del aceite", system="lubrication"),
    entry("wipers", "Essuie-glaces", "Wipers", "Limpiaparabrisas", system="visibility"),
    entry("wheel_change", "Changement de roue & roue de secours", "Wheel change & spare wheel", "Cambio de rueda y rueda de repuesto", system="wheels_tires"),
    entry("wheel_bearing", "Roulement / moyeu de roue", "Wheel bearing / hub", "Rodamiento / buje", system="wheels_tires"),
    entry("tires", "Pneus et pression", "Tires and pressure", "Neumáticos y presión", system="wheels_tires"),
    entry("brake_pads", "Plaquettes de frein", "Brake pads", "Pastillas de freno", system="braking"),
    entry("brake_discs", "Disques de frein", "Brake discs", "Discos de freno", system="braking"),
    entry("brake_drums", "Tambours et mâchoires", "Brake drums and shoes", "Tambores y zapatas", system="braking"),
    entry("brake_fluid", "Liquide et purge des freins", "Brake fluid and bleeding", "Líquido y purga de frenos", system="braking"),
    entry("brake_caliper", "Étrier de frein", "Brake caliper", "Pinza de freno", system="braking"),
    entry("battery", "Batterie et charge", "Battery and charging", "Batería y carga", system="electrical"),
    entry("fuses", "Fusibles et relais", "Fuses and relays", "Fusibles y relés", system="electrical"),
    entry("lighting", "Éclairage et ampoules", "Lighting and bulbs", "Luces y bombillas", system="electrical"),
    entry("diagnostics", "Diagnostic / OBD", "Diagnostics / OBD", "Diagnóstico / OBD", system="electronics"),
    entry("service_reset", "Remise à zéro / voyant entretien", "Service reminder reset", "Reinicio del mantenimiento", system="electronics"),
    entry("vehicle_menus", "Menus et écran du véhicule", "Vehicle menus and display", "Menús y pantalla del vehículo", system="electronics"),
    entry("equipment_controls", "Commandes et équipements", "Controls and equipment", "Mandos y equipamiento", system="electronics"),
    entry("key_battery", "Pile de clé / télécommande", "Key fob battery", "Pila de llave / mando", system="electrical"),
    entry("fuel_choice", "Carburants et indices", "Fuel types and ratings", "Combustibles e índices", system="fuel"),
    entry("fuel_filter", "Filtre à carburant", "Fuel filter", "Filtro de combustible", system="fuel"),
    entry("air_filter", "Filtre à air moteur", "Engine air filter", "Filtro de aire del motor", system="intake"),
    entry("cabin_filter", "Filtre habitacle", "Cabin filter", "Filtro del habitáculo", system="visibility"),
    entry("spark_plugs", "Bougies d’allumage", "Spark plugs", "Bujías de encendido", system="ignition"),
    entry("glow_plugs", "Bougies de préchauffage", "Glow plugs", "Bujías de precalentamiento", system="ignition"),
    entry("shock_absorbers", "Amortisseurs et jambes de force", "Shock absorbers and struts", "Amortiguadores y puntales", system="suspension"),
    entry("suspension_springs", "Ressorts de suspension", "Suspension springs", "Muelles de suspensión", system="suspension"),
    entry("suspension_arms", "Bras et rotules de suspension", "Suspension arms and ball joints", "Brazos y rótulas de suspensión", system="suspension"),
    entry("stabilizer_links", "Barre stabilisatrice et biellettes", "Anti-roll bar and links", "Barra estabilizadora y bieletas", system="suspension"),
    entry("steering", "Direction et rotules", "Steering and tie rods", "Dirección y rótulas", system="steering"),
    entry("belts", "Courroies et distribution", "Belts and timing", "Correas y distribución", system="engine"),
    entry("cooling", "Refroidissement", "Cooling system", "Refrigeración", system="cooling"),
    entry("transmission", "Transmission et embrayage", "Transmission and clutch", "Transmisión y embrague", system="transmission"),
    entry("engine_mounts", "Supports moteur", "Engine mounts", "Soportes del motor", system="engine"),
    entry("sensors", "Capteurs moteur / échappement", "Engine / exhaust sensors", "Sensores del motor / escape", system="electronics"),
    entry("body_hardware", "Portes, hayon et carrosserie", "Doors, tailgate and body hardware", "Puertas, portón y carrocería", system="body"),
]
SYSTEMS = [
    entry("lubrication", "Lubrification moteur", "Engine lubrication", "Lubricación del motor"),
    entry("visibility", "Visibilité et habitacle", "Visibility and cabin", "Visibilidad y habitáculo"),
    entry("wheels_tires", "Roues et pneus", "Wheels and tires", "Ruedas y neumáticos"),
    entry("braking", "Freinage", "Brakes", "Frenos"),
    entry("electrical", "Électricité", "Electrical", "Electricidad"),
    entry("electronics", "Électronique et diagnostic", "Electronics and diagnostics", "Electrónica y diagnóstico"),
    entry("fuel", "Carburant et alimentation", "Fuel system", "Combustible y alimentación"),
    entry("intake", "Admission d’air", "Air intake", "Admisión de aire"),
    entry("ignition", "Allumage et préchauffage", "Ignition and preheating", "Encendido y precalentamiento"),
    entry("suspension", "Suspension", "Suspension", "Suspensión"),
    entry("steering", "Direction", "Steering", "Dirección"),
    entry("engine", "Moteur et distribution", "Engine and timing", "Motor y distribución"),
    entry("cooling", "Refroidissement", "Cooling", "Refrigeración"),
    entry("transmission", "Transmission", "Transmission", "Transmisión"),
    entry("body", "Carrosserie", "Body", "Carrocería"),
]
BODY_TYPES = [
    entry("sedan", "Berline", "Sedan / saloon", "Berlina"),
    entry("estate", "Break", "Estate / wagon", "Familiar"),
    entry("hatchback", "Berline à hayon", "Hatchback", "Compacto con portón"),
    entry("van", "Fourgon", "Van", "Furgoneta"),
    entry("coupe", "Coupé", "Coupe", "Cupé"),
    entry("convertible", "Cabriolet", "Convertible", "Descapotable"),
    entry("suv", "SUV", "SUV", "SUV"),
    entry("pickup", "Pick-up", "Pickup", "Pickup"),
]
FUEL_TYPES = [
    entry("petrol", "Essence", "Petrol / gasoline", "Gasolina"),
    entry("diesel", "Diesel", "Diesel", "Diésel"),
    entry("hybrid", "Hybride", "Hybrid", "Híbrido"),
    entry("electric", "Électrique", "Electric", "Eléctrico"),
    entry("lpg", "GPL", "LPG", "GLP"),
    entry("ethanol", "Éthanol / E85", "Ethanol / E85", "Etanol / E85"),
]
TAXONOMY = {
    "version": VERSION, "tasks": TASKS, "systems": SYSTEMS,
    "body_types": BODY_TYPES, "fuel_types": FUEL_TYPES,
    "specification_kinds": [
        entry("oil_viscosity", "Viscosité SAE mentionnée", "Mentioned SAE viscosity", "Viscosidad SAE mencionada"),
        entry("oil_standard", "Norme d’huile mentionnée", "Mentioned oil standard", "Norma de aceite mencionada"),
        entry("fuel_grade", "Carburant mentionné", "Mentioned fuel grade", "Combustible mencionado"),
        entry("battery_voltage", "Tension mentionnée", "Mentioned voltage", "Tensión mencionada"),
    ],
    "disclaimer": {
        "fr": "Mentions extraites des titres ou légendes sources. Elles ne confirment ni la compatibilité avec votre véhicule ni une préconisation d’entretien.",
        "en": "Mentions extracted from source titles or captions. They do not confirm vehicle compatibility or maintenance recommendations.",
        "es": "Menciones extraídas de los títulos o descripciones originales. No confirman compatibilidad ni recomendaciones de mantenimiento.",
    },
}

# Expressions describe explicit components or operations, not inferred vehicle compatibility.
PATTERNS = {
    "oil_change": r"\b(?:engine oil|motor oil|huile moteur|aceite (?:de )?motor|oleo (?:do )?motor|motorol|olej silnikowy|olio motore|vidange|oil change|changing oil)\b",
    "oil_filter": r"\b(?:oil filter|filtre (?:a |d.)?huile|filtro (?:de |del |do |d.)?(?:aceite|oleo|olio)|olfilter|filtr oleju)\b",
    "oil_spec": r"\b(?:(?:choos\w*|select\w*|right|correct|which)(?:\s+\w+){0,4}\s+(?:engine|motor)?\s*oil|(?:choisir|choix|quelle|bonne)(?:\s+\w+){0,3}\s+huile|(?:elegir|elegir el|que|cual)(?:\s+\w+){0,3}\s+aceite|oil (?:grade|viscosity|specification)|viscosite|norme.*huile|grado.*aceite)\b",
    "wipers": r"\b(?:wipers?|wiper blades?|essuie[- ]glaces?|limpiaparabrisas|scheibenwischer|wycieraczk\w*|tergicristall\w*|limpa[- ]para[- ]brisas|limpa[- ]vidros)\b",
    "wheel_bearing": r"\b(?:wheel bearings?|wheel hubs?|roulement\w*(?:\s+\w+){0,3}\s+roues?|moyeu\w*|cojinet\w*(?:\s+\w+){0,3}\s+ruedas?|rodamiento\w*|radlager\w*|lozysk\w*(?:\s+\w+){0,3}\s+kol\w*|rolamento\w*(?:\s+\w+){0,3}\s+rodas?|cuscinetto\w*(?: della| di)? ruota)\b",
    "tires": r"\b(?:tires?|tyres?|pneus?|pneumatic\w*|neumatic\w*|reifen\w*|opony|opon|opone)\b",
    "brake_pads": r"\b(?:brake pads?|plaquett\w*(?: de)? frein|pastill\w*(?: de)? freno|pastilh\w*(?: de)? travao|bremsbelag\w*|klock\w* hamulcow\w*|pastigli\w*(?: dei)? freni)\b",
    "brake_discs": r"\b(?:brake (?:discs?|rotors?)|disqu\w*(?: de)? frein|disc\w*(?: de)? freno|disc\w*(?: de)? travao|bremsscheib\w*|tarcz\w* hamulcow\w*|disch\w*(?: dei)? freni)\b",
    "brake_drums": r"\b(?:brake (?:drums?|shoes?)|tambour\w*|machoir\w*|bremsback\w*|bremstrommel\w*|szczek\w* hamulcow\w*|beben\w* hamulcow\w*|zapatas? (?:de )?freno|tambor\w*|gana[sc]\w* freni)\b",
    "brake_fluid": r"\b(?:brake fluid|brake bleed\w*|bleed\w*(?: the)? brakes|liquide de frein|purge\w*(?: les| des| de)? freins|bremsflussigkeit|bremsen entluft\w*|plyn hamulcowy|liquido (?:de |dos )?frenos?|fluido (?:de )?travao|liquido (?:dei )?freni)\b",
    "brake_caliper": r"\b(?:calipers?|etrier\w*|bremssattel|zacisk\w* hamulcow\w*|pinz\w* (?:de )?freno|pinca\w* (?:de )?travao)\b",
    "battery": r"\b(?:batter(?:y|ies|ie)|bateri\w*|akumulator\w*|alternator\w*|alternateur|lichtmaschine)\b",
    "fuses": r"\b(?:fuses?|fusibles?|fusiv\w*|sicherung\w*|bezpiecznik\w*|relays?|relais|reles?|przekaznik\w*)\b",
    "lighting": r"\b(?:headlights?|taillights?|tail lights?|bulbs?|ampoules?|phares?|feux|bombill\w*|faros?|scheinwerfer|gluhlampe\w*|zarowk\w*|lampad\w*|farol\w*|pisca\w*|clignotant\w*)\b",
    "diagnostics": r"\b(?:obd(?:[- ]?ii|2)?|diagnos\w*|diagnost\w*|fault codes?|trouble codes?|dtc|scan tool|codes? defaut|codes? erreur|check engine)\b",
    "service_reset": r"\b(?:service reset|oil reset|maintenance reset|reset (?:oil|service|maintenance)|resetting (?:the )?(?:oil|service)|remise a zero|voyant entretien|service zurucksetzen|wartung zurucksetzen|intervall zurucksetzen|reset\w* (?:servicio|manutencao|serwis)|azzeramento (?:service|manutenzione))\b",
    "vehicle_menus": r"\b(?:infotainment|vehicle menus?|car menus?|on[- ]board computer|ordinateur de bord|bordcomputer|menu(?:s)? (?:du vehicule|voiture)|android auto|apple carplay)\b",
    "equipment_controls": r"\b(?:steering wheel buttons|steering wheel controls|stalk switch|indicator stalk|cruise control|regulateur de vitesse|commandes? au volant|boutons? du volant|commodo|tempomat|lenkradtasten|mandos? del volante|control de crucero|controlo de cruzeiro)\b",
    "key_battery": r"\b(?:key fob|key battery|remote battery|pile (?:de |d.une )?cle|pile (?:de )?telecommande|schluesselbatterie|schlusselbatterie|pila (?:de |del )?(?:llave|mando)|bateria (?:da |de )?chave|bateria (?:w )?kluczy\w*|batteria (?:della )?chiave)\b",
    "fuel_choice": (
        r"\b(?:octan\w*|fuel (?:choice|grades?|types?|ratings?)|ethanol\w*|quel(?:le)?s? carburants?|types? de carburant)\b"
        r"|\b(?:choos\w*|select\w*|chois\w*|eleg\w*|escog\w*|scegli\w*|escolh\w*|wybor|wahlen)\b.{0,40}"
        r"\b(?:fuel|carburant|essence|gasoline|petrol|diesel|gasolina|benzina|benzyna|kraftstoff|combustible|combustivel)\b"
        r"|\b(?:petrol|gasoline|diesel|essence|gasolina|fuel)\b.{0,45}\b(?:vs|versus|or|ou|o|oder)\b.{0,25}"
        r"\b(?:petrol|gasoline|diesel|essence|gasolina|95|98)\b"
    ),
    "fuel_filter": r"\b(?:fuel filter|filtre (?:a |de )?(?:carburant|gazole|gasoil|essence)|filtro (?:de |do )?(?:combustible|combustivel|carburante|gasolio)|kraftstofffilter|benzinfilter|dieselfilter|filtr paliwa)\b",
    "air_filter": r"\b(?:air filter|filtre a air|filtro (?:de |do |dell.)?(?:aire|ar|aria)|luftfilter|filtr powietrza)\b",
    "cabin_filter": r"\b(?:cabin filter|pollen filter|filtre (?:d.|de )?(?:habitacle|pollen)|filtro (?:de |do )?(?:habitaculo|cabina|polen|polline)|innenraumfilter|pollenfilter|filtr kabinowy)\b",
    "spark_plugs": r"\b(?:spark plugs?|bougie\w* d.allumage|zundkerz\w*|swiec\w* zaplonow\w*|bujias?(?: de encendido)?|velas? de ignicao|candel\w* (?:di )?accensione)\b",
    "glow_plugs": r"\b(?:glow plugs?|bougie\w* de prechauffage|gluhkerz\w*|swiec\w* zarow\w*|bujias? de precalentamiento|velas? (?:de )?incandescencia|candellett\w*)\b",
    "shock_absorbers": r"\b(?:shock absorbers?|shock struts?|strut mounts?|dampers?|amortisseur\w*|jambe\w* de force|amortiguador\w*|amortecedor\w*|stossdampfer|stoßdampfer|domlager|amortyzator\w*|ammortizzator\w*)\b",
    "suspension_springs": r"\b(?:suspension springs?|coil springs?|ressorts?(?: de suspension)?|molas? de suspensao|spr[ei]zyn\w*|schraubenfeder\w*|fahrwerksfeder\w*|muelles?(?: de suspension)?|molle (?:di )?sospensione)\b",
    "suspension_arms": r"\b(?:suspension arms?|control arms?|wishbones?|ball joints?|bras de suspension|rotule\w* de suspension|querlenker|trag|wahacz\w*|brazos? de suspension|bracos? de suspensao|bracci\w*(?: di )?sospensione)\b",
    "stabilizer_links": r"\b(?:anti[- ]roll|stabiliz\w*|stabilis\w*|koppelstang\w*|stabigummi\w*|sway bar)\b",
    "steering": r"\b(?:tie[- ]rod|track rod|steering rack|steering fluid|rotule\w* de direction|biellette\w* de direction|terminal de direcao|spurstang\w*|drazk\w* kierownicz\w*|drazka kierowniczego|rotul\w* de direccion|testin\w* (?:di )?sterzo)\b",
    "belts": r"\b(?:serpentine belt|timing belt|drive belt|timing chain|courroie|chaine de distribution|cambelt|zahnriemen|keilrippenriemen|steuerkette|pasek|rozrzad\w*|correa|correia|cinghia|catena di distribuzione)\b",
    "cooling": r"\b(?:coolant|radiator|thermostat|water pump|refroidissement|liquide de refroidissement|kuhlmittel|kuhler|wasserpumpe|refrigerante|bomba (?:de |d.)?agua|chlodnic\w*|pompa acqua)\b",
    "transmission": r"\b(?:transmission|gearbox|clutch|embrayage|embrague|embreagem|getriebe|kupplung|sprzegl\w*|frizione|cambio automatico)\b",
    "engine_mounts": r"\b(?:engine mounts?|motor mounts?|supports? moteur|motorlager|poduszk\w* silnika|soportes? (?:del )?motor|apoios? (?:do )?motor|support\w* motore)\b",
    "sensors": r"\b(?:lambda|oxygen sensor|crankshaft sensor|camshaft sensor|capteur|sensor|sensore|sonde|sonda|czujnik\w*)\b",
    "body_hardware": r"\b(?:tailgate struts?|boot struts?|door lock|window regulator|mudguard|verin\w* de (?:coffre|hayon)|leve[- ]vitre|serrure|heckklappendampfer|fensterheber|turschloss|si[łl]ownik\w*|podnosnik\w* szyb|amortiguador\w* (?:del )?maletero)\b",
}
TASK_REGEX = {key: re.compile(pattern, re.I) for key, pattern in PATTERNS.items()}
CHANGE = re.compile(r"\b(?:chang\w*|replac\w*|remov\w*|swap\w*|remplac\w*|demon\w*|depos\w*|cambi\w*|sostitu\w*|substitu\w*|wechsel\w*|wymien\w*|wymian\w*)\b", re.I)
WHEEL = re.compile(r"\b(?:wheels?|roues?|ruedas?|rodas?|rader|rad|kola|kolo|ruota|ruote)\b", re.I)
WHEEL_OPERATION = re.compile(
    r"\b(?:(?:change|replace|remove|install|changing|removing)(?:\s+(?:a|an|the|your|front|rear|stuck|spare)){0,3}\s+wheels?"
    r"|wheel change|(?:changer|remplacer|deposer|monter|remettre)(?:\s+(?:une|la|les|des|un)){0,2}\s+roues?"
    r"|(?:cambiar|cambio de|desmontar)(?:\s+(?:una|la|las|de)){0,2}\s+ruedas?"
    r"|(?:substituir|trocar)(?:\s+(?:uma|a|as|de)){0,2}\s+rodas?"
    r"|(?:wymienic|wymiana)\s+(?:kolo|kola|kol)|radwechsel|rader wechseln|rad wechseln"
    r"|(?:sostituire|cambiare)\s+(?:una |la )?ruot[ae])\b", re.I)
SPARE_WHEEL = re.compile(
    r"\b(?:spare wheels?|roues? de secours|ruedas? de repuesto|rodas? sobressalentes?"
    r"|reserverad|ersatzrad|ruota di scorta|kolo zapasowe|kola zapasowego)\b", re.I)

MAKES = {
    "Volkswagen": ["Volkswagen", "VW"], "Mercedes-Benz": ["Mercedes-Benz", "Mercedes Benz", "Mercedes"],
    "BMW": ["BMW"], "Audi": ["Audi"], "Ford": ["Ford"], "Opel": ["Opel"], "Vauxhall": ["Vauxhall"],
    "Renault": ["Renault"], "Peugeot": ["Peugeot"], "Citroën": ["Citroen"], "Toyota": ["Toyota"],
    "Nissan": ["Nissan"], "Hyundai": ["Hyundai"], "Kia": ["Kia"], "Volvo": ["Volvo"],
    "Škoda": ["Skoda"], "SEAT": ["Seat"], "Fiat": ["Fiat"], "Honda": ["Honda"], "Mazda": ["Mazda"],
    "Suzuki": ["Suzuki"], "Dacia": ["Dacia"], "Mitsubishi": ["Mitsubishi"], "Subaru": ["Subaru"],
    "Alfa Romeo": ["Alfa Romeo"], "Chevrolet": ["Chevrolet", "Chevy"], "GMC": ["GMC"],
    "Dodge": ["Dodge"], "Ram": ["Ram"], "Chrysler": ["Chrysler"], "Jeep": ["Jeep"],
    "Buick": ["Buick"], "Cadillac": ["Cadillac"], "Pontiac": ["Pontiac"], "Saturn": ["Saturn"],
    "Acura": ["Acura"], "Lexus": ["Lexus"], "Infiniti": ["Infiniti"], "Lincoln": ["Lincoln"],
    "Mini": ["Mini"], "Porsche": ["Porsche"], "Land Rover": ["Land Rover"],
    "Jaguar": ["Jaguar"], "Saab": ["Saab"], "Tesla": ["Tesla"], "Smart": ["Smart"],
    "SsangYong": ["SsangYong"], "Isuzu": ["Isuzu"], "Ferrari": ["Ferrari"],
}
MODELS = {
    "Volkswagen": ["Golf", "Passat", "Polo", "Touran", "Sharan", "Transporter", "Multivan", "Caravelle", "Caddy", "Bora", "Jetta", "Lupo", "Tiguan", "Touareg", "Beetle", "New Beetle", "Scirocco", "Up", "Amarok", "T4", "T5", "T6"],
    "Mercedes-Benz": ["A-Class", "B-Class", "C-Class", "E-Class", "S-Class", "Vito", "Viano", "Sprinter", "CLK", "CLA", "CLS", "GLA", "GLC", "GLE", "ML", "SLK", "SL", "GL", "G", "A", "B", "C", "E", "S", "M", "190", "B200", "A160", "C200", "C220", "E200", "E220", "E320"],
    "BMW": ["1 Series", "2 Series", "3 Series", "4 Series", "5 Series", "6 Series", "7 Series", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "Z3", "Z4", "M2", "M3", "M4", "M5", "M6", "520i", "525i", "530i", "540i", "318i", "320i", "325i", "328i", "330i", "330d", "320d", "335i", "1", "2", "3", "4", "5", "6", "7"],
    "Audi": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "Q2", "Q3", "Q5", "Q7", "Q8", "TT", "80", "100", "S3", "S4", "S6", "RS3", "RS4", "RS6", "R8"],
    "Ford": ["Focus", "Fiesta", "Mondeo", "Transit", "Transit Connect", "C-Max", "S-Max", "Galaxy", "Ka", "Fusion", "Kuga", "Ranger", "Explorer", "Escape", "Edge", "Expedition", "F-150", "F150", "F-250", "F250", "F-350", "F350", "Mustang", "Contour", "Taurus", "Escort", "Econoline", "Crown Victoria", "Thunderbird", "Freestar", "Windstar"],
    "Opel": ["Meriva", "Zafira", "Corsa", "Vivaro", "Astra", "Vectra", "Insignia", "Omega", "Agila", "Antara", "Mokka", "Combo"],
    "Vauxhall": ["Meriva", "Zafira", "Corsa", "Vivaro", "Astra", "Vectra", "Insignia"],
    "Renault": ["Grand Scenic", "Megane Scenic", "Symbol/Thalia", "Duster", "Clio", "Scenic", "Megane", "Master", "Twingo", "Kangoo", "Symbol", "Thalia", "Laguna", "Trafic", "Espace", "Captur", "Kadjar", "Fluence"],
    "Peugeot": ["107", "108", "106", "206", "207", "208", "306", "307", "308", "309", "406", "407", "408", "508", "2008", "3008", "5008", "Partner", "Boxer", "Expert"],
    "Citroën": ["Xsara Picasso", "C4 Picasso", "Grand C4 Picasso", "C1", "C2", "C3", "C4", "C5", "C6", "Berlingo", "Xsara", "Saxo", "Jumper", "Jumpy", "Xantia"],
    "Toyota": ["Land Cruiser Prado", "Land Cruiser", "Corolla Verso", "Yaris", "Corolla", "Auris", "Aygo", "Prius", "Avensis", "RAV4", "RAV 4", "Camry", "Hilux", "Verso", "Celica", "Supra", "Sienna", "Highlander", "4Runner", "Tacoma", "Tundra", "Sequoia", "Matrix"],
    "Nissan": ["Qashqai", "X-Trail", "X Trail", "Micra", "Leaf", "Juke", "Almera", "Note", "Primera", "Pathfinder", "Navara", "Altima", "Maxima", "Sentra", "Rogue", "Murano", "Frontier", "Titan", "350Z", "370Z", "GT-R"],
    "Hyundai": ["Santa Fe", "Elantra", "i10", "i20", "i30", "i40", "Coupe", "Getz", "Tucson", "Accent", "Sonata", "Kona", "Veloster", "Genesis", "Tiburon", "Santa Cruz", "Palisade"],
    "Kia": ["Sorento", "Carnival", "Ceed", "Cee'd", "Sportage", "Picanto", "Rio", "Optima", "Soul", "Sedona", "Forte", "Cerato", "Stinger"],
    "Volvo": ["V70", "V50", "V40", "V60", "V90", "S40", "S60", "S80", "S90", "XC60", "XC70", "XC90", "C30", "C70", "850", "240"],
    "Škoda": ["Fabia", "Octavia", "Superb", "Roomster", "Yeti", "Rapid", "Kodiaq", "Karoq"],
    "SEAT": ["Ibiza", "Leon", "Altea", "Alhambra", "Toledo", "Cordoba", "Arosa", "Ateca", "Arona"],
    "Fiat": ["Bravo", "Punto", "Grande Punto", "Panda", "Doblo", "500", "500L", "Ducato", "Tipo", "Stilo", "Seicento", "Multipla"],
    "Honda": ["Insight", "Civic", "Accord", "Jazz", "Fit", "CR-V", "HR-V", "CRX", "Prelude", "S2000", "Odyssey", "Pilot", "Element", "Ridgeline", "CR-Z"],
    "Mazda": ["MX-5", "MX5", "Miata", "RX-7", "RX7", "RX-8", "RX8", "CX-3", "CX-5", "CX-7", "CX-9", "2", "3", "5", "6", "323", "626", "Demio", "Protege", "Tribute"],
    "Suzuki": ["Swift", "SX4", "Vitara", "Grand Vitara", "Jimny", "Alto", "Ignis", "Splash"],
    "Dacia": ["Logan", "Duster", "Sandero", "Lodgy", "Dokker"],
    "Mitsubishi": ["Lancer", "Lancer Evolution", "Outlander", "Colt", "Pajero", "L200", "ASX", "Eclipse", "Galant"],
    "Subaru": ["Impreza", "Forester", "Outback", "Legacy", "WRX", "STI", "BRZ", "Crosstrek", "Tribeca"],
    "Chevrolet": ["Silverado", "Cruze", "Malibu", "Impala", "Equinox", "Tahoe", "Suburban", "Traverse", "Sonic", "Spark", "Aveo", "Colorado", "Corvette", "Camaro", "Trailblazer", "Cobalt", "HHR", "S10", "S-10", "Express", "Blazer"],
    "GMC": ["Sierra", "Yukon", "Terrain", "Acadia", "Envoy", "Canyon", "Savana"],
    "Dodge": ["Ram", "Dakota", "Durango", "Charger", "Challenger", "Journey", "Neon", "Caliber", "Avenger", "Caravan", "Grand Caravan"],
    "Ram": ["1500", "2500", "3500", "ProMaster"],
    "Chrysler": ["Town and Country", "Town & Country", "Pacifica", "PT Cruiser", "200", "300", "Sebring"],
    "Jeep": ["Grand Cherokee", "Cherokee", "Wrangler", "Compass", "Patriot", "Liberty", "Renegade", "Gladiator"],
    "Buick": ["LeSabre", "Regal", "Enclave", "Encore", "LaCrosse", "Century"],
    "Cadillac": ["Escalade", "CTS", "DTS", "SRX", "STS", "DeVille"],
    "Pontiac": ["Grand Prix", "Grand Am", "G6", "G5", "Vibe", "Sunfire", "Bonneville"],
    "Saturn": ["Vue", "Ion", "Aura", "SL", "SL2"],
    "Acura": ["TL", "TSX", "MDX", "RDX", "Integra", "RSX"],
    "Lexus": ["RX300", "RX350", "RX400h", "RX450h", "LX470", "IS250", "IS300", "LS400", "ES350", "RX", "IS", "GS", "LS"],
    "Infiniti": ["G35", "G37", "Q50", "QX56", "FX35"],
    "Lincoln": ["Town Car", "Navigator", "MKX", "MKZ"],
    "Mini": ["Cooper", "Countryman", "Clubman"],
    "Porsche": ["911", "944", "Boxster", "Cayman", "Cayenne", "Macan", "Panamera"],
    "Land Rover": ["Range Rover", "Discovery", "Freelander", "Defender", "Range Rover Sport"],
    "Jaguar": ["X-Type", "S-Type", "XF", "XJ", "XE"],
    "Saab": ["9-3", "9-5", "900", "9000"],
    "Tesla": ["Model 3", "Model S", "Model X", "Model Y", "Cybertruck"],
    "Smart": ["Fortwo", "Forfour"],
    "SsangYong": ["Rodius", "Rexton", "Korando"],
    "Isuzu": ["Rodeo", "Trooper", "D-Max"],
    "Alfa Romeo": ["147", "156", "159", "Giulietta", "Giulia", "Mito"],
    "Ferrari": ["F430", "458", "488", "360", "F40", "F50"],
}
ALIASES = {fold(alias): make for make, aliases in MAKES.items() for alias in aliases}
MAKE_RE = re.compile(r"(?<!\w)(" + "|".join(re.escape(a) for a in sorted(ALIASES, key=len, reverse=True)) + r")(?!\w)")
MODEL_RE = {make: re.compile(r"(?<!\w)(" + "|".join(re.escape(fold(m)) for m in sorted(models, key=len, reverse=True)) + r")(?!\w)") for make, models in MODELS.items()}
MODEL_CANON = {make: {fold(m): m for m in models} for make, models in MODELS.items()}
MODEL_ALIASES = {"RAV 4": "RAV4", "X Trail": "X-Trail", "F150": "F-150", "F250": "F-250",
                 "F350": "F-350", "MX5": "MX-5", "RX7": "RX-7", "RX8": "RX-8"}
ROMAN = {str(i): v for i, v in enumerate(["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"])}
GENERIC_GEN = re.compile(r"^\s*[-(]?\s*(?:(?:mk|mark|generation|gen\.?)\s*)?(VIII|VII|III|VI|IV|IX|II|V|X|I|[1-9])(?=$|[\s(),/])", re.I)
# Chassis codes only from text; their relationship to model years is never inferred.
CHASSIS_RE = re.compile(r"\b(?:[EFGW]\d{2,3}|[ABC]\d{1,2}|[A-Z]{1,3}\d{1,3}[A-Z]?|\d[A-Z]\d?|[A-Z]{2,3})\b", re.I)
CHASSIS_ALLOW = set("DAW DA DY GY GF BK BL VQ HD CM CW GK CU ZE JH JA8 FC FN JM LM KC LS PM PN SW BW ZE0U AB10 NHW20 XP10 XP9 T25 T30 J10 NJ10 N68 C06 T98 A05 S93 F08 F68 P12 K12 K11 L15 L1 L2 GB JC GK GE GM GH GD FF FD FE GG GG1 GG2 SF SG SH SJ SK VA VB CG C65 NJ B5 B6 B7 B8 B9 C5 C6 C7 C8 MK7".split())
BODY_REGEX = {
    "sedan": r"\b(?:sedan|saloon|berline|berlina|limousine)\b",
    "estate": r"\b(?:estate|touring|avant|variant|break|wagon|familiar|kombi)\b",
    "hatchback": r"\b(?:hatchback|schragheck|hatch)\b",
    "van": r"\b(?:van|kastenwagen|fourgon|furgoneta|furgon)\b",
    "coupe": r"\bcoupe\b", "convertible": r"\b(?:cabriolet|convertible|cabrio|descapotable)\b",
    "suv": r"\bsuv\b", "pickup": r"\b(?:pick[- ]?up)\b",
}
FUEL_REGEX = {
    "petrol": r"\b(?:petrol|gasoline|essence|gasolina|benzina|benzyna|benzin)\b",
    "diesel": r"\b(?:diesel|gazole|gasoil)\b", "hybrid": r"\b(?:hybrid|hybride|hibrid\w*)\b",
    "electric": r"\b(?:electric|electrique|elektrisch|elektr\w*|electrico)\b",
    "lpg": r"\b(?:lpg|gpl|glp)\b", "ethanol": r"\bethanol\b",
}
ENGINE_RE = re.compile(r"\b(?:[0-8][.,]\d(?:\s*(?:l|litre|liter))?(?:\s*(?:tdi|hdi|cdti|cdi|dci|tdci|tsi|tfsi|gdi|mpi|vtec|ecoboost|jtd|d4d|d-4d|16v|8v|v[468]))?|v[468]|(?:b58|n52|n54|n55|m52|m54|k20|k24|b18)[a-z]?\d{0,2}|[12]jz(?:-g[et]e)?)\b", re.I)
YEAR_RE = re.compile(r"(?<![\w.])((?:19|20)\d{2})(?:\s*[-–/]\s*((?:19|20)\d{2}))?(?!\w)")


def extract_specifications(title):
    text = fold(title)
    found = []
    def add(kind, value, evidence):
        if not any(x["kind"] == kind and x["value"] == value for x in found):
            found.append({"kind": kind, "value": value, "evidence": evidence, "status": "title_mention"})
    for match in re.finditer(r"\b(\d{1,2})\s*w\s*[- /]?\s*(\d{2})(?!\d)", text):
        add("oil_viscosity", f"{match[1]}W-{match[2]}", match[0])
    for match in re.finditer(r"\bsae\s*(20|30|40|50|60)\b", text):
        add("oil_viscosity", "SAE " + match[1], match[0])
    for match in re.finditer(r"\b(?:acea\s*[abc]\d(?:\s*/\s*[abc]?\d)?|api\s*(?:s[a-p]|c[kjifh](-?4)?)|dexos\s*[12]|vw\s*(?:50[0-9]|51[0-9])(?:[. ]?00)?|mb(?:[- ]approval)?\s*22[69][.]\d{1,2}|bmw\s*(?:longlife[- ]?|ll[- ]?)\d{2}(?:\s*fe)?|rn\s*(?:0700|0710|0720|17)|psa\s*b71\s*\d{4}|ford\s*wss[- ]?m2c[- ]?\d{3,4}[a-z]?(?:[- ]?[a-z0-9])?)\b", text):
        add("oil_standard", re.sub(r"\s+", " ", match[0]).upper(), match[0])
    # A chassis code or an episode number is not a fuel label.
    fuel_text = re.sub(
        r"\b(?:s(?:eason)?\s*\d+\s*[-.:]?\s*e(?:pisode)?\s*\d+|(?:episode|ep)\s*\d+)\b",
        " ", text)
    if re.search(r"\b(?:fuel|carburant|essence|sans plomb|unleaded|gasoline|petrol|diesel|ethanol|combustible|combustivel|benzina|benzyna|kraftstoff|octane|sp95|sp98)\b", fuel_text):
        for match in re.finditer(r"\b(?:e5|e10|e85|b7|b10|sp\s*95(?:[- ]?e10)?|sp\s*98|ron\s*(?:91|95|98|100)|(?:95|98)\s*ron)\b", fuel_text):
            add("fuel_grade", re.sub(r"\s+", "", match[0]).upper(), match[0])
    if TASK_REGEX["battery"].search(text):
        for match in re.finditer(r"\b(6|12|24|48)\s*(?:v|volt[s]?)\b", text):
            add("battery_voltage", match[1] + "V", match[0])
    return found


def extract_vehicles(title):
    text = fold(title)
    # The compound model name is unambiguous; do not split arbitrary numeric models.
    text = re.sub(r"(?<!\w)clio(?=[1-5](?!\w|[.,]\d))", "clio ", text)
    matches = list(MAKE_RE.finditer(text))
    vehicles = []
    contexts = []
    inferred_make = False
    if not matches:
        clio_mentions = list(re.finditer(r"(?<!\w)clio\s*(?:iii|iv|ii|v|i|[1-5])(?!\w|[.,]\d)", text))
        if len(clio_mentions) == 1:
            mention = clio_mentions[0]
            contexts.append(("Renault", text[mention.start():], text[max(0, mention.start()-12):mention.start()]))
            inferred_make = True
    for index, mention in enumerate(matches):
        make = ALIASES[mention[0]]
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        segment = text[mention.end():end]
        if index + 1 < len(matches):
            segment = re.sub(r"(?:19|20)\d{2}(?:\s*[-–/]\s*(?:19|20)\d{2})?\s*$", "", segment)
        prefix = text[max(0, mention.start() - 12):mention.start()]
        models = list(MODEL_RE[make].finditer(segment)) if make in MODEL_RE else []
        starts = [m for i, m in enumerate(models) if (i == 0 and m.start() < 30) or
                  (i > 0 and re.search(r"(?:/|\band\b|\bet\b|\by\b|,)\s*$", segment[models[i-1].end():m.start()]))]
        if len(starts) > 1:
            for i, model in enumerate(starts):
                start = 0 if i == 0 else model.start()
                stop = starts[i + 1].start() if i + 1 < len(starts) else len(segment)
                contexts.append((make, segment[start:stop], prefix if i == 0 else ""))
        else:
            contexts.append((make, segment, prefix))
    for make, segment, prefix in contexts:
        # Exclude ambiguous common nouns unless an explicit known model follows.
        model_match = MODEL_RE.get(make).search(segment[:85]) if make in MODEL_RE else None
        if make in {"Mini", "Smart", "SEAT", "Ram"} and (not model_match or model_match.start() > 12):
            continue
        model = MODEL_CANON[make][model_match[0]] if model_match and model_match.start() < 30 else ""
        model = MODEL_ALIASES.get(model, model)
        after_model = segment[model_match.end():] if model and model_match else segment
        gen = ""
        gm = GENERIC_GEN.match(after_model) if make != "BMW" else None
        if gm:
            token = gm[1].upper()
            gen = ROMAN.get(token, token)
        elif make in {"Opel", "Vauxhall"}:
            letter_gen = re.match(r"^\s*[-(]?\s*([A-K])(?=$|[\s(),/])", after_model, re.I)
            if letter_gen:
                gen = letter_gen[1].upper()
        if not gen:
            # Only tightly associated text after the model/make, stopping before tutorial suffix.
            region = re.split(r"\b(?:tutorial|tutoriel|poradnik|anleitung|instruc|wechseln|how|comment)\b", after_model[:32])[0]
            for code in CHASSIS_RE.finditer(region.upper()):
                token = code[0].upper()
                if not model and not (token in CHASSIS_ALLOW or re.fullmatch(r"[EFGW]\d{2,3}", token)):
                    continue
                if (token in CHASSIS_ALLOW or re.fullmatch(r"[EFGW]\d{2,3}", token)
                        or re.fullmatch(r"[ABC]\d", token)
                        or re.fullmatch(r"\d[A-Z]\d", token)
                        or re.fullmatch(r"[A-Z]{1,3}\d{2,3}[A-Z]?", token)):
                    if not ENGINE_RE.fullmatch(token) and token not in {"OBD2", "V6", "V8", "12V", "24V", "48V", "LL04", "LL01", "LL12", "LL17"}:
                        gen = token
                        break
        engine_match = ENGINE_RE.search(after_model)
        engine = re.sub(r"\s+", " ", engine_match[0].upper().replace(",", ".")) if engine_match else ""
        body = next((key for key, pattern in BODY_REGEX.items() if re.search(pattern, segment)), "")
        fuel = next((key for key, pattern in FUEL_REGEX.items() if re.search(pattern, segment)), "")
        # Years must be adjacent to the vehicle designation, not a race/upload date later in a title.
        year_region = after_model.lstrip(" ()-")
        if gm:
            year_region = after_model[gm.end():].lstrip(" ()-")
        elif gen:
            year_region = re.sub(r"^\s*[(]?\s*" + re.escape(gen) + r"[)]?\s*", "", after_model, flags=re.I).lstrip(" ()-")
        suffix_year = YEAR_RE.match(year_region)
        # A year immediately preceding a make belongs to that vehicle.
        prefix_year = re.search(r"((?:19|20)\d{2})(?:\s*[-–/]\s*((?:19|20)\d{2}))?\s*$", prefix)
        year = prefix_year or suffix_year
        year_from = int(year[1]) if year else None
        year_to = int(year[2] or year[1]) if year else None
        if year_from and not (1900 <= year_from <= 2035 and year_from <= year_to <= 2035):
            year_from = year_to = None
        vehicle = {"make": make, "model": model, "generation": gen, "engine": engine,
                   "body_type": body, "fuel_type": fuel, "year_from": year_from, "year_to": year_to,
                   "evidence": title, "status": "inferred_from_unambiguous_model" if inferred_make else "title_mention"}
        if not any(all(v[k] == vehicle[k] for k in ["make", "model", "generation", "engine", "year_from", "year_to"]) for v in vehicles):
            vehicles.append(vehicle)
    return vehicles


def extract_automotive(title, **_ignored):
    text = fold(title)
    tasks = [key for key, pattern in TASK_REGEX.items() if pattern.search(text)]
    if "glow_plugs" in tasks and "spark_plugs" in tasks:
        tasks.remove("spark_plugs")
    if "oil_change" in tasks and not (CHANGE.search(text) or re.search(r"\b(?:vidange|oil change|changing oil)\b", text)):
        tasks.remove("oil_change")
    if "key_battery" in tasks and "battery" in tasks:
        tasks.remove("battery")
    if (WHEEL_OPERATION.search(text) or SPARE_WHEEL.search(text)) and not re.search(r"\b(?:pit[\s-]*stop|steering wheel|wheel drive|wheel locks|volant|volante|lenkrad|bearing\w*|hub\w*|roulement\w*|lozysk\w*|cojinet\w*|rolament\w*|cylind\w*|cilind\w*|zylinder\w*)\b", text) and not any(x in tasks for x in ["wheel_bearing", "tires", "brake_pads", "brake_discs", "brake_caliper", "steering", "suspension_arms", "shock_absorbers", "suspension_springs", "sensors"]):
        tasks.append("wheel_change")
    specs = extract_specifications(title)
    if any(x["kind"] in {"oil_viscosity", "oil_standard"} for x in specs):
        tasks.append("oil_spec")
    elif re.search(r"\b(?:oil (?:grade|viscosity|specification)|viscosite|norme.*huile|grado.*aceite)\b", text):
        tasks.append("oil_spec")
    if any(x["kind"] == "fuel_grade" for x in specs) and "fuel_filter" not in tasks:
        tasks.append("fuel_choice")
    tasks = list(dict.fromkeys(tasks))
    systems = list(dict.fromkeys(x["system"] for x in TASKS if x["id"] in tasks))
    return {"vehicles": extract_vehicles(title), "tasks": tasks, "systems": systems,
            "specifications": specs, "status": "metadata_extraction", "version": VERSION}
