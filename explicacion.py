import math
from typing import Dict, Any, List


class ModuloExplicacion3D:
    """
    Módulo de Explicación Avanzado (v3.0):
    - Árbol Causal de Inferencia
    - Evaluación Difusa (Fuzzy Logic) y Factor de Certeza (Certainty Factor)
    - Generador de Grafo Causal (Mermaid/Texto) y Reporte Markdown
    """

    @staticmethod
    def calcular_logica_difusa_y_certeza(
        memoria_final: Dict[str, Any],
        horas_totales: float,
        alertas: List[Dict[str, str]],
        costo_base: float,
    ) -> Dict[str, Any]:
        """
        Aplica funciones de pertenencia trapezoidal/triangular sobre la complejidad
        y calcula el Factor de Certeza (CF) estilo MYCIN.
        """
        accesorios = float(memoria_final.get("cantidad_accesorios", 0))

        # Grados de pertenencia difusa (0.0 a 1.0) para densidad de accesorios
        mu_bajo = max(0.0, min(1.0, (3.0 - accesorios) / 3.0)) if accesorios <= 3 else 0.0
        mu_medio = max(0.0, min((accesorios - 1.0) / 2.0, (6.0 - accesorios) / 2.0)) if 1 < accesorios < 6 else 0.0
        mu_alto = max(0.0, min(1.0, (accesorios - 4.0) / 4.0)) if accesorios > 4 else 0.0

        # Ajuste fino difuso por interpolación continua (\$8 USD por pieza suavizada)
        ajuste_difuso = round((mu_medio * 12.0) + (mu_alto * 28.0), 2)

        # Cálculo del Factor de Certeza (CF inicial = 0.95)
        cf = 0.95
        if memoria_final.get("complejidad") == "high_poly":
            cf -= 0.06  # Esculpido orgánico/denso tiene mayor variabilidad artística
        if memoria_final.get("animacion"):
            cf -= 0.05  # Ciclos de animación pueden requerir iteraciones extra
        if accesorios > 5:
            cf -= 0.05

        # Penalizar certeza si existen alertas de tipo warning
        warnings = sum(1 for a in alertas if a.get("nivel") == "warning")
        cf -= warnings * 0.08
        cf = round(max(0.60, min(0.98, cf)), 2)

        # Rango de estimación basado en la incertidumbre (1 - CF)
        margen = 1.0 - cf
        rango_min = round(costo_base * (1.0 - (margen * 0.5)), 2)
        rango_max = round(costo_base * (1.0 + margen), 2)

        etiqueta_difusa = "Baja"
        if mu_alto >= mu_medio and mu_alto > mu_bajo:
            etiqueta_difusa = f"Alta ({int(mu_alto * 100)}%)"
        elif mu_medio > mu_bajo:
            etiqueta_difusa = f"Media ({int(mu_medio * 100)}%)"
        else:
            etiqueta_difusa = f"Baja ({int(mu_bajo * 100)}%)"

        return {
            "certeza_porcentaje": int(cf * 100),
            "rango_min": rango_min,
            "rango_max": rango_max,
            "ajuste_difuso": ajuste_difuso,
            "densidad_difusa": etiqueta_difusa,
            "pertenencia": {
                "bajo": round(mu_bajo, 2),
                "medio": round(mu_medio, 2),
                "alto": round(mu_alto, 2),
            },
        }

    @staticmethod
    def generar_grafo_causal(
        hechos_deducidos: List[Dict[str, Any]],
        reglas_aplicadas: List[Dict[str, Any]],
    ) -> List[str]:
        """Construye las cadenas causales legibles del encadenamiento hacia adelante."""
        cadenas = []
        for h in hechos_deducidos:
            regla_origen = h["deducido_por"].split(" ")[0]
            # Buscar qué reglas posteriores consumieron este hecho deducido
            consumidores = [
                r["id"]
                for r in reglas_aplicadas
                if any(h["clave"] in dep for dep in r.get("dependencias", []))
            ]
            if consumidores:
                cadenas.append(
                    f"Cliente → [{regla_origen}] deduce ({h['clave']}={h['valor']}) ➔ dispara {', '.join(consumidores)}"
                )
            else:
                cadenas.append(
                    f"Cliente → [{regla_origen}] deduce ({h['clave']}={h['valor']})"
                )
        return cadenas

    @staticmethod
    def generar_markdown(informe: Dict[str, Any]) -> str:
        """Exporta el dictamen completo del Sistema Experto en formato Markdown."""
        md = [
            "# Dictamen Técnico de Cotización 3D (Sistema Experto v3.0)",
            f"**Precio Estimado:** \${informe['costo_total']:.2f} USD *(Rango: ${informe['fuzzy']['rango_min']:.2f} -${informe['fuzzy']['rango_max']:.2f} USD)*",
            f"**Factor de Certeza (CF):** {informe['fuzzy']['certeza_porcentaje']}% | **Esfuerzo:** {informe['horas_totales']}h | **Entrega:** {informe['dias_estimados']} día(s)",
            "\n## 1. Cadena Causal de Inferencia (Forward Chaining)",
        ]
        if informe["grafo_causal"]:
            for c in informe["grafo_causal"]:
                md.append(f"- `{c}`")
        else:
            md.append("- Inferencia directa de nivel 1 (sin hechos intermedios).")

        md.append("\n## 2. Reglas Activadas")
        for r in informe["reglas_aplicadas"]:
            md.append(f"- **[{r['id']}] {r['nombre']}** (Fase {r['fase']}) → Subtotal: `${r['subtotal_acumulado']:.2f} USD`")
            for d in r["detalles"]:
                md.append(f"  - {d}")

        if informe.get("recomendaciones_presupuesto"):
            md.append("\n## 3. Optimización Hacia Atrás (Backward Chaining)")
            for rec in informe["recomendaciones_presupuesto"]:
                md.append(f"- {rec}")

        return "\n".join(md)

    @staticmethod
    def generar_informe(
        hechos_iniciales: Dict[str, Any],
        memoria_final: Dict[str, Any],
        origen_hechos: Dict[str, str],
        reglas_aplicadas: List[Dict[str, Any]],
        horas_por_depto: Dict[str, float],
        alertas: List[Dict[str, str]],
        costo_total: float,
        recomendaciones_presupuesto: List[str] = None,
    ) -> Dict[str, Any]:
        hechos_deducidos = []
        for clave, valor in memoria_final.items():
            origen = origen_hechos.get(clave, "Cliente")
            if origen != "Cliente":
                hechos_deducidos.append({
                    "clave": clave,
                    "valor": valor,
                    "deducido_por": origen,
                })

        horas_totales = round(sum(horas_por_depto.values()), 1)
        urgencia = memoria_final.get("urgencia", "normal")

        horas_por_dia = 6.0
        if urgencia == "alta":
            horas_por_dia = 8.0
        elif urgencia == "express":
            horas_por_dia = 11.0

        dias_estimados = max(1, math.ceil(horas_totales / horas_por_dia)) if horas_totales > 0 else 1

        alertas_finales = list(alertas)
        if urgencia == "express" and horas_totales >= 22:
            alertas_finales.append({
                "nivel": "warning",
                "regla": "CRONOGRAMA",
                "mensaje": f"Riesgo de Cronograma: El proyecto requiere {horas_totales}h técnicas. En modalidad Express exigirá al menos {dias_estimados} días intensivos.",
            })

        fuzzy_data = ModuloExplicacion3D.calcular_logica_difusa_y_certeza(
            memoria_final, horas_totales, alertas_finales, costo_total
        )
        grafo_causal = ModuloExplicacion3D.generar_grafo_causal(
            hechos_deducidos, reglas_aplicadas
        )

        informe = {
            "costo_total": costo_total,
            "horas_totales": horas_totales,
            "dias_estimados": dias_estimados,
            "horas_por_departamento": horas_por_depto,
            "hechos_iniciales": hechos_iniciales,
            "hechos_deducidos": hechos_deducidos,
            "alertas": alertas_finales,
            "reglas_aplicadas": reglas_aplicadas,
            "fuzzy": fuzzy_data,
            "grafo_causal": grafo_causal,
            "recomendaciones_presupuesto": recomendaciones_presupuesto or [],
        }
        informe["reporte_markdown"] = ModuloExplicacion3D.generar_markdown(informe)
        return informe


class Explicador:
    """Clase de compatibilidad para reportes básicos."""

    def generar_reporte(self, precio_final: float, reglas_aplicadas: List[Dict[str, Any]]) -> str:
        reporte = f"=== COTIZACIÓN DE PROYECTO 3D: \${precio_final:.2f} USD ===\n\n"
        for regla in reglas_aplicadas:
            reporte += f"- [{regla.get('id')}] {regla.get('nombre')}\n"
        return reporte