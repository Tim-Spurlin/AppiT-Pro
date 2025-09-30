#!/usr/bin/env python3
"""
HAASP System Status Checker
Comprehensive verification of all components and features
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime

class HAASPSystemChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "components": {},
            "services": {},
            "features": {},
            "recommendations": []
        }
    
    def check_all(self):
        """Run comprehensive system check"""
        print("🔍 HAASP System Status Check")
        print("============================")
        
        # Check core components
        self.check_cpp_components()
        self.check_qml_interfaces()
        self.check_python_services()
        self.check_rust_webapp()
        self.check_ai_pilots()
        
        # Check running services
        self.check_running_services()
        
        # Check features
        self.check_advanced_features()
        
        # Generate overall status
        self.calculate_overall_status()
        
        # Print results
        self.print_results()
        
        return self.results
    
    def check_cpp_components(self):
        """Check C++ core components"""
        print("\n📋 Checking C++ Components...")
        
        cpp_components = {
            "executable": "build/haasp",
            "associative_nexus": "src/nucleus/associative_nexus.cpp",
            "git_service": "src/nucleus/git_service.cpp", 
            "quantum_conduit": "src/nucleus/quantum_conduit.cpp",
            "retrieval_client": "src/services/retrieval_client.cpp",
            "cmake_config": "CMakeLists.txt"
        }
        
        cpp_status = {}
        for name, path in cpp_components.items():
            file_path = self.project_root / path
            exists = file_path.exists()
            cpp_status[name] = {
                "exists": exists,
                "path": str(file_path),
                "size": file_path.stat().st_size if exists else 0
            }
            print(f"   {'✅' if exists else '❌'} {name}: {path}")
        
        self.results["components"]["cpp"] = cpp_status
    
    def check_qml_interfaces(self):
        """Check QML interface files"""
        print("\n🎨 Checking QML Interfaces...")
        
        qml_interfaces = {
            "simple_main": "src/ui/qml/SimpleMain.qml",
            "advanced_main": "src/ui/qml/AdvancedMain.qml", 
            "full_advanced": "src/ui/qml/FullAdvancedMain.qml",
            "infinite_canvas": "src/ui/qml/InfiniteCanvas.qml",
            "pilot_card": "src/ui/qml/PilotCard.qml",
            "resources": "resources.qrc"
        }
        
        qml_status = {}
        for name, path in qml_interfaces.items():
            file_path = self.project_root / path
            exists = file_path.exists()
            qml_status[name] = {
                "exists": exists,
                "path": str(file_path),
                "size": file_path.stat().st_size if exists else 0
            }
            print(f"   {'✅' if exists else '❌'} {name}: {path}")
        
        self.results["components"]["qml"] = qml_status
    
    def check_python_services(self):
        """Check Python retrieval services"""
        print("\n🐍 Checking Python Services...")
        
        python_services = {
            "faiss_manager": "retrieval_service/faiss_manager.py",
            "fts_manager": "retrieval_service/fts_manager.py",
            "graph_memory": "retrieval_service/graph_memory.py",
            "rag_orchestrator": "retrieval_service/rag_orchestrator.py",
            "main_service": "retrieval_service/main.py",
            "requirements": "retrieval_service/requirements.txt",
            "venv": "retrieval_service/.venv"
        }
        
        python_status = {}
        for name, path in python_services.items():
            file_path = self.project_root / path
            exists = file_path.exists()
            python_status[name] = {
                "exists": exists,
                "path": str(file_path),
                "is_directory": file_path.is_dir() if exists else False
            }
            print(f"   {'✅' if exists else '❌'} {name}: {path}")
        
        # Test Python imports
        print("   Testing Python imports...")
        try:
            sys.path.insert(0, str(self.project_root / "retrieval_service"))
            
            # Test basic imports
            import sentence_transformers
            print("   ✅ sentence-transformers available")
            
            try:
                import faiss
                print("   ✅ faiss available")
            except ImportError:
                print("   ⚠️ faiss not available - install with: pip install faiss-cpu")
            
            try:
                import networkx
                print("   ✅ networkx available")
            except ImportError:
                print("   ⚠️ networkx not available - install with: pip install networkx")
            
        except ImportError as e:
            print(f"   ❌ Import test failed: {e}")
        
        self.results["components"]["python"] = python_status
    
    def check_rust_webapp(self):
        """Check Rust analytics webapp"""
        print("\n🦀 Checking Rust WebApp...")
        
        rust_components = {
            "cargo_toml": "webapp/Cargo.toml",
            "main_rs": "webapp/src/main.rs",
            "executable": "webapp/target/release/haasp-insights"
        }
        
        rust_status = {}
        for name, path in rust_components.items():
            file_path = self.project_root / path
            exists = file_path.exists()
            rust_status[name] = {
                "exists": exists,
                "path": str(file_path)
            }
            print(f"   {'✅' if exists else '❌'} {name}: {path}")
        
        self.results["components"]["rust"] = rust_status
    
    def check_ai_pilots(self):
        """Check AI pilot implementations"""
        print("\n🤖 Checking AI Pilots...")
        
        pilot_files = {
            "sentinel": "pilots/sentinel.py",
            "doc_architect": "pilots/doc_architect.py",
            "remediator": "pilots/remediator.py", 
            "codewright": "pilots/codewright.py"
        }
        
        pilot_status = {}
        for name, path in pilot_files.items():
            file_path = self.project_root / path
            exists = file_path.exists()
            pilot_status[name] = {
                "exists": exists,
                "path": str(file_path),
                "size": file_path.stat().st_size if exists else 0
            }
            print(f"   {'✅' if exists else '❌'} {name}: {path}")
        
        self.results["components"]["pilots"] = pilot_status
    
    def check_running_services(self):
        """Check if services are currently running"""
        print("\n🔌 Checking Running Services...")
        
        services = {
            "retrieval_api": {"url": "http://127.0.0.1:8000", "name": "Retrieval Service"},
            "analytics_webapp": {"url": "https://127.0.0.1:7420", "name": "Analytics WebApp"}
        }
        
        service_status = {}
        for service_id, service_info in services.items():
            try:
                response = requests.get(service_info["url"], timeout=2, verify=False)
                is_running = response.status_code == 200
                service_status[service_id] = {
                    "running": is_running,
                    "url": service_info["url"],
                    "status_code": response.status_code if is_running else None
                }
                print(f"   {'✅' if is_running else '❌'} {service_info['name']}: {service_info['url']}")
                
            except Exception as e:
                service_status[service_id] = {
                    "running": False,
                    "url": service_info["url"],
                    "error": str(e)
                }
                print(f"   ❌ {service_info['name']}: Not responding ({e})")
        
        self.results["services"] = service_status
    
    def check_advanced_features(self):
        """Check availability of advanced features"""
        print("\n🎯 Checking Advanced Features...")
        
        features = {}
        
        # Check for FAISS availability
        try:
            import faiss
            features["vector_search"] = {
                "available": True,
                "gpu_support": faiss.get_num_gpus() > 0,
                "version": getattr(faiss, '__version__', 'unknown')
            }
            print(f"   ✅ Vector search (FAISS) - GPU: {'Yes' if features['vector_search']['gpu_support'] else 'No'}")
        except ImportError:
            features["vector_search"] = {"available": False, "error": "FAISS not installed"}
            print("   ❌ Vector search - FAISS not available")
        
        # Check for voice capabilities
        try:
            import sounddevice
            features["voice_activation"] = {
                "available": True,
                "devices": len(sounddevice.query_devices())
            }
            print(f"   ✅ Voice activation - {features['voice_activation']['devices']} audio devices")
        except ImportError:
            features["voice_activation"] = {"available": False, "error": "sounddevice not installed"}
            print("   ❌ Voice activation - sounddevice not available")
        
        # Check for graph capabilities
        try:
            import networkx
            features["graph_memory"] = {
                "available": True,
                "version": networkx.__version__
            }
            print(f"   ✅ Graph memory (NetworkX {networkx.__version__})")
        except ImportError:
            features["graph_memory"] = {"available": False, "error": "networkx not installed"}
            print("   ❌ Graph memory - networkx not available")
        
        # Check Qt6 capabilities
        try:
            result = subprocess.run(['qml', '--version'], capture_output=True, text=True)
            qt_version = result.stdout.strip() if result.returncode == 0 else "unknown"
            features["qt6_qml"] = {
                "available": result.returncode == 0,
                "version": qt_version
            }
            print(f"   {'✅' if features['qt6_qml']['available'] else '❌'} Qt6/QML: {qt_version}")
        except FileNotFoundError:
            features["qt6_qml"] = {"available": False, "error": "qml command not found"}
            print("   ❌ Qt6/QML - qml command not available")
        
        self.results["features"] = features
    
    def calculate_overall_status(self):
        """Calculate overall system status"""
        # Count working components
        total_components = 0
        working_components = 0
        
        for category, components in self.results["components"].items():
            for component, status in components.items():
                total_components += 1
                if status.get("exists", False):
                    working_components += 1
        
        # Count running services
        running_services = sum(1 for s in self.results["services"].values() if s.get("running", False))
        total_services = len(self.results["services"])
        
        # Count available features
        available_features = sum(1 for f in self.results["features"].values() if f.get("available", False))
        total_features = len(self.results["features"])
        
        # Calculate scores
        component_score = working_components / max(total_components, 1)
        service_score = running_services / max(total_services, 1)
        feature_score = available_features / max(total_features, 1)
        
        overall_score = (component_score * 0.5 + service_score * 0.3 + feature_score * 0.2)
        
        if overall_score >= 0.9:
            self.results["overall_status"] = "excellent"
        elif overall_score >= 0.7:
            self.results["overall_status"] = "good"
        elif overall_score >= 0.5:
            self.results["overall_status"] = "fair"
        else:
            self.results["overall_status"] = "poor"
        
        self.results["scores"] = {
            "component_score": component_score,
            "service_score": service_score,
            "feature_score": feature_score,
            "overall_score": overall_score
        }
        
        # Generate recommendations
        if component_score < 0.8:
            self.results["recommendations"].append("Some core components are missing - check build process")
        
        if service_score < 0.5:
            self.results["recommendations"].append("Services are not running - start with ./start_haasp_complete.sh")
        
        if feature_score < 0.7:
            self.results["recommendations"].append("Install missing Python packages for full functionality")
        
        if overall_score >= 0.8:
            self.results["recommendations"].append("System is ready for advanced usage!")
    
    def print_results(self):
        """Print formatted results"""
        print(f"\n📊 SYSTEM STATUS: {self.results['overall_status'].upper()}")
        print("=" * 40)
        
        scores = self.results["scores"]
        print(f"Overall Score: {scores['overall_score']:.1%}")
        print(f"Components: {scores['component_score']:.1%}")
        print(f"Services: {scores['service_score']:.1%}")
        print(f"Features: {scores['feature_score']:.1%}")
        
        if self.results["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                print(f"   • {rec}")
        
        print(f"\n🎯 NEXT STEPS:")
        if scores['overall_score'] >= 0.8:
            print("   🚀 Run: ./quick_test.sh")
            print("   📊 Visit: https://127.0.0.1:7420 for analytics")
            print("   💬 Use intelligent search and RAG features")
        else:
            print("   🔧 Fix missing components first")
            print("   📦 Install missing dependencies")
            print("   🚀 Run: ./start_haasp_complete.sh")

if __name__ == "__main__":
    checker = HAASPSystemChecker()
    results = checker.check_all()
    
    # Save results to file
    status_file = Path("~/.local/state/haasp/system_status.json").expanduser()
    status_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(status_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {status_file}")