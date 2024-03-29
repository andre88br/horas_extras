from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from empregados.models import Importacoes
from .models import PlanilhaConfirmacao, PlanilhaSolicitacao, ListaEmpregados


def salva_solicitacao_planilha(fields, usuario, mes, ano, nao_cadastrados, setor):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='PlanilhaSolicitação', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='PlanilhaSolicitação')
    try:
        empregado = ListaEmpregados.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = PlanilhaSolicitacao.objects.update_or_create(
                empregado=empregado, importacao=importacao, setor=str(setor).upper(), defaults={
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


def salva_confirmacao_planilha(fields, usuario, mes, ano, nao_cadastrados, setor):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='PlanilhaConfirmação', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='PlanilhaConfirmação')
    try:
        empregado = ListaEmpregados.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = PlanilhaConfirmacao.objects.update_or_create(
                empregado=empregado, importacao=importacao, setor=str(setor).upper(), defaults={
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


def salva_listaempregados(empregado, mes, ano, usuario):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='listaempregados', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='listaempregados')

    document = ListaEmpregados.objects.update_or_create(matricula=empregado[0], importacao=importacao, defaults={
        'matricula': empregado['matricula'],
        'nome': empregado['nome'],
        'cargo': empregado['cargo'],
        'data_atualizacao': datetime.now(),
        'mes': mes,
        'ano': ano,
    })
    return document
