"""
Pilot 1.0: Doc Architect - Documentation synthesis and organization
Creates comprehensive documentation from code analysis and user interactions
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import markdown
from jinja2 import Template

logger = logging.getLogger(__name__)

class DocArchitectPilot:
    """
    Doc Architect: The master of documentation and knowledge organization

    Responsibilities:
    - Analyze codebases and generate comprehensive documentation
    - Create API documentation, READMEs, and architectural diagrams
    - Maintain documentation consistency and completeness
    - Generate tutorials and usage examples
    - Organize knowledge in structured formats
    """

    def __init__(self, docs_path: str = "~/.local/share/haasp/docs"):
        self.docs_path = Path(docs_path).expanduser()
        self.docs_path.mkdir(parents=True, exist_ok=True)

        # Documentation templates
        self.templates = {
            'readme': self._load_readme_template(),
            'api': self._load_api_template(),
            'architecture': self._load_architecture_template()
        }

        # Documentation state
        self.project_docs = {}
        self.generated_docs = set()

        logger.info("Doc Architect initialized")

    def _load_readme_template(self) -> Template:
        template_str = """
# {{ project_name }}

{{ description }}

## Features

{% for feature in features %}
- {{ feature }}
{% endfor %}

## Installation

```bash
{{ installation_instructions }}
```

## Usage

{{ usage_examples }}

## API Reference

{{ api_reference }}

## Architecture

{{ architecture_overview }}

## Contributing

{{ contributing_guidelines }}

## License

{{ license_info }}
"""
        return Template(template_str)

    def _load_api_template(self) -> Template:
        template_str = """
# API Reference - {{ module_name }}

## Overview

{{ overview }}

## Classes

{% for class_info in classes %}
### {{ class_info.name }}

{{ class_info.description }}

**Methods:**
{% for method in class_info.methods %}
- `{{ method.signature }}` - {{ method.description }}
{% endfor %}

**Properties:**
{% for prop in class_info.properties %}
- `{{ prop.name }}` - {{ prop.description }}
{% endfor %}
{% endfor %}

## Functions

{% for func in functions %}
### {{ func.name }}

**Signature:** `{{ func.signature }}`

{{ func.description }}

**Parameters:**
{% for param in func.parameters %}
- `{{ param.name }}` ({{ param.type }}): {{ param.description }}
{% endfor %}

**Returns:** {{ func.returns }}
{% endfor %}
"""
        return Template(template_str)

    def _load_architecture_template(self) -> Template:
        template_str = """
# Architecture Overview - {{ project_name }}

## System Components

```mermaid
graph TD
{% for component in components %}
    {{ component.id }}[{{ component.name }}]
{% endfor %}

{% for connection in connections %}
    {{ connection.from }} --> {{ connection.to }}
{% endfor %}
```

## Data Flow

{{ data_flow_description }}

## Key Design Decisions

{% for decision in design_decisions %}
### {{ decision.title }}

{{ decision.description }}

**Rationale:** {{ decision.rationale }}
{% endfor %}

## Technology Stack

{% for tech in tech_stack %}
- **{{ tech.category }}:** {{ tech.technologies|join(', ') }}
{% endfor %}
"""
        return Template(template_str)

    async def analyze_codebase(self, repo_path: str) -> Dict[str, Any]:
        """Analyze a codebase and generate documentation structure"""
        logger.info(f"Analyzing codebase: {repo_path}")

        # This would integrate with the Git service to analyze code
        # For now, return a basic structure

        analysis = {
            'project_name': Path(repo_path).name,
            'language': self._detect_language(repo_path),
            'structure': self._analyze_structure(repo_path),
            'dependencies': self._analyze_dependencies(repo_path),
            'entry_points': self._find_entry_points(repo_path)
        }

        return analysis

    async def generate_readme(self, analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive README.md"""
        logger.info("Generating README.md")

        context = {
            'project_name': analysis.get('project_name', 'Project'),
            'description': self._generate_description(analysis),
            'features': self._extract_features(analysis),
            'installation_instructions': self._generate_installation(analysis),
            'usage_examples': self._generate_usage_examples(analysis),
            'api_reference': 'See API documentation for details',
            'architecture_overview': 'See Architecture documentation',
            'contributing_guidelines': self._generate_contributing(),
            'license_info': 'MIT License - see LICENSE file'
        }

        return self.templates['readme'].render(**context)

    async def generate_api_docs(self, analysis: Dict[str, Any]) -> str:
        """Generate API documentation"""
        logger.info("Generating API documentation")

        # Extract classes, functions, etc. from analysis
        classes = self._extract_classes(analysis)
        functions = self._extract_functions(analysis)

        context = {
            'module_name': analysis.get('project_name', 'Module'),
            'overview': f"API documentation for {analysis.get('project_name', 'the module')}",
            'classes': classes,
            'functions': functions
        }

        return self.templates['api'].render(**context)

    async def generate_architecture_docs(self, analysis: Dict[str, Any]) -> str:
        """Generate architecture documentation"""
        logger.info("Generating architecture documentation")

        components = self._extract_components(analysis)
        connections = self._extract_connections(analysis)

        context = {
            'project_name': analysis.get('project_name', 'Project'),
            'components': components,
            'connections': connections,
            'data_flow_description': self._generate_data_flow(analysis),
            'design_decisions': self._extract_design_decisions(analysis),
            'tech_stack': self._extract_tech_stack(analysis)
        }

        return self.templates['architecture'].render(**context)

    def _detect_language(self, repo_path: str) -> str:
        """Detect primary programming language"""
        # Simple detection based on file extensions
        extensions = {}
        for file_path in Path(repo_path).rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1

        # Map extensions to languages
        lang_map = {
            '.py': 'Python',
            '.cpp': 'C++',
            '.hpp': 'C++',
            '.rs': 'Rust',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.qml': 'QML'
        }

        max_ext = max(extensions.items(), key=lambda x: x[1], default=('', 0))[0]
        return lang_map.get(max_ext, 'Unknown')

    def _analyze_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze project structure"""
        structure = {
            'directories': [],
            'main_files': [],
            'config_files': []
        }

        for item in Path(repo_path).iterdir():
            if item.is_dir():
                structure['directories'].append(item.name)
            elif item.is_file():
                if item.name in ['main.py', 'main.cpp', 'main.rs', 'index.js']:
                    structure['main_files'].append(item.name)
                elif item.name in ['CMakeLists.txt', 'Cargo.toml', 'package.json', 'requirements.txt']:
                    structure['config_files'].append(item.name)

        return structure

    def _analyze_dependencies(self, repo_path: str) -> List[str]:
        """Analyze project dependencies"""
        deps = []

        # Check for requirements.txt
        req_file = Path(repo_path) / 'requirements.txt'
        if req_file.exists():
            with open(req_file, 'r') as f:
                deps.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])

        # Check for Cargo.toml
        cargo_file = Path(repo_path) / 'Cargo.toml'
        if cargo_file.exists():
            # Simple parsing - in real implementation, use toml library
            deps.append("Rust dependencies (see Cargo.toml)")

        return deps

    def _find_entry_points(self, repo_path: str) -> List[str]:
        """Find application entry points"""
        entry_points = []

        # Common entry point files
        candidates = ['main.py', 'main.cpp', 'main.rs', 'index.js', 'app.py', '__main__.py']
        for candidate in candidates:
            if (Path(repo_path) / candidate).exists():
                entry_points.append(candidate)

        return entry_points

    def _generate_description(self, analysis: Dict[str, Any]) -> str:
        """Generate project description"""
        name = analysis.get('project_name', 'Project')
        lang = analysis.get('language', 'Unknown')
        return f"A {lang} project called {name} built with HAASP."

    def _extract_features(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract key features from analysis"""
        features = ["Advanced code analysis", "Documentation generation"]

        if analysis.get('language') == 'Python':
            features.append("Python-based implementation")
        elif analysis.get('language') == 'C++':
            features.append("High-performance C++ core")
        elif analysis.get('language') == 'Rust':
            features.append("Memory-safe Rust components")

        return features

    def _generate_installation(self, analysis: Dict[str, Any]) -> str:
        """Generate installation instructions"""
        lang = analysis.get('language', 'Unknown')

        if lang == 'Python':
            return "pip install -r requirements.txt"
        elif lang == 'Rust':
            return "cargo build --release"
        elif lang == 'C++':
            return "mkdir build && cd build && cmake .. && make"
        else:
            return "See project documentation for installation instructions"

    def _generate_usage_examples(self, analysis: Dict[str, Any]) -> str:
        """Generate usage examples"""
        return """
## Basic Usage

```bash
# Run the application
./run.sh

# For development
./start.sh development
```
"""

    def _generate_contributing(self) -> str:
        """Generate contributing guidelines"""
        return """
## Development

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Code Style

- Follow the existing code style
- Add tests for new features
- Update documentation as needed
"""

    def _extract_classes(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract class information from analysis"""
        # This would require actual code parsing
        # For now, return empty list
        return []

    def _extract_functions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract function information from analysis"""
        # This would require actual code parsing
        return []

    def _extract_components(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract system components"""
        components = [
            {'id': 'ui', 'name': 'User Interface'},
            {'id': 'core', 'name': 'Core Logic'},
            {'id': 'data', 'name': 'Data Layer'}
        ]

        lang = analysis.get('language', '')
        if lang:
            components.append({'id': 'lang', 'name': f'{lang} Runtime'})

        return components

    def _extract_connections(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract component connections"""
        return [
            {'from': 'ui', 'to': 'core'},
            {'from': 'core', 'to': 'data'}
        ]

    def _generate_data_flow(self, analysis: Dict[str, Any]) -> str:
        """Generate data flow description"""
        return """
Data flows from the user interface through the core logic layer to the data persistence layer.
Results are processed and returned through the same path in reverse.
"""

    def _extract_design_decisions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract design decisions"""
        return [
            {
                'title': 'Architecture Choice',
                'description': f'Chose {analysis.get("language", "the selected")} language for its performance and ecosystem fit.',
                'rationale': 'Best tool for the job requirements.'
            }
        ]

    def _extract_tech_stack(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract technology stack"""
        stack = [
            {'category': 'Language', 'technologies': [analysis.get('language', 'Unknown')]}
        ]

        deps = analysis.get('dependencies', [])
        if deps:
            stack.append({'category': 'Dependencies', 'technologies': deps[:5]})  # Limit to 5

        return stack