#!/usr/bin/env python3
"""
Servidor MCP básico para Azure Schools
Versión inicial - solo estructura básica
"""

import asyncio
import logging
from typing import Any, Dict, List

# Importaciones MCP
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("azure-schools-mcp")

# Crear servidor MCP
server = Server("azure-schools-mcp")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Lista las herramientas disponibles"""
    return [
        Tool(
            name="test_server",
            description="Prueba básica del servidor MCP",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string", 
                        "description": "Mensaje de prueba"
                    }
                },
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Maneja las llamadas a herramientas"""
    
    if name == "test_server":
        message = arguments.get('message', 'Hola desde Azure Schools MCP!')
        
        return [TextContent(
            type="text",
            text=f"✅ Servidor funcionando correctamente! Mensaje: {message}"
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"❌ Herramienta desconocida: {name}"
        )]

async def main():
    """Función principal del servidor"""
    logger.info("🚀 Iniciando servidor MCP Azure Schools...")
    
    # Ejecutar servidor
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="azure-schools-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities()
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
