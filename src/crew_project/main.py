from crew_project.crew import crew

if __name__ == "__main__":
    try:
        resultado = crew.kickoff(inputs={"arquivo_zip": "dados/vales_refeicao.zip"})
        print("\n=== RESULTADO FINAL ===\n")
        print(resultado)
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")