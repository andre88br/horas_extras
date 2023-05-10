import warnings
from datetime import time, datetime
from zipfile import BadZipFile

import pandas as pd

from empregados.models import Empregado

warnings.filterwarnings("ignore", category=UserWarning)


def arruma_frequencia(planilhas):
    # Colunas padrão:
    #  'Unidade', 'Setor', 'Nome', 'Matrícula', 'Vínculo', 'Cargo Efetivo',
    #  'Carga Horária', 'Ingresso', 'Rescisão', 'Data', 'Batida-1', 'Batida-2',
    #  'Batida-3', 'Batida-4', 'Batida-5', 'Batida-6', 'Batida-7', 'Batida-8',
    #  'Batida-9', 'Batida-10', 'Dia Semana', 'Horário Dia', 'Detalhe / Observação',
    #  'Unnamed: 23'

    df_list = []
    for planilha in planilhas:
        df = pd.read_excel(planilha, engine='openpyxl')
        df_list.append(df)

    df = pd.concat(df_list, ignore_index=True)
    df.drop(columns={'Unidade', 'Setor', 'Vínculo', 'Cargo Efetivo',
                     'Carga Horária', 'Ingresso', 'Rescisão', 'Data',
                     'Horário Dia', 'Unnamed: 23', 'Batida-8', 'Batida-9',
                     'Batida-10', 'Dia Semana'}, inplace=True)
    df.rename(columns={'Nome': 'nome', 'Matrícula': 'matricula', 'Batida-1': 'data',
                       'Batida-2': 'batida1', 'Batida-3': 'batida2', 'Batida-4': 'batida3',
                       'Batida-5': 'batida4', 'Batida-6': 'batida5', 'Batida-7': 'batida6',
                       'Detalhe / Observação': 'escala'}, inplace=True)
    df['batida1'] = df['batida1'].str.replace('r', '', regex=True).str.replace('m', '', regex=True) \
        .str.replace('c', '', regex=True).str.replace('---', str(time(0, 0, 0)), regex=True)
    df['batida2'] = df['batida2'].str.replace('r', '', regex=True).str.replace('m', '', regex=True) \
        .str.replace('c', '', regex=True).str.replace('---', str(time(0, 0, 0)), regex=True)
    df['batida3'] = df['batida3'].str.replace('r', '', regex=True).str.replace('m', '', regex=True) \
        .str.replace('c', '', regex=True).str.replace('---', str(time(0, 0, 0)), regex=True)
    df['batida4'] = df['batida4'].str.replace('r', '', regex=True).str.replace('m', '', regex=True) \
        .str.replace('c', '', regex=True).str.replace('---', str(time(0, 0, 0)), regex=True)
    df['batida5'] = df['batida5'].str.replace('r', '', regex=True).str.replace('m', '', regex=True) \
        .str.replace('c', '', regex=True).str.replace('---', str(time(0, 0, 0)), regex=True)
    df['batida6'] = df['batida6'].str.replace('r', '', regex=True).str.replace('m', '', regex=True) \
        .str.replace('c', '', regex=True).str.replace('---', str(time(0, 0, 0)), regex=True)
    df['batida1'] = [x + ':00' if len(x) == 5 else x for x in df['batida1']]
    df['batida2'] = [x + ':00' if len(x) == 5 else x for x in df['batida2']]
    df['batida3'] = [x + ':00' if len(x) == 5 else x for x in df['batida3']]
    df['batida4'] = [x + ':00' if len(x) == 5 else x for x in df['batida4']]
    df['batida5'] = [x + ':00' if len(x) == 5 else x for x in df['batida5']]
    df['batida6'] = [x + ':00' if len(x) == 5 else x for x in df['batida6']]
    df['batida1'].fillna(time(0, 0, 0), inplace=True)
    df['batida2'].fillna(time(0, 0, 0), inplace=True)
    df['batida3'].fillna(time(0, 0, 0), inplace=True)
    df['batida4'].fillna(time(0, 0, 0), inplace=True)
    df['batida5'].fillna(time(0, 0, 0), inplace=True)
    df['batida6'].fillna(time(0, 0, 0), inplace=True)
    df['escala'].fillna('', inplace=True)
    df[['entrada_saida', 'escala', 'outro', 'outro2']] = df['escala']\
        .str.split('-', expand=True).fillna('')
    df.drop(columns={'outro', 'outro2'}, inplace=True)
    df[['entrada', 'saida']] = df['entrada_saida'].str.split(' As ', expand=True).fillna('')
    df.drop(columns={'entrada_saida'}, inplace=True)
    df = df[['matricula', 'nome', 'data', 'batida1',
             'batida2', 'batida3', 'batida4', 'batida5',
             'batida6', 'entrada', 'saida', 'escala']]
    df['data'] = pd.to_datetime(df['data'])
    data_min = df['data'][0]
    if data_min.month < 12:
        data_max = datetime(data_min.year, data_min.month + 1, 1)
    else:
        data_max = datetime(data_min.year + 1, data_min.month - 11, 1)
    df = df[df['data'] <= data_max].reset_index(drop=True)
    print(df)
    return df, data_min, data_max


def arruma_saldo_mes(planilha):
    # Colunas padrão:
    # ['Mes/Ano' 'Nome' 'Matricula' 'Cargo' 'Horario' 'Normal' 'Excedentes'
    #  'Normal.1' 'Excedentes.1' 'Adic. Not.' 'Feriado' 'Dias' 'Util'
    #  'Considerada' 'Saldo']

    df = pd.read_excel(planilha, skiprows=3)
    df = df.rename(columns={'Mes/Ano': 'mes_ano', 'Nome': 'matricula', 'Matricula': 'nome',
                            'Util': 'util', 'Considerada': 'considerada', 'Saldo': 'saldo'})
    df[['mes', 'ano']] = df['mes_ano'].str.split('/', expand=True)
    df = df.drop(['Horario', 'Normal', 'Excedentes', 'Normal.1', 'Excedentes.1',
                  'Adic. Not.', 'Feriado', 'Dias', 'mes_ano', 'Cargo'], axis=1)
    df[['nome', 'matricula']] = df[['matricula', 'nome']]
    df = df.dropna(subset=['matricula'], how='any')
    df['matricula'] = pd.to_numeric(df['matricula'], errors='coerce')
    df = df.dropna(subset=['matricula'], how='any')
    df['matricula'] = df['matricula'].astype(int)
    df = df[['matricula', 'nome', 'util', 'considerada', 'mes', 'ano', 'saldo']]
    df['sinal'] = df['saldo'].str[:1]
    df['saldo_decimal'] = df['saldo'].str.replace('-', '', regex=True)
    df['saldo_decimal'] = df['saldo_decimal'].str.lstrip('0')
    saldo_decimal = ['00' + x if x[:1] == ':' else x for x in df['saldo_decimal']]
    saldo_decimal = ['0' + x if len(x) == 4 else x for x in saldo_decimal]
    df['saldo_decimal'] = saldo_decimal
    df['saldo_decimal'] = pd.to_timedelta(df['saldo_decimal'] + ':00')
    saldo_decimal = [x.seconds / 86400 * 24
                     if x < pd.Timedelta(days=1)
                     else x / pd.Timedelta(days=1) * 24
                     for x in df['saldo_decimal']]
    df['saldo_decimal'] = saldo_decimal
    df['saldo_decimal'] = df['saldo_decimal'].astype(float)
    df.loc[df['sinal'] == '-', 'saldo_decimal'] *= -1
    df['saldo'] = df['saldo'].str.lstrip('+')
    df.reset_index(drop=True, inplace=True)
    return df


def arruma_banco(planilha):
    df = pd.read_excel(planilha, skiprows=8)
    df['Unnamed: 6'].fillna(method='bfill', inplace=True)
    df['Unnamed: 4'].fillna(method='ffill', inplace=True)
    df = df.rename(columns={'Unnamed: 4': 'matricula_nome', 'Unnamed: 6': 'saldo_banco'})
    df.dropna(subset='saldo_banco', inplace=True)
    df.drop_duplicates(subset='matricula_nome', inplace=True)
    df[['matricula', 'nome']] = df['matricula_nome'].str.split('-', expand=True)
    df = df[['matricula', 'nome', 'saldo_banco']]
    df['sinal'] = df['saldo_banco'].str[:1]
    df['saldo_decimal'] = df['saldo_banco'].str.replace('-', '', regex=True)
    df['saldo_decimal'] = df['saldo_decimal'].str.lstrip('0')
    saldo_decimal = ['00' + x
                     if x[:1] == ':'
                     else x
                     for x in df['saldo_decimal']]
    saldo_decimal = ['0' + x
                     if len(x) == 4
                     else x
                     for x in saldo_decimal]
    df['saldo_decimal'] = saldo_decimal
    df['saldo_decimal'] = pd.to_timedelta(df['saldo_decimal'] + ':00')
    saldo_decimal = [x.seconds / 86400 * 24
                     if x < pd.Timedelta(days=1)
                     else x / pd.Timedelta(days=1) * 24
                     for x in df['saldo_decimal']]
    df['saldo_decimal'] = saldo_decimal
    df.loc[df['sinal'] == '-', 'saldo_decimal'] *= -1
    df.drop('sinal', axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['matricula'] = df['matricula'].astype(int)
    return df


def arruma_rubricas_calculadas(planilha):
    # Colunas padrão:
    # ['Matricula', 'Nome', 'Tipo', 'Oper.', 'Detalhe', 'Parcela', 'Valor']

    try:
        df = pd.read_excel(planilha, skiprows=2)
    except ValueError:
        return "Erro"

    df = df.rename(columns={'Matricula': 'matricula', 'Nome': 'nome', 'Valor': 'valor'})
    try:
        df[['matricula1', 'matricula2']] = df['matricula'].str.split('-', expand=True)
        df.drop(['Tipo', 'Oper.', 'Detalhe', 'Parcela', 'matricula', 'matricula2'], axis=1, inplace=True)
    except ValueError:
        try:
            df[['matricula1', 'matricula2', 'matricula3']] = df['matricula'].str.split('-', expand=True)
            df.drop(['Tipo', 'Oper.', 'Detalhe', 'Parcela', 'matricula', 'matricula2', 'matricula3'], axis=1, inplace=True)
        except ValueError:
            df[['matricula1', 'matricula2', 'matricula3', 'matricula4']] = df['matricula'].str.split('-', expand=True)
            df.drop(['Tipo', 'Oper.', 'Detalhe', 'Parcela', 'matricula', 'matricula2', 'matricula3', 'matricula4'], axis=1,
                    inplace=True)
        except KeyError:
            return "Erro"
    except KeyError:
        return "Erro"

    df.rename(columns={'matricula1': 'matricula'}, inplace=True)
    df.dropna(subset=['matricula'], how='any', inplace=True)
    df['matricula'] = pd.to_numeric(df['matricula'], errors='coerce')
    df.dropna(subset=['matricula'], how='any', inplace=True)
    df['matricula'] = df['matricula'].astype(int)
    df['valor'] = df['valor'].str.replace('.', '', regex=True).str.replace(',', '.', regex=True).astype(float)
    df = df[['matricula', 'nome', 'valor']]
    df.dropna().reset_index(drop=True)

    return df


def arruma_confirmacao_solicitacao(planilhas):
    df_list = []
    planilhas_com_erro = []
    sem_setor = []
    for planilha in planilhas:
        try:
            df = pd.read_excel(planilha, sheet_name='HORAS EXTRAS',  engine='openpyxl')
            setor = df.at[2, 'Unnamed: 2']
            if str(setor).strip() == '':
                sem_setor.append(planilha.name)
            setor = arruma_setor(setor)
            df = pd.read_excel(planilha, skiprows=4, engine='openpyxl')
            df['setor'] = setor
            df_list.append(df)
        except BadZipFile:
            planilhas_com_erro.append(planilha.name)
    df = pd.concat(df_list, ignore_index=True)
    df2 = df.copy(deep=True)
    df = df.iloc[:, :35]
    df['setor'] = df2['setor']
    df = df.drop('Unnamed: 0', axis=1)
    df = df.rename(columns={'SIAPE': 'matricula', 'NOME COMPLETO': 'nome', 'CARGO': 'cargo'})
    df['matricula'] = pd.to_numeric(df['matricula'], errors='coerce')
    df.dropna(subset='matricula', inplace=True)
    df['matricula'] = df['matricula'].astype(int)
    df = df.fillna(value='')
    df = df.groupby(['matricula', 'nome', 'cargo']) \
        .apply(lambda x: x.iloc[:, :33].agg(lambda y: ''.join(set(y)))) \
        .reset_index(drop=False)

    for i, j in df.iterrows():
        if 'EXTRA' not in str(df.iloc[i:i + 1, 1:2]):
            df.iloc[i:i + 1, 1:2] = None

    df.dropna(subset='nome', inplace=True)
    df['nome'] = df['nome'].str.replace(' - EXTRA', '')
    df = df.reset_index(drop=True)
    return df, planilhas_com_erro, sem_setor


def arruma_carga_horaria(planilha, mes, ano):
    try:
        empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
        empregados = pd.DataFrame(empregados)
        df = empregados[['matricula', 'nome']].copy(deep=True)

        cargas_horaria = pd.read_excel(planilha, skiprows=1)
        cargas_horaria = pd.DataFrame(cargas_horaria)
        cargas_horaria = cargas_horaria.rename(columns={'Matricula': 'matricula', 'Carga Horaria': 'carga_horaria'})
        cargas_horaria = cargas_horaria.dropna(subset='matricula')
        cargas_horaria['matricula'] = cargas_horaria['matricula'].astype(int)

        df = pd.merge(df, cargas_horaria, on=['matricula', 'nome'], how='left')
        df = df.fillna(0)
    except ValueError:
        return "Erro"
    except KeyError:
        return "Erro"

    return df


def arruma_setor(setor):
    if str(setor).strip().upper() == 'USCV':
        setor = 'UNIDADE DO SISTEMA CARDIOVASCULAR'
    if str(setor).strip().upper() == 'UNIDADE DE URGÊNCIA E EMERGÊNCIA':
        setor = 'UNIDADE DE URGENCIA E EMERGENCIA'
    if str(setor).strip().upper() == 'UNIDADE DE CRIANÇA E ADOLESCENTE - PS PED':
        setor = 'UNIDADE DE CRIANCA E ADOLESCENTE'
    if str(setor).strip().upper() == 'UNIDADE DE CLINICA CIRÚRGICA':
        setor = 'UNIDADE DE CLINICA CIRURGICA'
    if str(setor).strip().upper() == 'UNIDADE DA CRIANÇA E DO ADOLESCENTE / UTI PEDIATRICA':
        setor = 'UNIDADE DE CRIANCA E ADOLESCENTE'
    if str(setor).strip().upper() == 'UNIDADE DE FARMACIA CLÍNICA E DISPENSAÇÃO FARMACEUTICA':
        setor = 'UNIDADE DE FARMACIA CLINICA E DISPENSACAO FARMACEUTICA'
    if str(setor).strip().upper() == 'UNIDADE DE SAÚDE DA MULHER':
        setor = 'UNIDADE DE SAUDE DA MULHER'

    return setor
