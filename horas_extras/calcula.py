import locale

import pandas as pd

from empregados.models import Empregado, CargaHoraria, Importacoes
from horas_extras.models import Confirmacao, Frequencia, BancoMes, BancoTotal, Solicitacao
from pos_calculo.models import RelatorioBatidasRejeitadas
from relatorios.dbchanges import salva_relatorio_solicitacao, salva_relatorio_erros, salva_relatorio_entrada_saida, \
    salva_relatorio_confirmacao, salva_relatorio_negativos, salva_relatorio_codigo90, \
    salva_relatorio_rejeitar_batidas, salva_relatorio_pagas, salva_voltar_negativos
from relatorios.models import RelatorioConfirmacao, RelatorioPagas, RelatorioNegativos, RelatorioErros, \
    RelatorioCodigo90, RelatorioRejeitarBatidas, RelatorioEntradaSaida
from relatorios.processa_relatorios import gera_relatorio_solicitacao, gera_relatorio_confirmacao

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

escalas = {'M10': 4, 'M11': 4, 'M12': 4, 'M8': 4, 'T10': 4, 'T11': 4, 'T12': 4, 'T9': 4,
           'M13': 6, 'M14': 6, 'M15': 6, 'M16': 6, 'M17': 6, 'M18': 6,
           'N5': 7, 'T13': 6, 'T14': 6, 'T15': 6, 'T16': 6, 'T17': 6,
           'T18': 6, 'T19': 6, 'MT15': 8.5, 'MT16': 8.5, 'MT17': 8.5, 'MT18': 8.5,
           'MT19': 8.5, 'MT20': 8.5, 'MT21': 8.5, 'MT22': 8.5, 'MT23': 8.5, 'MT24': 8,
           'MT25': 8, 'MT26': 8, 'MT27': 8, 'MT28': 8, 'MT29': 8, 'MT30': 8, 'MT31': 8,
           'MT32': 8, 'MT33': 8, 'MT34': 8, 'MT35': 8, 'MT36': 10, 'MT37': 10, 'MT38': 10,
           'MT39': 10, 'MT40': 10, 'MT41': 10, 'MT42': 10, 'MT43': 10, 'D5': 12, 'D6': 12,
           'D7': 12, 'D8': 12, 'N6': 13, 'N7': 13, 'N8': 13, 'N9': 13, 'N10': 13, 'DN4': 25,
           'DN5': 25, 'DN6': 25, 'M9': 4, 'N11': 4, 'TN1': 8, 'D9': 12, 'D10': 12, 'D11': 12,
           'N12': 7}

escalas_codigos = {'M10': 500, 'M11': 501, 'M12': 502, 'M8': 503, 'T10': 504, 'T11': 505, 'T12': 506, 'T9': 507,
                   'M13': 513, 'M14': 516, 'M15': 518, 'M16': 520, 'M17': 522, 'M18': 524,
                   'N5': 526, 'T13': 527, 'T14': 529, 'T15': 531, 'T16': 533, 'T17': 535,
                   'T18': 537, 'T19': 539, 'MT15': 541, 'MT16': 542, 'MT17': 543, 'MT18': 544,
                   'MT19': 545, 'MT20': 546, 'MT21': 547, 'MT22': 548, 'MT23': 549, 'MT24': 550,
                   'MT25': 551, 'MT26': 552, 'MT27': 554, 'MT28': 556, 'MT29': 558, 'MT30': 560, 'MT31': 562,
                   'MT32': 564, 'MT33': 566, 'MT34': 568, 'MT35': 569, 'MT36': 570, 'MT37': 572, 'MT38': 574,
                   'MT39': 576, 'MT40': 578, 'MT41': 580, 'MT42': 582, 'MT43': 583, 'D5': 584, 'D6': 586,
                   'D7': 588, 'D8': 590, 'N6': 592, 'N7': 594, 'N8': 596, 'N9': 598, 'N10': 600, 'DN4': 602,
                   'DN5': 603, 'DN6': 604, 'M9': 605, 'N11': 607, 'TN1': 618, 'D9': 619, 'D10': 621, 'D11': 623}


def calcula_solicitacao(ano, mes, user):
    deleta_relatorios('solicitacao', mes, ano, final='')

    empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    empregados.drop(columns={'data_atualizacao', 'importacao_id', 'id'}, inplace=True)

    solicitacao = Solicitacao.objects.filter(importacao_id__mes=mes, importacao_id__ano=ano).values()
    solicitacao = pd.DataFrame(solicitacao)
    solicitacao['matricula'] = 0
    pega_matricula(solicitacao, mes, ano)
    solicitacao.drop(columns={'id', 'data_upload', 'importacao_id', 'empregado_id', 'nome'}, inplace=True)
    solicitacao.dropna(subset='matricula')
    solicitacao = solicitacao.fillna('')
    df = pd.merge(solicitacao, empregados, on='matricula', how='left')
    df = df.dropna(subset='matricula')

    renomeacao = {}
    for i in range(1, 32):
        renomeacao['dia' + str(i)] = str(i)
    df = df.rename(columns=renomeacao)

    saldo_banco = BancoTotal.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    saldo_banco = pd.DataFrame(saldo_banco)
    pega_matricula(saldo_banco, mes, ano)
    saldo_banco.drop(columns={'id', 'data_upload', 'importacao_id', 'empregado_id', 'nome',
                              'data_upload', 'importado_por', 'importado_por_id'}, inplace=True)
    saldo_banco = saldo_banco.rename(columns={'saldo': 'saldo_banco',
                                              'saldo_decimal': 'saldo_banco_decimal'})
    df = pd.merge(df, saldo_banco, on='matricula', how='left')

    df['horas_totais'] = df['horas_totais'] = [0] * len(df)
    df['valor_total'] = df['valor_total'] = [0] * len(df)
    df['horas_diurnas'] = df['horas_diurnas'] = [0] * len(df)
    df['valor_diurnas'] = df['valor_diurnas'] = [0] * len(df)
    df['horas_noturnas'] = df['horas_noturnas'] = [0] * len(df)
    df['valor_noturnas'] = df['valor_noturnas'] = [0] * len(df)

    cargas = CargaHoraria.objects.filter(importacao__mes=mes, importacao__ano=ano, carga_horaria__gt=0).values()
    cargas = pd.DataFrame(cargas)
    pega_matricula(cargas, mes, ano)
    cargas = cargas[['matricula', 'carga_horaria']]
    cargas['carga_horaria'] = cargas['carga_horaria'].astype(int)
    df = pd.merge(df, cargas, on='matricula', how='left')

    N = 0
    D = 0
    DN = 0
    ERRO = 0
    erros = []
    for i, j in df.iterrows():
        matricula = j['matricula']
        nome = j['nome']
        for b, a in j[1:32].items():
            linha = {}
            a_maiusculo = str(a).upper().strip()
            if a_maiusculo in escalas.keys():
                df.at[i, 'horas_totais'] += escalas[a_maiusculo]
                if ('D' in a_maiusculo or 'M' in a_maiusculo or 'T' in a_maiusculo) and 'N' not in a_maiusculo:
                    df.at[i, 'horas_diurnas'] += escalas[a_maiusculo]
                    D += 1
                elif 'N' in a_maiusculo and 'D' not in a_maiusculo:
                    df.at[i, 'horas_diurnas'] += (escalas[a_maiusculo] - 8)
                    df.at[i, 'horas_noturnas'] += 8
                    N += 1
                elif 'DN' in a_maiusculo:
                    df.at[i, 'horas_diurnas'] += (escalas[a_maiusculo] - 8)
                    df.at[i, 'horas_noturnas'] += 8
                    DN += 1
            elif a != '' and a != ' ':
                linha.update({'matricula': matricula, 'nome': nome, 'data': f'{b}/{mes}/{ano}', 'escala': a_maiusculo})
                erros.append(linha)
                ERRO += 1

    for i, j in df.iterrows():
        df.at[i, 'valor_diurnas'] = (j['salario'] + j['insalubridade']) / j['carga_horaria'] * j['horas_diurnas'] * 1.5
        df.at[i, 'valor_noturnas'] = (j['salario'] + j['insalubridade']) / j['carga_horaria'] * j[
            'horas_noturnas'] * 1.5 * 1.2
        df.at[i, 'valor_total'] = df.at[i, 'valor_diurnas'] + df.at[i, 'valor_noturnas']

    df['saldo_banco'] = df['saldo_banco'].astype(str)

    for i, j in df.iterrows():
        if j['saldo_banco_decimal'] >= 0:
            salva_relatorio_solicitacao(j, user, mes, ano)

    erros = pd.DataFrame(erros)
    for i, j in erros.iterrows():
        salva_relatorio_erros(j, user, mes, ano, 'solicitacao')

    negativos = df[(df['saldo_banco_decimal'] < 0)].copy(deep=True)
    negativos = negativos[['matricula', 'nome', 'cargo', 'saldo_banco', 'saldo_banco_decimal', 'setor']]

    for i, j in negativos.iterrows():
        salva_relatorio_negativos(j, user, mes, ano, 'solicitacao')

    response, excel_path_solicitacao, df = gera_relatorio_solicitacao(mes, ano, '', '', '')

    conclusao = f'Processamento efetuado com sucesso:\n' \
                f'D: {D}, N: {N}, DN: {DN}, Erros: {ERRO}'

    return df, conclusao


def calcula_he(ano, mes, user, final):
    deleta_relatorios('confirmacao', mes, ano, final)
    #  Busca empregados
    empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    empregados.drop(columns={'data_atualizacao', 'importacao_id', 'id'}, inplace=True)

    # Busca planilha de confirmação e junta com a tabela empregados
    confirmacao = Confirmacao.objects.filter(importacao__ano=ano, importacao__mes=mes).values()
    confirmacao = pd.DataFrame(confirmacao)
    confirmacao['matricula'] = 0
    pega_matricula(confirmacao, mes, ano)
    confirmacao.drop(columns={'id', 'nome', 'data_upload', 'importacao_id', 'empregado_id'}, inplace=True)
    confirmacao.dropna(subset='matricula')

    df = pd.merge(confirmacao, empregados, on='matricula', how='left')
    df = df.dropna(subset='matricula')

    renomeacao = {}
    for i in range(1, 32):
        renomeacao['dia' + str(i)] = str(i)
    df = df.rename(columns=renomeacao)

    # Busca planilha de saldo do banco do mês e junta com a tabela anterior
    saldo_mes = BancoMes.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    saldo_mes = pd.DataFrame(saldo_mes)
    pega_matricula(saldo_mes, mes, ano)
    saldo_mes = saldo_mes.rename(columns={'saldo': 'saldo_mes',
                                          'saldo_decimal': 'saldo_mes_decimal'})
    saldo_mes.drop(columns={'id', 'data_upload', 'importacao_id', 'empregado_id', 'nome',
                            'importado_por', 'importado_por_id'}, inplace=True)
    df = pd.merge(df, saldo_mes, on='matricula', how='left')

    # Busca planilha de saldo do banco total e junta com a tabela anterior
    saldo_banco = BancoTotal.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    saldo_banco = pd.DataFrame(saldo_banco)
    pega_matricula(saldo_banco, mes, ano)
    saldo_banco = saldo_banco.rename(columns={'saldo': 'saldo_banco',
                                              'saldo_decimal': 'saldo_banco_decimal'})
    saldo_banco.drop(columns={'id', 'data_upload', 'importacao_id', 'empregado_id', 'nome',
                              'importado_por', 'importado_por_id'}, inplace=True)

    df = pd.merge(df, saldo_banco, on='matricula', how='left')

    # Busca planilha de frequência e junta com a tabela anterior
    frequencia = Frequencia.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    frequencia = pd.DataFrame(frequencia)
    pega_matricula(frequencia, mes, ano)
    frequencia.drop(columns={'id', 'data_upload', 'importacao_id', 'empregado_id', 'nome',
                             'importado_por', 'importado_por_id', 'escala'}, inplace=True)

    df = pd.merge(df, frequencia, on='matricula', how='left')
    df['data'] = pd.to_datetime(df['data'])

    df['horas_trabalhadas'] = df['horas_trabalhadas'] = [0] * len(df)
    df['valor_total'] = df['valor_total'] = [0] * len(df)
    df['horas_diurnas'] = df['horas_diurnas'] = [0] * len(df)
    df['valor_diurnas'] = df['valor_diurnas'] = [0] * len(df)
    df['horas_noturnas'] = df['horas_noturnas'] = [0] * len(df)
    df['valor_noturnas'] = df['valor_noturnas'] = [0] * len(df)

    cargas = CargaHoraria.objects.filter(importacao__mes=mes, importacao__ano=ano, carga_horaria__gt=0).values()
    cargas = pd.DataFrame(cargas)
    pega_matricula(cargas, mes, ano)
    cargas.drop(columns={'id', 'importacao_id', 'empregado_id', 'nome',
                         'importado_por', 'importado_por_id'}, inplace=True)
    cargas['carga_horaria'] = cargas['carga_horaria'].astype(int)
    df = pd.merge(df, cargas, on='matricula', how='left')

    df = df.sort_values(by=['matricula', 'data'])
    df = df.reset_index(drop=True)
    df.index += 1

    N = 0
    D = 0
    DN = 0
    ERRO = 0
    mes = df['data'][1].month
    erros = []
    entrada_saida = []
    ind = 1

    for i, j in df.iterrows():
        linha = {}
        matricula = j['matricula']
        nome = j['nome']
        data = j['data'].strftime('%d/%m/%Y')
        cargo = j['cargo']
        c2 = 1
        for a in j[1:32]:
            a_maiusculo = str(a).upper()
            if str(j['cargo']).upper() != 'ASSISTENTE ADMINISTRATIVO':
                if ('D' in a_maiusculo or 'M' in a_maiusculo or 'T' in a_maiusculo) and 'N' not in a_maiusculo \
                        and j['data'].day == c2 and j['data'].month == mes:
                    if (j['batida1'].hour + j['batida1'].minute / 60) != 0 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) != 0 and \
                            (j['batida3'].hour + j['batida3'].minute / 60) == 0:
                        horas_trabalhadas = (j['batida2'].hour + j['batida2'].minute / 60) - \
                                            (j['batida1'].hour + j['batida1'].minute / 60)
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida1'], j['batida2'], df.at[i, 'horas_trabalhadas'],
                                                          df.at[i, 'horas_diurnas'], df.at[i, 'horas_noturnas'],
                                                          df.at[i, 'setor']))
                        D += 1
                    elif (j['batida1'].hour + j['batida1'].minute / 60) < 10 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) < 10 and \
                            (j['batida3'].hour + j['batida3'].minute / 60) > 16 and j['batida4'] == 0:
                        horas_trabalhadas = (j['batida3'].hour + j['batida3'].minute / 60) - \
                                            (j['batida2'].hour + j['batida2'].minute / 60)
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida2'], j['batida3'], df.at[i, 'horas_trabalhadas'],
                                                          df.at[i, 'horas_diurnas'], df.at[i, 'horas_noturnas'],
                                                          df.at[i, 'setor']))
                        D += 1
                    elif (j['batida1'].hour + j['batida1'].minute / 60) < 10 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) < 10 and \
                            (j['batida3'].hour + j['batida3'].minute / 60) < 16 and \
                            (j['batida4'].hour + j['batida4'].minute / 60) > 16:
                        horas_trabalhadas = (j['batida4'].hour + j['batida4'].minute / 60) - \
                                            (j['batida3'].hour + j['batida3'].minute / 60)
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida3'], j['batida4'], df.at[i, 'horas_trabalhadas'],
                                                          df.at[i, 'horas_diurnas'], df.at[i, 'horas_noturnas'],
                                                          df.at[i, 'setor']))
                        D += 1
                    else:
                        df.at[i, 'horas_trabalhadas'] = 0
                        df.at[i, 'horas_diurnas'] = 0
                        df.at[i, 'horas_noturnas'] = 0
                        erros.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, 0, 0,
                                                  df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                  df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        ERRO += 1
                elif 'N' in a_maiusculo and 'D' not in a_maiusculo and j['data'].day == c2 and j['data'].month == mes \
                        and (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) <= 11 and \
                        (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) != 0:
                    if (j['batida1'].hour + j['batida1'].minute / 60) >= 17 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) == 0:
                        horas_trabalhadas = ((25 - (j['batida1'].hour + j['batida1'].minute / 60)) +
                                             (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60))
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas - 8
                        df.at[i, 'horas_noturnas'] = 8
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida1'], df.loc[ind + 1]['batida1'],
                                                          df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                          df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        N += 1
                    elif ((j['batida1'].hour + j['batida1'].minute / 60) > 0) and \
                            ((j['batida2'].hour + j['batida2'].minute / 60) >= 17) and \
                            (j['batida3'].hour + j['batida3'].minute / 60) == 0 and \
                            (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) != 0:
                        horas_trabalhadas = ((25 - (j['batida2'].hour + j['batida2'].minute / 60)) +
                                             (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60))
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas - 8
                        df.at[i, 'horas_noturnas'] = 8
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida2'], df.loc[ind + 1]['batida1'],
                                                          df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                          df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        N += 1
                    elif (j['batida1'].hour + j['batida1'].minute / 60) > 0 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) > 0 and \
                            (j['batida3'].hour + j['batida3'].minute / 60) >= 17 and \
                            (j['batida4'].hour + j['batida4'].minute / 60) == 0 and \
                            (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) != 0:
                        horas_trabalhadas = ((25 - (j['batida3'].hour + j['batida3'].minute / 60)) +
                                             (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60))
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas - 8
                        df.at[i, 'horas_noturnas'] = 8
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida3'], df.loc[ind + 1]['batida1'],
                                                          df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                          df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        N += 1
                    elif (j['batida1'].hour + j['batida1'].minute / 60) > 0 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) > 0 and \
                            (j['batida3'].hour + j['batida3'].minute / 60) > 0 and \
                            (j['batida4'].hour + j['batida4'].minute / 60) >= 17 and \
                            (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) != 0:
                        horas_trabalhadas = ((25 - (j['batida4'].hour + j['batida4'].minute / 60)) +
                                             (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60))
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas - 8
                        df.at[i, 'horas_noturnas'] = 8
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida4'], df.loc[ind + 1]['batida1'],
                                                          df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                          df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        N += 1
                    else:
                        df.at[i, 'horas_trabalhadas'] = 0
                        df.at[i, 'horas_diurnas'] = 0
                        df.at[i, 'horas_noturnas'] = 0
                        erros.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, 0, 0,
                                                  df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                  df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        ERRO += 1
                elif 'DN' in a_maiusculo and j['data'].day == c2 and j['data'].month == mes:
                    if (11 > (j['batida1'].hour + j['batida1'].minute / 60) > 0) and \
                            (11 > (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) > 0) and \
                            (j['batida2'].hour + j['batida2'].minute / 60) == 0:
                        horas_trabalhadas = (25 - (j['batida1'].hour + j['batida1'].minute / 60)) +\
                                            (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60)
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas - 8
                        df.at[i, 'horas_noturnas'] = 8
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida1'], df.loc[ind + 1]['batida1'],
                                                          df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                          df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        DN += 1
                    else:
                        df.at[i, 'horas_trabalhadas'] = 0
                        df.at[i, 'horas_diurnas'] = 0
                        df.at[i, 'horas_noturnas'] = 0
                        erros.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, 0, 0,
                                                  df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                  df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        ERRO += 1
                elif a != '' and j['data'].day == c2 and j['data'].month == mes:
                    df.at[i, 'horas_trabalhadas'] = 0
                    df.at[i, 'horas_diurnas'] = 0
                    df.at[i, 'horas_noturnas'] = 0
                    erros.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, 0, 0,
                                              df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                              df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                    ERRO += 1
            else:
                if a != '' and j['data'].day == c2 and j['data'].month == mes and \
                        (j['batida1'].hour + j['batida1'].minute / 60) != 0 and \
                        (j['batida4'].hour + j['batida4'].minute / 60) != 0:
                    horas_trabalhadas = ((j['batida4'].hour + j['batida4'].minute / 60) - (
                            j['batida1'].hour + j['batida1'].minute / 60)) \
                                        - ((j['batida3'].hour + j['batida3'].minute / 60) - (
                                            j['batida2'].hour + j['batida2'].minute / 60))
                    df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                    df.at[i, 'horas_diurnas'] = horas_trabalhadas
                    entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                      j['batida1'], j['batida4'], df.at[i, 'horas_trabalhadas'],
                                                      df.at[i, 'horas_diurnas'], df.at[i, 'horas_noturnas'],
                                                      df.at[i, 'setor']))
                    D += 1
                elif a != '' and j['data'].day == c2 and j['data'].month == mes:
                    df.at[i, 'horas_trabalhadas'] = 0
                    df.at[i, 'horas_diurnas'] = 0
                    df.at[i, 'horas_noturnas'] = 0
                    erros.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, 0, 0,
                                              df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                              df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                    ERRO += 1
            c2 += 1
        ind += 1

    for i, j in df.iterrows():
        df.at[i, 'valor_diurnas'] = (j['salario'] + j['insalubridade']) / j['carga_horaria'] * j['horas_diurnas'] * 1.5
        df.at[i, 'valor_noturnas'] = (j['salario'] + j['insalubridade']) / j['carga_horaria'] * j[
            'horas_noturnas'] * 1.5 * 1.2
        df.at[i, 'valor_total'] = df.at[i, 'valor_diurnas'] + df.at[i, 'valor_noturnas']

    entrada_saida = pd.DataFrame(entrada_saida)
    for i, j in entrada_saida.iterrows():
        salva_relatorio_entrada_saida(j, user, mes, ano)
        if not final == 'true':
            salva_relatorio_codigo90(j, user, mes, ano)

    if not final == 'true':
        rejeitar_batidas_d(df, entrada_saida, user, mes, ano)
        rejeitar_batidas_n(df, entrada_saida, user, mes, ano)
        rejeitar_batidas_dn(df, entrada_saida, user, mes, ano)

    df = df.drop(columns={'data', 'batida1', 'batida2', 'batida3', 'batida4', 'batida5', 'batida6'})
    df = df.groupby(['matricula', 'nome', 'salario', 'insalubridade', 'cargo',
                     '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
                     '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23',
                     '24', '25', '26', '27', '28', '29', '30', '31', 'saldo_mes',
                     'saldo_mes_decimal', 'saldo_banco', 'saldo_banco_decimal', 'carga_horaria', 'setor']
                    )[['horas_trabalhadas', 'valor_total', 'horas_diurnas', 'valor_diurnas',
                       'horas_noturnas', 'valor_noturnas']].sum(numeric_only=False)
    df = df.reset_index(drop=False)

    for i, j in df.iterrows():
        salva_relatorio_confirmacao(j, user, mes, ano)

    erros = pd.DataFrame(erros)
    for i, j in erros.iterrows():
        salva_relatorio_erros(j, user, mes, ano, 'confirmacao')

    negativos = df[(df['saldo_banco_decimal'] < 0) | (df['saldo_mes_decimal'] < 0)].copy(deep=True)
    negativos = negativos[['matricula', 'nome', 'cargo', 'saldo_mes', 'saldo_mes_decimal',
                           'saldo_banco', 'saldo_banco_decimal', 'setor']]

    for i, j in negativos.iterrows():
        salva_relatorio_negativos(j, user, mes, ano, 'confirmacao')

    response, excel_path_confirmacao, df = gera_relatorio_confirmacao(mes, ano, '', '', '')
    if final == 'true':
        negativos = RelatorioNegativos.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
        negativos = pd.DataFrame(negativos)
        pega_matricula(negativos, mes, ano)
        volta_negativos = RelatorioConfirmacao.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
        volta_negativos = pd.DataFrame(volta_negativos)
        pega_matricula(volta_negativos, mes, ano)
        volta_negativos = volta_negativos[volta_negativos['matricula'].isin(negativos['matricula'])]

        for i, j in volta_negativos.iterrows():
            c = 1
            for dia in j[17:48]:
                if dia != '':
                    volta_negativos.at[i, f'dia{c}'] = escalas_codigos[str(dia)]
                c += 1
        for i, j in volta_negativos.iterrows():
            salva_voltar_negativos(j, user, mes, ano)

        pagas = RelatorioConfirmacao.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                    saldo_mes_decimal__gte=0, saldo_banco_decimal__gte=0,
                                                    valor_total__gt=0).values()
        pagas = pd.DataFrame(pagas)
        pega_matricula(pagas, mes, ano)
        coluna_matricula = pagas['matricula']
        pagas = pagas.drop(columns={'matricula'})
        pagas.insert(0, 'matricula', coluna_matricula)
        for i, j in pagas.iterrows():
            salva_relatorio_pagas(j, user, mes, ano)

    conclusao = f'Processamento efetuado com sucesso:\n' \
                f'D: {D}, N: {N}, DN: {DN}, Erros: {ERRO}'

    return df, conclusao


def pega_matricula(df, mes, ano):
    empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    for i, j in df.iterrows():
        matricula = int(empregados[empregados['id'] == j['empregado_id']]['matricula'].values)
        df.at[i, 'matricula'] = matricula


def insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, entrada, saida,
                 horas_trabalhadas, horas_diurnas, horas_noturnas, setor):
    linha.update({'matricula': matricula, 'nome': nome, 'cargo': cargo, 'data': data,
                  'escala': a_maiusculo, 'entrada': entrada, 'saida': saida,
                  'horas_trabalhadas': horas_trabalhadas, 'horas_diurnas': horas_diurnas,
                  'horas_noturnas': horas_noturnas, 'setor': setor})
    return linha


def rejeitar_batidas_d(df, entrada_saida, user, mes, ano):
    rejeitar_batidas_d = df[(df['saldo_banco_decimal'] >= 0) & (df['saldo_mes_decimal'] >= 0) &
                            (df['horas_diurnas'] >= 0)].copy(deep=True)
    if not rejeitar_batidas_d.empty:
        rejeitar_batidas_d = rejeitar_batidas_d.reset_index(drop=True)
        rejeitar_batidas_d.index += 1

        for j in range(1, rejeitar_batidas_d.shape[0]):
            if rejeitar_batidas_d.at[j, 'data'].month == rejeitar_batidas_d['data'][1].month:
                for i in range(1, 32):
                    if not entrada_saida.loc[(entrada_saida['matricula'] == rejeitar_batidas_d.at[j, 'matricula']) &
                                             (entrada_saida['data'] == rejeitar_batidas_d.at[j, 'data'].strftime(
                                                 '%d/%m/%Y'))].empty:
                        rejeitar_batidas_d.at[j, str(i)] = rejeitar_batidas_d.at[j, 'data'] \
                            if rejeitar_batidas_d.at[j, str(i)] != '' \
                            and rejeitar_batidas_d.at[j, 'data'].day == i \
                            and 'DN' not in str(rejeitar_batidas_d.at[j, str(i)]).upper() \
                            and 'N' not in str(rejeitar_batidas_d.at[j, str(i)]).upper() \
                            else ''

        for i in range(1, 32):
            rejeitar_batidas_d[str(i)] = rejeitar_batidas_d[str(i)]. \
                apply(lambda x: x.strftime('%d/%m/%Y') if x != '' and x not in escalas.keys() else '')
        rejeitar_batidas_d = rejeitar_batidas_d.drop(columns={'data', 'batida1', 'batida2', 'batida3', 'batida4',
                                                              'batida5', 'batida6', 'salario', 'insalubridade',
                                                              'cargo', 'saldo_mes', 'saldo_mes_decimal', 'saldo_banco',
                                                              'saldo_banco_decimal', 'carga_horaria',
                                                              'horas_trabalhadas',
                                                              'valor_total', 'horas_diurnas', 'valor_diurnas',
                                                              'horas_noturnas',
                                                              'valor_noturnas'})
        rejeitar_batidas_d = rejeitar_batidas_d.groupby(['matricula', 'nome'])[
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
             '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23',
             '24', '25', '26', '27', '28', '29', '30', '31']].sum(numeric_only=False)
        rejeitar_batidas_d = rejeitar_batidas_d.reset_index(drop=False)

        for i, j in rejeitar_batidas_d.iterrows():
            salva_relatorio_rejeitar_batidas(j, user, mes, ano, 'D')


def rejeitar_batidas_n(df, entrada_saida, user, mes, ano):
    rejeitar_batidas_d = df[(df['saldo_banco_decimal'] >= 0) & (df['saldo_mes_decimal'] >= 0) &
                            (df['horas_diurnas'] >= 0)].copy(deep=True)
    if not rejeitar_batidas_d.empty:
        rejeitar_batidas_d = rejeitar_batidas_d.reset_index(drop=True)
        rejeitar_batidas_d.index += 1

        for j in range(1, rejeitar_batidas_d.shape[0]):
            if rejeitar_batidas_d.at[j, 'data'].month == rejeitar_batidas_d['data'][1].month:
                for i in range(1, 32):
                    if not entrada_saida.loc[(entrada_saida['matricula'] == rejeitar_batidas_d.at[j, 'matricula']) &
                                             (entrada_saida['data'] == rejeitar_batidas_d.at[j, 'data'].strftime(
                                                 '%d/%m/%Y'))].empty:
                        rejeitar_batidas_d.at[j, str(i)] = rejeitar_batidas_d.at[j, 'data'] \
                            if rejeitar_batidas_d.at[j, str(i)] != '' \
                            and rejeitar_batidas_d.at[j, 'data'].day == i \
                            and 'N' in str(rejeitar_batidas_d.at[j, str(i)]).upper() \
                            and 'D' not in str(rejeitar_batidas_d.at[j, str(i)]).upper() \
                            else ''

        for i in range(1, 32):
            rejeitar_batidas_d[str(i)] = rejeitar_batidas_d[str(i)]. \
                apply(lambda x: x.strftime('%d/%m/%Y') if x != '' and x not in escalas.keys() else '')

        rejeitar_batidas_d = rejeitar_batidas_d.drop(columns={'data', 'batida1', 'batida2', 'batida3', 'batida4',
                                                              'batida5', 'batida6', 'salario', 'insalubridade',
                                                              'cargo', 'saldo_mes', 'saldo_mes_decimal', 'saldo_banco',
                                                              'saldo_banco_decimal', 'carga_horaria',
                                                              'horas_trabalhadas',
                                                              'valor_total', 'horas_diurnas', 'valor_diurnas',
                                                              'horas_noturnas',
                                                              'valor_noturnas'})
        rejeitar_batidas_d = rejeitar_batidas_d.groupby(['matricula', 'nome'])[
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
             '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23',
             '24', '25', '26', '27', '28', '29', '30', '31']].sum(numeric_only=False)
        rejeitar_batidas_d = rejeitar_batidas_d.reset_index(drop=False)

        for i, j in rejeitar_batidas_d.iterrows():
            salva_relatorio_rejeitar_batidas(j, user, mes, ano, 'N')


def rejeitar_batidas_dn(df, entrada_saida, user, mes, ano):
    rejeitar_batidas_d = df[(df['saldo_banco_decimal'] >= 0) & (df['saldo_mes_decimal'] >= 0) &
                            (df['horas_diurnas'] >= 0)].copy(deep=True)
    if not rejeitar_batidas_d.empty:
        rejeitar_batidas_d = rejeitar_batidas_d.reset_index(drop=True)
        rejeitar_batidas_d.index += 1

        for j in range(1, rejeitar_batidas_d.shape[0]):
            if rejeitar_batidas_d.at[j, 'data'].month == rejeitar_batidas_d['data'][1].month:
                for i in range(1, 32):
                    if not entrada_saida.loc[(entrada_saida['matricula'] == rejeitar_batidas_d.at[j, 'matricula']) &
                                             (entrada_saida['data'] == rejeitar_batidas_d.at[j, 'data'].strftime(
                                                 '%d/%m/%Y'))].empty:
                        rejeitar_batidas_d.at[j, str(i)] = rejeitar_batidas_d.at[j, 'data'] \
                            if rejeitar_batidas_d.at[j, str(i)] != '' \
                            and rejeitar_batidas_d.at[j, 'data'].day == i \
                            and 'DN' in str(rejeitar_batidas_d.at[j, str(i)]).upper() \
                            else ''

        for i in range(1, 32):
            rejeitar_batidas_d[str(i)] = rejeitar_batidas_d[str(i)]. \
                apply(lambda x: x.strftime('%d/%m/%Y') if x != '' and x not in escalas.keys() else '')

        rejeitar_batidas_d = rejeitar_batidas_d.drop(columns={'data', 'batida1', 'batida2', 'batida3', 'batida4',
                                                              'batida5', 'batida6', 'salario', 'insalubridade',
                                                              'cargo', 'saldo_mes', 'saldo_mes_decimal', 'saldo_banco',
                                                              'saldo_banco_decimal', 'carga_horaria',
                                                              'horas_trabalhadas',
                                                              'valor_total', 'horas_diurnas', 'valor_diurnas',
                                                              'horas_noturnas',
                                                              'valor_noturnas'})
        rejeitar_batidas_d = rejeitar_batidas_d.groupby(['matricula', 'nome'])[
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
             '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23',
             '24', '25', '26', '27', '28', '29', '30', '31']].sum(numeric_only=False)
        rejeitar_batidas_d = rejeitar_batidas_d.reset_index(drop=False)

        for i, j in rejeitar_batidas_d.iterrows():
            salva_relatorio_rejeitar_batidas(j, user, mes, ano, 'DN')


def deleta_relatorios(tipo, mes, ano, final):
    if tipo == 'solicitacao':
        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='rel_solicitacao').all()
        if busca:
            busca.delete()

        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='erros_solicitacao').all()
        if busca:
            busca.delete()

        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='rel_negativos_sol').all()
        if busca:
            busca.delete()

    if tipo == 'confirmacao':
        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='rel_confirmacao').all()
        if busca:
            busca.delete()

        if final != 'true':
            busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='rel_codigo90').all()
            if busca:
                busca.delete()

            busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='rel_rejeitar_batidas').all()
            if busca:
                busca.delete()

        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='rel_pagas').all()
        if busca:
            busca.delete()

        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='rel_entrada_saida').all()
        if busca:
            busca.delete()

        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='erros_confirmacao').all()
        if busca:
            busca.delete()

        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='rel_negativos_conf').all()
        if busca:
            busca.delete()


def recalcula_solicitacao(matricula, ano, mes, user):
    empregados = Empregado.objects.filter(matricula=matricula, mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    empregados.drop(columns={'data_atualizacao', 'importacao_id', 'id'}, inplace=True)

    solicitacao = Solicitacao.objects.filter(empregado__matricula=matricula,
                                             importacao_id__mes=mes, importacao_id__ano=ano).values()
    solicitacao = pd.DataFrame(solicitacao)
    solicitacao['matricula'] = 0
    pega_matricula(solicitacao, mes, ano)
    solicitacao.drop(columns={'id', 'data_upload', 'importacao_id', 'empregado_id', 'nome'}, inplace=True)
    solicitacao.dropna(subset='matricula')
    df = pd.merge(solicitacao, empregados, on='matricula', how='left')
    df = df.dropna(subset='matricula')

    renomeacao = {}
    for i in range(1, 32):
        renomeacao['dia' + str(i)] = str(i)
    df = df.rename(columns=renomeacao)

    saldo_banco = BancoTotal.objects.filter(empregado__matricula=matricula,
                                            importacao__mes=mes, importacao__ano=ano).values()
    saldo_banco = pd.DataFrame(saldo_banco)
    pega_matricula(saldo_banco, mes, ano)
    saldo_banco.drop(columns={'id', 'data_upload', 'importacao_id', 'empregado_id', 'nome',
                              'data_upload', 'importado_por', 'importado_por_id'}, inplace=True)
    saldo_banco = saldo_banco.rename(columns={'saldo': 'saldo_banco',
                                              'saldo_decimal': 'saldo_banco_decimal'})
    df = pd.merge(df, saldo_banco, on='matricula', how='left')

    df['horas_totais'] = df['horas_totais'] = [0] * len(df)
    df['valor_total'] = df['valor_total'] = [0] * len(df)
    df['horas_diurnas'] = df['horas_diurnas'] = [0] * len(df)
    df['valor_diurnas'] = df['valor_diurnas'] = [0] * len(df)
    df['horas_noturnas'] = df['horas_noturnas'] = [0] * len(df)
    df['valor_noturnas'] = df['valor_noturnas'] = [0] * len(df)

    cargas = CargaHoraria.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                         importacao__ano=ano, carga_horaria__gt=0).values()
    cargas = pd.DataFrame(cargas)
    pega_matricula(cargas, mes, ano)
    cargas = cargas[['matricula', 'carga_horaria']]
    cargas['carga_horaria'] = cargas['carga_horaria'].astype(int)
    df = pd.merge(df, cargas, on='matricula', how='left')
    N = 0
    D = 0
    DN = 0
    ERRO = 0
    erros = []
    for i, j in df.iterrows():
        matricula = j['matricula']
        nome = j['nome']
        for b, a in j[1:32].items():
            linha = {}
            a_maiusculo = str(a).upper()
            if a_maiusculo in escalas.keys():
                df.at[i, 'horas_totais'] += escalas[a_maiusculo]
                if ('D' in a_maiusculo or 'M' in a_maiusculo or 'T' in a_maiusculo) and 'N' not in a_maiusculo:
                    df.at[i, 'horas_diurnas'] += escalas[a_maiusculo]
                    D += 1
                elif 'N' in a_maiusculo and 'D' not in a_maiusculo:
                    df.at[i, 'horas_diurnas'] += (escalas[a_maiusculo] - 8)
                    df.at[i, 'horas_noturnas'] += 8
                    N += 1
                elif 'DN' in a_maiusculo:
                    df.at[i, 'horas_diurnas'] += (escalas[a_maiusculo] - 8)
                    df.at[i, 'horas_noturnas'] += 8
                    DN += 1
            elif a_maiusculo != '':
                linha.update({'matricula': matricula, 'nome': nome, 'data': f'{b}/{mes}/{ano}', 'escala': a_maiusculo})
                erros.append(linha)
                ERRO += 1

    for i, j in df.iterrows():
        df.at[i, 'valor_diurnas'] = (j['salario'] + j['insalubridade']) / j['carga_horaria'] * j['horas_diurnas'] * 1.5
        df.at[i, 'valor_noturnas'] = (j['salario'] + j['insalubridade']) / j['carga_horaria'] * j[
            'horas_noturnas'] * 1.5 * 1.2
        df.at[i, 'valor_total'] = df.at[i, 'valor_diurnas'] + df.at[i, 'valor_noturnas']

    df['saldo_banco'] = df['saldo_banco'].astype(str)

    for i, j in df.iterrows():
        salva_relatorio_solicitacao(j, user, mes, ano)

    erros = pd.DataFrame(erros)
    for i, j in erros.iterrows():
        salva_relatorio_erros(j, user, mes, ano, 'solicitacao')

    negativos = df[(df['saldo_banco_decimal'] < 0)].copy(deep=True)
    negativos = negativos[['matricula', 'nome', 'cargo', 'saldo_banco', 'saldo_banco_decimal', 'setor']]

    for i, j in negativos.iterrows():
        salva_relatorio_negativos(j, user, mes, ano, 'solicitacao')

    response, excel_path_solicitacao, df = gera_relatorio_solicitacao(mes, ano, '', '', matricula)

    conclusao = f'Processamento efetuado com sucesso:\n' \
                f'D: {D}, N: {N}, DN: {DN}, Erros: {ERRO}'

    return df, conclusao


def deleta_relatorios2(matricula, mes, ano):
    busca = RelatorioNegativos.objects.filter(empregado__matricula=matricula, importacao__ano=ano,
                                              importacao__mes=mes, tipo='confirmacao').all()
    if busca:
        busca.delete()
    busca = RelatorioErros.objects.filter(empregado__matricula=matricula, importacao__ano=ano, importacao__mes=mes,
                                          tipo='confirmacao').all()
    if busca:
        busca.delete()
    busca = RelatorioConfirmacao.objects.filter(empregado__matricula=matricula, importacao__ano=ano,
                                                importacao__mes=mes).all()
    if busca:
        busca.delete()
    busca = RelatorioCodigo90.objects.filter(empregado__matricula=matricula, importacao__ano=ano,
                                             importacao__mes=mes).all()
    if busca:
        busca.delete()
    busca = RelatorioRejeitarBatidas.objects.filter(empregado__matricula=matricula, importacao__ano=ano,
                                                    importacao__mes=mes).all()
    if busca:
        busca.delete()
    busca = RelatorioBatidasRejeitadas.objects.filter(empregado__matricula=matricula, importacao__ano=ano,
                                                      importacao__mes=mes).all()
    if busca:
        busca.delete()
    busca = RelatorioPagas.objects.filter(empregado__matricula=matricula, importacao__ano=ano,
                                          importacao__mes=mes).all()
    if busca:
        busca.delete()
    busca = RelatorioEntradaSaida.objects.filter(empregado__matricula=matricula, importacao__ano=ano,
                                                 importacao__mes=mes).all()
    if busca:
        busca.delete()


def recalcula_he(matricula, ano, mes, user):
    deleta_relatorios2(matricula, mes, ano)

    #  Busca empregados
    empregados = Empregado.objects.filter(matricula=matricula, mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    empregados.drop(columns={'data_atualizacao', 'importacao_id', 'id'}, inplace=True)

    # Busca planilha de confirmação e junta com a tabela empregados
    confirmacao = Confirmacao.objects.filter(empregado__matricula=matricula,
                                             importacao__ano=ano, importacao__mes=mes).values()
    confirmacao = pd.DataFrame(confirmacao)
    confirmacao['matricula'] = 0
    pega_matricula(confirmacao, mes, ano)
    confirmacao.drop(columns={'id', 'nome', 'data_upload', 'importacao_id', 'empregado_id'}, inplace=True)
    confirmacao.dropna(subset='matricula')

    df = pd.merge(confirmacao, empregados, on='matricula', how='left')
    df = df.dropna(subset='matricula')

    renomeacao = {}
    for i in range(1, 32):
        renomeacao['dia' + str(i)] = str(i)
    df = df.rename(columns=renomeacao)

    # Busca planilha de saldo do banco do mês e junta com a tabela anterior
    saldo_mes = BancoMes.objects.filter(empregado__matricula=matricula,
                                        importacao__mes=mes, importacao__ano=ano).values()
    saldo_mes = pd.DataFrame(saldo_mes)
    pega_matricula(saldo_mes, mes, ano)
    saldo_mes = saldo_mes.rename(columns={'saldo': 'saldo_mes',
                                          'saldo_decimal': 'saldo_mes_decimal'})
    saldo_mes.drop(columns={'id', 'data_upload', 'importacao_id', 'empregado_id', 'nome',
                            'importado_por', 'importado_por_id'}, inplace=True)
    df = pd.merge(df, saldo_mes, on='matricula', how='left')

    # Busca planilha de saldo do banco total e junta com a tabela anterior
    saldo_banco = BancoTotal.objects.filter(empregado__matricula=matricula,
                                            importacao__mes=mes, importacao__ano=ano).values()
    saldo_banco = pd.DataFrame(saldo_banco)
    pega_matricula(saldo_banco, mes, ano)
    saldo_banco = saldo_banco.rename(columns={'saldo': 'saldo_banco',
                                              'saldo_decimal': 'saldo_banco_decimal'})
    saldo_banco.drop(columns={'id', 'data_upload', 'importacao_id', 'empregado_id', 'nome',
                              'importado_por', 'importado_por_id'}, inplace=True)

    df = pd.merge(df, saldo_banco, on='matricula', how='left')

    # Busca planilha de frequência e junta com a tabela anterior
    frequencia = Frequencia.objects.filter(empregado__matricula=matricula,
                                           importacao__mes=mes, importacao__ano=ano).values()
    frequencia = pd.DataFrame(frequencia)
    pega_matricula(frequencia, mes, ano)
    frequencia.drop(columns={'id', 'data_upload', 'importacao_id', 'empregado_id', 'nome',
                             'importado_por', 'importado_por_id', 'escala'}, inplace=True)

    df = pd.merge(df, frequencia, on='matricula', how='left')
    df['data'] = pd.to_datetime(df['data'])

    df['horas_trabalhadas'] = df['horas_trabalhadas'] = [0] * len(df)
    df['valor_total'] = df['valor_total'] = [0] * len(df)
    df['horas_diurnas'] = df['horas_diurnas'] = [0] * len(df)
    df['valor_diurnas'] = df['valor_diurnas'] = [0] * len(df)
    df['horas_noturnas'] = df['horas_noturnas'] = [0] * len(df)
    df['valor_noturnas'] = df['valor_noturnas'] = [0] * len(df)

    cargas = CargaHoraria.objects.filter(empregado__matricula=matricula,
                                         importacao__mes=mes, importacao__ano=ano, carga_horaria__gt=0).values()
    cargas = pd.DataFrame(cargas)
    pega_matricula(cargas, mes, ano)
    cargas.drop(columns={'id', 'importacao_id', 'empregado_id', 'nome',
                         'importado_por', 'importado_por_id'}, inplace=True)
    cargas['carga_horaria'] = cargas['carga_horaria'].astype(int)
    df = pd.merge(df, cargas, on='matricula', how='left')

    df = df.sort_values(by=['matricula', 'data'])
    df = df.reset_index(drop=True)
    df.index += 1
    N = 0
    D = 0
    DN = 0
    ERRO = 0
    mes = df['data'][1].month
    erros = []
    entrada_saida = []
    ind = 1

    for i, j in df.iterrows():
        linha = {}
        matricula = j['matricula']
        nome = j['nome']
        data = j['data'].strftime('%d/%m/%Y')
        cargo = j['cargo']
        c2 = 1
        for a in j[1:32]:
            a_maiusculo = str(a).upper()
            if str(j['cargo']).upper() != 'ASSISTENTE ADMINISTRATIVO':
                if ('D' in a_maiusculo or 'M' in a_maiusculo or 'T' in a_maiusculo) and 'N' not in a_maiusculo \
                        and j['data'].day == c2 and j['data'].month == mes:
                    if (j['batida1'].hour + j['batida1'].minute / 60) != 0 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) != 0 and \
                            (j['batida3'].hour + j['batida3'].minute / 60) == 0:
                        horas_trabalhadas = (j['batida2'].hour + j['batida2'].minute / 60) - \
                                            (j['batida1'].hour + j['batida1'].minute / 60)
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida1'], j['batida2'], df.at[i, 'horas_trabalhadas'],
                                                          df.at[i, 'horas_diurnas'], df.at[i, 'horas_noturnas'],
                                                          df.at[i, 'setor']))
                        D += 1
                    elif (j['batida1'].hour + j['batida1'].minute / 60) < 10 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) < 10 and \
                            (j['batida3'].hour + j['batida3'].minute / 60) > 16 and j['batida4'] == 0:
                        horas_trabalhadas = (j['batida3'].hour + j['batida3'].minute / 60) - \
                                            (j['batida2'].hour + j['batida2'].minute / 60)
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida2'], j['batida3'], df.at[i, 'horas_trabalhadas'],
                                                          df.at[i, 'horas_diurnas'], df.at[i, 'horas_noturnas'],
                                                          df.at[i, 'setor']))
                        D += 1
                    elif (j['batida1'].hour + j['batida1'].minute / 60) < 10 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) < 10 and \
                            (j['batida3'].hour + j['batida3'].minute / 60) < 16 and \
                            (j['batida4'].hour + j['batida4'].minute / 60) > 16:
                        horas_trabalhadas = (j['batida4'].hour + j['batida4'].minute / 60) - \
                                            (j['batida3'].hour + j['batida3'].minute / 60)
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida3'], j['batida4'], df.at[i, 'horas_trabalhadas'],
                                                          df.at[i, 'horas_diurnas'], df.at[i, 'horas_noturnas'],
                                                          df.at[i, 'setor']))
                        D += 1
                    else:
                        df.at[i, 'horas_trabalhadas'] = 0
                        df.at[i, 'horas_diurnas'] = 0
                        df.at[i, 'horas_noturnas'] = 0
                        erros.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, 0, 0,
                                                  df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                  df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        ERRO += 1
                elif 'N' in a_maiusculo and 'D' not in a_maiusculo and j['data'].day == c2 and j['data'].month == mes \
                        and (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) <= 11 and \
                        (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) != 0:
                    if (j['batida1'].hour + j['batida1'].minute / 60) >= 17 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) == 0:
                        horas_trabalhadas = ((25 - (j['batida1'].hour + j['batida1'].minute / 60)) +
                                             (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60))
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas - 8
                        df.at[i, 'horas_noturnas'] = 8
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida1'], df.loc[ind + 1]['batida1'],
                                                          df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                          df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        N += 1
                    elif ((j['batida1'].hour + j['batida1'].minute / 60) > 0) and \
                            ((j['batida2'].hour + j['batida2'].minute / 60) >= 17) and \
                            (j['batida3'].hour + j['batida3'].minute / 60) == 0 and \
                            (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) != 0:
                        horas_trabalhadas = ((25 - (j['batida2'].hour + j['batida2'].minute / 60)) +
                                             (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60))
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas - 8
                        df.at[i, 'horas_noturnas'] = 8
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida2'], df.loc[ind + 1]['batida1'],
                                                          df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                          df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        N += 1
                    elif (j['batida1'].hour + j['batida1'].minute / 60) > 0 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) > 0 and \
                            (j['batida3'].hour + j['batida3'].minute / 60) >= 17 and \
                            (j['batida4'].hour + j['batida4'].minute / 60) == 0 and \
                            (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) != 0:
                        horas_trabalhadas = ((25 - (j['batida3'].hour + j['batida3'].minute / 60)) +
                                             (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60))
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas - 8
                        df.at[i, 'horas_noturnas'] = 8
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida3'], df.loc[ind + 1]['batida1'],
                                                          df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                          df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        N += 1
                    elif (j['batida1'].hour + j['batida1'].minute / 60) > 0 and \
                            (j['batida2'].hour + j['batida2'].minute / 60) > 0 and \
                            (j['batida3'].hour + j['batida3'].minute / 60) > 0 and \
                            (j['batida4'].hour + j['batida4'].minute / 60) >= 17 and \
                            (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) != 0:
                        horas_trabalhadas = ((25 - (j['batida4'].hour + j['batida4'].minute / 60)) +
                                             (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60))
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas - 8
                        df.at[i, 'horas_noturnas'] = 8
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida4'], df.loc[ind + 1]['batida1'],
                                                          df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                          df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        N += 1
                    else:
                        df.at[i, 'horas_trabalhadas'] = 0
                        df.at[i, 'horas_diurnas'] = 0
                        df.at[i, 'horas_noturnas'] = 0
                        erros.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, 0, 0,
                                                  df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                  df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        ERRO += 1
                elif 'DN' in a_maiusculo and j['data'].day == c2 and j['data'].month == mes:
                    if (11 > (j['batida1'].hour + j['batida1'].minute / 60) > 0) and \
                            (11 > (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60) > 0) and \
                            (j['batida2'].hour + j['batida2'].minute / 60) == 0:
                        horas_trabalhadas = (25 - (j['batida1'].hour + j['batida1'].minute / 60)) +\
                                            (df.loc[ind + 1]['batida1'].hour + df.loc[ind + 1]['batida1'].minute / 60)
                        df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                        df.at[i, 'horas_diurnas'] = horas_trabalhadas - 8
                        df.at[i, 'horas_noturnas'] = 8
                        entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                          j['batida1'], df.loc[ind + 1]['batida1'],
                                                          df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                          df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        DN += 1
                    else:
                        df.at[i, 'horas_trabalhadas'] = 0
                        df.at[i, 'horas_diurnas'] = 0
                        df.at[i, 'horas_noturnas'] = 0
                        erros.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, 0, 0,
                                                  df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                                  df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                        ERRO += 1
                elif a != '' and j['data'].day == c2 and j['data'].month == mes:
                    df.at[i, 'horas_trabalhadas'] = 0
                    df.at[i, 'horas_diurnas'] = 0
                    df.at[i, 'horas_noturnas'] = 0
                    erros.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, 0, 0,
                                              df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                              df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                    ERRO += 1
            else:
                if a != '' and j['data'].day == c2 and j['data'].month == mes and \
                        (j['batida1'].hour + j['batida1'].minute / 60) != 0 and \
                        (j['batida4'].hour + j['batida4'].minute / 60) != 0:
                    horas_trabalhadas = ((j['batida4'].hour + j['batida4'].minute / 60) - (
                            j['batida1'].hour + j['batida1'].minute / 60)) \
                                        - ((j['batida3'].hour + j['batida3'].minute / 60) - (
                                            j['batida2'].hour + j['batida2'].minute / 60))
                    df.at[i, 'horas_trabalhadas'] = horas_trabalhadas
                    df.at[i, 'horas_diurnas'] = horas_trabalhadas
                    entrada_saida.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo,
                                                      j['batida1'], j['batida4'], df.at[i, 'horas_trabalhadas'],
                                                      df.at[i, 'horas_diurnas'], df.at[i, 'horas_noturnas'],
                                                      df.at[i, 'setor']))
                    D += 1
                elif a != '' and j['data'].day == c2 and j['data'].month == mes:
                    df.at[i, 'horas_trabalhadas'] = 0
                    df.at[i, 'horas_diurnas'] = 0
                    df.at[i, 'horas_noturnas'] = 0
                    erros.append(insere_linha(linha, matricula, nome, cargo, data, a_maiusculo, 0, 0,
                                              df.at[i, 'horas_trabalhadas'], df.at[i, 'horas_diurnas'],
                                              df.at[i, 'horas_noturnas'], df.at[i, 'setor']))
                    ERRO += 1
            c2 += 1
        ind += 1

    for i, j in df.iterrows():
        df.at[i, 'valor_diurnas'] = (j['salario'] + j['insalubridade']) / j['carga_horaria'] * j['horas_diurnas'] * 1.5
        df.at[i, 'valor_noturnas'] = (j['salario'] + j['insalubridade']) / j['carga_horaria'] * j[
            'horas_noturnas'] * 1.5 * 1.2
        df.at[i, 'valor_total'] = df.at[i, 'valor_diurnas'] + df.at[i, 'valor_noturnas']

    entrada_saida = pd.DataFrame(entrada_saida)

    rejeitar_batidas_d(df, entrada_saida, user, mes, ano)
    rejeitar_batidas_n(df, entrada_saida, user, mes, ano)
    rejeitar_batidas_dn(df, entrada_saida, user, mes, ano)

    df = df.drop(columns={'data', 'batida1', 'batida2', 'batida3', 'batida4', 'batida5', 'batida6'})
    df = df.groupby(['matricula', 'nome', 'salario', 'insalubridade', 'cargo',
                     '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
                     '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23',
                     '24', '25', '26', '27', '28', '29', '30', '31', 'saldo_mes',
                     'saldo_mes_decimal', 'saldo_banco', 'saldo_banco_decimal', 'carga_horaria', 'setor']
                    )[['horas_trabalhadas', 'valor_total', 'horas_diurnas', 'valor_diurnas',
                       'horas_noturnas', 'valor_noturnas']].sum(numeric_only=False)
    df = df.reset_index(drop=False)

    for i, j in df.iterrows():
        salva_relatorio_confirmacao(j, user, mes, ano)

    erros = pd.DataFrame(erros)
    for i, j in erros.iterrows():
        salva_relatorio_erros(j, user, mes, ano, 'confirmacao')

    negativos = df[(df['saldo_banco_decimal'] < 0) | (df['saldo_mes_decimal'] < 0)].copy(deep=True)
    negativos = negativos[['matricula', 'nome', 'cargo', 'saldo_mes', 'saldo_mes_decimal',
                           'saldo_banco', 'saldo_banco_decimal', 'setor']]

    for i, j in negativos.iterrows():
        salva_relatorio_negativos(j, user, mes, ano, 'confirmacao')
        entrada_saida = entrada_saida[entrada_saida['matricula'] != j['matricula']]

    for i, j in entrada_saida.iterrows():
        salva_relatorio_entrada_saida(j, user, mes, ano)
        salva_relatorio_codigo90(j, user, mes, ano)

    response, excel_path_confirmacao, df = gera_relatorio_confirmacao(mes, ano, '', '', matricula)

    pagas = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    pagas = pd.DataFrame(pagas)

    if not pagas.empty:
        pagar = RelatorioConfirmacao.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                                    importacao__ano=ano, saldo_mes_decimal__gte=0,
                                                    saldo_banco_decimal__gte=0, horas_trabalhadas__gt=0).values()
        if pagar:
            pagar = pd.DataFrame(pagar)
            pega_matricula(pagar, mes, ano)
            coluna_matricula = pagar['matricula']
            pagar = pagar.drop(columns={'matricula'})
            pagar.insert(0, 'matricula', coluna_matricula)
            for i, j in pagar.iterrows():
                salva_relatorio_pagas(j, user, mes, ano)

    conclusao = f'Processamento efetuado com sucesso:\n' \
                f'D: {D}, N: {N}, DN: {DN}, Erros: {ERRO}'

    return df, conclusao
