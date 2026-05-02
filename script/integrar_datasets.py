import pandas as pd
import unicodedata

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return texto
    # Remove espaços extras, deixa em minusculo e remove acentos
    texto = texto.strip().lower()
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

# Carregar os datasets
df_verde = pd.read_csv('dados/verde_por_bairro.csv')
df_clima = pd.read_csv('dados/clima_otimizado.csv') 

# Criar colunas temporárias de comparação para não perder o nome original
# Serve para manter o nome bonito (com acento) no CSV final
df_verde['bairro_id'] = df_verde['bairro'].apply(normalizar_texto)
df_clima['bairro'] = df_clima['bairro'].apply(normalizar_texto) 

# Realizar o Merge (Inner Join por padrão)
# Usamos how='inner' para manter apenas os bairros presentes em ambos
df_projeto = pd.merge(
    df_verde, 
    df_clima, 
    left_on='bairro_id', 
    right_on='bairro', 
    how='inner'
)

# Remove a coluna minúscula (bairro_y)
df_projeto = df_projeto.drop(columns=['bairro_y'])

# Renomeia a sua (bairro_x) para ficar apenas 'bairro'
df_projeto = df_projeto.rename(columns={'bairro_x': 'bairro'})

# Limpeza pós-merge
# Removemos a coluna temporária e resolvemos nomes duplicados se necessário
df_projeto = df_projeto.drop(columns=['bairro_id'])

# Salvar o dataset final para a regressão
df_projeto.to_csv('dados/df_regressao.csv', index=False)

print(f"Merge concluído!")
print(f"Bairros no dataset verde: {len(df_verde)}")
print(f"Linhas no dataset de clima: {len(df_clima)}")
print(f"Linhas restantes para o modelo: {len(df_projeto)}")