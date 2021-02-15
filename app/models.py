from datetime import datetime
from app import db,login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Operacion(db.Model):
    __tablename__ = 'operaciones'

    id = db.Column(db.Integer, primary_key = True)
    concepto = db.Column(db.String(120))
    fecha = db.Column(db.Date, index = True, default = datetime.today)
    total = db.Column(db.Float)
    billetes = db.Column(db.String(18))
    monedas = db.Column(db.Float, default = 0.0)
    tipo = db.Column(db.String(7), index = True)

    def __repr__(self):
        return f'Operacion de tipo {self.tipo} con total {self.total} y secuencia {self.billetes}, en fecha {self.fecha}'

class Resumen(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fecha = db.Column(db.Date, index = True, default = datetime.today)
    cambio = db.Column(db.Float, default = 0.0)
    total = db.Column(db.Float, default = 0.0)
    balance_billetes = db.Column(db.String(60), default = '0 0 0 0 0 0')
    caja_entregada = db.Column(db.Boolean, default = False)

    def __repr__(self):
        return f'Resumen de {self.fecha} con total {self.total} y cambio {self.cambio}'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(20), unique = True)
    passwd_hash = db.Column(db.String(128))
    ultimo_login_diario = db.Column(db.String(10))

    def set_passwd(self, password):
        self.passwd_hash = generate_password_hash(password)

    def check_passwd(self, password):
        return check_password_hash(self.passwd_hash,password)

    def __repr__(self):
        return f'User {self.nombre}'