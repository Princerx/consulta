import pandas as pd
import json
from pathlib import Path
import re
import os
import sys

def formatar_valor(valor, tipo='string'):
    """Formata valores removendo decimais desnecessários e espaços em branco"""
    if pd.isna(valor):
        return ""
        
    if tipo == 'string':
        return str(valor).strip()
        
    elif tipo == 'inteiro':
        try:
            # Remove .0 de floats inteiros
            if isinstance(valor, float) and valor.is_integer():
                return str(int(valor))
            return re.sub(r'\.0$', '', str(valor)).strip()
        except:
            return str(valor).strip()
    
    return str(valor).strip()

# Definição de caminhos
# Caminho para salvar o arquivo JSON
caminho_saida = r"C:\Users\wanderson.oliveira\Desktop\consulta-imobilizados"

# Detecta o sistema operacional e ajusta o caminho do arquivo de entrada
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
nome_arquivo = "Relação imobilizados Rio Verde - 27_03_2025 (1).XLSX"
caminho_arquivo = os.path.join(diretorio_atual, nome_arquivo)

# Verifica se o arquivo existe
if not os.path.exists(caminho_arquivo):
    print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
    print(f"Por favor, coloque o arquivo '{nome_arquivo}' na mesma pasta deste script.")
    exit()

# Verifica se o diretório de saída existe, se não, tenta criar
if not os.path.exists(caminho_saida):
    try:
        os.makedirs(caminho_saida)
        print(f"✅ Diretório de saída criado: {caminho_saida}")
    except Exception as e:
        print(f"❌ Erro ao criar diretório de saída: {str(e)}")
        print("Por favor, crie manualmente o diretório ou ajuste o caminho no código.")
        exit()

# Conversão para JSON com validações
try:
    # Carrega o arquivo Excel
    df = pd.read_excel(caminho_arquivo, engine='openpyxl')
    
    # Verifica colunas obrigatórias
    colunas_obrigatorias = ['Imobilizado', 'Subnº', 'Incorporação em', 
                           'Denominação do imobilizado', 'Nº inventário', 
                           'Nº de série', 'Centro custo']
    
    faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
    if faltantes:
        print(f"❌ Colunas obrigatórias ausentes: {', '.join(faltantes)}")
        exit()

    # Pré-processamento de dados
    df['Incorporação em'] = pd.to_datetime(df['Incorporação em'], errors='coerce')
    df['Imobilizado'] = df['Imobilizado'].apply(lambda x: formatar_valor(x, 'string'))

    # Estrutura para armazenamento
    dados = {}
    linhas_ignoradas = 0
    codigos_invalidos = set()

    for idx, row in df.iterrows():
        # Validação do código imobilizado
        codigo = formatar_valor(row['Imobilizado'], 'string')
        if not codigo or codigo.lower() in ['nan', 'none', 'null']:
            codigos_invalidos.add(str(row['Imobilizado']))
            linhas_ignoradas += 1
            continue

        # Validação de campos críticos
        if any([
            pd.isna(row['Denominação do imobilizado']),
            pd.isna(row['Centro custo'])
        ]):
            linhas_ignoradas += 1
            continue

        # Construção do item
        item = {
            "Subnº": formatar_valor(row['Subnº'], 'inteiro'),
            "Data": row['Incorporação em'].strftime('%d/%m/%Y') if pd.notna(row['Incorporação em']) else "Data desconhecida",
            "Descrição": formatar_valor(row['Denominação do imobilizado']),
            "Inventário": formatar_valor(row['Nº inventário'], 'inteiro'),
            "Série": formatar_valor(row['Nº de série'], 'inteiro'),
            "Centro Custo": formatar_valor(row['Centro custo'], 'inteiro'),
            "Link": f"https://videplast.com.br/consulta-imobilizado?id={codigo}&nome={formatar_valor(row['Denominação do imobilizado']).replace(' ', '%20')}",
            "QRCODE": ""
        }

        # Adiciona à estrutura de dados
        if codigo not in dados:
            dados[codigo] = {"itens": []}
        
        # Adiciona o item à lista de itens do imobilizado
        dados[codigo]["itens"].append(item)

    # Geração do arquivo JSON
    output_json = os.path.join(caminho_saida, "dados_imobilizados_corrigidos.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    # Relatório de processamento
    total_codigos = len(dados)
    total_itens = sum(len(v["itens"]) for v in dados.values())
    
    print(f"\n✅ Conversão concluída!")
    print(f"👉 Códigos processados: {total_codigos}")
    print(f"👉 Itens totais: {total_itens}")
    print(f"👉 Linhas ignoradas: {linhas_ignoradas}")
    
    if codigos_invalidos:
        print(f"\n⚠️  Códigos inválidos encontrados: {', '.join(codigos_invalidos)[:50]}...")

    print(f"\nArquivo JSON gerado em:\n{output_json}")

    # Verificação específica do imobilizado 20000076
    if "20000076" in dados:
        print(f"\n🔍 Verificação do imobilizado 20000076:")
        print(f"   Total de itens: {len(dados['20000076']['itens'])}")
        for i, item in enumerate(dados['20000076']['itens']):
            print(f"   Item {i+1}: Subnº {item['Subnº']} - {item['Descrição'][:40]}...")

    # Aguarda entrada do usuário antes de fechar (útil para Windows)
    input("\nPressione Enter para sair...")

except Exception as e:
    print(f"\n❌ Erro durante o processamento:")
    print(f"Tipo do erro: {type(e).__name__}")
    print(f"Detalhes: {str(e)}")
    if 'df' in locals():
        print(f"\n📄 Amostra dos dados problemáticos:\n{df.head(3)}")
    
    # Aguarda entrada do usuário antes de fechar (útil para Windows)
    input("\nPressione Enter para sair...")
