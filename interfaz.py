import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from motor import MotorInferencia3D

RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_REGLAS = os.path.join(RUTA_BASE, "conocimiento", "reglas.json")
motor = MotorInferencia3D(RUTA_REGLAS)

HTML_UI = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Experto 3D v3.0 — Cotizador e Inferencia</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #fafafa; color: #18181b; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .pill-btn { transition: all 0.15s ease; }
        .pill-btn.active {
            background-color: #18181b;
            color: #ffffff;
            border-color: #18181b;
        }
        input[type="range"] { accent-color: #18181b; }
    </style>
</head>
<body class="antialiased selection:bg-zinc-900 selection:text-white">

    <div class="max-w-6xl mx-auto px-6 py-10 md:py-12">

        <!-- Encabezado Minimalista -->
        <header class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-zinc-200 pb-6 mb-8 gap-4">
            <div>
                <div class="flex items-center gap-2.5">
                    <h1 class="text-xl font-semibold tracking-tight text-zinc-900">Sistema Experto de Cotización y Pipeline 3D</h1>
                    <span id="badge-total-reglas" class="text-[11px] mono px-2 py-0.5 rounded bg-zinc-900 text-white font-medium">32 Reglas</span>
                    <span class="text-[11px] mono px-2 py-0.5 rounded bg-zinc-200/80 text-zinc-700">v3.0 Hybrid + Fuzzy</span>
                </div>
                <p class="text-sm text-zinc-500 mt-1">Forward & Backward Chaining · Factores de Certeza · Adquisición de Conocimiento</p>
            </div>
            <div class="flex items-center gap-3 self-start sm:self-auto">
                <button onclick="abrirModalRegla()" class="text-xs font-medium px-3 py-1.5 rounded-lg border border-zinc-300 bg-white hover:border-zinc-900 transition">
                    + Nueva Regla
                </button>
                <button onclick="exportarMarkdown()" class="text-xs font-medium px-3 py-1.5 rounded-lg bg-zinc-900 text-white hover:bg-zinc-800 transition">
                    Exportar .MD
                </button>
                <button onclick="reiniciar()" class="text-xs font-medium text-zinc-500 hover:text-zinc-900 transition-colors underline underline-offset-4 ml-1">
                    Restablecer
                </button>
            </div>
        </header>

        <!-- Grid Principal -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">

            <!-- COLUMNA IZQUIERDA: Hechos de Entrada (6 columnas) -->
            <div class="lg:col-span-6 space-y-6">

                <!-- 1. Destino / Plataforma -->
                <div>
                    <div class="flex justify-between items-baseline mb-2">
                        <label class="text-xs font-medium uppercase tracking-wider text-zinc-400">1. Plataforma / Destino Técnico</label>
                        <span class="text-[11px] text-zinc-400">Fase 1: Restricciones</span>
                    </div>
                    <div class="grid grid-cols-3 gap-2" data-group="destino">
                        <button type="button" onclick="setOpcion('destino', 'videojuego', this)" class="pill-btn active border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            Videojuego / Real-Time
                        </button>
                        <button type="button" onclick="setOpcion('destino', 'cine_vfx', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            Cine / Render VFX
                        </button>
                        <button type="button" onclick="setOpcion('destino', 'impresion_3d', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            Impresión 3D (STL)
                        </button>
                    </div>
                </div>

                <!-- 2. Categoría -->
                <div>
                    <label class="block text-xs font-medium uppercase tracking-wider text-zinc-400 mb-2">2. Categoría del Modelo</label>
                    <div class="grid grid-cols-3 gap-2" data-group="categoria">
                        <button type="button" onclick="setOpcion('categoria', 'prop', this)" class="pill-btn active border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            Prop / Objeto
                        </button>
                        <button type="button" onclick="setOpcion('categoria', 'entorno', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            Entorno / Escenario
                        </button>
                        <button type="button" onclick="setOpcion('categoria', 'personaje', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            Personaje / Criatura
                        </button>
                    </div>
                </div>

                <!-- 3. Complejidad Geométrica -->
                <div>
                    <label class="block text-xs font-medium uppercase tracking-wider text-zinc-400 mb-2">3. Complejidad Geométrica</label>
                    <div class="grid grid-cols-3 gap-2" data-group="complejidad">
                        <button type="button" onclick="setOpcion('complejidad', 'low_poly', this)" class="pill-btn active border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            Low Poly
                        </button>
                        <button type="button" onclick="setOpcion('complejidad', 'mid_poly', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            Mid Poly
                        </button>
                        <button type="button" onclick="setOpcion('complejidad', 'high_poly', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            High Poly / Sculpt
                        </button>
                    </div>
                </div>

                <!-- 4. Texturizado -->
                <div>
                    <label class="block text-xs font-medium uppercase tracking-wider text-zinc-400 mb-2">4. Nivel de Texturizado</label>
                    <div class="grid grid-cols-3 gap-2" data-group="texturizado">
                        <button type="button" onclick="setOpcion('texturizado', 'sin_texturas', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            Sin Texturas
                        </button>
                        <button type="button" onclick="setOpcion('texturizado', 'colores_planos', this)" class="pill-btn active border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            Colores Planos
                        </button>
                        <button type="button" onclick="setOpcion('texturizado', 'pbr_completo', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                            PBR Completo
                        </button>
                    </div>
                </div>

                <!-- 5. Deslizador de Sub-objetos con Lógica Difusa -->
                <div class="bg-white border border-zinc-200 rounded-xl p-4">
                    <div class="flex justify-between items-center mb-2">
                        <label class="text-xs font-medium uppercase tracking-wider text-zinc-500">5. Accesorios Extra (Evaluación Difusa)</label>
                        <div class="flex items-center gap-2">
                            <span id="lbl-fuzzy" class="text-[11px] mono text-zinc-500">Densidad: Baja</span>
                            <span id="lbl-accesorios" class="text-xs mono font-semibold text-zinc-900 bg-zinc-100 px-2 py-0.5 rounded">0 piezas</span>
                        </div>
                    </div>
                    <input type="range" id="cantidad_accesorios" min="0" max="10" value="0" oninput="actualizarSlider(this.value)" class="w-full h-1.5 bg-zinc-200 rounded-lg cursor-pointer">
                </div>

                <!-- 6. Licencia y Urgencia -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div>
                        <label class="block text-xs font-medium uppercase tracking-wider text-zinc-400 mb-2">6. Derechos de Uso</label>
                        <div class="grid grid-cols-2 gap-2" data-group="uso">
                            <button type="button" onclick="setOpcion('uso', 'personal', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                                Personal
                            </button>
                            <button type="button" onclick="setOpcion('uso', 'comercial', this)" class="pill-btn active border border-zinc-200 bg-white rounded-lg py-2.5 px-3 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                                Comercial
                            </button>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-medium uppercase tracking-wider text-zinc-400 mb-2">7. Urgencia</label>
                        <div class="grid grid-cols-3 gap-2" data-group="urgencia">
                            <button type="button" onclick="setOpcion('urgencia', 'normal', this)" class="pill-btn active border border-zinc-200 bg-white rounded-lg py-2.5 px-2 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                                Normal
                            </button>
                            <button type="button" onclick="setOpcion('urgencia', 'alta', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-2 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                                Alta
                            </button>
                            <button type="button" onclick="setOpcion('urgencia', 'express', this)" class="pill-btn border border-zinc-200 bg-white rounded-lg py-2.5 px-2 text-xs font-medium text-zinc-700 hover:border-zinc-400">
                                Express
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 8. Extras Técnicos -->
                <div>
                    <label class="block text-xs font-medium uppercase tracking-wider text-zinc-400 mb-2">8. Rigging, Animación y Entregables</label>
                    <div class="divide-y divide-zinc-200/60 bg-white border border-zinc-200 rounded-xl px-4">
                        <label class="py-3 flex items-center justify-between cursor-pointer">
                            <div>
                                <span class="text-sm font-medium text-zinc-800">Rigging Corporal / Mecánico</span>
                                <p class="text-xs text-zinc-400">Esqueleto, controles IK/FK y pesos de vértices</p>
                            </div>
                            <input type="checkbox" id="rigging" onchange="cotizar()" class="w-4 h-4 accent-zinc-900 rounded cursor-pointer">
                        </label>
                        <label class="py-3 flex items-center justify-between cursor-pointer">
                            <div>
                                <span class="text-sm font-medium text-zinc-800">Rigging Facial (Expresiones / Lip-sync)</span>
                                <p class="text-xs text-zinc-400">Aplica para personajes orgánicos</p>
                            </div>
                            <input type="checkbox" id="rig_facial" onchange="cotizar()" class="w-4 h-4 accent-zinc-900 rounded cursor-pointer">
                        </label>
                        <label class="py-3 flex items-center justify-between cursor-pointer">
                            <div>
                                <span class="text-sm font-medium text-zinc-800">Animación (Ciclo / Acción)</span>
                                <p class="text-xs text-zinc-400">Activa Rigging automáticamente por inferencia</p>
                            </div>
                            <input type="checkbox" id="animacion" onchange="cotizar()" class="w-4 h-4 accent-zinc-900 rounded cursor-pointer">
                        </label>
                        <label class="py-3 flex items-center justify-between cursor-pointer">
                            <div>
                                <span class="text-sm font-medium text-zinc-800">Entrega de Archivos Fuente (.blend / .spp)</span>
                                <p class="text-xs text-zinc-400">Incluye archivos editables originales (+25%)</p>
                            </div>
                            <input type="checkbox" id="entrega_archivos_fuente" onchange="cotizar()" class="w-4 h-4 accent-zinc-900 rounded cursor-pointer">
                        </label>
                    </div>
                </div>

                <!-- 9. Meta de Presupuesto (Backward Chaining) -->
                <div class="bg-white border border-zinc-200 rounded-xl p-4">
                    <div class="flex items-center justify-between">
                        <div>
                            <label class="text-xs font-medium uppercase tracking-wider text-zinc-500 block">9. Límite de Presupuesto (Backward Chaining)</label>
                            <p class="text-xs text-zinc-400">Opcional: Si se supera, el motor deducirá qué recortar</p>
                        </div>
                        <div class="flex items-center gap-1.5">
                            <span class="text-xs mono text-zinc-400">$</span>
                            <input type="number" id="presupuesto_max" placeholder="Sin límite" oninput="cotizar()" class="w-28 border border-zinc-200 rounded-lg px-2.5 py-1.5 text-xs mono text-zinc-900 focus:outline-none focus:border-zinc-900">
                        </div>
                    </div>
                </div>

            </div>

            <!-- COLUMNA DERECHA: Diagnóstico del Sistema Experto (6 columnas) -->
            <div class="lg:col-span-6 space-y-5">

                <!-- Tarjeta de Métricas Principales + Factor de Certeza -->
                <div class="bg-white border border-zinc-200 rounded-2xl p-6 shadow-sm">
                    <div class="grid grid-cols-3 divide-x divide-zinc-100">
                        <div class="pr-4">
                            <span class="text-[11px] font-medium uppercase tracking-wider text-zinc-400">Total Estimado</span>
                            <div class="mt-1 flex items-baseline gap-1">
                                <span id="precio-total" class="text-3xl font-semibold tracking-tight text-zinc-900 mono">$0.00</span>
                                <span class="text-[11px] text-zinc-400 mono">USD</span>
                            </div>
                            <div id="rango-difuso" class="text-[11px] mono text-zinc-400 mt-1">Rango: $0 - $0</div>
                        </div>
                        <div class="px-4">
                            <span class="text-[11px] font-medium uppercase tracking-wider text-zinc-400">Esfuerzo / Entrega</span>
                            <div class="mt-1 flex items-baseline gap-1">
                                <span id="horas-total" class="text-2xl font-semibold tracking-tight text-zinc-900 mono">0</span>
                                <span class="text-xs text-zinc-500">h</span>
                                <span class="text-zinc-300 mx-1">·</span>
                                <span id="dias-total" class="text-2xl font-semibold tracking-tight text-zinc-900 mono">1</span>
                                <span class="text-xs text-zinc-500">d</span>
                            </div>
                            <div class="text-[11px] text-zinc-400 mt-1">Cronograma técnico</div>
                        </div>
                        <div class="pl-4">
                            <span class="text-[11px] font-medium uppercase tracking-wider text-zinc-400">Certeza (CF)</span>
                            <div class="mt-1 flex items-baseline gap-1">
                                <span id="certeza-val" class="text-2xl font-semibold tracking-tight text-zinc-900 mono">95%</span>
                            </div>
                            <div class="w-full bg-zinc-100 h-1.5 rounded-full mt-2 overflow-hidden">
                                <div id="certeza-bar" class="bg-zinc-900 h-full transition-all" style="width: 95%"></div>
                            </div>
                        </div>
                    </div>

                    <div class="mt-5 pt-4 border-t border-zinc-100">
                        <span class="uppercase tracking-wider font-medium text-[11px] text-zinc-400 block mb-2">Carga por Departamento</span>
                        <div id="barras-depto" class="grid grid-cols-5 gap-1.5 text-[11px] mono"></div>
                    </div>
                </div>

                <!-- Recomendaciones Backward Chaining (Si supera presupuesto) -->
                <div id="box-backward" class="bg-zinc-900 text-white rounded-2xl p-5 hidden">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-[11px] mono uppercase tracking-wider text-zinc-400">↺ Encadenamiento Hacia Atrás (Optimización de Meta)</span>
                    </div>
                    <p class="text-xs text-zinc-300 mb-3">La cotización supera tu presupuesto objetivo. El motor sugiere modificar uno de estos hechos:</p>
                    <ul id="lista-backward" class="space-y-1.5 text-xs mono text-zinc-100"></ul>
                </div>

                <!-- Alertas y Recomendaciones del Experto -->
                <div id="contenedor-alertas" class="space-y-2 hidden"></div>

                <!-- Cadena Causal de Inferencia -->
                <div class="bg-white border border-zinc-200 rounded-2xl p-5 shadow-sm">
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-xs font-medium uppercase tracking-wider text-zinc-400">Árbol Causal (Forward Chaining)</span>
                        <span id="deducidos-count" class="text-xs mono text-zinc-400">0 deducciones</span>
                    </div>
                    <div id="lista-grafo" class="space-y-1.5 text-xs mono text-zinc-700"></div>
                </div>

                <!-- Trazabilidad de Reglas Disparadas -->
                <div class="bg-white border border-zinc-200 rounded-2xl p-6 shadow-sm">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-xs font-medium uppercase tracking-wider text-zinc-400">Trazabilidad de Reglas Disparadas</span>
                        <span id="reglas-count" class="text-xs mono text-zinc-400">0 reglas</span>
                    </div>
                    <div id="lista-reglas" class="space-y-3.5"></div>
                </div>

            </div>

        </div>
    </div>

    <!-- Modal de Adquisición de Conocimiento (+ Nueva Regla) -->
    <div id="modal-regla" class="fixed inset-0 bg-black/40 backdrop-blur-xs hidden items-center justify-center z-50 p-4">
        <div class="bg-white border border-zinc-200 rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div class="flex justify-between items-center border-b border-zinc-100 pb-3">
                <h3 class="text-sm font-semibold text-zinc-900">Módulo de Adquisición de Conocimiento</h3>
                <button onclick="cerrarModalRegla()" class="text-xs text-zinc-400 hover:text-zinc-900">✕</button>
            </div>
            <div class="space-y-3 text-xs">
                <div>
                    <label class="block text-zinc-500 mb-1">Nombre de la Regla</label>
                    <input id="nr-nombre" type="text" placeholder="Ej. Optimización VR Quest" class="w-full border border-zinc-200 rounded-lg px-3 py-2">
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-zinc-500 mb-1">Si el hecho (IF)</label>
                        <select id="nr-hecho" class="w-full border border-zinc-200 rounded-lg px-2 py-2 bg-white">
                            <option value="destino">destino</option>
                            <option value="categoria">categoria</option>
                            <option value="complejidad">complejidad</option>
                            <option value="texturizado">texturizado</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-zinc-500 mb-1">Es igual a (==)</label>
                        <input id="nr-valor" type="text" placeholder="videojuego / personaje..." class="w-full border border-zinc-200 rounded-lg px-3 py-2">
                    </div>
                </div>
                <div class="grid grid-cols-3 gap-2">
                    <div>
                        <label class="block text-zinc-500 mb-1">Depto.</label>
                        <select id="nr-depto" class="w-full border border-zinc-200 rounded-lg px-2 py-2 bg-white">
                            <option value="modelado">modelado</option>
                            <option value="texturizado">texturizado</option>
                            <option value="rigging">rigging</option>
                            <option value="optimizacion">optimizacion</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-zinc-500 mb-1">Horas (+)</label>
                        <input id="nr-horas" type="number" value="2" class="w-full border border-zinc-200 rounded-lg px-3 py-2">
                    </div>
                    <div>
                        <label class="block text-zinc-500 mb-1">Costo USD (+)</label>
                        <input id="nr-costo" type="number" value="35" class="w-full border border-zinc-200 rounded-lg px-3 py-2">
                    </div>
                </div>
                <div>
                    <label class="block text-zinc-500 mb-1">Concepto de explicación (THEN)</label>
                    <input id="nr-concepto" type="text" placeholder="Ajuste técnico especializado" class="w-full border border-zinc-200 rounded-lg px-3 py-2">
                </div>
            </div>
            <div class="flex justify-end gap-2 pt-2">
                <button onclick="cerrarModalRegla()" class="px-3 py-2 text-xs text-zinc-500">Cancelar</button>
                <button onclick="guardarNuevaRegla()" class="px-4 py-2 text-xs font-medium bg-zinc-900 text-white rounded-lg hover:bg-zinc-800">Guardar en reglas.json</button>
            </div>
        </div>
    </div>

    <script>
        let ultimoInforme = null;
        const estado = {
            destino: 'videojuego',
            categoria: 'prop',
            complejidad: 'low_poly',
            texturizado: 'colores_planos',
            uso: 'comercial',
            urgencia: 'normal'
        };

        function actualizarSlider(val) {
            document.getElementById('lbl-accesorios').textContent = val + (val == 1 ? ' pieza' : ' piezas');
            cotizar();
        }

        function setOpcion(clave, valor, btnElement) {
            estado[clave] = valor;
            const contenedor = btnElement.parentElement;
            contenedor.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
            btnElement.classList.add('active');
            cotizar();
        }

        async function cotizar() {
            const pMax = parseFloat(document.getElementById('presupuesto_max').value) || 0;
            const payload = {
                ...estado,
                cantidad_accesorios: parseInt(document.getElementById('cantidad_accesorios').value, 10),
                rigging: document.getElementById('rigging').checked,
                rig_facial: document.getElementById('rig_facial').checked,
                animacion: document.getElementById('animacion').checked,
                entrega_archivos_fuente: document.getElementById('entrega_archivos_fuente').checked,
                presupuesto_max: pMax
            };

            try {
                const res = await fetch('/api/cotizar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                ultimoInforme = data;
                renderizar(data);
            } catch (err) {
                console.error(err);
            }
        }

        function renderizar(data) {
            document.getElementById('precio-total').textContent = '$' + data.costo_total.toFixed(2);
            document.getElementById('horas-total').textContent = data.horas_totales;
            document.getElementById('dias-total').textContent = data.dias_estimados;
            document.getElementById('badge-total-reglas').textContent = data.total_reglas_base + ' Reglas';

            if (data.fuzzy) {
                document.getElementById('rango-difuso').textContent =
                    'Rango: $' + data.fuzzy.rango_min.toFixed(0) + ' - $' + data.fuzzy.rango_max.toFixed(0) + ' USD';
                document.getElementById('certeza-val').textContent = data.fuzzy.certeza_porcentaje + '%';
                document.getElementById('certeza-bar').style.width = data.fuzzy.certeza_porcentaje + '%';
                document.getElementById('lbl-fuzzy').textContent = 'Densidad: ' + data.fuzzy.densidad_difusa;
            }

            // Backward Chaining
            const boxBack = document.getElementById('box-backward');
            const listaBack = document.getElementById('lista-backward');
            listaBack.innerHTML = '';
            if (data.recomendaciones_presupuesto && data.recomendaciones_presupuesto.length > 0) {
                boxBack.classList.remove('hidden');
                data.recomendaciones_presupuesto.forEach(rec => {
                    const li = document.createElement('li');
                    li.textContent = '• ' + rec;
                    listaBack.appendChild(li);
                });
            } else {
                boxBack.classList.add('hidden');
            }

            // Departamentos
            const barras = document.getElementById('barras-depto');
            barras.innerHTML = '';
            Object.entries(data.horas_por_departamento).forEach(([depto, h]) => {
                const activo = h > 0;
                const box = document.createElement('div');
                box.className = 'p-2 rounded-lg border ' + (activo ? 'bg-zinc-900 text-white border-zinc-900' : 'bg-zinc-50 text-zinc-400 border-zinc-200/70');
                box.innerHTML = '<div class="capitalize text-[10px] opacity-75">' + depto + '</div><div class="font-semibold mt-0.5">' + h + 'h</div>';
                barras.appendChild(box);
            });

            // Alertas
            const divAlertas = document.getElementById('contenedor-alertas');
            divAlertas.innerHTML = '';
            if (data.alertas && data.alertas.length > 0) {
                divAlertas.classList.remove('hidden');
                data.alertas.forEach(a => {
                    const esWarn = a.nivel === 'warning';
                    const box = document.createElement('div');
                    box.className = 'p-3.5 rounded-xl border text-xs leading-relaxed ' + (
                        esWarn ? 'bg-amber-50/90 border-amber-300 text-amber-900' : 'bg-zinc-100 border-zinc-300 text-zinc-800'
                    );
                    const titulo = esWarn ? '⚠ Auditoría Técnica (' + a.regla + ')' : 'ℹ Inferencia Automática (' + a.regla + ')';
                    box.innerHTML = '<span class="font-semibold uppercase tracking-wider text-[10px] block mb-0.5">' + titulo + '</span>' + a.mensaje;
                    divAlertas.appendChild(box);
                });
            } else {
                divAlertas.classList.add('hidden');
            }

            // Grafo Causal
            const divGrafo = document.getElementById('lista-grafo');
            divGrafo.innerHTML = '';
            document.getElementById('deducidos-count').textContent = data.hechos_deducidos.length + ' deducciones';
            if (!data.grafo_causal || data.grafo_causal.length === 0) {
                divGrafo.innerHTML = '<span class="text-xs text-zinc-400">Sin encadenamiento intermedio.</span>';
            } else {
                data.grafo_causal.forEach(linea => {
                    const row = document.createElement('div');
                    row.className = 'px-3 py-1.5 rounded-lg bg-zinc-50 border border-zinc-200/80';
                    row.textContent = linea;
                    divGrafo.appendChild(row);
                });
            }

            // Reglas Disparadas
            document.getElementById('reglas-count').textContent = data.reglas_aplicadas.length + ' de ' + data.total_reglas_base + ' reglas activas';
            const lista = document.getElementById('lista-reglas');
            lista.innerHTML = '';

            data.reglas_aplicadas.forEach(regla => {
                const item = document.createElement('div');
                item.className = 'text-sm border-b border-zinc-100 pb-3.5 last:border-none last:pb-0';

                const depsHtml = (regla.dependencias && regla.dependencias.length > 0)
                    ? '<span class="ml-2 px-1.5 py-0.5 text-[10px] mono bg-zinc-100 text-zinc-600 rounded border border-zinc-200">Encadenada: ' + regla.dependencias.join(', ') + '</span>'
                    : '';

                const detallesHtml = regla.detalles.map(d => {
                    const esInferencia = d.includes('Hecho deducido') || d.includes('Nota:');
                    return '<div class="text-xs ' + (esInferencia ? 'text-zinc-900 font-medium' : 'text-zinc-500') + ' mt-0.5">' +
                                (esInferencia ? '↳ ' : '• ') + d +
                           '</div>';
                }).join('');

                item.innerHTML =
                    '<div class="flex items-baseline justify-between gap-2">' +
                        '<div class="font-medium text-zinc-800 text-xs flex flex-wrap items-center gap-1">' +
                            '<span class="mono text-zinc-400">F' + regla.fase + '·' + regla.id + '</span>' +
                            '<span>' + regla.nombre + '</span>' +
                            depsHtml +
                        '</div>' +
                        '<span class="mono text-xs text-zinc-900 font-medium">$' + regla.subtotal_acumulado.toFixed(2) + '</span>' +
                    '</div>' +
                    '<div class="mt-1">' + detallesHtml + '</div>';
                lista.appendChild(item);
            });
        }

        function exportarMarkdown() {
            if (!ultimoInforme || !ultimoInforme.reporte_markdown) return;
            const blob = new Blob([ultimoInforme.reporte_markdown], { type: 'text/markdown;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'dictamen_cotizacion_3d.md';
            a.click();
            URL.revokeObjectURL(url);
        }

        function abrirModalRegla() {
            document.getElementById('modal-regla').classList.remove('hidden');
            document.getElementById('modal-regla').classList.add('flex');
        }

        function cerrarModalRegla() {
            document.getElementById('modal-regla').classList.add('hidden');
            document.getElementById('modal-regla').classList.remove('flex');
        }

        async function guardarNuevaRegla() {
            const payload = {
                nombre: document.getElementById('nr-nombre').value || 'Regla Experta Personalizada',
                hecho: document.getElementById('nr-hecho').value,
                valor_condicion: document.getElementById('nr-valor').value || 'videojuego',
                departamento: document.getElementById('nr-depto').value,
                horas: parseFloat(document.getElementById('nr-horas').value) || 2,
                costo: parseFloat(document.getElementById('nr-costo').value) || 30,
                concepto: document.getElementById('nr-concepto').value || 'Ajuste técnico agregado al sistema'
            };

            await fetch('/api/agregar_regla', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            cerrarModalRegla();
            cotizar();
        }

        function reiniciar() {
            estado.destino = 'videojuego';
            estado.categoria = 'prop';
            estado.complejidad = 'low_poly';
            estado.texturizado = 'colores_planos';
            estado.uso = 'comercial';
            estado.urgencia = 'normal';

            document.getElementById('cantidad_accesorios').value = 0;
            document.getElementById('lbl-accesorios').textContent = '0 piezas';
            document.getElementById('presupuesto_max').value = '';
            document.getElementById('rigging').checked = false;
            document.getElementById('rig_facial').checked = false;
            document.getElementById('animacion').checked = false;
            document.getElementById('entrega_archivos_fuente').checked = false;

            const defaults = { destino: 0, categoria: 0, complejidad: 0, texturizado: 1, uso: 1, urgencia: 0 };
            Object.entries(defaults).forEach(([grupo, index]) => {
                const div = document.querySelector('[data-group="' + grupo + '"]');
                if (div) {
                    div.querySelectorAll('.pill-btn').forEach((b, i) => {
                        if (i === index) b.classList.add('active');
                        else b.classList.remove('active');
                    });
                }
            });

            cotizar();
        }

        window.addEventListener('DOMContentLoaded', cotizar);
    </script>
</body>
</html>
"""


class ServidorWebExperto(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_UI.encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        payload = json.loads(body)

        if self.path == "/api/cotizar":
            informe = motor.cotizar_detallado(payload)
            informe["total_reglas_base"] = len(motor.reglas)

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(informe).encode("utf-8"))

        elif self.path == "/api/agregar_regla":
            nueva = motor.agregar_regla_nueva(payload)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "regla": nueva}).encode("utf-8"))


def ejecutar_interfaz():
    puerto = 8080
    url = f"http://127.0.0.1:{puerto}"
    servidor = HTTPServer(("127.0.0.1", puerto), ServidorWebExperto)

    print(f"Sistema Experto v3.0 ({len(motor.reglas)} reglas) activo en {url} (Ctrl+C para salir)")
    webbrowser.open(url)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        servidor.server_close()


if __name__ == "__main__":
    ejecutar_interfaz()