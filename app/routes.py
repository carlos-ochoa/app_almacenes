from flask import render_template, redirect, url_for, request, flash
from datetime import datetime, timedelta
from app import app
from app import db
from app.forms import OperacionForm, OperacionSalidaForm, CambioForm, BusquedaFechaForm, BusquedaSalidaForm, LoginForm
from app.models import Operacion, Resumen, User
from app.ops import calcular_total, obtener_billetes, actualizar_balance, verificar_balance, actualizar_balance_verificado
from flask_login import current_user,login_user, logout_user, login_required
from werkzeug.urls import url_parse

@app.route('/operacion/entrada', methods = ['GET','POST'])
@login_required
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
@login_required
def operacion_salida():
    denominaciones = ['20','50','100','200','500','1000']
    info_cambio = 0.0
    balance_impresion = {}
    form = OperacionSalidaForm()
    if request.method == 'GET':
        fecha = datetime.today().strftime('%Y-%m-%d')
        r = Resumen.query.filter_by(fecha = fecha).first()
        if r:
            info_cambio = r.cambio 
            balance_impresion = dict(zip(denominaciones, r.balance_billetes.split()))
        else:
            balance_impresion = dict(zip(denominaciones, '0 0 0 0 0 0'.split()))
    if request.method == 'POST':
        if form.validate_on_submit():
            monedas = form.monedas.data
            billetes_str =  f'{form.billetes_20.data} {form.billetes_50.data} {form.billetes_100.data} \
                {form.billetes_200.data} {form.billetes_500.data} {form.billetes_1000.data}'
            total = form.total.data
            o = Operacion(concepto = form.concepto.data, billetes = billetes_str, total = total,monedas = monedas, tipo = 'salida')
            db.session.add(o)
            fecha = datetime.today().strftime('%Y-%m-%d')
            r = Resumen.query.filter_by(fecha = fecha).first()
            cambio_parcial = calcular_total(billetes_str) + float(monedas) - float(total)
            total_salido_caja = calcular_total(billetes_str) + float(monedas)
            if float(monedas) > r.cambio:
                flash('No se puede pagar con monedas si no hay cambio en monedas registrado')
                return redirect(url_for('operacion_salida'))
            if float(total) > total_salido_caja:
                flash('Los billetes y monedas no alcanzan para realizar la salida')
                return redirect(url_for('operacion_salida'))    
            if r is not None:
                balance_nuevo = actualizar_balance(billetes_str, r.balance_billetes, tipo = 'salida')
                if float(total) > r.total or not verificar_balance(balance_nuevo):
                    flash('El total de la salida no puede superar al dinero en caja')
                    return redirect(url_for('operacion_salida'))
                else:
                    r.total -= float(total)
                    r.cambio += cambio_parcial - float(monedas)
                    r.balance_billetes = balance_nuevo
            else:
                if float(total) > r.total or not verificar_balance(balance_nuevo):
                    flash('El total de la salida no puede superar al dinero en caja')
                    return redirect(url_for('operacion_salida'))
                else:
                    r = Resumen(total = total, cambio = cambio_parcial - float(monedas))
                    balance_nuevo = actualizar_balance(billetes_str, r.balance_billetes, tipo = 'salida')
                    r.balance_billetes = balance_nuevo
                    db.session.add(r)
            db.session.commit()
            return redirect(url_for('caja'))
        else:
            flash('Ha ocurrido un error en la alta de la operación')
    return render_template('operacion.html',title = 'Operaciones', form = form, tipo = 'salida', balance = balance_impresion, info_cambio = info_cambio)

@app.route('/')
@app.route('/caja')
@login_required
def caja():
    denominaciones = ['20','50','100','200','500','1000']
    fecha = datetime.today().strftime('%Y-%m-%d')
    ayer = (datetime.today() - timedelta(days = 1)).strftime('%Y-%m-%d')
    entradas = Operacion.query.filter_by(tipo = 'entrada', fecha = fecha).all()
    salidas = Operacion.query.filter_by(tipo = 'salida', fecha = fecha).all()
    r = Resumen.query.filter_by(fecha = fecha).first()
    r_ayer = Resumen.query.filter_by(fecha = ayer).first()
    cambios = Operacion.query.filter_by(fecha = fecha, tipo = 'cambio').all()
    if len(cambios) == 0:
        cambios = None
    if r is not None:
        balance = dict(zip(denominaciones,r.balance_billetes.split()))
        total_billetes = calcular_total(r.balance_billetes)
        saldo_total = r.total
        cambio = r.cambio
    else:
        r = Resumen()
        db.session.add(r)
        if r_ayer is None:
            balance = dict(zip(denominaciones,'0 0 0 0 0 0'.split()))
            total_billetes = 0.0
            saldo_total = 0.0
            cambio = 0.0
        else:
            r.total = r_ayer.total
            r.cambio = r_ayer.cambio
            r.balance_billetes = r_ayer.balance_billetes
            r.caja_actualizada = True
            total_billetes = calcular_total(r.balance_billetes)
               
            cambio = r.cambio
            total_billetes = calcular_total(r.balance_billetes)
            saldo_total = total_billetes + cambio
            balance = dict(zip(denominaciones,r.balance_billetes.split()))
    db.session.commit()
    return render_template('caja.html', saldo_total = saldo_total, cambio = cambio, entradas = entradas, salidas = salidas, balance = balance, total_billetes = total_billetes, \
        cambios = cambios)

@app.route('/cambiar/', methods = ['GET','POST'])
@login_required
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
            if total > float(cambio_total) or r.cambio == 0.0:
                flash('La cantidad a cambiar no puede ser superior al cambio en monedas existente')
                return redirect(url_for('cambiar', cambio_total = cambio_total))
            balance_nuevo = actualizar_balance(billetes_str, r.balance_billetes ,tipo = 'entrada')
            balance_valido = verificar_balance(balance_nuevo)
            if balance_valido:
                r.balance_billetes = balance_nuevo
                r.cambio -= total
                o = Operacion(concepto = 'Cambio de monedas', total = total, billetes = billetes_str, tipo = 'cambio')
                db.session.add(o)
            db.session.commit()
            return redirect(url_for('caja', actualizar_valores_caja = False))
    return render_template('cambio.html', form = form)

@app.route('/ver', methods = ['GET','POST'])
@login_required
def ver():
    id = request.args.get('id')
    tipo = request.args.get('tipo')
    operacion = Operacion.query.filter_by(id = id).first()
    billetes = obtener_billetes(operacion.billetes)
    if request.method == 'POST':
        form = OperacionForm()
        if form.validate_on_submit():
            fecha = datetime.today().strftime('%Y-%m-%d')
            r = Resumen.query.filter_by(fecha = fecha).first()
            billetes_str =  f'{form.billetes_20.data} {form.billetes_50.data} {form.billetes_100.data} \
                    {form.billetes_200.data} {form.billetes_500.data} {form.billetes_1000.data}'
            balance_final = actualizar_balance_verificado(r.balance_billetes, billetes_str, operacion.billetes, tipo)
            balance_valido = verificar_balance(balance_final)
            if balance_valido:
                operacion.concepto = form.concepto.data
                operacion.billetes = billetes_str
                if tipo == 'salida':
                    operacion.monedas = form.monedas.data
                    operacion.total = calcular_total(billetes_str) + float(form.monedas.data)
                    r.cambio += float(form.monedas.data)
                else:
                    operacion.total = calcular_total(billetes_str)
                r.balance_billetes = balance_final
                r.total = calcular_total(r.balance_billetes) + r.cambio
                db.session.commit()
            else:
                flash('Balance de billetes no válido')
            return redirect(url_for('caja'))
    if request.method == 'GET':
        if tipo == 'entrada':
            form = OperacionForm(concepto = operacion.concepto, billetes_20 = billetes[0], \
                billetes_50 = billetes[1], billetes_100 = billetes[2], \
                billetes_200 = billetes[3], billetes_500 = billetes[4], \
                billetes_1000 = billetes[5])
        elif tipo == 'salida':
            form = OperacionSalidaForm(concepto = operacion.concepto, total = operacion.total, \
                monedas = operacion.monedas, billetes_20 = billetes[0], \
                billetes_50 = billetes[1], billetes_100 = billetes[2], \
                billetes_200 = billetes[3], billetes_500 = billetes[4], \
                billetes_1000 = billetes[5])
    return render_template('ver.html', operacion = operacion, form = form)

@app.route('/eliminar')
@login_required
def eliminar():
    id = request.args.get('id')
    tipo = request.args.get('tipo')
    fecha = datetime.today().strftime('%Y-%m-%d')
    operacion = Operacion.query.filter_by(id = id).first()
    r = Resumen.query.filter_by(fecha = fecha).first()
    tipo_operacion = 'salida' if tipo == 'entrada' else 'entrada'
    if tipo == 'salida':
        r.cambio += operacion.monedas
    r.balance_billetes = actualizar_balance(operacion.billetes, r.balance_billetes, tipo = tipo_operacion)
    r.total = calcular_total(r.balance_billetes) + r.cambio    
    db.session.delete(operacion)
    db.session.commit()
    return redirect(url_for('caja'))

@app.route('/buscar_por_fecha', methods = ['GET','POST'])
@login_required
def buscarFecha():
    form = BusquedaFechaForm()
    r, entradas, salidas, cambios = None, None, None, None
    total_billetes = 0.0
    if request.method == 'POST':
        if form.validate_on_submit():
            denominaciones = ['20','50','100','200','500','1000']
            r = Resumen.query.filter_by(fecha = form.fecha.data).first()
            if r is not None:
                total_billetes = calcular_total(r.balance_billetes)
            entradas = Operacion.query.filter_by(fecha = form.fecha.data, tipo = 'entrada').all()
            salidas = Operacion.query.filter_by(fecha = form.fecha.data, tipo = 'salida').all()
            cambios = Operacion.query.filter_by(fecha = form.fecha.data, tipo = 'cambio').all()
    return render_template('busquedaFecha.html', form = form, r = r, entradas = entradas, salidas = salidas, total_billetes = total_billetes, cambios = cambios)

@app.route('/buscar_por_concepto', methods = ['GET','POST'])
@login_required
def buscarSalida():
    form = BusquedaSalidaForm()
    salidas = []
    if request.method == 'POST':
        if form.validate_on_submit():
            concepto = form.concepto.data
            salidas = Operacion.query.filter((Operacion.concepto.contains(concepto)) & (Operacion.tipo == 'salida')).all()
    return render_template('busquedaSalida.html', form = form, salidas = salidas)

@app.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('caja'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nombre = form.username.data).first()
        if user is None or not user.check_passwd(form.password.data):
            flash('Usuario o clave inválidos')
            return redirect(url_for('login'))
        fecha = datetime.today().strftime('%Y-%m-%d')
        ultimo_login_diario = user.ultimo_login_diario
        user.ultimo_login_diario = fecha
        db.session.commit()
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '' or url_parse(next_page) == '/caja' \
            or url_parse(next_page) == '/':
            next_page = url_for('caja')
        return redirect(next_page)
    return render_template('login.html', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('caja'))