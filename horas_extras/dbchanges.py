from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from .models import Confirmacao, Frequencia, Solicitacao, BancoMes, BancoTotal
from empregados.models import Empregado, Importacoes


def salva_confirmacao(fields, usuario, mes, ano, nao_cadastrados):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='Confirmação', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='Confirmação')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = Confirmacao.objects.update_or_create(
                empregado=empregado, importacao=importacao, setor=str(fields['setor']).upper(), defaults={
                    'nome': str(fields['nome']).upper(),
                    'cargo': str(fields['cargo']).upper(),
                    'dia1': str(fields[1]).upper(),
                    'dia2': str(fields[2]).upper(),
                    'dia3': str(fields[3]).upper(),
                    'dia4': str(fields[4]).upper(),
                    'dia5': str(fields[5]).upper(),
                    'dia6': str(fields[6]).upper(),
                    'dia7': str(fields[7]).upper(),
                    'dia8': str(fields[8]).upper(),
                    'dia9': str(fields[9]).upper(),
                    'dia10': str(fields[10]).upper(),
                    'dia11': str(fields[11]).upper(),
                    'dia12': str(fields[12]).upper(),
                    'dia13': str(fields[13]).upper(),
                    'dia14': str(fields[14]).upper(),
                    'dia15': str(fields[15]).upper(),
                    'dia16': str(fields[16]).upper(),
                    'dia17': str(fields[17]).upper(),
                    'dia18': str(fields[18]).upper(),
                    'dia19': str(fields[19]).upper(),
                    'dia20': str(fields[20]).upper(),
                    'dia21': str(fields[21]).upper(),
                    'dia22': str(fields[22]).upper(),
                    'dia23': str(fields[23]).upper(),
                    'dia24': str(fields[24]).upper(),
                    'dia25': str(fields[25]).upper(),
                    'dia26': str(fields[26]).upper(),
                    'dia27': str(fields[27]).upper(),
                    'dia28': str(fields[28]).upper(),
                    'dia29': str(fields[29]).upper(),
                    'dia30': str(fields[30]).upper(),
                    'dia31': str(fields[31]).upper(),
                    'data_upload': datetime.now(),
                })
            return document, nao_cadastrados
    except ObjectDoesNotExist:
        document = {}
        nao_cadastrados.append({'matricula': fields['matricula'], 'nome': fields['nome']})
        return document, nao_cadastrados


def salva_solicitacao(fields, usuario, mes, ano, nao_cadastrados):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='Solicitação', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='Solicitação')
    try:
        print(fields)
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = Solicitacao.objects.update_or_create(
                empregado=empregado, importacao=importacao, setor=str(fields['setor']).upper(), defaults={
                    'nome': str(fields['nome']).upper(),
                    'cargo': str(fields['cargo']).upper(),
                    'dia1': str(fields[1]).upper(),
                    'dia2': str(fields[2]).upper(),
                    'dia3': str(fields[3]).upper(),
                    'dia4': str(fields[4]).upper(),
                    'dia5': str(fields[5]).upper(),
                    'dia6': str(fields[6]).upper(),
                    'dia7': str(fields[7]).upper(),
                    'dia8': str(fields[8]).upper(),
                    'dia9': str(fields[9]).upper(),
                    'dia10': str(fields[10]).upper(),
                    'dia11': str(fields[11]).upper(),
                    'dia12': str(fields[12]).upper(),
                    'dia13': str(fields[13]).upper(),
                    'dia14': str(fields[14]).upper(),
                    'dia15': str(fields[15]).upper(),
                    'dia16': str(fields[16]).upper(),
                    'dia17': str(fields[17]).upper(),
                    'dia18': str(fields[18]).upper(),
                    'dia19': str(fields[19]).upper(),
                    'dia20': str(fields[20]).upper(),
                    'dia21': str(fields[21]).upper(),
                    'dia22': str(fields[22]).upper(),
                    'dia23': str(fields[23]).upper(),
                    'dia24': str(fields[24]).upper(),
                    'dia25': str(fields[25]).upper(),
                    'dia26': str(fields[26]).upper(),
                    'dia27': str(fields[27]).upper(),
                    'dia28': str(fields[28]).upper(),
                    'dia29': str(fields[29]).upper(),
                    'dia30': str(fields[30]).upper(),
                    'dia31': str(fields[31]).upper(),
                    'data_upload': datetime.now(),
                })
            return document, nao_cadastrados
    except ObjectDoesNotExist:
        document = {}
        nao_cadastrados.append({'matricula': fields['matricula'], 'nome': fields['nome']})
        return document, nao_cadastrados


def salva_frequencia(fields, usuario, mes, ano):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='frequencia', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='frequencia')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = Frequencia.objects.update_or_create(
                empregado=empregado, importacao=importacao,
                data=fields['data'], defaults={
                    'nome': str(fields['nome']).upper(),
                    'batida1': fields['batida1'],
                    'batida2': fields['batida2'],
                    'batida3': fields['batida3'],
                    'batida4': fields['batida4'],
                    'batida5': fields['batida5'],
                    'batida6': fields['batida6'],
                    'escala': str(fields['escala']).upper(),
                    'data_upload': datetime.now(),
                    'importado_por': usuario.username,
                    'importado_por_id': usuario.id,
                })
            return document
    except ObjectDoesNotExist:
        pass


def salva_banco_mes(fields, usuario, mes, ano):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='banco_mes', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='banco_mes')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = BancoMes.objects.update_or_create(empregado=empregado, importacao=importacao, defaults={
                'nome': str(fields['nome']).upper(),
                'saldo': fields['saldo'],
                'saldo_decimal': fields['saldo_decimal'],
                'data_upload': datetime.now(),
                'importado_por': usuario.username,
                'importado_por_id': usuario.id,
            })
            return document
    except ObjectDoesNotExist:
        pass


def salva_banco_total(fields, usuario, mes, ano):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='banco_total', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='banco_total')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = BancoTotal.objects.update_or_create(empregado=empregado, importacao=importacao, defaults={
                'nome': str(fields['nome']).upper(),
                'saldo': fields['saldo_banco'],
                'saldo_decimal': fields['saldo_decimal'],
                'data_upload': datetime.now(),
                'importado_por': usuario.username,
                'importado_por_id': usuario.id,
            })
            return document
    except ObjectDoesNotExist:
        pass
