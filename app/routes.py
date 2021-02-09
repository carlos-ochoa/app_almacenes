from flask import render_template, redirect, url_for, request, flash
from datetime import datetime, timedelta
from app import app
from app import db
from app.forms import OperacionForm, OperacionSalidaForm, CambioForm, BusquedaFechaForm, BusquedaSalidaForm
from app.models import Operacion, Resumen
from app.ops import calcular_total, obtener_billetes, actualizar_balance, verificar_balance


@app.route('/operacion/entrada', methods = ['GET','POST'])
def operacion():
    form = OperacionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            billetes_str =  f'{form.billetes_20.data} {form.billetes_50.data} {form.billetes_100.data} \
                {form.billetes_200.data} {form.billetes_500.data} {form.billetes_1000.data}'
            total = calcular_total(billetes_str)
            o = Operacion(concepto = form.concepto.data, billetes = billetes_str, total = total, tipo = 'entrada')
            db.session.add(o)
            fecha = datetime.today().strftime('%Y-%m-%d')
            r = Resumen.query.filter_by(fecha = fecha).first()   
            if r is not None:
                r.total += total
                r.balance_billetes = actualizar_balance(billetes_str, r.balance_billetes, tipo = 'entrada')
            else:
                r = Resumen(total = total, cambio = 0.0)
                r.balance_billetes = actualizar_balance(billetes_str, '0 0 0 0 0 0', tipo = 'entrada')
                db.session.add(r)
            db.session.commit()
            return redirect(url_for('caja'))
        else:
            flash('Ha ocurrido un error en la alta de la operación')
    return render_template('operacion.html',title = 'Operaciones', form = form, tipo = 'entrada')

@app.route('/operacion/salida', methods = ['GET','POST'])
def operacion_salida():
    form = OperacionSalidaForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            billetes_str =  f'{form.billetes_20.data} {form.billetes_50.data} {form.billetes_100.data} \
                {form.billetes_200.data} {form.billetes_500.data} {form.billetes_1000.data}'
            total = form.total.data
            o = Operacion(concepto = form.concepto.data, billetes = billetes_str, total = total, tipo = 'salida')
            db.session.add(o)
            fecha = datetime.today().strftime('%Y-%m-%d')
            r = Resumen.query.filter_by(fecha = fecha).first()
            cambio_parcial = calcular_total(billetes_str) - float(total)    
            if r is not None:
                balance_nuevo = actualizar_balance(billetes_str, r.balance_billetes, tipo = 'salida')
                if float(total) > r.total or not verificar_balance(balance_nuevo):
                    flash('El total de la salida no puede superar al dinero en caja')
                    return redirect(url_for('caja'))
                else:
                    r.total -= float(total)
                    r.cambio += cambio_parcial
                    r.balance_billetes = balance_nuevo
            else:
                balance_nuevo = actualizar_balance(billetes_str, r.balance_billetes, tipo = 'salida')
                if float(total) > r.total or not verificar_balance(balance_nuevo):
                    flash('El total de la salida no puede superar al dinero en caja')
                    return redirect(url_for('caja'))
                else:
                    r = Resumen(total = total, cambio = cambio_parcial)
                    r.balance_billetes = balance_nuevo
                    db.session.add(r)
            db.session.commit()
            return redirect(url_for('caja'))
        else:
            flash('Ha ocurrido un error en la alta de la operación')
    return render_template('operacion.html',title = 'Operaciones', form = form, tipo = 'salida')

@app.route('/resumen')
def resumen():
    return "Hola mundo"

@app.route('/')
@app.route('/caja')
def caja():
    denominaciones = ['20','50','100','200','500','1000']
    fecha = datetime.today().strftime('%Y-%m-%d')
    ayer = (datetime.today() - timedelta(days = 1)).strftime('%Y-%m-%d')
    entradas = Operacion.query.filter_by(tipo = 'entrada', fecha = fecha).all()
    salidas = Operacion.query.filter_by(tipo = 'salida', fecha = fecha).all()
    r = Resumen.query.filter_by(fecha = fecha).first()
    r_ayer = Resumen.query.filter_by(fecha = ayer).first()
    if r is not None:
        balance = dict(zip(denominaciones,r.balance_billetes.split()))
        total_billetes = calcular_total(r.balance_billetes)
        saldo_total = r.total
        if r_ayer is not None:
            cambio = r_ayer.cambio + r.cambio    
        else:
            cambio = r.cambio
    else:
        balance = dict(zip(denominaciones,'0 0 0 0 0 0'.split()))
        total_billetes = 0.0
        saldo_total = 0.0
        if r_ayer is None:
            cambio = 0.0
        else:
            cambio = r_ayer.cambio
    return render_template('caja.html', saldo_total = saldo_total, cambio = cambio, entradas = entradas, salidas = salidas, balance = balance, total_billetes = total_billetes)

@app.route('/cambiar/', methods = ['GET','POST'])
def cambiar():
    cambio_total = request.args.get('cambio_total')
    form = CambioForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            billetes_str =  f'{form.billetes_20.data} {form.billetes_50.data} {form.billetes_100.data} \
                {form.billetes_200.data} {form.billetes_500.data} {form.billetes_1000.data}'
            total = calcular_total(billetes_str)
            fecha = datetime.today().strftime('%Y-%m-%d')
            r = Resumen.query.filter_by(fecha = fecha).first()
            if r is None:
                flash('No hay registros monetarios')
                return redirect(url_for('caja'))
            if total > cambio_total or r.cambio == 0.0:
                flash('La cantidad a cambiar no puede ser superior al cambio en monedas existente')
                return redirect(url_for('cambiar'))
            balance_nuevo = actualizar_balance(billetes_str, r.balance_billetes ,tipo = 'entrada')
            balance_valido = verificar_balance(balance_nuevo)
            if balance_valido:
                r.balance_billetes = balance_nuevo
                r.cambio -= total
                r.total += total
            db.session.commit()
            return redirect(url_for('caja'))
    return render_template('cambio.html', form = form)

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

@app.route('/buscar_por_fecha', methods = ['GET','POST'])
def buscarFecha():
    form = BusquedaFechaForm()
    r, entradas, salidas = None, [], []
    if request.method == 'POST':
        if form.validate_on_submit():
            denominaciones = ['20','50','100','200','500','1000']
            r = Resumen.query.filter_by(fecha = form.fecha.data).first()
            entradas = Operacion.query.filter_by(fecha = form.fecha.data, tipo = 'entrada').all()
            salidas = Operacion.query.filter_by(fecha = form.fecha.data, tipo = 'salida').all()
    return render_template('busquedaFecha.html', form = form, r = r, entradas = entradas, salidas = salidas)

@app.route('/buscar_por_concepto', methods = ['GET','POST'])
def buscarSalida():
    form = BusquedaSalidaForm()
    salidas = []
    if request.method == 'POST':
        if form.validate_on_submit():
            concepto = form.concepto.data
            salidas = Operacion.query.filter((Operacion.concepto.contains(concepto)) & (Operacion.tipo == 'salida')).all()
    return render_template('busquedaSalida.html', form = form, salidas = salidas)

        
          