from abc import ABC, abstractmethod
from django.db.models import Count, Sum
from .models import Cita, Campana, PuntoVacunacion, Almacenamiento, Vacunacion


# ─── PRODUCTO ────────────────────────────────────────────────────────────────
class Reporte:
    """El objeto final que se construye paso a paso."""
    def __init__(self):
        self.titulo = ""
        self.grafico = None       # datos para un gráfico de barras
        self.tabla = None         # filas de tabla
        self.puntos_vacunacion = None  # resumen por punto
        self.adherencia = None    # % adherencia a campaña

    def __repr__(self):
        secciones = [k for k, v in self.__dict__.items() if v is not None and k != "titulo"]
        return f"Reporte('{self.titulo}', secciones={secciones})"


# ─── INTERFAZ BUILDER ────────────────────────────────────────────────────────
class ReporteBuilder(ABC):
    @abstractmethod
    def set_titulo(self, titulo: str): pass

    @abstractmethod
    def build_grafico(self, campana_id: int): pass

    @abstractmethod
    def build_tabla(self, campana_id: int): pass

    @abstractmethod
    def build_puntos_vacunacion(self, campana_id: int): pass

    @abstractmethod
    def build_adherencia(self, campana_id: int): pass

    @abstractmethod
    def get_reporte(self) -> Reporte: pass
    
# ─── BUILDER CONCRETO ────────────────────────────────────────────────────────
class ReporteCampanaBuilder(ReporteBuilder):
    """
    Builder concreto que obtiene datos reales desde los modelos Django.
    """
    def __init__(self):
        self._reporte = Reporte()

    def set_titulo(self, titulo: str):
        self._reporte.titulo = titulo
        return self  # permite encadenamiento opcional

    def build_grafico(self, campana_id: int):
        """
        Gráfico de barras: citas por estado (Agendada, Cancelada, Vacunado).
        """
        datos = (
            Cita.objects
            .filter(campana_id=campana_id)
            .values('estado')
            .annotate(total=Count('id_cita'))
            .order_by('estado')
        )
        self._reporte.grafico = {
            "tipo": "barras",
            "etiquetas": [d['estado'] for d in datos],
            "valores":   [d['total']  for d in datos],
        }
        return self

    def build_tabla(self, campana_id: int):
        """
        Tabla de asistencia: lista de citas con persona, punto y estado.
        """
        citas = (
            Cita.objects
            .filter(campana_id=campana_id)
            .select_related('persona', 'punto_vacunacion')
            .values(
                'id_cita',
                'persona__nombres',
                'persona__apellidos',
                'punto_vacunacion__nombre',
                'fecha_hora',
                'estado',
            )
        )
        self._reporte.tabla = {
            "columnas": ["ID", "Paciente", "Centro", "Fecha/Hora", "Estado"],
            "filas": [
                [
                    c['id_cita'],
                    f"{c['persona__nombres']} {c['persona__apellidos']}",
                    c['punto_vacunacion__nombre'],
                    c['fecha_hora'].strftime('%d/%m/%Y %H:%M'),
                    c['estado'],
                ]
                for c in citas
            ],
        }
        return self

    def build_puntos_vacunacion(self, campana_id: int):
        """
        Stock disponible por punto de vacunación en esta campaña.
        """
        puntos = (
            PuntoVacunacion.objects
            .filter(campanas__id_campana=campana_id)
            .prefetch_related('inventarios__tipo_vacuna')
        )
        resumen = []
        for p in puntos:
            stock_total = sum(
                inv.stock_disponible for inv in p.inventarios.all()
            )
            resumen.append({
                "punto":  p.nombre,
                "comuna": p.comuna,
                "stock":  stock_total,
            })
        self._reporte.puntos_vacunacion = resumen
        return self

    def build_adherencia(self, campana_id: int):
        """
        % de citas que terminaron en vacunación efectiva.
        """
        total    = Cita.objects.filter(campana_id=campana_id).count()
        vacunados = Cita.objects.filter(campana_id=campana_id, estado='Vacunado').count()
        porcentaje = round((vacunados / total * 100), 1) if total > 0 else 0
        self._reporte.adherencia = {
            "total_citas":   total,
            "vacunados":     vacunados,
            "porcentaje":    porcentaje,
        }
        return self

    def get_reporte(self) -> Reporte:
        return self._reporte
# ─── DIRECTOR ────────────────────────────────────────────────────────────────
class DirectorReportes:
    """
    Ordena al Builder los pasos según el tipo de reporte pedido.
    No construye nada por sí mismo.
    """
    def __init__(self, builder: ReporteBuilder):
        self._builder = builder

    def reporte_completo(self, campana_id: int, nombre_campana: str) -> Reporte:
        """Todas las secciones: para el administrador general."""
        self._builder.set_titulo(f"Informe Completo — {nombre_campana}")
        self._builder.build_grafico(campana_id)
        self._builder.build_tabla(campana_id)
        self._builder.build_puntos_vacunacion(campana_id)
        self._builder.build_adherencia(campana_id)
        return self._builder.get_reporte()

    def reporte_stock(self, campana_id: int, nombre_campana: str) -> Reporte:
        """Solo stock por punto: para coordinadores de bodega."""
        self._builder.set_titulo(f"Informe de Stock — {nombre_campana}")
        self._builder.build_puntos_vacunacion(campana_id)
        self._builder.build_grafico(campana_id)
        return self._builder.get_reporte()

    def reporte_adherencia(self, campana_id: int, nombre_campana: str) -> Reporte:
        """Solo adherencia: para enviar cifras al gobierno."""
        self._builder.set_titulo(f"Informe de Adherencia — {nombre_campana}")
        self._builder.build_adherencia(campana_id)
        return self._builder.get_reporte()