import pandas as pd
from django.core.exceptions import ObjectDoesNotExist

from arruma_arquivos import arruma_rubricas_calculadas, arruma_carga_horaria
from empregados.dbchanges import salva_empregado, salva_carga_horaria


def importa_empregados(request):
    empregados_a_mostrar = []
    salarios, insalubridades = '', ''
    try:
        if request.method == "POST":
            planilha_salarios = request.FILES.get("salarios")
            planilha_insalubridades = request.FILES.get("insalubridade")
            planilha_carga_horaria = request.FILES.get("carga_horaria")
            data = request.POST.get('data')
            ano, mes = str(data).split('-')

            if planilha_salarios != '' and planilha_salarios is not None:
                salarios = arruma_rubricas_calculadas(planilha_salarios)
                if str(salarios) == 'Erro':
                    return 'Erro'
                salarios = salarios.rename(columns={'valor': 'salario'})
            if planilha_insalubridades != '' and planilha_insalubridades is not None:
                insalubridades = arruma_rubricas_calculadas(planilha_insalubridades)
                if str(insalubridades) == 'Erro':
                    return 'Erro'
                insalubridades = insalubridades.rename(columns={'valor': 'insalubridade'})

            empregados = pd.merge(salarios, insalubridades, on=["matricula", "nome"], how="left")
            empregados = empregados.dropna(subset='nome')
            empregados.salario = empregados.salario.astype(float)
            empregados.insalubridade = empregados.insalubridade.astype(float)
            empregados = empregados.fillna(0.00)

            usuario = request.user

            for i, j in empregados.iterrows():
                empregado = j
                document = salva_empregado(empregado, mes, ano, usuario)
                empregados_a_mostrar.append(document)

            if planilha_carga_horaria != '' and planilha_carga_horaria is not None:
                carga_horaria = arruma_carga_horaria(planilha_carga_horaria, mes, ano)
                if str(carga_horaria) == 'Erro':
                    return 'Erro'

                for i, j in carga_horaria.iterrows():
                    salva_carga_horaria(j, mes, ano, usuario)

            if len(empregados_a_mostrar) == 0:
                return "arquivo_vazio"
            else:
                resposta = "OK"
                return resposta
    except IndexError:
        resposta = "dados_inválidos"
        return resposta
    except ObjectDoesNotExist:
        resposta = "arquivo_vazio"
        return resposta

