from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DecimalField, DateField
from wtforms.widgets.html5 import NumberInput, DateInput
from wtforms.validators import DataRequired, Optional

class OperacionForm(FlaskForm):
    concepto = StringField('Concepto de operación', validators = [DataRequired()])
    billetes_20 = IntegerField('Billetes de 20 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_50 = IntegerField('Billetes de 50 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_100 = IntegerField('Billetes de 100 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_200 = IntegerField('Billetes de 200 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_500 = IntegerField('Billetes de 500 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_1000 = IntegerField('Billetes de 1000 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    submit = SubmitField('Guardar')

class OperacionSalidaForm(FlaskForm):
    concepto = StringField('Concepto de operación', validators = [DataRequired()])
    total = DecimalField('Total de la salida', validators = [DataRequired()])
    billetes_20 = IntegerField('Billetes de 20 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_50 = IntegerField('Billetes de 50 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_100 = IntegerField('Billetes de 100 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_200 = IntegerField('Billetes de 200 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_500 = IntegerField('Billetes de 500 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_1000 = IntegerField('Billetes de 1000 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    submit = SubmitField('Crear')

class CambioForm(FlaskForm):
    billetes_20 = IntegerField('Billetes de 20 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_50 = IntegerField('Billetes de 50 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_100 = IntegerField('Billetes de 100 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_200 = IntegerField('Billetes de 200 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_500 = IntegerField('Billetes de 500 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    billetes_1000 = IntegerField('Billetes de 1000 usados', validators = [Optional()], default = 0, widget = NumberInput(min = 0))
    submit = SubmitField('Cambiar')

class BusquedaFechaForm(FlaskForm):
    fecha = DateField('Fecha', validators=[DataRequired()], widget = DateInput())
    submit = SubmitField('Buscar')

class BusquedaSalidaForm(FlaskForm):
    concepto = StringField('Concepto o nombre', validators=[DataRequired()])
    submit = SubmitField('Buscar')