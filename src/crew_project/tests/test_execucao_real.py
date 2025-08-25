# test_execucao_real.py
import time
import logging
from crew_vr_project.main import *

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_execution.log'),
        logging.StreamHandler()
    ]
)

def main():
    print("🚀 === EXECUÇÃO REAL DO SISTEMA ===\n")
    
    # Verificar arquivo de dados
    arquivo_dados = "dados/vales_refeicao.zip"
    if not Path(arquivo_dados).exists():
        print(f"❌ Arquivo não encontrado: {arquivo_dados}")
        print("   Coloque seus dados reais neste caminho ou ajuste em main.py")
        return
    
    print(f"📁 Arquivo de dados: {arquivo_dados}")
    print("⏳ Iniciando execução... (pode levar alguns minutos)")
    
    start_time = time.time()
    
    try:
        # Executa o crew
        from crew_vr_project.crew import crew
        resultado = crew.kickoff(inputs={"arquivo_zip": arquivo_dados})
        
        execution_time = time.time() - start_time
        
        print(f"\n🎉 === EXECUÇÃO CONCLUÍDA em {execution_time:.2f}s ===\n")
        print("📄 RESULTADO FINAL:")
        print("=" * 60)
        print(resultado)
        print("=" * 60)
        
        # Salvar resultado
        with open(f"resultado_{int(time.time())}.txt", "w") as f:
            f.write(str(resultado))
        
        print(f"\n💾 Resultado salvo em: resultado_{int(time.time())}.txt")
        print(f"📋 Log detalhado em: test_execution.log")
        
    except KeyboardInterrupt:
        print("\n⏹️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        logging.error(f"Erro durante execução: {e}", exc_info=True)

if __name__ == "__main__":
    main()