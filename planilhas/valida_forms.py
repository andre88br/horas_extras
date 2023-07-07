

def ValidaFormDate(formDate):
    mes = formDate.data['data_month']
    ano = formDate.data['data_year']

    return int(mes), int(ano)


def ValidaFormTipo(formTipo):
    if formTipo.is_valid():
        tipo = formTipo.cleaned_data['tipo']

        return tipo


def ValidaFormDivisao(formDiv):
    if formDiv.is_valid():
        divisao = formDiv.cleaned_data['divisao']

        return divisao


def ValidaFormSetor(formSetor, divisao):
    if formSetor.is_valid():
        if str(divisao).lower() == 'assistencial':
            setor = formSetor.cleaned_data['setor']
        else:
            setor = formSetor.cleaned_data['setor2']
        return setor


def ValidaFormSetor2(formSetor):
    if formSetor.is_valid():
        setor = formSetor.cleaned_data['setor']
        return setor
