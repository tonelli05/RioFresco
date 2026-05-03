# RioFresco: Análise de Resiliência Térmica e Saúde Urbana no Rio de Janeiro 🌡️🏙️

O **RioFresco** é um projeto de Engenharia e Ciência de Dados desenvolvido para analisar a correlação entre a cobertura vegetal, as ondas de calor e os impactos na saúde pública na cidade do Rio de Janeiro. Este projeto utiliza dados climáticos históricos, mapeamento geoespacial de uso do solo e indicadores oficiais de saúde do Data.Rio e DataSUS.

---

## 🚀 Destaques Técnicos
*   **Pipeline de Dados Completo (ETL):** Coleta automatizada via API, limpeza de dados brutos e agregação em camadas (Bronze/Silver).
*   **Engenharia de Dados Geoespaciais:** Uso de `Geopandas` para *Spatial Join* entre polígonos de vegetação e limites de bairros.
*   **Integração Colaborativa:** Projeto estruturado com Git Workflow (Feature Branches e Conventional Commits).
*   **Otimização de Performance:** Redução de 96% no volume de dados para treinamento de modelos via agregação mensal inteligente.

---

## 🛠️ Arquitetura do Projeto

### 1. Coleta e Ingestão (`baixa_csv.py`)
Script robusto em Python para extração de dados da API Open-Meteo Archive.
*   **Resiliência:** Implementação de *Exponential Backoff* para lidar com *Rate Limits* (Erro 429).
*   **Consistência:** Sistema de *Checkpoint* para retomada de downloads interrompidos.
*   **Escalabilidade:** Coleta dados de mais de 160 bairros com suporte a argumentos via CLI.

### 2. Processamento e Limpeza (EDA)
*   **Clima:** Normalização de strings, tratamento de tipos e criação de novas features.
*   **Saúde:** Tratamento de encodings brasileiros (Latin1) e padronização de decimais do DataSUS.
*   **Vegetação:** Cálculo de área real (m²) utilizando o sistema **SIRGAS 2000 / UTM 23S (EPSG:31983)**.

### 3. Integração de Dados
Unificação de três fontes distintas em um dataset consolidado para modelos de regressão:
*   **Dataset Verde:** % de cobertura vegetal por bairro.
*   **Dataset Clima:** Médias e máximas térmicas mensais.
*   **Dataset Saúde:** Taxas de internação por doenças respiratórias e circulatórias.

---

## 🧠 Pesquisa e Machine Learning (`/research`)

### 1. Regressão Linear (`regressao_linear.ipynb`)
Testamos a hipótese de que maior área verde reduziria diretamente a temperatura máxima.
*   **Resultado:** O modelo apresentou um $R^2$ de apenas 5% e um coeficiente positivo.
*   **Insight:** A temperatura no Rio é multivariada; fatores como altitude e proximidade do mar exercem maior influência que a vegetação isolada.
*   **Artefato:** `assets/scatter_temp_verde.png`.

### 2. Clusterização e Índice de Vulnerabilidade (`clusterizacao.ipynb`)
Aplicamos **Aprendizado Não Supervisionado (K-Means)** para segmentar os bairros em 3 perfis de risco baseados no **IVT (Índice de Vulnerabilidade Térmica)**:

| Categoria | Descrição |
| :--- | :--- |
| 🔴 **Emergência Térmica** | Bairros com maior IVT e prioridade máxima de intervenção. |
| 🟡 **Vulnerabilidade Urbana** | Zonas densas com resiliência moderada e exposição intermediária. |
| 🟢 **Zonas de Resiliência** | Refúgios térmicos com maior vegetação ou influência oceânica. |

*   **PCA (Principal Component Analysis):** Redução de dimensionalidade para visualização 2D da separação dos clusters.
*   **Artefato Mestre:** `dados/ranking_vulnerabilidade.json` (Contém Bairros, IVT, Lat/Lon e PC1/PC2 para o Front-end).

---

## 📊 Estrutura de Pastas
```text
RioFresco/
├── dados/         # Datasets Brutos e JSON unificado para o Front-end
├── research/      # Notebooks de Regressão e Clusterização
├── script/        # Scripts de automação e coleta de API
├── assets/        # Visualizações de PCA e Mapas Interativos (HTML)
├── requirements.txt
└── README.md
```
👷 Autores<br>
Lucas de Moraes Brandão
Pedro Tonelli da Cunha
Isac Freire
Nargylla Fernanda Cloviel Lima
