#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_linge = Blueprint('admin_declinaison_linge', __name__,
                         template_folder='templates')


@admin_declinaison_linge.route('/admin/declinaison_linge/add')
def add_declinaison_linge():
    id_linge=request.args.get('id_linge')
    mycursor = get_db().cursor()
    linge=[]
    couleurs=None
    tailles=None
    d_taille_uniq=None
    d_couleur_uniq=None
    return render_template('admin/linge/add_declinaison_linge.html'
                           , linge=linge
                           , couleurs=couleurs
                           , tailles=tailles
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_linge.route('/admin/declinaison_linge/add', methods=['POST'])
def valid_add_declinaison_linge():
    mycursor = get_db().cursor()

    id_linge = request.form.get('id_linge')
    stock = request.form.get('stock')
    taille = request.form.get('taille')
    couleur = request.form.get('couleur')
    # attention au doublon
    get_db().commit()
    return redirect('/admin/linge/edit?id_linge=' + id_linge)


@admin_declinaison_linge.route('/admin/declinaison_linge/edit', methods=['GET'])
def edit_declinaison_linge():
    id_declinaison_linge = request.args.get('id_declinaison_linge')
    mycursor = get_db().cursor()
    declinaison_linge=[]
    couleurs=None
    tailles=None
    d_taille_uniq=None
    d_couleur_uniq=None
    return render_template('admin/linge/edit_declinaison_linge.html'
                           , tailles=tailles
                           , couleurs=couleurs
                           , declinaison_linge=declinaison_linge
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_linge.route('/admin/declinaison_linge/edit', methods=['POST'])
def valid_edit_declinaison_linge():
    id_declinaison_linge = request.form.get('id_declinaison_linge','')
    id_linge = request.form.get('id_linge','')
    stock = request.form.get('stock','')
    taille_id = request.form.get('id_taille','')
    couleur_id = request.form.get('id_couleur','')
    mycursor = get_db().cursor()

    message = u'declinaison_linge modifié , id:' + str(id_declinaison_linge) + '- stock :' + str(stock) + ' - taille_id:' + str(taille_id) + ' - couleur_id:' + str(couleur_id)
    flash(message, 'alert-success')
    return redirect('/admin/linge/edit?id_linge=' + str(id_linge))


@admin_declinaison_linge.route('/admin/declinaison_linge/delete', methods=['GET'])
def admin_delete_declinaison_linge():
    id_declinaison_linge = request.args.get('id_declinaison_linge','')
    id_linge = request.args.get('id_linge','')

    flash(u'declinaison supprimée, id_declinaison_linge : ' + str(id_declinaison_linge),  'alert-success')
    return redirect('/admin/linge/edit?id_linge=' + str(id_linge))
