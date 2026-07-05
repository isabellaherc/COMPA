export type Rubro =
  | "Alimentos y Bebidas"
  | "Textiles y Uniformes"
  | "Construccion y Mantenimiento"
  | "Suministros Agricolas"
  | "Mobiliario y Equipo"
  | "Tecnologia y Servicios Digitales"
  | "Servicios de Limpieza y Mantenimiento"
  | "Transporte y Logistica"
  | "Imprenta y Publicidad";

export type Productor = {
  id: string;
  nombre: string;
  rubro: Rubro;
  ubicacion: string;
  capacidad: string;
  telefono: string;
  experienciaEstado: string;
  ingresoMensual: number;
  nombreNegocio: string;
  antiguedadAnos: number;
  empleados: number;
};

export type Oportunidad = {
  id: string;
  titulo: string;
  institucion: string;
  monto: number;
  fechaCierre: string;
  rubroRequerido: Rubro;
  unspscCode: string;
  urlFuente: string;
  tipoContratacion: string;
};

export type Proveedor = {
  id: string;
  nombre: string;
  rubro: Rubro;
  ubicacion: string;
  capacidad: string;
  telefono: string;
  personalidad: "estrategico" | "agresivo" | "conservador";
};

export type PreguntaDura = {
  pregunta: string;
  intencion: string;
  palabrasClave: string[];
};

export type OpportunityMatch = Oportunidad & {
  score: number;
  reason: string;
};
