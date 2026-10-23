import json
import os
from typing import Dict, Any, List, Tuple
from explicacion import ModuloExplicacion3D


class MotorInferencia3D:
    def __init__(self, ruta_reglas: str = "conocimiento/reglas.json"):
        if not os.path.isabs(ruta_reglas):
            ruta_base = os.path.dirname(os.path.abspath(__file__))
            ruta_candidata = os.path.join(ruta_base, ruta_reglas)
            if os.path.exists(ruta_candidata):
                ruta_reglas = ruta_candidata

        self.ruta_reglas = ruta_reglas
        self.base_conocimiento = self._cargar_reglas()
        self.reglas = self.base_conocimiento.get("reglas", [])
        self.ultimo_informe: Dict[str, Any] = {}

    def _cargar_reglas(self) -> Dict[str, Any]:
        if not os.path.exists(self.ruta_reglas):
            raise FileNotFoundError(
                f"No se encontró la base de conocimientos en: {self.ruta_reglas}"
            )
        with open(self.ruta_reglas, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    def _normalizar_hechos(self, hechos_cliente: Dict[str, Any]) -> Dict[str, Any]:
        hechos = {}
        mapa_claves = {
            "texturas": "texturizado",
            "archivos_fuente": "entrega_archivos_fuente",
        }
        mapa_valores = {
            "prop": "prop",
            "objeto": "prop",
            "entorno": "entorno",
            "escenario": "entorno",
            "personaje": "personaje",
            "criatura": "personaje",
            "low poly": "low_poly",
            "low_poly": "low_poly",
            "mid poly": "mid_poly",
            "mid_poly": "mid_poly",
            "high poly": "high_poly",
            "high_poly": "high_poly",
            "esculpido": "high_poly",
            "sin texturas": "sin_texturas",
            "sin_texturas": "sin_texturas",
            "colores planos": "colores_planos",
            "colores_planos": "colores_planos",
            "pbr": "pbr_completo",
            "pbr completo": "pbr_completo",
            "pbr_completo": "pbr_completo",
        }

        for clave, valor in hechos_cliente.items():
            clave_norm = clave.strip().lower()
            clave_final = mapa_claves.get(clave_norm, clave_norm)

            if clave_final == "comercial" and isinstance(valor, bool):
                hechos["uso"] = "comercial" if valor else "personal"
                continue

            if isinstance(valor, str):
                valor_norm = valor.strip().lower()
                hechos[clave_final] = mapa_valores.get(valor_norm, valor_norm)
            else:
                hechos[clave_final] = valor

        hechos.setdefault("destino", "videojuego")
        hechos.setdefault("rigging", False)
        hechos.setdefault("rig_facial", False)
        hechos.setdefault("animacion", False)
        hechos.setdefault("cantidad_accesorios", 0)
        hechos.setdefault("entrega_archivos_fuente", False)
        hechos.setdefault("uso", "personal")
        hechos.setdefault("urgencia", "normal")

        return hechos

    def _evaluar_condicion(self, condicion: Dict[str, Any], hechos: Dict[str, Any]) -> bool:
        clave = condicion["hecho"]
        if clave not in hechos:
            return False

        op = condicion["operador"]
        actual = hechos[clave]
        esperado = condicion["valor"]

        if op == "==":
            return actual == esperado
        elif op == "!=":
            return actual != esperado
        elif op == ">":
            return actual > esperado
        elif op == "<":
            return actual < esperado
        elif op == ">=":
            return actual >= esperado
        elif op == "<=":
            return actual <= esperado
        return False

    def _cumple_regla(self, regla: Dict[str, Any], hechos: Dict[str, Any]) -> bool:
        return all(self._evaluar_condicion(c, hechos) for c in regla.get("condiciones", []))

    def _ejecutar_inferencia_pura(self, hechos_iniciales: Dict[str, Any]) -> Tuple[float, Dict[str, Any], Dict[str, str], List[Dict[str, Any]], Dict[str, float], List[Dict[str, str]]]:
        """Ejecuta el ciclo Forward Chaining sin efectos secundarios para permitir simulaciones."""
        memoria_trabajo = dict(hechos_iniciales)
        origen_hechos = {k: "Cliente" for k in memoria_trabajo}

        reglas_disparadas_ids = set()
        historial_reglas = []

        while True:
            agenda = []
            for regla in self.reglas:
                if regla["id"] not in reglas_disparadas_ids and self._cumple_regla(regla, memoria_trabajo):
                    agenda.append(regla)

            if not agenda:
                break

            agenda.sort(
                key=lambda r: (
                    r.get("fase", 1),
                    r.get("prioridad", 99),
                    -len(r.get("condiciones", [])),
                )
            )

            regla_ganadora = agenda[0]
            reglas_disparadas_ids.add(regla_ganadora["id"])

            for accion in regla_ganadora.get("acciones", []):
                if accion["tipo"] == "agregar_hecho":
                    clave_nueva = accion["clave"]
                    memoria_trabajo[clave_nueva] = accion["valor"]
                    origen_hechos[clave_nueva] = f"{regla_ganadora['id']} ({regla_ganadora['nombre']})"

            historial_reglas.append(regla_ganadora)

        historial_reglas.sort(key=lambda r: (r.get("fase", 1), r.get("prioridad", 99)))

        precio_actual = 0.0
        horas_por_depto = {
            "modelado": 0.0,
            "texturizado": 0.0,
            "rigging": 0.0,
            "animacion": 0.0,
            "optimizacion": 0.0,
        }
        alertas = []
        reglas_aplicadas_explicacion = []

        for regla in historial_reglas:
            impacto_regla = []
            horas_regla = 0.0

            dependencias = []
            for cond in regla.get("condiciones", []):
                creador = origen_hechos.get(cond["hecho"], "Cliente")
                if creador != "Cliente":
                    dependencias.append(f"{cond['hecho']} ← {creador.split(' ')[0]}")

            for accion in regla.get("acciones", []):
                tipo = accion["tipo"]

                if tipo in ("sumar_costo", "sumar_horas"):
                    monto = float(accion.get("costo", accion.get("valor", 0.0)))
                    horas = float(accion.get("horas", 0.0))
                    depto = accion.get("departamento", "modelado")

                    precio_actual += monto
                    horas_regla += horas
                    if depto in horas_por_depto:
                        horas_por_depto[depto] += horas

                    prefijo_h = f"[{horas:g}h {depto}] " if horas > 0 else ""
                    impacto_regla.append(f"+${monto:.2f} · {prefijo_h}{accion['concepto']}")

                elif tipo == "aplicar_multiplicador":
                    factor = float(accion["valor"])
                    aumento = precio_actual * (factor - 1.0)
                    precio_actual *= factor
                    porcentaje = round((factor - 1.0) * 100)
                    impacto_regla.append(
                        f"+{porcentaje}% (+${aumento:.2f}) · {accion['concepto']}"
                    )

                elif tipo == "agregar_hecho":
                    impacto_regla.append(
                        f"Hecho deducido: {accion['clave']} = {accion['valor']}"
                    )

                elif tipo in ("agregar_nota", "agregar_alerta"):
                    msg = accion["mensaje"]
                    nivel = accion.get("nivel", "info")
                    alertas.append({"nivel": nivel, "mensaje": msg, "regla": regla["id"]})
                    impacto_regla.append(f"Nota: {msg}")

            reglas_aplicadas_explicacion.append({
                "id": regla["id"],
                "nombre": regla["nombre"],
                "fase": regla.get("fase", 1),
                "prioridad": regla.get("prioridad", 99),
                "especificidad": len(regla.get("condiciones", [])),
                "dependencias": dependencias,
                "horas": horas_regla,
                "detalles": impacto_regla,
                "subtotal_acumulado": round(precio_actual, 2),
            })

        return (
            round(precio_actual, 2),
            memoria_trabajo,
            origen_hechos,
            reglas_aplicadas_explicacion,
            horas_por_depto,
            alertas,
        )

    def optimizar_presupuesto(self, hechos_iniciales: Dict[str, Any], costo_actual: float, presupuesto_max: float) -> List[str]:
        """
        Encadenamiento Hacia Atrás (Backward Chaining):
        Busca qué hipótesis/hechos del cliente modificar para alcanzar la meta (costo <= presupuesto_max).
        """
        if presupuesto_max <= 0 or costo_actual <= presupuesto_max:
            return []

        candidatos_recorte = [
            ("urgencia", "normal", "Cambiar Urgencia a 'Normal'"),
            ("entrega_archivos_fuente", False, "Desactivar 'Entrega de Archivos Fuente'"),
            ("complejidad", "mid_poly", "Reducir Complejidad a 'Mid Poly'"),
            ("complejidad", "low_poly", "Reducir Complejidad a 'Low Poly'"),
            ("texturizado", "colores_planos", "Cambiar Texturizado a 'Colores Planos'"),
            ("rig_facial", False, "Omitir 'Rigging Facial'"),
            ("animacion", False, "Omitir 'Animación'"),
            ("cantidad_accesorios", 0, "Reducir 'Accesorios Extra' a 0"),
        ]

        recomendaciones = []
        # Evaluamos cambios individuales
        for clave, valor_alt, descripcion in candidatos_recorte:
            if hechos_iniciales.get(clave) != valor_alt:
                simulacion = dict(hechos_iniciales)
                simulacion[clave] = valor_alt
                nuevo_costo, *_ = self._ejecutar_inferencia_pura(simulacion)
                ahorro = round(costo_actual - nuevo_costo, 2)
                if ahorro > 0:
                    cumple = "¡Cumple tu presupuesto!" if nuevo_costo <= presupuesto_max else f"Quedaría en ${nuevo_costo:.2f}"
                    recomendaciones.append(
                        f"{descripcion} → Ahorras ${ahorro:.2f} USD ({cumple})"
                    )

        return recomendaciones[:4]

    def cotizar(self, hechos_cliente: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        hechos_iniciales = self._normalizar_hechos(hechos_cliente)
        presupuesto_max = float(hechos_cliente.get("presupuesto_max", 0) or 0)

        (
            costo_total,
            memoria_trabajo,
            origen_hechos,
            reglas_aplicadas_explicacion,
            horas_por_depto,
            alertas,
        ) = self._ejecutar_inferencia_pura(hechos_iniciales)

        recomendaciones = self.optimizar_presupuesto(
            hechos_iniciales, costo_total, presupuesto_max
        )

        self.ultimo_informe = ModuloExplicacion3D.generar_informe(
            hechos_iniciales=hechos_iniciales,
            memoria_final=memoria_trabajo,
            origen_hechos=origen_hechos,
            reglas_aplicadas=reglas_aplicadas_explicacion,
            horas_por_depto=horas_por_depto,
            alertas=alertas,
            costo_total=costo_total,
            recomendaciones_presupuesto=recomendaciones,
        )

        return costo_total, reglas_aplicadas_explicacion

    def cotizar_detallado(self, hechos_cliente: Dict[str, Any]) -> Dict[str, Any]:
        self.cotizar(hechos_cliente)
        return self.ultimo_informe

    def agregar_regla_nueva(self, datos_regla: Dict[str, Any]) -> Dict[str, Any]:
        """
        Módulo de Adquisición de Conocimiento:
        Valida y guarda una nueva regla en conocimiento/reglas.json manteniendo 1 regla por línea.
        """
        nuevo_id = f"R{len(self.reglas) + 1:02d}"
        nueva_regla = {
            "id": nuevo_id,
            "nombre": datos_regla.get("nombre", "Regla personalizada").strip(),
            "fase": int(datos_regla.get("fase", 3)),
            "prioridad": int(datos_regla.get("prioridad", 6)),
            "condiciones": [
                {
                    "hecho": datos_regla["hecho"],
                    "operador": datos_regla.get("operador", "=="),
                    "valor": datos_regla["valor_condicion"],
                }
            ],
            "acciones": [
                {
                    "tipo": "sumar_horas",
                    "departamento": datos_regla.get("departamento", "modelado"),
                    "horas": float(datos_regla.get("horas", 2)),
                    "costo": float(datos_regla.get("costo", 30.0)),
                    "concepto": datos_regla.get("concepto", "Cargo técnico adicional"),
                }
            ],
        }

        self.reglas.append(nueva_regla)
        self.base_conocimiento["metadata"]["total_reglas"] = len(self.reglas)

        # Guardar con formato exacto de 1 regla por línea
        lineas_reglas = [
            "    " + json.dumps(r, ensure_ascii=False) for r in self.reglas
        ]
        contenido_json = (
            "{\n"
            f'  "metadata": {json.dumps(self.base_conocimiento["metadata"], ensure_ascii=False)},\n'
            '  "reglas": [\n'
            + ",\n".join(lineas_reglas)
            + "\n  ]\n}\n"
        )

        with open(self.ruta_reglas, "w", encoding="utf-8") as f:
            f.write(contenido_json)

        return nueva_regla