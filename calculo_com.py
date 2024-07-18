import pandas as pd
from datetime import datetime
import logging
import re

# TAREFA 1: CALCULO DE COMISSÕES
def calcula_comissao():
    try:
        df_original = pd.read_excel('Vendas_aaws.xlsx', sheet_name=None, index_col=None)
        df_vendas = df_original['Vendas']

        
        # Criando um novo DF com apenas os dados necessários e com base no original para não modificarmos os dados originais
        dados_vendas = df_vendas[['Nome do Vendedor','Valor da Venda','Canal de Venda']]
        
        # Removendo todos os carateres não necessários e convertendo os valores da coluna "valor da venda"
        dados_vendas['Valor da Venda'] = df_vendas['Valor da Venda'].replace({'R\$ ': '',',00':'','\.':''}, regex=True).astype(float)

        dados_vendas['Comissão do Vendedor'] = dados_vendas['Valor da Venda'] * 0.10

        # Comissão DO MARKETING: foi utilizado o parametro 'axis=1' para refernciar a operação ao longo das colunas e não somente na série
        dados_vendas['comissão do marketing'] = dados_vendas.apply(lambda row: row['Comissão do Vendedor'] * 0.20 if row['Canal de Venda'] == 'Online' else 0, axis=1)

        # tabela pronta
        dados_vendas = dados_vendas.groupby('Nome do Vendedor').agg({'Valor da Venda': 'sum', 'Comissão do Vendedor': 'sum', 'comissão do marketing': 'sum'}).reset_index()       

        dados_vendas['comissão do gerente'] = dados_vendas.apply(lambda row: row['Comissão do Vendedor'] * 0.10 if row['Comissão do Vendedor'] >= 1500 else 0, axis=1)
        dados_vendas['Valor a Receber'] = round(dados_vendas['Comissão do Vendedor'] - dados_vendas['comissão do marketing'] - dados_vendas['comissão do gerente'],2)

        dados_vendas = dados_vendas[['Nome do Vendedor','Comissão do Vendedor','Valor a Receber']]
        print(dados_vendas)

        return dados_vendas

    except BaseException as error:
        logging.exception(error)
        log_falhas[datetime.now().strftime('%Y-%m-%d %H:%M:%S')] = error

# TAREFA 2 - Verifica pagamentos incorretos
def valida_pagamentos(df_vendas):
    try:
        # tive que utilizar o index_col para que o df não utilizasse o nome da coluna como indice.
        # Estava acusando um erro no incio por ele não estar encontrando o nome da coluna "Nome do Vendedor" quando não utilizei a função
        df_original = pd.read_excel('Vendas_aaws.xlsx', sheet_name=None, index_col=None)
        df_pagamentos = df_original['Pagamentos']
        
        df_mesclado = pd.merge(df_pagamentos, df_vendas, on='Nome do Vendedor', how='right')
        df_mesclado = df_mesclado[df_mesclado['Comissão'] != df_mesclado['Valor a Receber']][['Nome do Vendedor','Comissão','Valor a Receber']]
    
        print(df_mesclado)
        return df_mesclado
    
    except BaseException as error:
        logging.exception(error)
        log_falhas[datetime.now().strftime('%Y-%m-%d %H:%M:%S')] = error
    
# TAREFA 3 - Buscar o nome dos sócios e suas cotas
def contrato_partnership():
    try:
        with open('Partnership.txt','r') as arq:
            contrato = arq.readlines()
    except BaseException as erro:
        logging.exception(erro)
        log_falhas[datetime.now().strftime('%Y-%m-%d %H:%M:%S')] = erro

    lista_socios = []
    for linha in contrato:
        try:
            if "SÃ³cio" and 'CPF' in linha :
                lista_socios.append(linha)
        except BaseException as e:
            log_falhas[datetime.now().strftime('%Y-%m-%d %H:%M:%S')] = e
            print('Falha na iteração.. pulando para a proxima linha!')
            
    cotas_socios = []
    # foi encontrado um padrão no nome de cada socio, onde o nome sempre começa a partir de um . e temrina após a ,
    padrao_nomes_socios = r'\.\s(.*?),'
    # O padrão encontrado nas cotas é que ele sempre é a ultima palavra de cada linha e está entre uma , e um .
    padrao_cotas = r',\s*([^,]+)\.'
     
    for linha in lista_socios:
        try:
            nomes_socios = re.findall(padrao_nomes_socios, linha)
            cotas = re.findall(padrao_cotas,linha)[1:]
            cotas_socios.append((nomes_socios[0], cotas[0]))
        except BaseException as e:
            log_falhas[datetime.now().strftime('%Y-%m-%d %H:%M:%S')] = e

    print(cotas_socios)
    return cotas_socios

def main():
    # Variável criada para armazenar um log de possíveis erros
    global log_falhas
    log_falhas = {}
    try:
        dados_vendas = calcula_comissao()
        comissoes = valida_pagamentos(dados_vendas)
        cotas_socios = contrato_partnership()
    except BaseException as e:
        log_falhas[datetime.now().strftime('%Y-%m-%d %H:%M:%S')] = e
    print(log_falhas)

if __name__ == "__main__":
    main()
    
