import geopandas as gpd
import pandas as pd

# Carregando os arquivos
limite_bairros = gpd.read_file("dados/Limite_de_Bairros.geojson") 
solo = gpd.read_file("zip://dados/Uso_do_Solo_2019.zip")

# Colunas do json limite_bairros
print("Colunas encontradas no arquivo de bairros:", limite_bairros.columns)

# Analisando os valores presentes nas colunas desejadas
print("--- Valores únicos na coluna GRUPO ---")
print(solo['grupo'].unique())

print("\n--- Valores únicos na coluna USOAGREGAD ---")
print(solo['usoagregad'].unique())

# Valores representantes de areas verdes na coluna 'usoagregad' do arquivo solo
categorias_verdes = [
    'Cobertura arbórea e arbustiva', 
    'Cobertura gramíneo lenhosa', 
    'Áreas agrícolas'
]

# Harmonização de Coordenadas (Essencial para o sjoin) - garante que o mapa do solo use exatamente a mesma referência que o mapa de bairros (estar na mesma escala e posição)
solo = solo.to_crs(limite_bairros.crs)

# Filtrando apenas o que é vegetacao do dataset solo
vegetacao = solo[solo['usoagregad'].isin(categorias_verdes)].copy()

# Spatial Join (Cruzamento Geográfico)
# verifica a localizacao de cada polígono de vegetacao e identifica de qual bairro esse espaco eh referente
# ele cria uma nova tabela onde cada linha de vegetacao agora possui uma coluna extra com o nome do bairro ao qual ela pertence
# 'nome_bairro' deve ser o nome da coluna no seu GeoJSON de limites
verde_no_bairro = gpd.sjoin(vegetacao, limite_bairros, how="inner", predicate='within')



# ================================ CALCULANDO AREA VERDE POR BAIRRO ================================

# Antes de calcular a área, vamos converter para um sistema métrico (SIRGAS 2000 / UTM 23S - EPSG:31983)
# Isso garante que a área seja calculada em metros quadrados (m²)
verde_no_bairro = verde_no_bairro.to_crs(epsg=31983)
limite_bairros_metrico = limite_bairros.to_crs(epsg=31983)

# Calcular a área real de cada pedaço de verde (em m²)
verde_no_bairro['area_m2'] = verde_no_bairro.geometry.area

# Somar o total de area verde por bairro
relatorio_verde = verde_no_bairro.groupby('nome')['area_m2'].sum().reset_index()

# Calcular a área total do bairro (também em m²)
limite_bairros_metrico['area_total_m2'] = limite_bairros_metrico.geometry.area
area_bairros = limite_bairros_metrico[['nome', 'area_total_m2']].copy()

# Merge e Cálculo do Percentual de Area Verde por Bairro
df_final = pd.merge(relatorio_verde, area_bairros, on='nome')
df_final['percentual_verde'] = (df_final['area_m2'] / df_final['area_total_m2']) * 100

df_final = df_final[['nome', 'percentual_verde']]
df_final.columns = ['bairro', 'percentual_verde']
df_final.to_csv("dados/verde_por_bairro.csv", index=False)

print(f"Processado com unidades corrigidas! Exemplo: {df_final.iloc[0]['bairro']} = {df_final.iloc[0]['percentual_verde']:.2f}%")
print(f"Processado! {len(df_final)} bairros mapeados com áreas verdes.")




# ================================ VISUALIZAÇÃO INICIAL ================================
import matplotlib.pyplot as plt
import os

# Garantir que a pasta assets existe
os.makedirs("assets", exist_ok=True)

# Criando a visualização inicial dos dados: Mapa de Bairros e Áreas Verdes
fig, ax = plt.subplots(figsize=(12, 10))

# Plotando os limites dos bairros (em cinza claro)
limite_bairros.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.5, label='Bairros')

# Plotando as áreas de vegetação por cima (em verde)
vegetacao.plot(ax=ax, color='forestgreen', alpha=0.7, label='Vegetação')

# Adicionando título e ajustes
ax.set_title("Limites de Bairros e Áreas de Vegetação", fontsize=14)
ax.set_axis_off()

# Salvando a imagem na pasta assets
caminho_imagem = os.path.join("assets", "limte_bairros_vegetacao.png")
plt.savefig(caminho_imagem, dpi=300, bbox_inches='tight')
plt.close()
