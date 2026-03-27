#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_type_linge = Blueprint('admin_type_linge', __name__,
                        template_folder='templates')

@admin_type_linge.route('/admin/type-linge/show')
def show_type_linge():
    mycursor = get_db().cursor()
    # sql = '''         '''
    # mycursor.execute(sql)
    # types_linge = mycursor.fetchall()
    types_linge=[]
    return render_template('admin/type_linge/show_type_linge.html', types_linge=types_linge)

@admin_type_linge.route('/admin/type-linge/add', methods=['GET'])
def add_type_linge():
    return render_template('admin/type_linge/add_type_linge.html')

@admin_type_linge.route('/admin/type-linge/add', methods=['POST'])
def valid_add_type_linge():
    libelle = request.form.get('libelle', '')
    tuple_insert = (libelle,)
    mycursor = get_db().cursor()
    sql = '''         '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = u'type ajouté , libellé :'+libelle
    flash(message, 'alert-success')
    return redirect('/admin/type-linge/show') #url_for('show_type_linge')

@admin_type_linge.route('/admin/type-linge/delete', methods=['GET'])
def delete_type_linge():
    id_type_linge = request.args.get('id_type_linge', '')
    mycursor = get_db().cursor()

    flash(u'suppression type linge , id : ' + id_type_linge, 'alert-success')
    return redirect('/admin/type-linge/show')

@admin_type_linge.route('/admin/type-linge/edit', methods=['GET'])
def edit_type_linge():
    id_type_linge = request.args.get('id_type_linge', '')
    mycursor = get_db().cursor()
    sql = '''   '''
    mycursor.execute(sql, (id_type_linge,))
    type_linge = mycursor.fetchone()
    return render_template('admin/type_linge/edit_type_linge.html', type_linge=type_linge)

@admin_type_linge.route('/admin/type-linge/edit', methods=['POST'])
def valid_edit_type_linge():
    libelle = request.form['libelle']
    id_type_linge = request.form.get('id_type_linge', '')
    tuple_update = (libelle, id_type_linge)
    mycursor = get_db().cursor()
    sql = '''   '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    flash(u'type linge modifié, id: ' + id_type_linge + " libelle : " + libelle, 'alert-success')
    return redirect('/admin/type-linge/show')








