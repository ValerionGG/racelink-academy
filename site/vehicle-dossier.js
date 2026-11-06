import {vehicleIndex} from './atlas/index.js?v=41';
import {matchCars,carHref} from './atlas/search.js?v=41';
// Dossiers are separate from tutorial results and retain their source-dated scope.
export function matchVehicleDossiers(query,filters={}) {
  return matchCars(vehicleIndex,query,filters).map(hit=>({
    type:'vehicle-dossier',id:hit.model.id,
    label:`${hit.model.make} ${hit.model.model} ${hit.model.generation} · ${hit.model.year}`,
    href:carHref(hit),photo:hit.model.photo||'',immersive:hit.model.hasImmersive,
  }));
}
export const resolveClioDossier=(query,filters={})=>matchVehicleDossiers(query,filters).find(m=>m.id==='renault-clio-v')?.href||null;
export const showClioDossier=(query,filters={})=>Boolean(resolveClioDossier(query,filters));
