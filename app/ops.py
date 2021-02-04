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