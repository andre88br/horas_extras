import locale
import calendar

import pandas as pd
from django.http import HttpResponse

from pos_calculo.models import RelatorioBatidasRejeitadas
from .dbchanges import *

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def arruma_campos(df, tipo, mes, ano):
    if tipo == 'confirmacao':
        df['saldo_mes_decimal'] = df['saldo_mes_decimal']. \
            map(lambda x: format(x, '.2f'))
        df['saldo_mes_decimal'] = df['saldo_mes_decimal']. \
            astype(str).str.replace('.', ',', regex=False)
        df['horas_trabalhadas'] = df['horas_trabalhadas']. \
            map(lambda x: format(x, '.2f'))
        df['horas_trabalhadas'] = df['horas_trabalhadas']. \
            astype(str).str.replace('.', ',', regex=False)

    if tipo == 'solicitacao':
        df['horas_totais'] = df['horas_totais']. \
            map(lambda x: format(x, '.2f'))
        df['horas_totais'] = df['horas_totais']. \
            astype(str).str.replace('.', ',', regex=False)
        df['mes/ano'] = 0

        for i, j in df.iterrows():
            importacao = Importacoes.objects.filter(id=j['importacao_id']).values()
            importacao = pd.DataFrame(importacao)
            df.at[i, 'mes/ano'] = f'{importacao.mes}/{importacao.ano}' \
                if len(str(f'{importacao.mes}/{importacao.ano}')) == 7 \
                else f'0{int(importacao.mes)}/{int(importacao.ano)}'
        coluna_mes_ano = df['mes/ano']
        df = df.drop(columns={'mes/ano'})
        df.insert(0, 'mes/ano', coluna_mes_ano)

        df = df.sort_values(by=['nome', 'mes/ano'])

    if tipo == 'solicitacao' or tipo == 'confirmacao':
        df['salario'] = df['salario']. \
            map(lambda x: locale.currency(x, symbol=True))
        df['insalubridade_periculosidade'] = df['insalubridade_periculosidade']. \
            map(lambda x: locale.currency(x, symbol=True))
        df['valor_diurnas'] = df['valor_diurnas']. \
            map(lambda x: locale.currency(x, symbol=True))
        df['valor_noturnas'] = df['valor_noturnas']. \
            map(lambda x: locale.currency(x, symbol=True))
        df['valor_total'] = df['valor_total']. \
            map(lambda x: locale.currency(x, symbol=True))
        df['saldo_banco_decimal'] = df['saldo_banco_decimal']. \
            map(lambda x: format(x, '.2f'))
        df['saldo_banco_decimal'] = df['saldo_banco_decimal']. \
            astype(str).str.replace('.', ',', regex=False)
        df['horas_diurnas'] = df['horas_diurnas']. \
            map(lambda x: format(x, '.2f'))
        df['horas_diurnas'] = df['horas_diurnas']. \
            astype(str).str.replace('.', ',', regex=False)
        df['horas_noturnas'] = df['horas_noturnas']. \
            map(lambda x: format(x, '.2f'))
        df['horas_noturnas'] = df['horas_noturnas']. \
            astype(str).str.replace('.', ',', regex=False)
        df.columns = df.columns.str.replace('dia', '')
        if calendar.monthrange(int(ano), int(mes))[1] == 30:
            df = df.drop(columns={'31'})
        if calendar.monthrange(int(ano), int(mes))[1] == 29:
            df = df.drop(columns={'30', '31'})
        if calendar.monthrange(int(ano), int(mes))[1] == 28:
            df = df.drop(columns={'29', '30', '31'})
        df = df.rename(columns={'insalubridade_periculosidade': 'insalubridade/periculosidade'})
        df = df.drop(columns={'empregado_id', 'importacao_id'})
        df = df.drop(columns={'id', 'importado_por',
                              'importado_por_id', 'data_upload'})

    if tipo == 'entrada_saida':
        df['horas_diurnas'] = df['horas_diurnas']. \
            astype(str).str.replace(',', '.').astype(float)
        df['horas_trabalhadas'] = df['horas_trabalhadas']. \
            astype(str).str.replace(',', '.').astype(float)
        df['horas_trabalhadas'] = df['horas_trabalhadas']. \
            map(lambda x: format(x, '.2f'))
        df['horas_diurnas'] = df['horas_diurnas']. \
            map(lambda x: format(x, '.2f'))
        df['horas_diurnas'] = df['horas_diurnas']. \
            astype(str).str.replace('.', ',', regex=False)
        df['horas_trabalhadas'] = df['horas_trabalhadas']. \
            astype(str).str.replace('.', ',', regex=False)
        df = df.drop(columns={'empregado_id', 'importacao_id'})
        df = df.drop(columns={'id', 'importado_por',
                              'importado_por_id', 'data_upload'})

    if tipo == 'negativos_solicitacao':
        df = df.drop(columns={'saldo_mes', 'saldo_mes_decimal', 'saldo_banco_decimal',
                              'tipo', 'empregado_id', 'importacao_id'})
        df = df.drop(columns={'id', 'importado_por',
                              'importado_por_id', 'data_upload'})

    if tipo == 'negativos_confirmacao':
        df = df.drop(columns={'saldo_mes_decimal', 'saldo_banco_decimal', 'tipo',
                              'empregado_id', 'importacao_id'})
        df = df.drop(columns={'id', 'importado_por',
                              'importado_por_id', 'data_upload'})

    if tipo == 'erros':
        df = df.drop(columns={'empregado_id', 'importacao_id', 'tipo'})
        df = df.drop(columns={'id', 'importado_por',
                              'importado_por_id', 'data_upload'})

    if tipo == 'rejeitar_batidas':
        df.columns = df.columns.str.replace('dia', '')
        if calendar.monthrange(int(ano), int(mes))[1] == 30:
            df = df.drop(columns={'31'})
        if calendar.monthrange(int(ano), int(mes))[1] == 29:
            df = df.drop(columns={'30', '31'})
        if calendar.monthrange(int(ano), int(mes))[1] == 28:
            df = df.drop(columns={'29', '30', '31'})
        df = df.drop(columns={'empregado_id', 'importacao_id'})
        df = df.drop(columns={'id', 'importado_por',
                              'importado_por_id', 'data_upload'})

    if tipo == 'pagas':
        df['valor_diurnas'] = df['valor_diurnas']. \
            map(lambda x: locale.currency(x, symbol=True))
        df['valor_noturnas'] = df['valor_noturnas']. \
            map(lambda x: locale.currency(x, symbol=True))
        df['total'] = df['total']. \
            map(lambda x: locale.currency(x, symbol=True))
        df['hs_diurnas'] = df['hs_diurnas']. \
            map(lambda x: format(x, '.2f'))
        df['hs_diurnas'] = df['hs_diurnas']. \
            astype(str).str.replace('.', ',', regex=False)
        df['hs_noturnas'] = df['hs_noturnas']. \
            map(lambda x: format(x, '.2f'))
        df['hs_noturnas'] = df['hs_noturnas']. \
            astype(str).str.replace('.', ',', regex=False)

        df['mes/ano'] = 0

        for i, j in df.iterrows():
            importacao = Importacoes.objects.filter(id=j['importacao_id']).values()
            importacao = pd.DataFrame(importacao)
            df.at[i, 'mes/ano'] = f'{importacao.mes}/{importacao.ano}' \
                if len(str(f'{importacao.mes}/{importacao.ano}')) == 7 \
                else f'0{int(importacao.mes)}/{int(importacao.ano)}'

        df = df[['cargo', 'matricula', 'nome', 'hs_diurnas', 'valor_diurnas',
                'hs_noturnas', 'valor_noturnas', 'total', 'mes/ano', 'setor']]

        df = df.sort_values(by='mes/ano')

    if tipo == 'cod_90':
        df = df.drop(columns={'empregado_id', 'importacao_id'})

        df = df.drop(columns={'id', 'importado_por',
                              'importado_por_id', 'data_upload'})

    if tipo == 'setores':
        df['mes/ano'] = 0

        for i, j in df.iterrows():
            importacao = Importacoes.objects.filter(id=j['importacao_id']).values()
            importacao = pd.DataFrame(importacao)
            df.at[i, 'mes/ano'] = f'{importacao.mes}/{importacao.ano}' \
                if len(str(f'{importacao.mes}/{importacao.ano}')) == 7 \
                else f'0{int(importacao.mes)}/{int(importacao.ano)}'

        df = df.sort_values(by='mes/ano')

    df.columns = df.columns.str.replace('_', ' ', regex=False).str.upper()

    df = df.reset_index(drop=True)
    df.index += 1
    return df


def gera_relatorio_solicitacao(mes, ano, mes2, ano2, matricula):
    if matricula == '':
        if mes2 is not None and mes2 != '':
            empregados = Empregado.objects.filter(mes__gte=mes, mes__lte=mes2, ano__gte=ano, ano__lte=ano2).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioSolicitacao.objects.filter(importacao__mes__gte=mes, importacao__mes__lte=mes2,
                                                     importacao__ano__gte=ano, importacao__ano__lte=ano
                                                     ).order_by('nome').values()
        else:
            empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioSolicitacao.objects.filter(importacao__mes=mes, importacao__ano=ano).order_by('nome').values()
    else:
        if mes2 is not None and mes2 != '':
            empregados = Empregado.objects.filter(mes__gte=mes, mes__lte=mes2, ano__gte=ano, ano__lte=ano2).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioSolicitacao.objects.filter(empregado__matricula=matricula,
                                                     importacao__mes__gte=mes, importacao__mes__lte=mes2,
                                                     importacao__ano__gte=ano, importacao__ano__lte=ano
                                                     ).order_by('nome').values()
        else:
            empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioSolicitacao.objects.filter(empregado__matricula=matricula,
                                                     importacao__mes=mes, importacao__ano=ano
                                                     ).order_by('nome').values()

    response, excel_path_solicitacao = '', ''
    if not df:
        pass
    else:
        df = pd.DataFrame(df)
        print(df)
        pega_matricula(empregados, df)
        coluna_matricula = df['matricula']
        df = df.drop(columns={'matricula'})
        df.insert(0, 'matricula', coluna_matricula)
        df = arruma_campos(df, 'solicitacao', mes, ano)
        if mes2 is not None and mes2 != '':
            excel_path_solicitacao = f'Solicitação de {mes}-{ano} até {mes2}-{ano2}.xlsx'
            df.to_excel(excel_path_solicitacao, index=False, sheet_name='Solicitado')

            with open(excel_path_solicitacao, 'rb') as file:
                response = HttpResponse(file.read(),
                                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="Solicitação de {mes}-{ano} até {mes2}-{ano2}.xlsx"'
        else:
            excel_path_solicitacao = f'Solicitação {mes}-{ano}.xlsx'
            df.to_excel(excel_path_solicitacao, index=False, sheet_name='Solicitado')

            with open(excel_path_solicitacao, 'rb') as file:
                response = HttpResponse(file.read(),
                                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="Solicitação - {mes}-{ano}.xlsx"'

    return response, excel_path_solicitacao, df


def gera_relatorio_erros(mes, ano, mes2, ano2, tipo, matricula):
    empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    if matricula == '' and (mes2 == '' or mes2 is None):
        df = RelatorioErros.objects.filter(importacao__mes=mes,
                                           importacao__ano=ano, tipo=tipo).order_by('nome').values()
    else:
        df = RelatorioErros.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                           importacao__ano=ano, tipo=tipo).order_by('nome').values()
    response, excel_path_erros = '', ''
    if not df:
        pass
    else:
        df = pd.DataFrame(df)
        pega_matricula(empregados, df)
        coluna_matricula = df['matricula']
        df = df.drop(columns={'matricula'})
        df.insert(0, 'matricula', coluna_matricula)
        df = arruma_campos(df, 'erros', mes, ano)

        excel_path_erros = f'Erros {mes}-{ano}.xlsx'
        df.to_excel(excel_path_erros, index=False, sheet_name='Erros')

        with open(excel_path_erros, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="Erros - {mes}-{ano}.xlsx"'

    return response, excel_path_erros, df


def gera_relatorio_confirmacao(mes, ano, mes2, ano2, matricula):
    if matricula == '':
        if mes2 is not None and mes2 != '':
            empregados = Empregado.objects.filter(mes__gte=mes, mes__lte=mes2, ano__gte=ano, ano__lte=ano2).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioConfirmacao.objects.filter(importacao__mes__gte=mes, importacao__mes__lte=mes2,
                                                     importacao__ano__gte=ano, importacao__ano__lte=ano
                                                     ).order_by('nome').values()
        else:
            empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioConfirmacao.objects.filter(importacao__mes=mes, importacao__ano=ano).order_by('nome').values()
    else:
        if mes2 is not None and mes2 != '':
            empregados = Empregado.objects.filter(mes__gte=mes, mes__lte=mes2, ano__gte=ano, ano__lte=ano2).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioConfirmacao.objects.filter(empregado__matricula=matricula,
                                                     importacao__mes__gte=mes, importacao__mes__lte=mes2,
                                                     importacao__ano__gte=ano, importacao__ano__lte=ano
                                                     ).order_by('nome').values()
        else:
            empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioConfirmacao.objects.filter(empregado__matricula=matricula,
                                                     importacao__mes=mes, importacao__ano=ano
                                                     ).order_by('nome').values()

    response, excel_path = '', ''
    if not df:
        pass
    else:
        df = pd.DataFrame(df)
        print(df)
        pega_matricula(empregados, df)
        coluna_matricula = df['matricula']
        df = df.drop(columns={'matricula'})
        df.insert(0, 'matricula', coluna_matricula)
        df = arruma_campos(df, 'confirmacao', mes, ano)
        if mes2 is not None and mes2 != '':
            excel_path = f'Confirmação de {mes}-{ano} até {mes2}-{ano2}.xlsx'
            df.to_excel(excel_path, index=False, sheet_name='Confirmado')

            with open(excel_path, 'rb') as file:
                response = HttpResponse(file.read(),
                                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response[
                    'Content-Disposition'] = f'attachment; filename="Confirmação de {mes}-{ano} até {mes2}-{ano2}.xlsx"'
        else:
            excel_path = f'Confirmação {mes}-{ano}.xlsx'
            df.to_excel(excel_path, index=False, sheet_name='Confirmado')

            with open(excel_path, 'rb') as file:
                response = HttpResponse(file.read(),
                                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="Confirmação - {mes}-{ano}.xlsx"'

    return response, excel_path, df


def gera_relatorio_negativos(mes, ano, mes2, ano2, tipo, matricula):
    empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    if matricula == '':
        df = RelatorioNegativos.objects.filter(importacao__mes=mes,
                                               importacao__ano=ano, tipo=tipo).order_by('nome').values()

    else:
        df = RelatorioNegativos.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                               importacao__ano=ano, tipo=tipo).order_by('nome').values()
    response, excel_path_negativos = '', ''
    if not df:
        pass
    else:
        df = pd.DataFrame(df)
        pega_matricula(empregados, df)
        coluna_matricula = df['matricula']
        df = df.drop(columns={'matricula'})
        df.insert(0, 'matricula', coluna_matricula)
        df = arruma_campos(df, f'negativos_{tipo}', mes, ano)
        excel_path_negativos = f'Bancos negativos {mes}-{ano}.xlsx'
        df.to_excel(excel_path_negativos, index=False, sheet_name='Bancos Negativos')

        with open(excel_path_negativos, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="Bancos negativos - {mes}-{ano}.xlsx"'

    return response, excel_path_negativos, df


def gera_relatorio_codigo90(mes, ano, mes2, ano2, matricula):
    empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    if matricula == '':
        df = RelatorioCodigo90.objects.filter(importacao__mes=mes,
                                              importacao__ano=ano).values()
    else:
        df = RelatorioCodigo90.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                              importacao__ano=ano).values()

    response, txt_path_codigo90 = '', ''
    if not df:
        pass
    else:
        df = pd.DataFrame(df)
        pega_matricula(empregados, df)
        coluna_matricula = df['matricula']
        df = df.drop(columns={'matricula'})
        df.insert(0, 'matricula', coluna_matricula)
        df = arruma_campos(df, 'cod_90', mes, ano)
        txt_path_codigo90 = f'Código 90 {mes}-{ano}.txt'
        df.to_csv(txt_path_codigo90, sep='\t', index=False, header=False)

        with open(txt_path_codigo90, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='text/tab-separated-values')
            response['Content-Disposition'] = f'attachment; filename="Código 90 - {mes}-{ano}.txt"'

    return response, txt_path_codigo90, df


def gera_relatorio_entrada_saida(mes, ano, mes2, ano2, matricula):
    empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    if matricula == '':
        df = RelatorioEntradaSaida.objects.filter(importacao__mes=mes, importacao__ano=ano).order_by('nome').values()
    else:
        df = RelatorioEntradaSaida.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                                  importacao__ano=ano).order_by('nome').values()

    response, excel_path_entrada_saida = '', ''
    if not df:
        pass
    else:
        df = pd.DataFrame(df)
        pega_matricula(empregados, df)
        coluna_matricula = df['matricula']
        df = df.drop(columns={'matricula'})
        df.insert(0, 'matricula', coluna_matricula)
        df = arruma_campos(df, 'entrada_saida', mes, ano)

        excel_path_entrada_saida = f'Entrada e saída {mes}-{ano}.xlsx'
        df.to_excel(excel_path_entrada_saida, index=False, sheet_name='Entrada e Saída')

        with open(excel_path_entrada_saida, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="Entrada e saída - {mes}-{ano}.xlsx"'

    return response, excel_path_entrada_saida, df


def gera_relatorio_rejeitar_batidas(mes, ano, mes2, ano2, matricula):
    empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    if matricula == '':
        df = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano).order_by('nome').values()
    else:
        df = RelatorioRejeitarBatidas.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                                     importacao__ano=ano).order_by('nome').values()
    response, excel_path_rejeitar_batidas = '', ''
    if not df:
        pass
    else:
        df = pd.DataFrame(df)
        pega_matricula(empregados, df)
        coluna_matricula = df['matricula']
        df = df.drop(columns={'matricula'})
        df.insert(0, 'matricula', coluna_matricula)
        df = arruma_campos(df, 'rejeitar_batidas', mes, ano)
        excel_path_rejeitar_batidas = f'Rejeitar batidas {mes}-{ano}.xlsx'
        df.to_excel(excel_path_rejeitar_batidas, index=False, sheet_name='Rejeitar batidas')

        with open(excel_path_rejeitar_batidas, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="Rejeitar batidas - {mes}-{ano}.xlsx"'

    return response, excel_path_rejeitar_batidas, df


def gera_relatorio_pagas(mes, ano, matricula, mes2, ano2):
    if matricula == '':
        if mes2 is not None and mes2 != '':
            empregados = Empregado.objects.filter(mes__gte=mes, mes__lte=mes2, ano__gte=ano, ano__lte=ano2).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioPagas.objects.filter(importacao__mes__gte=mes, importacao__mes__lte=mes2,
                                               importacao__ano__gte=ano,
                                               importacao__ano__lte=ano2).order_by('cargo', 'nome').values()
        else:
            empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    else:
        if mes2 is not None and mes2 != '':
            empregados = Empregado.objects.filter(mes__gte=mes, mes__lte=mes2, ano__gte=ano, ano__lte=ano2,
                                                  matricula=matricula).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioPagas.objects.filter(importacao__mes__gte=mes, importacao__mes__lte=mes2,
                                               importacao__ano__gte=ano, importacao__ano__lte=ano2,
                                               empregado__matricula=matricula).values()
        else:
            empregados = Empregado.objects.filter(mes=mes, ano=ano, matricula=matricula).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                               empregado__matricula=matricula).values()

    df = pd.DataFrame(df)
    pega_matricula(empregados, df)
    coluna_matricula = df['matricula']
    df = df.drop(columns={'matricula'})
    df.insert(0, 'matricula', coluna_matricula)
    print(df)
    df = arruma_campos(df, 'pagas', mes, ano)

    if mes2 != '' and mes is not None:
        excel_path_pagas = f'HE Pagas de {mes}-{ano} até {mes2}-{ano2}.xlsx'
        df.to_excel(excel_path_pagas, index=False, sheet_name='Solicitado')

        with open(excel_path_pagas, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="HE Pagas  de {mes}-{ano} até {mes2}-{ano2}.xlsx"'
    else:
        excel_path_pagas = f'HE Pagas {mes}-{ano}.xlsx'
        df.to_excel(excel_path_pagas, index=False, sheet_name='Solicitado')

        with open(excel_path_pagas, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="HE Pagas  - {mes}-{ano}.xlsx"'
    if not df.empty:
        return response, excel_path_pagas, df
    else:
        pass


def gera_relatorio_setores(mes, ano, mes2, ano2):
    response, excel_path_setor = '', ''

    if mes2 != '' and mes2 is not None:
        df = RelatorioConfirmacao.objects.filter(importacao__mes__gte=mes, importacao__mes__lte=mes2,
                                                 importacao__ano__gte=ano,
                                                 importacao__ano__lte=ano2).values()
        empregados = Empregado.objects.filter(mes__gte=mes, mes__lte=mes2, ano__gte=ano, ano__lte=ano2).values()
        empregados = pd.DataFrame(empregados)
    else:
        df = RelatorioConfirmacao.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
        empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
        empregados = pd.DataFrame(empregados)

    if not df:
        pass
    else:
        df = pd.DataFrame(df)
        pega_matricula(empregados, df)
        coluna_matricula = df['matricula']
        df = df.drop(columns={'matricula'})
        df.insert(0, 'matricula', coluna_matricula)
        df = arruma_campos(df, 'setores', mes, ano)
        print(df)
        df = df[['MATRICULA', 'NOME', 'CARGO', 'MES/ANO', 'SETOR']]
        if mes2 == '' and mes2 is None:
            excel_path_setor = f'Horas Extras por setor {mes}-{ano}.xlsx'
            df.to_excel(excel_path_setor, index=False, sheet_name='Setores')

            with open(excel_path_setor, 'rb') as file:
                response = HttpResponse(file.read(),
                                        content_type='application/'
                                                     'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="Horas Extras por setor - {mes}-{ano}.xlsx"'
        else:
            excel_path_setor = f'Horas Extras por setor {mes}-{ano} até {mes2}-{ano2}.xlsx'
            df.to_excel(excel_path_setor, index=False, sheet_name='Setores')

            with open(excel_path_setor, 'rb') as file:
                response = HttpResponse(file.read(),
                                        content_type='application/'
                                                     'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="Horas Extras por setor - ' \
                                                  f'{mes}-{ano} até {mes2}-{ano2}.xlsx"'

    return response, excel_path_setor, df


def pega_matricula(empregados, df):
    for i, j in df.iterrows():
        matricula = int(empregados[empregados['id'] == j['empregado_id']]['matricula'].values)
        df.at[i, 'matricula'] = matricula
    df['matricula'] = df['matricula'].astype(int)


def gera_grafico_pagas(mes, ano, matricula, mes2, ano2):
    if matricula == '':
        if mes2 is not None:
            empregados = Empregado.objects.filter(mes__gte=mes, mes__lte=mes2, ano__gte=ano, ano__lte=ano2).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioPagas.objects.filter(importacao__mes__gte=mes, importacao__mes__lte=mes2,
                                               importacao__ano__gte=ano,
                                               importacao__ano__lte=ano2).order_by('cargo', 'nome').values()
        else:
            empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    else:
        if mes2 is not None:
            empregados = Empregado.objects.filter(mes__gte=mes, mes__lte=mes2, ano__gte=ano, ano__lte=ano2,
                                                  matricula=matricula).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioPagas.objects.filter(importacao__mes__gte=mes, importacao__mes__lte=mes2,
                                               importacao__ano__gte=ano, importacao__ano__lte=ano2,
                                               empregado__matricula=matricula).values()
        else:
            empregados = Empregado.objects.filter(mes=mes, ano=ano, matricula=matricula).values()
            empregados = pd.DataFrame(empregados)
            df = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                               empregado__matricula=matricula).values()

    df = pd.DataFrame(df)
    pega_matricula(empregados, df)
    coluna_matricula = df['matricula']
    df = df.drop(columns={'matricula'})
    df.insert(0, 'matricula', coluna_matricula)

    df['mes/ano'] = 0

    for i, j in df.iterrows():
        importacao = Importacoes.objects.filter(id=j['importacao_id']).values()
        importacao = pd.DataFrame(importacao)
        df.at[i, 'mes/ano'] = f'{importacao.mes}/{importacao.ano}' \
            if len(str(f'{importacao.mes}/{importacao.ano}')) == 7 \
            else f'0{int(importacao.mes)}/{int(importacao.ano)}'

    df = df[['cargo', 'matricula', 'nome', 'hs_diurnas', 'valor_diurnas',
             'hs_noturnas', 'valor_noturnas', 'total', 'mes/ano', 'setor']]

    df = df.groupby('mes/ano')['total'].sum()

    df = df.reset_index(drop=False)

    if not df.empty:
        return df
    else:
        pass


def gera_relatorio_rejeitadas(mes, ano, mes2, ano2, matricula):
    empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    if matricula == '':
        df = RelatorioBatidasRejeitadas.objects.filter(importacao__mes=mes, importacao__ano=ano).order_by('nome').values()
    else:
        df = RelatorioBatidasRejeitadas.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                                       importacao__ano=ano).order_by('nome').values()
    response, excel_path_rejeitar_batidas = '', ''
    if not df:
        pass
    else:
        df = pd.DataFrame(df)
        pega_matricula(empregados, df)
        coluna_matricula = df['matricula']
        df = df.drop(columns={'matricula'})
        df.insert(0, 'matricula', coluna_matricula)
        df = arruma_campos(df, 'batidas_rejeitadas', mes, ano)
        excel_path_rejeitar_batidas = f'Batidas rejeitadas {mes}-{ano}.xlsx'
        df.to_excel(excel_path_rejeitar_batidas, index=False, sheet_name='Batidas rejeitadas')

        with open(excel_path_rejeitar_batidas, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="Batidas rejeitadas - {mes}-{ano}.xlsx"'

    return response, excel_path_rejeitar_batidas, df
