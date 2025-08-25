# check_environment.py
import os
import sys
from pathlib import Path

def check_environment():
    print("🔍 === VERIFICAÇÃO DO AMBIENTE ===\n")
    
    issues = []
    
    # Verificar Python
    print(f"🐍 Python: {sys.version}")
    if sys.version_info < (3, 8):
        issues.append("❌ Python 3.8+ necessário")
    else:
        print("   ✅ Versão OK")
    
    # Verificar dependências
    print("\n📦 Dependências:")
    required_packages = [
        'crewai', 'pandas', 'openpyxl', 'yaml', 'requests',
        'langchain_openai', 'langchain_google_genai'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            issues.append(f"❌ {package} não instalado")
            print(f"   ❌ {package}")
    
    # Verificar variáveis de ambiente
    print("\n🔑 Variáveis de ambiente:")
    env_vars = ['LLM_PROVIDER', 'OPENAI_API_KEY']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else value
            print(f"   ✅ {var}: {masked}")
        else:
            issues.append(f"❌ {var} não configurada")
            print(f"   ❌ {var}: não configurada")
    
    # Verificar estrutura de arquivos
    print("\n📁 Estrutura de arquivos:")
    required_files = [
        'crew_project/__init__.py',
        'crew_project/config/__init__.py',
        'crew_project/config/get_llm.py',
        'crew_project/config/agents.yaml',
        'crew_project/config/tasks.yaml',
        'crew_project/tools/__init__.py',
        'crew_project/crew.py',
        'crew_project/main.py'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            issues.append(f"❌ {file_path} não encontrado")
            print(f"   ❌ {file_path}")
    
    # Resumo
    print(f"\n📊 === RESUMO ===")
    if not issues:
        print("🎉 Ambiente configurado corretamente!")
        return True
    else:
        print(f"❌ {len(issues)} problemas encontrados:")
        for issue in issues:
            print(f"   {issue}")
        return False

if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)