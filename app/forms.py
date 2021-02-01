from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, Optional

class OperacionForm(FlaskForm):
    concepto = StringField('Concepto de operación', validators = [DataRequired()])
    billetes_20 = IntegerField('Billetes de 20 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_50 = IntegerField('Billetes de 50 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_100 = IntegerField('Billetes de 100 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_200 = IntegerField('Billetes de 200 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_500 = IntegerField('Billetes de 500 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_1000 = IntegerField('Billetes de 1000 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    submit = SubmitField('Crear')
