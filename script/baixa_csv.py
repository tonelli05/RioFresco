"""
clima_bairros_rio.py
--------------------
Baixa dados climáticos diários de todos os bairros oficiais
do Rio de Janeiro usando a API gratuita do Open-Meteo Archive.

Melhorias:
  - Retry automático com backoff exponencial no erro 429
  - Checkpoint: salva progresso e continua de onde parou

Uso:
    pip install requests pandas

    python clima_bairros_rio.py --start 2020-01-01 --end 2023-12-31
    python clima_bairros_rio.py --start 2020-01-01 --end 2023-12-31 --output meu_arquivo.csv
    python clima_bairros_rio.py --start 2020-01-01 --end 2023-12-31 --delay 1.5

Parâmetros:
    --start     Data inicial no formato YYYY-MM-DD (padrão: 2020-01-01)
    --end       Data final   no formato YYYY-MM-DD (padrão: 2023-12-31)
    --output    Nome do CSV de saída                (padrão: clima_rio.csv)
    --delay     Segundos entre requisições           (padrão: 1.0)
    --max-retry Máximo de tentativas por bairro      (padrão: 5)
"""

import argparse
import time
import sys
import os

import requests
import pandas as pd


# ---------------------------------------------------------------------------
# 1. VARIÁVEIS CLIMÁTICAS
# ---------------------------------------------------------------------------
VARIAVEIS_DIARIAS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "rain_sum",
    "windspeed_10m_max",
    "relative_humidity_2m_max",
    "relative_humidity_2m_min",
    "et0_fao_evapotranspiration",
]


# ---------------------------------------------------------------------------
# 2. LISTA COMPLETA DOS BAIRROS OFICIAIS DO RIO DE JANEIRO
# ---------------------------------------------------------------------------
BAIRROS_RIO = [
    # ZONA SUL
    ("Catete",                      -22.9260, -43.1786),
    ("Flamengo",                    -22.9320, -43.1746),
    ("Glória",                      -22.9160, -43.1756),
    ("Laranjeiras",                 -22.9357, -43.1868),
    ("Cosme Velho",                 -22.9426, -43.1930),
    ("Botafogo",                    -22.9458, -43.1850),
    ("Humaitá",                     -22.9530, -43.1910),
    ("Urca",                        -22.9510, -43.1630),
    ("Copacabana",                  -22.9711, -43.1823),
    ("Leme",                        -22.9627, -43.1666),
    ("Ipanema",                     -22.9838, -43.2096),
    ("Leblon",                      -22.9846, -43.2227),
    ("Lagoa",                       -22.9735, -43.2140),
    ("Jardim Botânico",             -22.9660, -43.2260),
    ("Gávea",                       -22.9800, -43.2360),
    ("São Conrado",                 -22.9990, -43.2700),
    ("Vidigal",                     -22.9960, -43.2500),
    ("Alto Leblon",                 -22.9760, -43.2380),
    ("Joá",                         -23.0040, -43.2980),
    ("Rocinha",                     -22.9877, -43.2480),
    # CENTRO
    ("Centro",                      -22.9028, -43.1731),
    ("Gamboa",                      -22.8970, -43.1900),
    ("Saúde",                       -22.8940, -43.1820),
    ("Santo Cristo",                -22.8980, -43.2030),
    ("Caju",                        -22.8820, -43.2180),
    ("Cidade Nova",                 -22.9070, -43.2000),
    ("Estácio",                     -22.9130, -43.2010),
    ("Rio Comprido",                -22.9190, -43.2050),
    ("Catumbi",                     -22.9210, -43.2050),
    ("Santa Teresa",                -22.9206, -43.1770),
    ("Lapa",                        -22.9120, -43.1810),
    ("Paquetá",                     -22.7650, -43.1130),
    # ZONA NORTE - TIJUCA / VILA ISABEL
    ("Tijuca",                      -22.9231, -43.2340),
    ("Alto da Boa Vista",           -22.9460, -43.2700),
    ("Grajaú",                      -22.9000, -43.2600),
    ("Andaraí",                     -22.9148, -43.2540),
    ("Maracanã",                    -22.9122, -43.2302),
    ("Vila Isabel",                 -22.9200, -43.2700),
    ("Praça da Bandeira",           -22.9050, -43.2350),
    # ZONA NORTE - MÉIER E ADJACÊNCIAS
    ("Méier",                       -22.8980, -43.2960),
    ("Engenho Novo",                -22.8980, -43.2700),
    ("Lins de Vasconcelos",         -22.8900, -43.3020),
    ("Cachambi",                    -22.8860, -43.2760),
    ("Todos os Santos",             -22.8850, -43.3100),
    ("Riachuelo",                   -22.8950, -43.2860),
    ("Rocha",                       -22.8930, -43.2950),
    ("São Francisco Xavier",        -22.9020, -43.2600),
    ("Sampaio",                     -22.9030, -43.2990),
    ("Engenho de Dentro",           -22.9050, -43.3150),
    ("Água Santa",                  -22.8930, -43.3200),
    ("Abolição",                    -22.8810, -43.3300),
    ("Pilares",                     -22.8820, -43.3050),
    ("Del Castilho",                -22.8760, -43.3160),
    ("Inhaúma",                     -22.8680, -43.2960),
    ("Engenho da Rainha",           -22.8570, -43.3200),
    ("Tomás Coelho",                -22.8760, -43.3440),
    ("Higienópolis",                -22.8700, -43.2980),
    ("Jacaré",                      -22.8830, -43.2570),
    # ZONA NORTE - RAMOS / PENHA
    ("Ramos",                       -22.8530, -43.2600),
    ("Bonsucesso",                  -22.8600, -43.2530),
    ("Manguinhos",                  -22.8680, -43.2410),
    ("Benfica",                     -22.8870, -43.2280),
    ("São Cristóvão",               -22.8960, -43.2260),
    ("Mangueira",                   -22.9050, -43.2380),
    ("Olaria",                      -22.8560, -43.2690),
    ("Penha",                       -22.8490, -43.2960),
    ("Penha Circular",              -22.8470, -43.3060),
    ("Brás de Pina",                -22.8400, -43.3060),
    ("Cordovil",                    -22.8330, -43.3330),
    ("Parada de Lucas",             -22.8350, -43.3200),
    ("Vigário Geral",               -22.8280, -43.3440),
    ("Complexo do Alemão",          -22.8600, -43.2700),
    ("Maré",                        -22.8560, -43.2430),
    # ZONA NORTE - IRAJÁ / MADUREIRA
    ("Irajá",                       -22.8300, -43.3400),
    ("Colégio",                     -22.8450, -43.3560),
    ("Coelho Neto",                 -22.8430, -43.3700),
    ("Acari",                       -22.8450, -43.3940),
    ("Anchieta",                    -22.8180, -43.3440),
    ("Guadalupe",                   -22.8280, -43.3760),
    ("Parque Anchieta",             -22.8200, -43.3600),
    ("Ricardo de Albuquerque",      -22.8370, -43.3820),
    ("Madureira",                   -22.8700, -43.3400),
    ("Turiaçu",                     -22.8730, -43.3620),
    ("Rocha Miranda",               -22.8620, -43.3600),
    ("Honório Gurgel",              -22.8580, -43.3760),
    ("Campinho",                    -22.8780, -43.3580),
    ("Cascadura",                   -22.8790, -43.3700),
    ("Cavalcanti",                  -22.8820, -43.3860),
    ("Engenheiro Leal",             -22.8870, -43.3940),
    ("Quintino Bocaiuva",           -22.8910, -43.3800),
    ("Oswaldo Cruz",                -22.8820, -43.3640),
    ("Vaz Lobo",                    -22.8660, -43.3700),
    ("Vicente de Carvalho",         -22.8540, -43.3420),
    ("Vista Alegre",                -22.8600, -43.3500),
    ("Pavuna",                      -22.8110, -43.4000),
    # ILHA DO GOVERNADOR
    ("Ilha do Governador",          -22.7900, -43.1850),
    ("Bancários",                   -22.8020, -43.2060),
    ("Cacuia",                      -22.7840, -43.2120),
    ("Cocotá",                      -22.7960, -43.2030),
    ("Freguesia (Ilha)",            -22.8070, -43.2140),
    ("Galeão",                      -22.8090, -43.2440),
    ("Jardim Guanabara",            -22.7960, -43.1930),
    ("Moneró",                      -22.7990, -43.2300),
    ("Pitangueiras",                -22.8020, -43.2200),
    ("Portuguesa",                  -22.8100, -43.2350),
    ("Praia da Bandeira",           -22.8140, -43.2150),
    ("Ribeira",                     -22.7900, -43.2280),
    ("Tauá",                        -22.8030, -43.2470),
    ("Zumbi",                       -22.7970, -43.1990),
    # ZONA OESTE - BARRA / RECREIO / JACAREPAGUÁ
    ("Barra da Tijuca",             -23.0000, -43.3650),
    ("Recreio dos Bandeirantes",    -23.0200, -43.4600),
    ("Vargem Grande",               -22.9980, -43.4700),
    ("Vargem Pequena",              -22.9930, -43.4500),
    ("Camorim",                     -22.9780, -43.4280),
    ("Grumari",                     -23.0350, -43.5180),
    ("Itanhangá",                   -22.9850, -43.3220),
    ("Jacarepaguá",                 -22.9340, -43.3780),
    ("Taquara",                     -22.9340, -43.4000),
    ("Pechincha",                   -22.9360, -43.3600),
    ("Freguesia (Jacarepaguá)",     -22.9430, -43.3430),
    ("Praça Seca",                  -22.9200, -43.3700),
    ("Tanque",                      -22.9330, -43.3470),
    ("Anil",                        -22.9380, -43.3390),
    ("Gardênia Azul",               -22.9430, -43.3640),
    ("Curicica",                    -22.9500, -43.3780),
    ("Cidade de Deus",              -22.9580, -43.3660),
    ("Sulacap",                     -22.8980, -43.3980),
    ("Magalhães Bastos",            -22.8960, -43.4180),
    # ZONA OESTE - BANGU / CAMPO GRANDE / SANTA CRUZ
    ("Realengo",                    -22.8730, -43.4200),
    ("Padre Miguel",                -22.8820, -43.4460),
    ("Bangu",                       -22.8760, -43.4640),
    ("Senador Camará",              -22.8960, -43.4820),
    ("Gericinó",                    -22.8680, -43.4560),
    ("Deodoro",                     -22.8530, -43.3980),
    ("Vila Militar",                -22.8570, -43.4150),
    ("Campo dos Afonsos",           -22.8530, -43.4310),
    ("Jardim Sulacap",              -22.8980, -43.4120),
    ("Campo Grande",                -22.9020, -43.5570),
    ("Cosmos",                      -22.8980, -43.6180),
    ("Inhoaíba",                    -22.8900, -43.5680),
    ("Santíssimo",                  -22.8840, -43.5200),
    ("Senador Vasconcelos",         -22.9090, -43.5330),
    ("Santa Cruz",                  -22.9110, -43.6920),
    ("Sepetiba",                    -22.9750, -43.7100),
    ("Paciência",                   -22.8960, -43.6480),
    ("Guaratiba",                   -23.0500, -43.5800),
    ("Pedra de Guaratiba",          -23.0450, -43.6010),
    ("Barra de Guaratiba",          -23.0470, -43.5640),
    ("Antares",                     -22.8970, -43.6350),
]

# Remove duplicatas mantendo a primeira ocorrência
_seen = set()
BAIRROS_UNICOS = []
for b in BAIRROS_RIO:
    if b[0] not in _seen:
        _seen.add(b[0])
        BAIRROS_UNICOS.append(b)


# ---------------------------------------------------------------------------
# 3. DOWNLOAD COM RETRY + BACKOFF
# ---------------------------------------------------------------------------
URL_OPENMETEO = "https://archive-api.open-meteo.com/v1/archive"

def baixar_clima_bairro(bairro, lat, lon, start, end, max_retry=5, delay_base=1.0):
    """
    Baixa dados de um bairro com retry automático em caso de 429.
    Em cada tentativa, dobra o tempo de espera (backoff exponencial).
    """
    params = {
        "latitude":   lat,
        "longitude":  lon,
        "start_date": start,
        "end_date":   end,
        "daily":      ",".join(VARIAVEIS_DIARIAS),
        "timezone":   "America/Sao_Paulo",
    }

    for tentativa in range(1, max_retry + 1):
        try:
            resp = requests.get(URL_OPENMETEO, params=params, timeout=30)

            if resp.status_code == 429:
                wait = delay_base * (2 ** tentativa)  # 2s, 4s, 8s, 16s, 32s
                print(f"\n      ⏳ Rate limit (429). Tentativa {tentativa}/{max_retry}. Aguardando {wait:.0f}s...", end=" ", flush=True)
                time.sleep(wait)
                continue

            resp.raise_for_status()
            dados = resp.json()

            daily = dados.get("daily", {})
            if not daily or "time" not in daily:
                return None

            df = pd.DataFrame(daily)
            df.rename(columns={"time": "data"}, inplace=True)
            df.insert(0, "bairro", bairro)
            df.insert(1, "lat", lat)
            df.insert(2, "lon", lon)
            return df

        except requests.exceptions.HTTPError as e:
            if tentativa == max_retry:
                print(f"\n      ❌ Falhou após {max_retry} tentativas: {e}")
                return None
        except Exception as e:
            print(f"\n      ❌ Erro inesperado: {e}")
            return None

    return None


# ---------------------------------------------------------------------------
# 4. MAIN COM CHECKPOINT
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start",     default="2020-01-01")
    parser.add_argument("--end",       default="2023-12-31")
    parser.add_argument("--output",    default="clima_rio.csv")
    parser.add_argument("--delay",     type=float, default=1.0,
                        help="Segundos de espera entre bairros (padrão: 1.0)")
    parser.add_argument("--max-retry", type=int,   default=5,
                        help="Máx. tentativas por bairro em caso de 429 (padrão: 5)")
    args = parser.parse_args()

    # Arquivo de checkpoint: guarda bairros já baixados
    checkpoint_file = args.output.replace(".csv", "_checkpoint.csv")

    # Carrega checkpoint se existir
    ja_baixados = set()
    chunks_existentes = []
    if os.path.exists(checkpoint_file):
        df_check = pd.read_csv(checkpoint_file)
        ja_baixados = set(df_check["bairro"].unique())
        chunks_existentes.append(df_check)
        print(f"♻️  Checkpoint encontrado: {len(ja_baixados)} bairros já baixados. Continuando...")

    total = len(BAIRROS_UNICOS)
    pendentes = [(b, la, lo) for b, la, lo in BAIRROS_UNICOS if b not in ja_baixados]

    print(f"🌦️  Baixando dados de {args.start} até {args.end}")
    print(f"📍 {len(pendentes)} bairros restantes de {total} no total\n")

    resultados = list(chunks_existentes)
    falhos = []

    for i, (bairro, lat, lon) in enumerate(pendentes):
        idx_global = total - len(pendentes) + i + 1
        print(f"  [{idx_global:03d}/{total}] {bairro:<35} ({lat}, {lon})", end=" ", flush=True)

        df = baixar_clima_bairro(bairro, lat, lon, args.start, args.end,
                                  max_retry=args.max_retry, delay_base=args.delay)

        if df is not None:
            resultados.append(df)
            print(f"✅ {len(df)} dias")

            # Salva checkpoint a cada bairro concluído
            pd.concat(resultados, ignore_index=True).to_csv(
                checkpoint_file, index=False, encoding="utf-8-sig"
            )
        else:
            falhos.append(bairro)
            print("❌ falhou definitivamente")

        time.sleep(args.delay)

    # Salva CSV final
    if not resultados:
        print("\n❌ Nenhum dado coletado.")
        sys.exit(1)

    df_final = pd.concat(resultados, ignore_index=True)
    df_final.to_csv(args.output, index=False, encoding="utf-8-sig")

    # Remove checkpoint se tudo terminou
    if not falhos and os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)
        print(f"\n🗑️  Checkpoint removido (download completo).")

    print(f"\n✅ Concluído!")
    print(f"   Linhas:            {len(df_final):,}")
    print(f"   Bairros com dados: {df_final['bairro'].nunique()} de {total}")
    if falhos:
        print(f"   ⚠️  Bairros que falharam ({len(falhos)}): {', '.join(falhos)}")
    print(f"   Arquivo:           {args.output}")
    print(f"   Colunas:           {list(df_final.columns)}")


if __name__ == "__main__":
    main()


# python baixa_csv.py --start 2020-01-01 --end 2023-12-31 --delay 2.0