import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def gerar_matriz_correlacao():
    # 1. Carregar os dados
    # O arquivo df_regressao.csv parece ser o dataset ideal para isso
    df = pd.read_csv('c:/Users/user/RioFresco/dados/df_regressao.csv')
    
    # 2. Selecionar apenas as colunas numéricas de interesse
    # Excluímos 'ano' e 'mes' pois não são variáveis climáticas contínuas ou de interesse direto na matriz,
    # e 'bairro' pois é categórica. 'lat' e 'lon' podem ser interessantes, mas focaremos no clima.
    colunas_interesse = [
        'temp_max_media', 
        'temp_max_abs', 
        'percentual_verde', 
        'umidade_min_media', 
        'chuva_total'
    ]
    
    # Filtrar para ter apenas as colunas que existem no dataframe
    colunas_existentes = [col for col in colunas_interesse if col in df.columns]
    df_clima = df[colunas_existentes]
    
    # Renomeando as colunas para o gráfico ficar mais apresentável
    nomes_bonitos = {
        'temp_max_media': 'Temp. Máx. Média',
        'temp_max_abs': 'Temp. Máx. Absoluta',
        'percentual_verde': 'Área Verde (%)',
        'umidade_min_media': 'Umidade Mín. Média',
        'chuva_total': 'Chuva Total'
    }
    df_clima = df_clima.rename(columns=nomes_bonitos)
    
    # 3. Calcular a matriz de correlação (Pearson)
    matriz_corr = df_clima.corr()
    
    # 4. Configurar e gerar o gráfico (Heatmap)
    plt.figure(figsize=(10, 8))
    
    # Criar um heatmap com seaborn
    # cmap='coolwarm' é ótimo pois cores quentes (vermelho) indicam correlação positiva 
    # e cores frias (azul) indicam correlação negativa
    sns.heatmap(
        matriz_corr, 
        annot=True,          # Mostra os números dentro dos quadrados
        fmt=".2f",           # Formata para 2 casas decimais
        cmap='coolwarm', 
        vmin=-1, vmax=1,     # A correlação sempre vai de -1 a 1
        linewidths=0.5,      # Espaçamento entre os quadrados
        annot_kws={"size": 12}
    )
    
    plt.title('Matriz de Correlação - Variáveis Climáticas e Vegetação', fontsize=16, pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(rotation=0, fontsize=11)
    
    # 5. Garantir que a pasta assets existe e salvar a imagem
    os.makedirs('c:/Users/user/RioFresco/assets', exist_ok=True)
    caminho_imagem = 'c:/Users/user/RioFresco/assets/matriz_correlacao.png'
    
    plt.tight_layout()
    plt.savefig(caminho_imagem, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    gerar_matriz_correlacao()
