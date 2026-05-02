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

📊 Estrutura de Pastas
Plaintext
RioFresco/
├── dados/               # Datasets Brutos e Processados (.csv, .geojson, .zip)
├── script/              # Scripts de automação e processamento
│   ├── baixa_csv.py     # Script de coleta via API
│   └── eda_clima.ipynb  # Notebook de análise e limpeza
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

Como rodar o projeto
Clone o repositório: git clone [https://github.com/lucasm-brandao/RioFresco.git](https://github.com/lucasm-brandao/RioFresco.git)

Instale as dependências: pip install -r requirements.txt

Execute o script de coleta: python script/baixa_csv.py --start 2020-01-01 --end 2023-12-31