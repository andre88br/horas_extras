from datetime import datetime, date
import locale

locale.setlocale(locale.LC_MONETARY, "pt-BR.UTF-8")


def formata_data_hora(data_hora):
    if "T" in str(data_hora):
        data = data_hora.split("T")[0]
        dia = int(data.split("-")[2])
        mes = int(data.split("-")[1])
        ano = int(data.split("-")[0])
        hora = data_hora.split("T")[1]
        horas = int(hora.split(":")[0])
        minutos = int(hora.split(":")[1])
        segundos = int(hora.split(":")[2])
        data_formatada = datetime(ano, mes, dia, horas, minutos, segundos)
    else:
        data = data_hora.split(" ")[0]
        dia = int(data.split("-")[2])
        mes = int(data.split("-")[1])
        ano = int(data.split("-")[0])
        hora = data_hora.split(" ")[1]
        horas = int(hora.split(":")[0])
        minutos = int(hora.split(":")[1])
        segundos = int(hora.split(":")[2][0:2])
        data_formatada = datetime(ano, mes, dia, horas, minutos, segundos)
    return data_formatada


def formata_data(data):
    data = data.split("T")[0]
    dia = int(data.split("-")[2])
    mes = int(data.split("-")[1])
    ano = int(data.split("-")[0])
    return date(ano, mes, dia)


def pega_data(data_hora):
    if "T" in str(data_hora):
        data = str(data_hora).split("T")[0]
        dia = int(data.split("-")[2])
        mes = int(data.split("-")[1])
        ano = int(data.split("-")[0])
        data_formatada = date(ano, mes, dia)
    elif " " in str(data_hora):
        data = str(data_hora).split(" ")[0]
        dia = int(data.split("-")[2])
        mes = int(data.split("-")[1])
        ano = int(data.split("-")[0])
        data_formatada = date(ano, mes, dia)
    else:
        data = str(data_hora).split("-")
        dia = int(data[2])
        mes = int(data[1])
        ano = int(data[0])
        data_formatada = date(ano, mes, dia)

    return data_formatada.strftime("%d/%m/%Y")


def pega_data_hora(data_hora):
    if "T" in str(data_hora):
        data = str(data_hora).split("T")[0]
        dia = int(data.split("-")[2])
        mes = int(data.split("-")[1])
        ano = int(data.split("-")[0])
        hora = data_hora.split("T")[1]
        horas = int(hora.split(":")[0])
        minutos = int(hora.split(":")[1])
        segundos = int(hora.split(":")[2][0:2])
        data_formatada = datetime(ano, mes, dia, horas, minutos, segundos)
    else:
        data = str(data_hora).split(" ")[0]
        dia = int(data.split("-")[2])
        mes = int(data.split("-")[1])
        ano = int(data.split("-")[0])
        hora = data_hora.split(" ")[1]
        horas = int(hora.split(":")[0])
        minutos = int(hora.split(":")[1])
        segundos = int(hora.split(":")[2][0:2])
        data_formatada = datetime(ano, mes, dia, horas, minutos, segundos)

    return data_formatada.strftime("%d/%m/%Y %H:%M:%S")


def valida_data(data_transacoes, fields):
    if (data_transacoes != "") and (
        str(pega_data(data_transacoes)) == str(pega_data(fields))
    ):
        return True
    else:
        return False


def transforma_mes_ano(data):
    data = data.split("-")
    mes = data[1]
    ano = data[0]
    data = f"{mes}/{ano}"
    return data


def valida_vazio(fields):
    if (
        str(fields[0]).strip() == ""
        or str(fields[2]).strip() == ""
        or str(fields[3]).strip() == ""
        or str(fields[4]).strip() == ""
        or str(fields[5]).strip() == ""
        or str(fields[6]).strip() == ""
        or str(fields[1]).strip() == ""
        or str(fields[7]).strip() == ""
    ):
        return True
    else:
        return False


def transforma_data_contrario(data):
    data = datetime.strptime(data, '%d/%m/%Y').date().strftime('%Y-%m-%d')
    return data


def transforma_decimal(numero):
    numero = f'{numero:.2f}'
    return numero
