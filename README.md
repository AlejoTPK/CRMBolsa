# Sovereign CRM 🏛️

**Sovereign CRM** es una plataforma moderna y pedagógica de monitoreo financiero, especializada en materias primas (*commodities*) clave como el **Oro (XAU/USD)** y el **Petróleo Crudo (WTI)**. Diseñada con un enfoque premium, minimalista y reactivo, la aplicación empodera a inversores novatos mediante datos en tiempo real y análisis generados por Inteligencia Artificial.

![Sovereign CRM Banner](https://img.shields.io/badge/Sovereign-CRM-D4AF37?style=for-the-badge)

---

## 🚀 Características Principales

*   🏛️ **Lobby de Acceso Premium (Landing Page):** Un portal interactivo de entrada (`/`) con animaciones fluidas, destellos de fondo tipo *twinkle*, prueba social, grilla de mercados globales simulados, tarifas de suscripción y sección interactiva de FAQ.
*   📊 **Monitor de Commodities Avanzado:** Panel de control reactivo (`/dashboard`) con cotizaciones en tiempo real e histórico de precios mediante integración directa con `yfinance` y actualización en vivo vía WebSockets. Gráficos interactivos de velas y líneas construidos con Plotly.
*   💼 **Simulador de Portafolio:** Visualización dinámica de la distribución de activos representados con un gráfico de donut interactivo conectado al valor actual de los activos.
*   🤖 **Sovereign Insights (Motor de IA):**
    *   **Alertas Rápidas (Monitor 24/7):** Un proceso en segundo plano de FastAPI que audita los precios cada 30 minutos. Si detecta una anomalía (variación mayor al ±2%), invoca al modelo LLM de **Groq** (`llama-3.3-70b-versatile`) para generar alertas explicativas con persistencia automática en PostgreSQL.
    *   **Resumen Diario Automático:** Al final del día, consolida los datos de la jornada e invoca a la IA para generar reportes estructurados con una *"Lección del Día"*, asegurando no repetir lecciones pasadas e implementando actualizaciones inteligentes de tipo upsert.
*   📰 **Noticias de Impacto & Sentimiento IA:** Feed enriquecido de noticias extraído directamente desde Yahoo Finance y procesado por el LLM para calificar el sentimiento en tiempo real.
*   🎨 **Obsidian Sovereign UI:** Diseño visual e interactivo construido completamente en Python utilizando **Reflex** con un diseño *Glassmorphism* sofisticado, colores cuidadosamente calibrados y transiciones fluidas.

---

## 🛠️ Stack Tecnológico

*   **Backend:** [FastAPI](https://fastapi.tiangolo.com/), Uvicorn, Python 3.
*   **Frontend:** [Reflex](https://reflex.dev/).
*   **Inteligencia Artificial:** [Groq API](https://groq.com/) (Modelo Llama 3.3 70B).
*   **Data & Análisis:** `yfinance`, `pandas`.
*   **Base de Datos:** PostgreSQL (con TimescaleDB para series temporales), gestionado con `sqlalchemy` y migraciones con `alembic`.
*   **WebSockets:** Ingesta de datos en tiempo real mediante la API de Finnhub (`websockets`).
*   **Visualización:** Gráficos avanzados renderizados con `plotly`.

---

## 📂 Estructura del Proyecto

```text
AplicaciónWebBolsa/
├── api/
│   ├── main.py                 # Punto de entrada de FastAPI y background worker
│   ├── routers/                # Endpoints REST e inyección de insights.py
│   └── services/               # Lógica de negocio (market_data.py, insights_service.py)
├── db/
│   ├── database.py             # Configuración de TimescaleDB/PostgreSQL asyncpg
│   ├── models.py               # Modelos de SQLAlchemy (ej. DBAlertaMercado, DBResumenDiario)
│   └── migrations/             # Revisiones generadas por Alembic
├── ui/
│   ├── rxconfig.py             # Configuración del proyecto Reflex
│   └── sovereign_crm/
│       ├── sovereign_crm.py    # Layout principal y routing del Dashboard
│       ├── lobby.py            # Vista de la Landing Page Premium (Lobby)
│       ├── state.py            # Estado de Reflex (AppState) y streaming WebSocket
│       ├── insights_state.py   # Gestión de estado de alertas e historiales de IA
│       ├── components.py       # Estilos compartidos, navbar y tarjetas generales
│       ├── insights_components.py # Componentes dedicados para las alertas e historial de IA
│       └── ai_recommendation_card.py # Tarjeta interactiva de recomendación IA
├── .env                        # Variables de entorno (GROQ_API_KEY, DATABASE_URL, API_URL)
├── alembic.ini                 # Configuración del entorno de migraciones
└── requirements.txt            # Dependencias del proyecto (reflex>=0.9.1, plotly, httpx)
```

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio e instalar dependencias

Te recomendamos usar un entorno virtual (`.venv`):

```bash
python -m venv .venv
# Activar en Windows:
.venv\Scripts\activate
# Activar en Mac/Linux:
source .venv/bin/activate

# Instalar los requerimientos
pip install -r requirements.txt
```

### 2. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto (junto a la carpeta `api`) con la siguiente estructura:

```env
# URL de conexión para el frontend hacia el backend
API_URL=http://127.0.0.1:8001

# Conexión a Base de Datos PostgreSQL/TimescaleDB local
DATABASE_URL="postgresql+asyncpg://postgres:tu_contrasena@localhost:5432/sovereign"

# Finnhub WebSockets
FINNHUB_API_KEY="tu_api_key_finnhub"

# APIs Opcionales
ALPHAVANTAGE_API_KEY="tu_api_key"
NEWSAPI_KEY="tu_api_key"

# API Key de Groq para Sovereign Insights
GROQ_API_KEY="tu_api_key_groq"
```

### 3. Base de Datos y Migraciones

Antes de ejecutar el proyecto, asegúrate de tener una instancia local de PostgreSQL corriendo (idealmente con la extensión TimescaleDB instalada) y haber creado la base de datos que especificaste en `DATABASE_URL`. Luego, crea las tablas con Alembic:

```bash
alembic upgrade head
```

---

## 🏃‍♂️ Ejecución del Proyecto

El proyecto consta de dos servicios que deben ejecutarse simultáneamente: el Backend (FastAPI) y el Frontend (Reflex).

### Paso 1: Levantar el Backend (FastAPI)

Desde el directorio raíz del proyecto (`AplicaciónWebBolsa`):

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```
*Esto iniciará el servidor de la API en el puerto 8001 y comenzará la tarea en segundo plano del monitor de anomalías.*

### Paso 2: Levantar el Frontend (Reflex)

Abre **otra pestaña/ventana** en tu terminal, activa tu entorno virtual y navega a la carpeta `ui`:

```bash
cd ui
reflex run
```
*La primera vez que ejecutes este comando, Reflex compilará el proyecto (puede tardar un par de minutos). Una vez finalizado, podrás acceder al Dashboard en `http://localhost:3000`.*

---

## 💡 Notas Adicionales y Flujo de la IA

*   El sistema de **Sovereign Insights** fue diseñado con prompts estrictos en JSON (`response_format={"type": "json_object"}`) para asegurar una integración perfecta con la UI.
*   El umbral por defecto para las alertas rápidas es de **±2%** de variación en un lapso de 30 minutos. Esto se puede modificar en la variable `UMBRAL_VARIACION_PCT` dentro de `api/services/insights_service.py`.
