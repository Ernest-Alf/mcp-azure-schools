#!/usr/bin/env python3
"""
Script de Análisis Profundo del Proyecto MCP Azure Schools
Analiza estructura, dependencias, código y configuraciones
"""

import os
import sys
import json
import ast
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util
from datetime import datetime

class ProjectAnalyzer:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.analysis_results = {}
        
    def run_full_analysis(self) -> Dict[str, Any]:
        """Ejecuta análisis completo del proyecto"""
        print("🔍 Iniciando análisis profundo del proyecto...")
        print(f"📁 Directorio: {self.project_path}")
        print("=" * 60)
        
        try:
            self.analysis_results.update({
                'project_info': self.analyze_project_structure(),
                'dependencies': self.analyze_dependencies(),
                'python_modules': self.analyze_python_modules(),
                'mcp_tools': self.analyze_mcp_tools(),
                'configs': self.analyze_configurations(),
                'git_info': self.analyze_git_repository(),
                'azure_setup': self.analyze_azure_setup(),
                'data_files': self.analyze_data_files(),
                'code_quality': self.analyze_code_quality(),
                'recommendations': self.generate_recommendations()
            })
            
            self.print_analysis_report()
            self.save_analysis_report()
            
        except Exception as e:
            print(f"❌ Error durante análisis: {e}")
            
        return self.analysis_results
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analiza la estructura de directorios y archivos"""
        print("📂 Analizando estructura del proyecto...")
        
        structure = {
            'total_files': 0,
            'total_dirs': 0,
            'file_types': {},
            'directory_tree': {},
            'key_files': []
        }
        
        # Archivos clave a buscar
        key_files = [
            'README.md', 'requirements.txt', '.env', '.env.example',
            'setup.py', 'pyproject.toml', '.gitignore', 'LICENSE',
            'docker-compose.yml', 'Dockerfile'
        ]
        
        for root, dirs, files in os.walk(self.project_path):
            # Ignorar directorios comunes
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
            
            structure['total_dirs'] += len(dirs)
            structure['total_files'] += len(files)
            
            for file in files:
                ext = Path(file).suffix.lower()
                structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                
                if file in key_files:
                    structure['key_files'].append(str(Path(root) / file))
        
        # Generar árbol de directorios
        structure['directory_tree'] = self._generate_tree(self.project_path)
        
        return structure
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analiza dependencias del proyecto"""
        print("📦 Analizando dependencias...")
        
        deps_info = {
            'requirements_txt': None,
            'pyproject_toml': None,
            'installed_packages': None,
            'outdated_packages': None
        }
        
        # Analizar requirements.txt
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            deps_info['requirements_txt'] = self._parse_requirements(req_file)
        
        # Analizar pyproject.toml
        pyproject_file = self.project_path / 'pyproject.toml'
        if pyproject_file.exists():
            deps_info['pyproject_toml'] = self._parse_pyproject(pyproject_file)
        
        # Obtener paquetes instalados
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                deps_info['installed_packages'] = json.loads(result.stdout)
        except Exception as e:
            print(f"⚠️  No se pudo obtener lista de paquetes: {e}")
        
        return deps_info
    
    def analyze_python_modules(self) -> Dict[str, Any]:
        """Analiza módulos Python del proyecto"""
        print("🐍 Analizando módulos Python...")
        
        modules_info = {
            'python_files': [],
            'total_lines': 0,
            'imports': set(),
            'functions': [],
            'classes': [],
            'complexity': {}
        }
        
        python_files = list(self.project_path.rglob('*.py'))
        
        for py_file in python_files:
            if any(part.startswith('.') or part in ['__pycache__', 'venv'] for part in py_file.parts):
                continue
                
            file_info = self._analyze_python_file(py_file)
            modules_info['python_files'].append(file_info)
            modules_info['total_lines'] += file_info['lines']
            modules_info['imports'].update(file_info['imports'])
            modules_info['functions'].extend(file_info['functions'])
            modules_info['classes'].extend(file_info['classes'])
        
        modules_info['imports'] = list(modules_info['imports'])
        return modules_info
    
    def analyze_mcp_tools(self) -> Dict[str, Any]:
        """Analiza herramientas MCP específicamente"""
        print("🔧 Analizando herramientas MCP...")
        
        mcp_info = {
            'mcp_servers': [],
            'mcp_tools': [],
            'mcp_resources': [],
            'total_tools': 0
        }
        
        # Buscar archivos con decoradores MCP
        python_files = list(self.project_path.rglob('*.py'))
        
        for py_file in python_files:
            if any(part.startswith('.') or part in ['__pycache__', 'venv'] for part in py_file.parts):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Buscar decoradores @mcp.tool()
                tool_matches = re.findall(r'@mcp\.tool\(\)(.*?)?def\s+(\w+)', content, re.DOTALL)
                for match in tool_matches:
                    mcp_info['mcp_tools'].append({
                        'file': str(py_file),
                        'function': match[1],
                        'line': content[:content.find(f'def {match[1]}')].count('\n') + 1
                    })
                
                # Buscar decoradores @mcp.resource()
                resource_matches = re.findall(r'@mcp\.resource\((.*?)\)(.*?)?def\s+(\w+)', content, re.DOTALL)
                for match in resource_matches:
                    mcp_info['mcp_resources'].append({
                        'file': str(py_file),
                        'function': match[2],
                        'pattern': match[0]
                    })
                
                # Buscar instancias FastMCP
                if 'FastMCP' in content:
                    server_matches = re.findall(r'(\w+)\s*=\s*FastMCP\s*\(\s*["\'](.+?)["\']\s*\)', content)
                    for match in server_matches:
                        mcp_info['mcp_servers'].append({
                            'file': str(py_file),
                            'variable': match[0],
                            'name': match[1]
                        })
                        
            except Exception as e:
                print(f"⚠️  Error analizando {py_file}: {e}")
        
        mcp_info['total_tools'] = len(mcp_info['mcp_tools'])
        return mcp_info
    
    def analyze_configurations(self) -> Dict[str, Any]:
        """Analiza archivos de configuración"""
        print("⚙️  Analizando configuraciones...")
        
        configs = {
            'vscode_settings': None,
            'mcp_configs': None,
            'env_files': [],
            'docker_configs': None,
            'azure_configs': None
        }
        
        # Configuraciones VS Code
        vscode_dir = self.project_path / '.vscode'
        if vscode_dir.exists():
            configs['vscode_settings'] = self._analyze_vscode_config(vscode_dir)
        
        # Archivos .env
        for env_file in self.project_path.glob('.env*'):
            configs['env_files'].append(self._analyze_env_file(env_file))
        
        # Configuraciones Docker
        dockerfile = self.project_path / 'Dockerfile'
        if dockerfile.exists():
            configs['docker_configs'] = self._analyze_dockerfile(dockerfile)
        
        return configs
    
    def analyze_git_repository(self) -> Dict[str, Any]:
        """Analiza información del repositorio Git"""
        print("📋 Analizando repositorio Git...")
        
        git_info = {
            'is_git_repo': False,
            'remote_url': None,
            'current_branch': None,
            'last_commit': None,
            'total_commits': None,
            'gitignore_exists': False
        }
        
        git_dir = self.project_path / '.git'
        if git_dir.exists():
            git_info['is_git_repo'] = True
            
            try:
                # URL remota
                result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                      capture_output=True, text=True, cwd=self.project_path)
                if result.returncode == 0:
                    git_info['remote_url'] = result.stdout.strip()
                
                # Rama actual
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      capture_output=True, text=True, cwd=self.project_path)
                if result.returncode == 0:
                    git_info['current_branch'] = result.stdout.strip()
                
                # Último commit
                result = subprocess.run(['git', 'log', '-1', '--pretty=format:%H|%s|%an|%ad'], 
                                      capture_output=True, text=True, cwd=self.project_path)
                if result.returncode == 0:
                    parts = result.stdout.strip().split('|')
                    if len(parts) >= 4:
                        git_info['last_commit'] = {
                            'hash': parts[0][:8],
                            'message': parts[1],
                            'author': parts[2],
                            'date': parts[3]
                        }
                
            except Exception as e:
                print(f"⚠️  Error obteniendo info Git: {e}")
        
        gitignore = self.project_path / '.gitignore'
        git_info['gitignore_exists'] = gitignore.exists()
        
        return git_info
    
    def analyze_azure_setup(self) -> Dict[str, Any]:
        """Analiza configuración de Azure"""
        print("☁️  Analizando configuración Azure...")
        
        azure_info = {
            'azure_packages': [],
            'connection_strings': [],
            'env_variables': [],
            'sql_files': []
        }
        
        # Buscar paquetes relacionados con Azure
        python_files = list(self.project_path.rglob('*.py'))
        azure_imports = set()
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                # Buscar imports de Azure
                azure_matches = re.findall(r'import\s+(azure\.[.\w]+)', content)
                azure_imports.update(azure_matches)
                
                from_azure_matches = re.findall(r'from\s+(azure\.[.\w]+)', content)
                azure_imports.update(from_azure_matches)
                
                # Buscar strings de conexión
                conn_matches = re.findall(r'(Server=.*?;|Driver=.*?;)', content)
                azure_info['connection_strings'].extend(conn_matches)
                
            except Exception:
                continue
        
        azure_info['azure_packages'] = list(azure_imports)
        
        # Buscar archivos SQL
        sql_files = list(self.project_path.rglob('*.sql'))
        azure_info['sql_files'] = [str(f) for f in sql_files]
        
        return azure_info
    
    def analyze_data_files(self) -> Dict[str, Any]:
        """Analiza archivos de datos"""
        print("📊 Analizando archivos de datos...")
        
        data_info = {
            'excel_files': [],
            'csv_files': [],
            'json_files': [],
            'pdf_files': [],
            'total_size': 0
        }
        
        # Buscar archivos de datos
        data_extensions = {
            '.xlsx': 'excel_files',
            '.xls': 'excel_files',
            '.csv': 'csv_files',
            '.json': 'json_files',
            '.pdf': 'pdf_files'
        }
        
        for ext, key in data_extensions.items():
            files = list(self.project_path.rglob(f'*{ext}'))
            for file in files:
                try:
                    size = file.stat().st_size
                    data_info[key].append({
                        'path': str(file),
                        'size': size,
                        'size_mb': round(size / (1024 * 1024), 2)
                    })
                    data_info['total_size'] += size
                except Exception:
                    continue
        
        data_info['total_size_mb'] = round(data_info['total_size'] / (1024 * 1024), 2)
        
        return data_info
    
    def analyze_code_quality(self) -> Dict[str, Any]:
        """Analiza calidad del código"""
        print("✨ Analizando calidad del código...")
        
        quality_info = {
            'total_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'avg_function_length': 0,
            'docstring_coverage': 0,
            'potential_issues': []
        }
        
        python_files = list(self.project_path.rglob('*.py'))
        total_functions = 0
        total_function_lines = 0
        functions_with_docstrings = 0
        
        for py_file in python_files:
            if any(part.startswith('.') or part in ['__pycache__', 'venv'] for part in py_file.parts):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                quality_info['total_lines'] += len(lines)
                
                # Analizar funciones
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                        total_function_lines += func_lines
                        
                        # Verificar docstring
                        if (node.body and isinstance(node.body[0], ast.Expr) and 
                            isinstance(node.body[0].value, ast.Constant) and 
                            isinstance(node.body[0].value.value, str)):
                            functions_with_docstrings += 1
                    
                    elif isinstance(node, ast.ClassDef):
                        quality_info['total_classes'] += 1
                
                # Buscar problemas potenciales
                if 'TODO' in content or 'FIXME' in content:
                    quality_info['potential_issues'].append(f"TODOs/FIXMEs en {py_file}")
                
                if 'print(' in content and 'debug' not in str(py_file).lower():
                    quality_info['potential_issues'].append(f"Print statements en {py_file}")
                    
            except Exception as e:
                quality_info['potential_issues'].append(f"Error parseando {py_file}: {e}")
        
        quality_info['total_functions'] = total_functions
        if total_functions > 0:
            quality_info['avg_function_length'] = round(total_function_lines / total_functions, 1)
            quality_info['docstring_coverage'] = round((functions_with_docstrings / total_functions) * 100, 1)
        
        return quality_info
    
    def generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        print("💡 Generando recomendaciones...")
        
        recommendations = []
        
        # Revisar estructura MCP
        if self.analysis_results.get('mcp_tools', {}).get('total_tools', 0) == 0:
            recommendations.append("❌ No se encontraron herramientas MCP. Verificar implementación.")
        
        # Revisar dependencias
        if not self.analysis_results.get('dependencies', {}).get('requirements_txt'):
            recommendations.append("⚠️  Agregar archivo requirements.txt con dependencias.")
        
        # Revisar configuración Azure
        azure_packages = self.analysis_results.get('azure_setup', {}).get('azure_packages', [])
        if not azure_packages:
            recommendations.append("☁️  Agregar paquetes de Azure SDK para integración completa.")
        
        # Revisar archivos de datos
        data_files = self.analysis_results.get('data_files', {})
        if not any(data_files.get(key, []) for key in ['excel_files', 'csv_files']):
            recommendations.append("📊 Agregar archivos de datos de ejemplo para testing.")
        
        # Revisar calidad de código
        quality = self.analysis_results.get('code_quality', {})
        if quality.get('docstring_coverage', 0) < 70:
            recommendations.append("📝 Mejorar documentación: cobertura de docstrings baja.")
        
        # Revisar configuración Git
        git_info = self.analysis_results.get('git_info', {})
        if not git_info.get('gitignore_exists'):
            recommendations.append("📋 Agregar archivo .gitignore para excluir archivos innecesarios.")
        
        return recommendations
    
    def _generate_tree(self, path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """Genera árbol de directorios"""
        if current_depth >= max_depth:
            return {"truncated": True}
        
        tree = {}
        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            for item in items[:20]:  # Limitar a 20 items por directorio
                if item.name.startswith('.') and item.name not in ['.env', '.gitignore']:
                    continue
                if item.name in ['__pycache__', 'node_modules', 'venv']:
                    continue
                    
                if item.is_dir():
                    tree[f"📁 {item.name}"] = self._generate_tree(item, prefix + "  ", max_depth, current_depth + 1)
                else:
                    size = item.stat().st_size
                    size_str = f" ({size} bytes)" if size < 1024 else f" ({size//1024}KB)"
                    tree[f"📄 {item.name}{size_str}"] = None
        except PermissionError:
            tree["❌ Sin permisos"] = None
        
        return tree
    
    def _parse_requirements(self, req_file: Path) -> List[Dict[str, str]]:
        """Parsea archivo requirements.txt"""
        requirements = []
        try:
            content = req_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parsear package==version
                    if '==' in line:
                        package, version = line.split('==', 1)
                        requirements.append({'package': package.strip(), 'version': version.strip()})
                    elif '>=' in line:
                        package, version = line.split('>=', 1)
                        requirements.append({'package': package.strip(), 'version': f">={version.strip()}"})
                    else:
                        requirements.append({'package': line, 'version': 'no especificada'})
        except Exception as e:
            print(f"⚠️  Error parseando requirements.txt: {e}")
        
        return requirements
    
    def _parse_pyproject(self, pyproject_file: Path) -> Dict[str, Any]:
        """Parsea archivo pyproject.toml"""
        try:
            import tomllib
            content = pyproject_file.read_text(encoding='utf-8')
            return tomllib.loads(content)
        except ImportError:
            # Fallback para Python < 3.11
            try:
                import tomli
                content = pyproject_file.read_text(encoding='utf-8')
                return tomli.loads(content)
            except ImportError:
                return {"error": "tomllib/tomli no disponible"}
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_python_file(self, py_file: Path) -> Dict[str, Any]:
        """Analiza un archivo Python individual"""
        file_info = {
            'path': str(py_file),
            'lines': 0,
            'imports': set(),
            'functions': [],
            'classes': [],
            'has_main': False
        }
        
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            file_info['lines'] = len(lines)
            
            # Buscar if __name__ == "__main__"
            if '__name__' in content and '__main__' in content:
                file_info['has_main'] = True
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_info['imports'].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        file_info['imports'].add(node.module)
                elif isinstance(node, ast.FunctionDef):
                    file_info['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': len(node.args.args)
                    })
                elif isinstance(node, ast.ClassDef):
                    file_info['classes'].append({
                        'name': node.name,
                        'line': node.lineno
                    })
            
        except Exception as e:
            file_info['error'] = str(e)
        
        file_info['imports'] = list(file_info['imports'])
        return file_info
    
    def _analyze_vscode_config(self, vscode_dir: Path) -> Dict[str, Any]:
        """Analiza configuración de VS Code"""
        config = {}
        
        settings_file = vscode_dir / 'settings.json'
        if settings_file.exists():
            try:
                config['settings'] = json.loads(settings_file.read_text(encoding='utf-8'))
            except Exception as e:
                config['settings_error'] = str(e)
        
        mcp_file = vscode_dir / 'mcp.json'
        if mcp_file.exists():
            try:
                config['mcp'] = json.loads(mcp_file.read_text(encoding='utf-8'))
            except Exception as e:
                config['mcp_error'] = str(e)
        
        return config
    
    def _analyze_env_file(self, env_file: Path) -> Dict[str, Any]:
        """Analiza archivo .env"""
        env_info = {
            'file': str(env_file),
            'variables': [],
            'has_azure_vars': False,
            'has_sensitive_data': False
        }
        
        try:
            content = env_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if '=' in line and not line.strip().startswith('#'):
                    var_name = line.split('=')[0].strip()
                    env_info['variables'].append(var_name)
                    
                    if 'AZURE' in var_name.upper():
                        env_info['has_azure_vars'] = True
                    
                    if any(sensitive in var_name.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
                        env_info['has_sensitive_data'] = True
        except Exception as e:
            env_info['error'] = str(e)
        
        return env_info
    
    def _analyze_dockerfile(self, dockerfile: Path) -> Dict[str, Any]:
        """Analiza Dockerfile"""
        docker_info = {
            'base_image': None,
            'python_version': None,
            'exposed_ports': [],
            'commands': []
        }
        
        try:
            content = dockerfile.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('FROM'):
                    docker_info['base_image'] = line.split()[1]
                    if 'python' in line.lower():
                        # Extraer versión de Python
                        match = re.search(r'python:(\d+\.\d+)', line.lower())
                        if match:
                            docker_info['python_version'] = match.group(1)
                elif line.startswith('EXPOSE'):
                    ports = line.split()[1:]
                    docker_info['exposed_ports'].extend(ports)
                elif line.startswith(('RUN', 'CMD', 'ENTRYPOINT')):
                    docker_info['commands'].append(line)
        except Exception as e:
            docker_info['error'] = str(e)
        
        return docker_info
    
    def print_analysis_report(self):
        """Imprime reporte completo del análisis"""
        print("\n" + "=" * 80)
        print("📊 REPORTE DE ANÁLISIS COMPLETO")
        print("=" * 80)
        
        # Información del proyecto
        print(f"\n📁 ESTRUCTURA DEL PROYECTO")
        print("-" * 40)
        structure = self.analysis_results.get('project_info', {})
        print(f"📄 Total archivos: {structure.get('total_files', 0)}")
        print(f"📂 Total directorios: {structure.get('total_dirs', 0)}")
        print(f"🔑 Archivos clave encontrados: {len(structure.get('key_files', []))}")
        
        # Tipos de archivo
        file_types = structure.get('file_types', {})
        if file_types:
            print(f"\n📋 Tipos de archivo:")
            for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {ext or '(sin extensión)'}: {count}")
        
        # Módulos Python
        print(f"\n🐍 MÓDULOS PYTHON")
        print("-" * 40)
        modules = self.analysis_results.get('python_modules', {})
        print(f"📝 Archivos Python: {len(modules.get('python_files', []))}")
        print(f"📏 Total líneas: {modules.get('total_lines', 0)}")
        print(f"📦 Imports únicos: {len(modules.get('imports', []))}")
        print(f"⚙️  Funciones: {len(modules.get('functions', []))}")
        print(f"🏗️  Clases: {len(modules.get('classes', []))}")
        
        # Herramientas MCP
        print(f"\n🔧 HERRAMIENTAS MCP")
        print("-" * 40)
        mcp = self.analysis_results.get('mcp_tools', {})
        print(f"🛠️  Total herramientas MCP: {mcp.get('total_tools', 0)}")
        print(f"📡 Servidores MCP: {len(mcp.get('mcp_servers', []))}")
        print(f"📋 Recursos MCP: {len(mcp.get('mcp_resources', []))}")
        
        if mcp.get('mcp_tools'):
            print(f"\n   Herramientas encontradas:")
            for tool in mcp['mcp_tools'][:10]:  # Mostrar primeras 10
                print(f"   • {tool['function']} ({Path(tool['file']).name}:{tool['line']})")
        
        # Configuración Azure
        print(f"\n☁️  CONFIGURACIÓN AZURE")
        print("-" * 40)
        azure = self.analysis_results.get('azure_setup', {})
        print(f"📦 Paquetes Azure: {len(azure.get('azure_packages', []))}")
        print(f"🔗 Strings de conexión: {len(azure.get('connection_strings', []))}")
        print(f"🗃️  Archivos SQL: {len(azure.get('sql_files', []))}")
        
        # Archivos de datos
        print(f"\n📊 ARCHIVOS DE DATOS")
        print("-" * 40)
        data = self.analysis_results.get('data_files', {})
        print(f"📈 Excel: {len(data.get('excel_files', []))}")
        print(f"📋 CSV: {len(data.get('csv_files', []))}")
        print(f"📄 PDF: {len(data.get('pdf_files', []))}")
        print(f"📊 JSON: {len(data.get('json_files', []))}")
        print(f"💾 Tamaño total: {data.get('total_size_mb', 0)} MB")
        
        # Dependencias
        print(f"\n📦 DEPENDENCIAS")
        print("-" * 40)
        deps = self.analysis_results.get('dependencies', {})
        requirements = deps.get('requirements_txt', [])
        if requirements:
            print(f"📋 Requirements.txt: {len(requirements)} paquetes")
            print("   Principales:")
            for req in requirements[:8]:
                print(f"   • {req['package']} {req['version']}")
        else:
            print("❌ No se encontró requirements.txt")
        
        installed = deps.get('installed_packages', [])
        if installed:
            print(f"📦 Paquetes instalados: {len(installed)}")
        
        # Información Git
        print(f"\n📋 REPOSITORIO GIT")
        print("-" * 40)
        git = self.analysis_results.get('git_info', {})
        if git.get('is_git_repo'):
            print(f"✅ Es repositorio Git")
            print(f"🌐 URL remota: {git.get('remote_url', 'No configurada')}")
            print(f"🌿 Rama actual: {git.get('current_branch', 'Desconocida')}")
            
            last_commit = git.get('last_commit')
            if last_commit:
                print(f"📝 Último commit: {last_commit['hash']} - {last_commit['message'][:50]}...")
                print(f"👤 Autor: {last_commit['author']}")
        else:
            print("❌ No es repositorio Git")
        
        # Calidad del código
        print(f"\n✨ CALIDAD DEL CÓDIGO")
        print("-" * 40)
        quality = self.analysis_results.get('code_quality', {})
        print(f"📏 Total líneas: {quality.get('total_lines', 0)}")
        print(f"⚙️  Total funciones: {quality.get('total_functions', 0)}")
        print(f"🏗️  Total clases: {quality.get('total_classes', 0)}")
        print(f"📊 Promedio líneas/función: {quality.get('avg_function_length', 0)}")
        print(f"📝 Cobertura docstrings: {quality.get('docstring_coverage', 0)}%")
        
        issues = quality.get('potential_issues', [])
        if issues:
            print(f"⚠️  Problemas potenciales: {len(issues)}")
            for issue in issues[:5]:
                print(f"   • {issue}")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES")
        print("-" * 40)
        recommendations = self.analysis_results.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                print(f"   {rec}")
        else:
            print("✅ No se encontraron problemas críticos")
        
        print("\n" + "=" * 80)
        print("✅ Análisis completado")
        print("=" * 80)
    
    def save_analysis_report(self):
        """Guarda el reporte en archivo JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_path / f"project_analysis_{timestamp}.json"
        
        try:
            # Convertir sets a lists para JSON
            json_results = json.loads(json.dumps(self.analysis_results, default=str))
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(json_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Reporte guardado en: {report_file}")
            
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")


class EnhancedProjectAnalyzer(ProjectAnalyzer):
    """Versión mejorada del analizador con funciones específicas para MCP"""
    
    def analyze_mcp_server_structure(self) -> Dict[str, Any]:
        """Análisis específico de estructura de servidor MCP"""
        print("🔍 Analizando estructura específica del servidor MCP...")
        
        mcp_structure = {
            'server_files': [],
            'tool_functions': {},
            'resource_functions': {},
            'imports_mcp': [],
            'azure_integrations': [],
            'data_processing_functions': [],
            'error_handling': {},
            'async_functions': []
        }
        
        python_files = list(self.project_path.rglob('*.py'))
        
        for py_file in python_files:
            if any(part.startswith('.') or part in ['__pycache__', 'venv'] for part in py_file.parts):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Detectar archivos de servidor MCP
                if any(pattern in content for pattern in ['FastMCP', '@mcp.tool', 'mcp.server']):
                    mcp_structure['server_files'].append(str(py_file))
                    
                    # Analizar funciones con decoradores MCP
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Verificar si tiene decorador @mcp.tool
                            has_tool_decorator = any(
                                isinstance(decorator, ast.Attribute) and 
                                isinstance(decorator.value, ast.Name) and
                                decorator.value.id == 'mcp' and 
                                decorator.attr == 'tool'
                                for decorator in node.decorator_list
                            )
                            
                            if has_tool_decorator:
                                func_info = self._analyze_mcp_function(node, content)
                                mcp_structure['tool_functions'][node.name] = func_info
                            
                            # Verificar si es función async
                            if isinstance(node, ast.AsyncFunctionDef):
                                mcp_structure['async_functions'].append(node.name)
                    
                    # Buscar imports relacionados con MCP
                    mcp_imports = re.findall(r'from\s+(mcp\.[.\w]+)|import\s+(mcp\.[.\w]+)', content)
                    mcp_structure['imports_mcp'].extend([imp[0] or imp[1] for imp in mcp_imports])
                    
                    # Buscar integraciones con Azure
                    azure_patterns = [
                        r'pyodbc\.connect',
                        r'azure\.sql',
                        r'SqlAlchemy',
                        r'AZURE_SQL'
                    ]
                    
                    for pattern in azure_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            mcp_structure['azure_integrations'].append({
                                'file': str(py_file),
                                'pattern': pattern,
                                'lines': [i+1 for i, line in enumerate(content.split('\n')) 
                                        if re.search(pattern, line, re.IGNORECASE)]
                            })
                    
                    # Buscar funciones de procesamiento de datos
                    data_patterns = [
                        r'pd\.read_excel',
                        r'pd\.read_csv',
                        r'DataFrame',
                        r'\.describe\(',
                        r'\.groupby\(',
                        r'\.agg\('
                    ]
                    
                    for pattern in data_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            if str(py_file) not in [item['file'] for item in mcp_structure['data_processing_functions']]:
                                mcp_structure['data_processing_functions'].append({
                                    'file': str(py_file),
                                    'pattern': pattern,
                                    'line': line_num
                                })
                    
                    # Analizar manejo de errores
                    try_blocks = re.findall(r'try:(.*?)except\s+(\w+)', content, re.DOTALL)
                    mcp_structure['error_handling'][str(py_file)] = {
                        'try_blocks': len(try_blocks),
                        'exception_types': [match[1] for match in try_blocks]
                    }
                        
            except Exception as e:
                print(f"⚠️  Error analizando {py_file} para MCP: {e}")
        
        return mcp_structure
    
    def _analyze_mcp_function(self, func_node: ast.FunctionDef, content: str) -> Dict[str, Any]:
        """Analiza una función MCP específica"""
        func_info = {
            'name': func_node.name,
            'line': func_node.lineno,
            'args': [arg.arg for arg in func_node.args.args],
            'has_docstring': False,
            'has_type_hints': False,
            'returns_data': False,
            'uses_context': False
        }
        
        # Verificar docstring
        if (func_node.body and isinstance(func_node.body[0], ast.Expr) and 
            isinstance(func_node.body[0].value, ast.Constant)):
            func_info['has_docstring'] = True
        
        # Verificar type hints
        if func_node.returns or any(arg.annotation for arg in func_node.args.args):
            func_info['has_type_hints'] = True
        
        # Verificar si usa Context
        if any(arg.arg == 'ctx' or 'Context' in str(arg.annotation) for arg in func_node.args.args):
            func_info['uses_context'] = True
        
        # Verificar si retorna datos
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and node.value:
                func_info['returns_data'] = True
                break
        
        return func_info
    
    def analyze_data_pipeline(self) -> Dict[str, Any]:
        """Analiza el pipeline de procesamiento de datos"""
        print("📊 Analizando pipeline de datos...")
        
        pipeline_info = {
            'data_sources': [],
            'processing_steps': [],
            'output_formats': [],
            'caching_strategy': None,
            'error_handling': {},
            'performance_considerations': []
        }
        
        python_files = list(self.project_path.rglob('*.py'))
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Identificar fuentes de datos
                data_source_patterns = {
                    'Excel': r'pd\.read_excel|openpyxl|xlrd',
                    'CSV': r'pd\.read_csv|csv\.reader',
                    'SQL': r'pd\.read_sql|execute|cursor',
                    'JSON': r'pd\.read_json|json\.load',
                    'PDF': r'PyPDF2|pdfplumber|fitz'
                }
                
                for source_type, pattern in data_source_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        pipeline_info['data_sources'].append({
                            'type': source_type,
                            'file': str(py_file),
                            'pattern': pattern
                        })
                
                # Identificar pasos de procesamiento
                processing_patterns = {
                    'Cleaning': r'\.dropna\(|\.fillna\(|\.drop_duplicates\(',
                    'Transformation': r'\.apply\(|\.map\(|\.transform\(',
                    'Aggregation': r'\.groupby\(|\.agg\(|\.sum\(|\.mean\(',
                    'Filtering': r'\.query\(|\.loc\[|\.iloc\[',
                    'Sorting': r'\.sort_values\(|\.sort_index\(',
                    'Merging': r'\.merge\(|\.join\(|pd\.concat'
                }
                
                for step_type, pattern in processing_patterns.items():
                    matches = len(re.findall(pattern, content))
                    if matches > 0:
                        pipeline_info['processing_steps'].append({
                            'type': step_type,
                            'file': str(py_file),
                            'occurrences': matches
                        })
                
                # Identificar formatos de salida
                output_patterns = {
                    'JSON': r'\.to_json\(|json\.dump',
                    'CSV': r'\.to_csv\(',
                    'Excel': r'\.to_excel\(',
                    'SQL': r'\.to_sql\(',
                    'HTML': r'\.to_html\(',
                    'Dict': r'\.to_dict\('
                }
                
                for output_type, pattern in output_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        pipeline_info['output_formats'].append({
                            'type': output_type,
                            'file': str(py_file)
                        })
                
                # Verificar estrategias de caching
                cache_patterns = [
                    r'@lru_cache',
                    r'cache\[',
                    r'\.cache',
                    r'redis',
                    r'memcache'
                ]
                
                for pattern in cache_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        pipeline_info['caching_strategy'] = f"Detectado en {py_file}"
                        break
                
            except Exception as e:
                print(f"⚠️  Error analizando pipeline en {py_file}: {e}")
        
        return pipeline_info
    
    def analyze_statistical_capabilities(self) -> Dict[str, Any]:
        """Analiza capacidades estadísticas del proyecto"""
        print("📈 Analizando capacidades estadísticas...")
        
        stats_info = {
            'statistical_libraries': [],
            'descriptive_stats': [],
            'inferential_stats': [],
            'visualization_tools': [],
            'machine_learning': [],
            'time_series': [],
            'missing_capabilities': []
        }
        
        # Librerías estadísticas a buscar
        stat_libraries = {
            'pandas': r'import pandas|from pandas',
            'numpy': r'import numpy|from numpy',
            'scipy': r'import scipy|from scipy',
            'statsmodels': r'import statsmodels|from statsmodels',
            'scikit-learn': r'from sklearn|import sklearn',
            'matplotlib': r'import matplotlib|from matplotlib',
            'seaborn': r'import seaborn|from seaborn',
            'plotly': r'import plotly|from plotly'
        }
        
        # Funciones estadísticas descriptivas
        descriptive_functions = [
            r'\.describe\(',
            r'\.mean\(',
            r'\.median\(',
            r'\.std\(',
            r'\.var\(',
            r'\.corr\(',
            r'\.cov\(',
            r'\.quantile\('
        ]
        
        # Funciones estadísticas inferenciales
        inferential_functions = [
            r'ttest_',
            r'chi2_contingency',
            r'pearsonr',
            r'spearmanr',
            r'anova',
            r'regression',
            r'hypothesis'
        ]
        
        python_files = list(self.project_path.rglob('*.py'))
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Verificar librerías
                for lib_name, pattern in stat_libraries.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        stats_info['statistical_libraries'].append({
                            'library': lib_name,
                            'file': str(py_file)
                        })
                
                # Verificar funciones descriptivas
                for pattern in descriptive_functions:
                    matches = re.findall(pattern, content)
                    if matches:
                        stats_info['descriptive_stats'].append({
                            'function': pattern,
                            'file': str(py_file),
                            'count': len(matches)
                        })
                
                # Verificar funciones inferenciales
                for pattern in inferential_functions:
                    if re.search(pattern, content, re.IGNORECASE):
                        stats_info['inferential_stats'].append({
                            'function': pattern,
                            'file': str(py_file)
                        })
                
            except Exception as e:
                print(f"⚠️  Error analizando capacidades estadísticas en {py_file}: {e}")
        
        # Identificar capacidades faltantes
        expected_capabilities = [
            'Análisis de correlación avanzado',
            'Pruebas de hipótesis',
            'Análisis de regresión',
            'Análisis de series temporales',
            'Detección de outliers',
            'Análisis multivariado',
            'Visualizaciones estadísticas'
        ]
        
        # Esta lógica se puede expandir basada en lo que se encuentre
        if not stats_info['inferential_stats']:
            stats_info['missing_capabilities'].extend([
                'Pruebas de hipótesis',
                'Análisis inferencial'
            ])
        
        if not any('scipy' in lib['library'] for lib in stats_info['statistical_libraries']):
            stats_info['missing_capabilities'].append('Funciones estadísticas avanzadas (scipy)')
        
        return stats_info


def main():
    """Función principal para ejecutar el análisis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analizador profundo de proyecto MCP Azure Schools")
    parser.add_argument("--path", "-p", default=".", help="Ruta del proyecto a analizar")
    parser.add_argument("--enhanced", "-e", action="store_true", help="Usar análisis mejorado con características MCP específicas")
    parser.add_argument("--output", "-o", help="Archivo de salida para el reporte JSON")
    
    args = parser.parse_args()
    
    try:
        if args.enhanced:
            analyzer = EnhancedProjectAnalyzer(args.path)
            
            # Ejecutar análisis básico
            results = analyzer.run_full_analysis()
            
            # Ejecutar análisis específicos de MCP
            print("\n🚀 Ejecutando análisis avanzado MCP...")
            results['mcp_structure'] = analyzer.analyze_mcp_server_structure()
            results['data_pipeline'] = analyzer.analyze_data_pipeline()
            results['statistical_capabilities'] = analyzer.analyze_statistical_capabilities()
            
            # Imprimir resultados adicionales
            print(f"\n🔧 ANÁLISIS ESPECÍFICO MCP")
            print("-" * 40)
            mcp_struct = results['mcp_structure']
            print(f"📄 Archivos servidor MCP: {len(mcp_struct['server_files'])}")
            print(f"🛠️  Funciones herramientas: {len(mcp_struct['tool_functions'])}")
            print(f"☁️  Integraciones Azure: {len(mcp_struct['azure_integrations'])}")
            print(f"📊 Funciones procesamiento datos: {len(mcp_struct['data_processing_functions'])}")
            
            pipeline = results['data_pipeline']
            print(f"\n📊 PIPELINE DE DATOS")
            print("-" * 40)
            print(f"🔗 Fuentes de datos: {len(pipeline['data_sources'])}")
            print(f"⚙️  Pasos de procesamiento: {len(pipeline['processing_steps'])}")
            print(f"📤 Formatos de salida: {len(pipeline['output_formats'])}")
            
            stats = results['statistical_capabilities']
            print(f"\n📈 CAPACIDADES ESTADÍSTICAS")
            print("-" * 40)
            print(f"📚 Librerías estadísticas: {len(stats['statistical_libraries'])}")
            print(f"📊 Funciones descriptivas: {len(stats['descriptive_stats'])}")
            print(f"🔍 Funciones inferenciales: {len(stats['inferential_stats'])}")
            print(f"❌ Capacidades faltantes: {len(stats['missing_capabilities'])}")
            
        else:
            analyzer = ProjectAnalyzer(args.path)
            results = analyzer.run_full_analysis()
        
        if args.output:
            import json
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n💾 Reporte guardado en: {args.output}")
            
    except KeyboardInterrupt:
        print("\n❌ Análisis interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()