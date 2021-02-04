from datetime import datetime
from app import db

class Operacion(db.Model):
    __tablename__ = 'operaciones'

    id = db.Column(db.Integer, primary_key = True)
    concepto = db.Column(db.String(120))
    fecha = db.Column(db.Date, index = True, default = datetime.today)
    total = db.Column(db.Float)
    billetes = db.Column(db.String(18))
    tipo = db.Column(db.String(7), index = True)

    def __repr__(self):
        return f'Operacion de tipo {self.tipo} con total {self.total} y secuencia {self.billetes}, en fecha {self.fecha}'

class Resumen(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fecha = db.Column(db.Date, index = True, default = datetime.today)
    cambio = db.Column(db.Float)
    total = db.Column(db.Float)

    def __repr__(self):
        return f'Resumen de {self.fecha} con total {self.total} y cambio {self.cambio}'