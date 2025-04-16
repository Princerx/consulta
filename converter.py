import pandas as pd
import json
from pathlib import Path

# 1. Localiza o arquivo
nome_arquivo = "Relação imobilizados Rio Verde - 27_03_2025 (1).xlsx"
caminho_arquivo = Path.home() / "Downloads" / nome_arquivo

if not caminho_arquivo.exists():
    print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
    exit()

# 2. Conversão para JSON
try:
    # Lê o arquivo Excel
    df = pd.read_excel(caminho_arquivo, engine='openpyxl')
    
    # Mapeamento CORRIGIDO com base nas suas colunas reais
    dados = {}
    for _, row in df.iterrows():
        codigo = str(row['Imobilizado']).strip()
        
        dados[codigo] = {
            "Subnº": str(row['Subnº']) if pd.notna(row['Subnº']) else "",
            "Data": row['Incorporação em'].strftime('%d/%m/%Y') if pd.notna(row['Incorporação em']) else "",
            "Descrição": row['Denominação do imobilizado'],
            "Inventário": str(row['Nº inventário']) if pd.notna(row['Nº inventário']) else "",
            "Série": str(row['Nº de série']) if pd.notna(row['Nº de série']) else "",
            "Centro Custo": str(row['Centro custo']),
            "Link": row['Link'] if 'Link' in df.columns and pd.notna(row['Link']) else "",
            "QRCODE": row['QRCODE'] if 'QRCODE' in df.columns and pd.notna(row['QRCODE']) else ""
        }
    
    # Salva o JSON
    output_json = caminho_arquivo.parent / "dados_imobilizados.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    
    print(f"\n✅ Conversão concluída com {len(dados)} itens!")
    print(f"Arquivo JSON salvo em:\n{output_json}")

except Exception as e:
    print(f"\n❌ Erro durante o processamento:")
    print(str(e))