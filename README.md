# MCP Azure Schools

Servidor MCP (Model Context Protocol) para gestión de datos de escuelas en Azure SQL Database.

## Estado del proyecto
🚧 **En desarrollo** - Versión inicial básica

## Estructura del proyecto
```
mcp-azure-schools/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   └── azure_schools_mcp/
│       ├── __init__.py
│       └── server.py
├── tests/
├── docs/
└── scripts/
```

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración

1. Copiar archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```
2. Editar `.env` con tus credenciales de Azure SQL

## Uso

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar servidor
python src/azure_schools_mcp/server.py
```

## Próximos pasos

- [ ] Conectar con Azure SQL Database
- [ ] Implementar herramientas CRUD básicas
- [ ] Agregar esquema de base de datos para escuelas
- [ ] Implementar análisis de datos

## Requisitos

- Python 3.8+
- Azure SQL Database
- Node.js (para algunos clientes MCP)