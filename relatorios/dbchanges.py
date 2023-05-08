from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from empregados.models import Empregado, Importacoes
from relatorios.models import RelatorioConfirmacao, RelatorioSolicitacao, RelatorioNegativos, \
    RelatorioRejeitarBatidas, RelatorioErros, RelatorioEntradaSaida, RelatorioPagas, RelatorioCodigo90, VoltarNegativos


def salva_relatorio_confirmacao(fields, usuario, mes, ano):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='rel_confirmacao', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='rel_confirmacao')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = RelatorioConfirmacao.objects.update_or_create(
                empregado=empregado, importacao=importacao,
                defaults={
                    'nome': fields['nome'],
                    'cargo': fields['cargo'],
                    'salario': fields['salario'],
                    'insalubridade_periculosidade': fields['insalubridade'],
                    'saldo_mes': fields['saldo_mes'],
                    'saldo_mes_decimal': fields['saldo_mes_decimal'],
                    'saldo_banco': fields['saldo_banco'],
                    'saldo_banco_decimal': fields['saldo_banco_decimal'],
                    'horas_trabalhadas': fields['horas_trabalhadas'],
                    'valor_total': fields['valor_total'],
                    'horas_diurnas': fields['horas_diurnas'],
                    'valor_diurnas': fields['valor_diurnas'],
                    'horas_noturnas': fields['horas_noturnas'],
                    'valor_noturnas': fields['valor_noturnas'],
                    'dia1': fields['1'],
                    'dia2': fields['2'],
                    'dia3': fields['3'],
                    'dia4': fields['4'],
                    'dia5': fields['5'],
                    'dia6': fields['6'],
                    'dia7': fields['7'],
                    'dia8': fields['8'],
                    'dia9': fields['9'],
                    'dia10': fields['10'],
                    'dia11': fields['11'],
                    'dia12': fields['12'],
                    'dia13': fields['13'],
                    'dia14': fields['14'],
                    'dia15': fields['15'],
                    'dia16': fields['16'],
                    'dia17': fields['17'],
                    'dia18': fields['18'],
                    'dia19': fields['19'],
                    'dia20': fields['20'],
                    'dia21': fields['21'],
                    'dia22': fields['22'],
                    'dia23': fields['23'],
                    'dia24': fields['24'],
                    'dia25': fields['25'],
                    'dia26': fields['26'],
                    'dia27': fields['27'],
                    'dia28': fields['28'],
                    'dia29': fields['29'],
                    'dia30': fields['30'],
                    'dia31': fields['31'],
                    'importado_por': usuario.username,
                    'importado_por_id': usuario.id,
                    'data_upload': datetime.now(),
                    'setor': str(fields['setor']).upper(),
                })
            return document
    except ObjectDoesNotExist:
        pass


def salva_relatorio_solicitacao(fields, usuario, mes, ano):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='rel_solicitacao', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='rel_solicitacao')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = RelatorioSolicitacao.objects.update_or_create(
                empregado=empregado, importacao=importacao,
                defaults={
                    'nome': fields['nome'],
                    'cargo': fields['cargo'],
                    'salario': fields['salario'],
                    'insalubridade_periculosidade': fields['insalubridade'],
                    'saldo_banco': fields['saldo_banco'],
                    'saldo_banco_decimal': fields['saldo_banco_decimal'],
                    'horas_totais': fields['horas_totais'],
                    'valor_total': fields['valor_total'],
                    'horas_diurnas': fields['horas_diurnas'],
                    'valor_diurnas': fields['valor_diurnas'],
                    'horas_noturnas': fields['horas_noturnas'],
                    'valor_noturnas': fields['valor_noturnas'],
                    'dia1': fields['1'],
                    'dia2': fields['2'],
                    'dia3': fields['3'],
                    'dia4': fields['4'],
                    'dia5': fields['5'],
                    'dia6': fields['6'],
                    'dia7': fields['7'],
                    'dia8': fields['8'],
                    'dia9': fields['9'],
                    'dia10': fields['10'],
                    'dia11': fields['11'],
                    'dia12': fields['12'],
                    'dia13': fields['13'],
                    'dia14': fields['14'],
                    'dia15': fields['15'],
                    'dia16': fields['16'],
                    'dia17': fields['17'],
                    'dia18': fields['18'],
                    'dia19': fields['19'],
                    'dia20': fields['20'],
                    'dia21': fields['21'],
                    'dia22': fields['22'],
                    'dia23': fields['23'],
                    'dia24': fields['24'],
                    'dia25': fields['25'],
                    'dia26': fields['26'],
                    'dia27': fields['27'],
                    'dia28': fields['28'],
                    'dia29': fields['29'],
                    'dia30': fields['30'],
                    'dia31': fields['31'],
                    'importado_por': usuario.username,
                    'importado_por_id': usuario.id,
                    'data_upload': datetime.now(),
                    'setor': str(fields['setor']).upper(),
                })
            return document
    except ObjectDoesNotExist:
        pass


def salva_relatorio_negativos(fields, usuario, mes, ano, tipo):
    if tipo == 'solicitacao':
        Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='rel_negativos_sol', defaults={
            'importado_por_id': usuario.id,
            'importado_por': usuario.username,
            'data_upload': datetime.now(),
        })
        importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='rel_negativos_sol')
        try:
            empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
            if empregado:
                document = RelatorioNegativos.objects.update_or_create(
                    empregado=empregado, importacao=importacao,
                    defaults={
                        'nome': fields['nome'],
                        'cargo': fields['cargo'],
                        'saldo_mes': '',
                        'saldo_mes_decimal': 0,
                        'saldo_banco': fields['saldo_banco'],
                        'saldo_banco_decimal': fields['saldo_banco_decimal'],
                        'importado_por': usuario.username,
                        'importado_por_id': usuario.id,
                        'data_upload': datetime.now(),
                        'setor': fields['setor'],
                        'tipo': tipo,
                    })
                return document
        except ObjectDoesNotExist:
            pass
    else:
        Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='rel_negativos_conf', defaults={
            'importado_por_id': usuario.id,
            'importado_por': usuario.username,
            'data_upload': datetime.now(),
        })
        importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='rel_negativos_conf')
        try:
            empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
            if empregado:
                document = RelatorioNegativos.objects.update_or_create(
                    empregado=empregado, importacao=importacao,
                    defaults={
                        'nome': fields['nome'],
                        'cargo': fields['cargo'],
                        'saldo_mes': fields['saldo_mes'],
                        'saldo_mes_decimal': fields['saldo_mes_decimal'],
                        'saldo_banco': fields['saldo_banco'],
                        'saldo_banco_decimal': fields['saldo_banco_decimal'],
                        'importado_por': usuario.username,
                        'importado_por_id': usuario.id,
                        'data_upload': datetime.now(),
                        'setor': fields['setor'],
                        'tipo': tipo,
                    })
                return document
        except ObjectDoesNotExist:
            pass


def salva_relatorio_codigo90(fields, usuario, mes, ano):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='rel_codigo90', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='rel_codigo90')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = RelatorioCodigo90.objects.update_or_create(
                empregado=empregado, importacao=importacao, inicio=fields['data'],
                defaults={
                    'fim': fields['data'],
                    'importado_por': usuario.username,
                    'importado_por_id': usuario.id,
                    'data_upload': datetime.now(),
                })
            return document
    except ObjectDoesNotExist:
        pass


def salva_relatorio_rejeitar_batidas(fields, usuario, mes, ano, tipo):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='rel_rejeitar_batidas', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='rel_rejeitar_batidas')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)

        if empregado:
            document = RelatorioRejeitarBatidas.objects.update_or_create(
                empregado=empregado, importacao=importacao, tipo=tipo,
                defaults={
                    'nome': fields['nome'],
                    'dia1': fields['1'],
                    'dia2': fields['2'],
                    'dia3': fields['3'],
                    'dia4': fields['4'],
                    'dia5': fields['5'],
                    'dia6': fields['6'],
                    'dia7': fields['7'],
                    'dia8': fields['8'],
                    'dia9': fields['9'],
                    'dia10': fields['10'],
                    'dia11': fields['11'],
                    'dia12': fields['12'],
                    'dia13': fields['13'],
                    'dia14': fields['14'],
                    'dia15': fields['15'],
                    'dia16': fields['16'],
                    'dia17': fields['17'],
                    'dia18': fields['18'],
                    'dia19': fields['19'],
                    'dia20': fields['20'],
                    'dia21': fields['21'],
                    'dia22': fields['22'],
                    'dia23': fields['23'],
                    'dia24': fields['24'],
                    'dia25': fields['25'],
                    'dia26': fields['26'],
                    'dia27': fields['27'],
                    'dia28': fields['28'],
                    'dia29': fields['29'],
                    'dia30': fields['30'],
                    'dia31': fields['31'],
                    'importado_por': usuario.username,
                    'importado_por_id': usuario.id,
                    'data_upload': datetime.now(),
                })
            return document
    except ObjectDoesNotExist:
        pass


def salva_relatorio_pagas(fields, usuario, mes, ano):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='rel_pagas', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='rel_pagas')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = RelatorioPagas.objects.update_or_create(
                empregado=empregado, importacao=importacao,
                defaults={
                    'nome': fields['nome'],
                    'cargo': fields['cargo'],
                    'hs_diurnas': fields['horas_diurnas'],
                    'valor_diurnas': fields['valor_diurnas'],
                    'hs_noturnas': fields['horas_noturnas'],
                    'valor_noturnas': fields['valor_noturnas'],
                    'total': fields['valor_total'],
                    'importado_por': usuario.username,
                    'importado_por_id': usuario.id,
                    'data_upload': datetime.now(),
                    'setor': fields['setor']
                })
            return document
    except ObjectDoesNotExist:
        pass


def salva_relatorio_entrada_saida(fields, usuario, mes, ano):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='rel_entrada_saida', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='rel_entrada_saida')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = RelatorioEntradaSaida.objects.update_or_create(
                empregado=empregado, importacao=importacao, data=str(fields['data']),
                defaults={
                    'nome': fields['nome'],
                    'cargo': fields['cargo'],
                    'escala': fields['escala'],
                    'entrada': fields['entrada'],
                    'saida': fields['saida'],
                    'horas_trabalhadas': fields['horas_trabalhadas'],
                    'horas_diurnas': fields['horas_diurnas'],
                    'horas_noturnas': fields['horas_noturnas'],
                    'importado_por': usuario.username,
                    'importado_por_id': usuario.id,
                    'data_upload': datetime.now(),
                    'setor': fields['setor']
                })
            return document
    except ObjectDoesNotExist:
        pass


def salva_relatorio_erros(fields, usuario, mes, ano, tipo):
    if tipo == 'solicitacao':
        Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='erros_solicitacao', defaults={
            'importado_por_id': usuario.id,
            'importado_por': usuario.username,
            'data_upload': datetime.now(),
        })
        importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='erros_solicitacao')
        try:
            empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
            if empregado:
                document = RelatorioErros.objects.update_or_create(
                    empregado=empregado, importacao=importacao, data=fields['data'],
                    defaults={
                        'nome': fields['nome'],
                        'escala': fields['escala'],
                        'entrada': '00:00',
                        'saida': '00:00',
                        'horas_trabalhadas': 0,
                        'horas_diurnas': 0,
                        'horas_noturnas': 0,
                        'importado_por': usuario.username,
                        'importado_por_id': usuario.id,
                        'data_upload': datetime.now(),
                        'tipo': tipo,
                    })
                return document
        except ObjectDoesNotExist:
            pass
    else:
        Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='erros_confirmacao', defaults={
            'importado_por_id': usuario.id,
            'importado_por': usuario.username,
            'data_upload': datetime.now(),
        })
        importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='erros_confirmacao')
        try:
            empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
            if empregado:
                document = RelatorioErros.objects.update_or_create(
                    empregado=empregado, importacao=importacao, data=fields['data'],
                    defaults={
                        'nome': fields['nome'],
                        'escala': fields['escala'],
                        'entrada': '00:00',
                        'saida': '00:00',
                        'horas_trabalhadas': 0,
                        'horas_diurnas': 0,
                        'horas_noturnas': 0,
                        'importado_por': usuario.username,
                        'importado_por_id': usuario.id,
                        'data_upload': datetime.now(),
                        'tipo': tipo,
                    })
                return document
        except ObjectDoesNotExist:
            pass


def salva_voltar_negativos(fields, usuario, mes, ano):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='voltar_negativos', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='voltar_negativos')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = VoltarNegativos.objects.update_or_create(
                empregado=empregado, importacao=importacao,
                defaults={
                    'nome': fields['nome'],
                    'dia1': fields['1'],
                    'dia2': fields['2'],
                    'dia3': fields['3'],
                    'dia4': fields['4'],
                    'dia5': fields['5'],
                    'dia6': fields['6'],
                    'dia7': fields['7'],
                    'dia8': fields['8'],
                    'dia9': fields['9'],
                    'dia10': fields['10'],
                    'dia11': fields['11'],
                    'dia12': fields['12'],
                    'dia13': fields['13'],
                    'dia14': fields['14'],
                    'dia15': fields['15'],
                    'dia16': fields['16'],
                    'dia17': fields['17'],
                    'dia18': fields['18'],
                    'dia19': fields['19'],
                    'dia20': fields['20'],
                    'dia21': fields['21'],
                    'dia22': fields['22'],
                    'dia23': fields['23'],
                    'dia24': fields['24'],
                    'dia25': fields['25'],
                    'dia26': fields['26'],
                    'dia27': fields['27'],
                    'dia28': fields['28'],
                    'dia29': fields['29'],
                    'dia30': fields['30'],
                    'dia31': fields['31'],
                    'importado_por': usuario.username,
                    'importado_por_id': usuario.id,
                    'data_upload': datetime.now(),
                })
            return document
    except ObjectDoesNotExist:
        pass
