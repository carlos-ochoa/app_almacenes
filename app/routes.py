from flask import render_template, redirect, url_for, request, flash
from app import app
from app import db
from app.forms import OperacionForm
from app.models import Operacion, Resumen
from app.ops import calcular_total


@app.route('/operacion/<string:tipo>', methods = ['GET','POST'])
def operacion(tipo):
    form = OperacionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            billetes_str =  f'{form.billetes_20.data} {form.billetes_50.data} {form.billetes_100.data} \
                {form.billetes_200.data} {form.billetes_500.data} {form.billetes_1000.data}'
            total = calcular_total(billetes_str)
            o = Operacion(concepto = form.concepto.data, billetes = billetes_str, total = total, tipo = tipo)
            db.session.add(o)
            db.session.commit()
        else:
            flash('Ha ocurrido un error en la alta de la operación')
    return render_template('operacion.html',title = 'Operaciones', form = form, tipo = tipo)

@app.route('/resumen')
def resumen():
    return "Hola mundo"

@app.route('/caja')
def caja():
    return "caja"