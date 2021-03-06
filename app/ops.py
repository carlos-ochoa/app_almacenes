def calcular_total(billetes):
    billetes = billetes.split()
    return int(billetes[0]) * 20 + \
        int(billetes[1]) * 50 + \
            int(billetes[2]) * 100 + \
                int(billetes[3]) * 200 + \
                    int(billetes[4]) * 500 + int(billetes[5]) * 1000

def obtener_billetes(billetes):
    billetes = billetes.split()
    return billetes

def actualizar_balance(billetes_operacion, balance_actual, tipo):
    billetes_operacion = list(map(int,billetes_operacion.split()))
    balance_actual = list(map(int,balance_actual.split()))
    if tipo == 'entrada':
        balance_actual = list(map(lambda x,y : x + y, balance_actual, billetes_operacion))
    elif tipo == 'salida':
        balance_actual = list(map(lambda x,y : x - y, balance_actual, billetes_operacion))
    balance_actual = ' '.join(str(b) for b in balance_actual)
    return balance_actual

def verificar_balance(balance):
    balance_correcto = True
    balance = list(map(int,balance.split()))
    negativos = list(filter(lambda x : x < 0, balance))
    if len(negativos) > 0:
        balance_correcto = False
    return balance_correcto

def actualizar_balance_verificado(balance_anterior, billetes_nuevo, billetes_operacion, tipo):
    balance_anterior = list(map(int,balance_anterior.split()))
    billetes_nuevo = list(map(int,billetes_nuevo.split()))
    billetes_operacion = list(map(int,billetes_operacion.split()))
    mascara = list(map(lambda x,y : x != y, billetes_nuevo, billetes_operacion))
    for index,cambiar in enumerate(mascara):
        if cambiar:
            if tipo == 'entrada':
                balance_anterior[index] += billetes_nuevo[index]
            else:
                balance_anterior[index] -= billetes_nuevo[index]
    balance_actual = ' '.join(str(b) for b in balance_anterior)
    return balance_actual