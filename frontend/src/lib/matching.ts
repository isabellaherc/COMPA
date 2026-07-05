import type { OpportunityMatch, Oportunidad, Productor, Proveedor } from "@/types/domain";

export function getOpportunityMatches(
  productor: Productor,
  oportunidades: Oportunidad[],
): OpportunityMatch[] {
  return oportunidades
    .map((oportunidad) => {
      const exact = oportunidad.rubroRequerido === productor.rubro;
      const sharedWord = oportunidad.rubroRequerido
        .toLowerCase()
        .includes(productor.rubro.split(" ")[0].toLowerCase());
      const score = exact ? 100 : sharedWord ? 70 : 38;

      return {
        ...oportunidad,
        score,
        reason: exact
          ? "Rubro exacto y capacidad compatible"
          : sharedWord
            ? "Rubro parcialmente relacionado"
            : "Baja afinidad con el perfil",
      };
    })
    .filter((match) => match.score >= 60)
    .sort((a, b) => b.score - a.score || b.monto - a.monto);
}

export function getCompatibleSuppliers(
  productor: Productor,
  proveedores: Proveedor[],
): Proveedor[] {
  return proveedores.filter((proveedor) => proveedor.rubro === productor.rubro);
}
