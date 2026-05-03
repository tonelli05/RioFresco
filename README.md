RioFresco: Análise de Resiliência Térmica e Saúde Urbana no Rio de Janeiro 🌡️🏙️
O RioFresco é um projeto de Engenharia e Ciência de Dados desenvolvido para analisar a correlação entre a cobertura vegetal, as ondas de calor e os impactos na saúde pública (internações) na cidade do Rio de Janeiro.

Este projeto utiliza dados climáticos históricos, mapeamento geoespacial de uso do solo e indicadores oficiais de saúde do DataSUS.

🚀 Destaques Técnicos para Recrutadores
Pipeline de Dados Completo (ETL): Coleta automatizada via API, limpeza de dados brutos e agregação em camadas (Bronze/Silver).

Engenharia de Dados Geoespaciais: Uso de Geopandas para Spatial Join entre polígonos de vegetação e limites de bairros.

Integração Colaborativa: Projeto estruturado com Git Workflow (Feature Branches, Resolução de Conflitos e Conventional Commits).

Otimização de Performance: Redução de 96% no volume de dados para treinamento de modelos via agregação mensal inteligente.

🛠️ Arquitetura do Projeto
1. Coleta e Ingestão (baixa_csv.py)
Script robusto em Python para extração de dados da API Open-Meteo Archive.

Resiliência: Implementação de Exponential Backoff para lidar com Rate Limits (Erro 429).

Consistência: Sistema de Checkpoint que permite retomar downloads interrompidos sem perda de progresso.

Escalabilidade: Coleta dados diários de mais de 160 bairros do Rio de Janeiro com suporte a argumentos via CLI (argparse).

2. Processamento e Limpeza (EDA)
Processamento realizado em notebooks organizados:

Clima: Normalização de strings (NFC/NFKD), tratamento de tipos (Datetime) e criação de novas features como "Estação do Ano".

Saúde: Tratamento de encodings brasileiros (Latin1), padronização de decimais e limpeza de ruídos do DataSUS.

Vegetação: Cálculo de área real (m²) por bairro utilizando o sistema métrico SIRGAS 2000 / UTM 23S (EPSG:31983).

3. Integração de Dados 
Unificação de três fontes distintas em um dataset final para modelos de regressão:

Dataset Verde: % de cobertura vegetal por bairro.

Dataset Clima: Médias e máximas térmicas mensais.

Dataset Saúde: Taxas de internação por doenças respiratórias e circulatórias.

🧠 Pesquisa e Machine Learning (/research)

Nesta etapa, focamos a análise nos meses de verão (dezembro a fevereiro), cruzando as temperaturas e umidade recordes citadas no Anuário do Turismo 2024 com o dataset consolidado df_regressao.csv.

1. Regressão Linear (regressao_linear.ipynb)

Testamos a hipótese: "Quanto maior a porcentagem de área verde, menor a temperatura máxima do bairro".

Parâmetros analisados: Coeficiente da reta, Intercepto e $R^2$.Resultado do Modelo: O modelo apresentou um R squared de apenas 5% e um coeficiente positivo, contrariando a expectativa inicial.

Análise Crítica (Insights de Dados): A baixa performance indicou que a temperatura no Rio de Janeiro é um fenômeno multivariado. Fatores como proximidade do litoral, altitude (relevo) e densidade construída exercem maior influência que a vegetação isolada.

Artefato: Gráfico de dispersão (assets/scatter_temp_verde.png) mapeando a relação real entre essas variáveis.

2. Clusterização e Índice de Vulnerabilidade (clusterizacao.ipynb)
3. 
Diante da complexidade da regressão, aplicamos Aprendizado Não Supervisionado para segmentar os bairros conforme o risco climático.

Engenharia de Atributos - IVT: Criamos o Índice de Vulnerabilidade Térmica (IVT), uma métrica ponderada para priorizar bairros que necessitam de intervenção:
IVT = (Temp x 0.5) + ((1 - ÁreaVerde) x 0.3) + ((1 - Umidade) x 0.2)

Algoritmo KMeans (k=3): Os bairros foram segmentados em três perfis de risco:
🔴 Emergência Térmica: Altos IVTs e temperaturas extremas.
🟡 Vulnerabilidade Urbana: Nível intermediário de exposição e baixa resiliência.
🟢 Zonas de Resiliência: Baixo IVT, maior cobertura vegetal ou influência oceânica.

Redução de Dimensionalidade (PCA): Aplicamos PCA para visualizar a separação dos clusters em 2D, destacando os bairros com maior risco térmico.

Artefatos Gerados:
dados/ranking_vulnerabilidade.csv: Ranking decrescente para suporte à decisão em políticas 
públicas.assets/mapa_clusters_espacial.png: Visualização da distribuição geográfica dos riscos na capital.

📊 Estrutura de Pastas

RioFresco/
├── dados/               # Datasets Brutos e Processados (.csv, .geojson, .zip)
├── research/            # Pesquisa científica e modelagem de ML
├── script/              # Scripts de automação e processamento
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação

🧬 Principais Bibliotecas Utilizadas
Pandas: Manipulação de dados e agregação.

Geopandas: Processamento geoespacial e cruzamento de mapas.

Requests: Consumo de APIs REST.

Unicodedata: Normalização de texto e remoção de acentos.

Matplotlib/Seaborn: Visualização de padrões térmicos.

📉 Insights e Resultados Preliminares
Com base no Anuário do Turismo 2024, observamos que o Rio de Janeiro atingiu picos de 80% de ocupação hoteleira em períodos que coincidem com as maiores máximas térmicas registradas no projeto. O dataset final permite identificar se bairros com menor percentual de área verde apresentam taxas de internação superiores ao benchmark de 157,0 (média municipal para doenças respiratórias).

👷 Autor
Lucas de Moraes Brandão
Pedro Tonelli da Cunha
Isac Freire
Nargylla Fernanda Cloviel Lima

Como rodar o projeto
Clone o repositório: git clone [https://github.com/lucasm-brandao/RioFresco.git](https://github.com/lucasm-brandao/RioFresco.git)

Instale as dependências: pip install -r requirements.txt

Execute o script de coleta: python script/baixa_csv.py --start 2020-01-01 --end 2023-12-31
