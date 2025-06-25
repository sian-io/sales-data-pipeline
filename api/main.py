from fastapi import FastAPI
from datetime import date
import random

estados = ['SP', 'RJ', 'MG', 'ES', 'PR', 'SC', 'RS', 'MS', 'GO']
categorias = ['Eletrônicos', 'Roupas', 'Alimentos', 'Brinquedos']
statuss = ['Pendente', 'Enviado', 'Entregue', 'Cancelado']

app = FastAPI()

@app.get('/dados')
def get_dados():

    dados = []

    # Gerar uma quantidade aleatória de registros
    for _ in range(random.randint(100, 500)):

        # Dados completamente aleatórios
        id_vendedor = random.randint(1, 50)
        id_produto = random.randint(1, 100)
        quantidade = random.randint(1, 10)
        destino = random.choice(estados)
        status = random.choice(statuss)
        
        random.seed(id_produto)  # Seed baseada no id_produto para categorias e preços consistentes
        
        # Dados aleatórios consistentes
        categoria = random.choice(categorias)
        preco = round(random.uniform(19.99, 1499.99), 2)
        
        registro = {
            'id_vendedor': id_vendedor,
            'id_produto': id_produto,
            'categoria': categoria,
            'quantidade': quantidade,
            'preco': preco,
            'destino': destino,
            'status': status,
            'data': date.today()
        }
        dados.append(registro)

    return dados