from fastapi import FastAPI
import uvicorn

app = FastAPI()

rules = {
    "obrigatorias": ["CPF", "Nome", "Valor_VR", "Data"],
    "regras": [
        "Se CPF estiver vazio, marcar registro como inválido",
        "Se Nome estiver ausente, sinalizar erro crítico",
        "Se Valor_VR for menor ou igual a zero, sinalizar erro",
        "Aplicar desconto de até 20% sobre o VR conforme CLT Art. 458",
        "Valores devem ser somados por colaborador no mês"
    ]
}

@app.get("/rules")
def get_rules():
    return rules

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
