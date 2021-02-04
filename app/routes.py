from flask import render_template, redirect, url_for, request, flash
from datetime import datetime
from app import app
from app import db
from app.forms import OperacionForm, OperacionUpdateForm
from app.models import Operacion, Resumen
from app.ops import calcular_total, obtener_billetes


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
            return redirect(url_for('caja'))
        else:
            flash('Ha ocurrido un error en la alta de la operación')
    return render_template('operacion.html',title = 'Operaciones', form = form, tipo = tipo)

@app.route('/resumen')
def resumen():
    return "Hola mundo"

@app.route('/caja')
def caja():
    fecha = datetime.today().strftime('%Y-%m-%d')
    entradas = Operacion.query.filter_by(tipo = 'entrada', fecha = fecha).all()
    salidas = Operacion.query.filter_by(tipo = 'salida', fecha = fecha).all()
    return render_template('caja.html', saldo_total = 0.0, cambio = 0.0, entradas = entradas, salidas = salidas)

@app.route('/ver/<int:id>', methods = ['GET','POST'])
def ver(id):
    operacion = Operacion.query.filter_by(id = id).first()
    billetes = obtener_billetes(operacion.billetes)
    if request.method == 'POST':
        form = OperacionForm()
        billetes_str =  f'{form.billetes_20.data} {form.billetes_50.data} {form.billetes_100.data} \
                {form.billetes_200.data} {form.billetes_500.data} {form.billetes_1000.data}'
        operacion.concepto = form.concepto.data
        operacion.billetes = billetes_str
        operacion.total = calcular_total(billetes_str)
        db.session.commit()
        redirect(url_for('caja'))
    if request.method == 'GET':
        form = OperacionForm(concepto = operacion.concepto, billetes_20 = billetes[0], \
            billetes_50 = billetes[1], billetes_100 = billetes[2], \
            billetes_200 = billetes[3], billetes_500 = billetes[4], \
            billetes_1000 = billetes[5])
    return render_template('ver.html', operacion = operacion, form = form)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    operacion = Operacion.query.filter_by(id = id).first()
    db.session.delete(operacion)
    db.session.commit()
    return redirect(url_for('caja'))