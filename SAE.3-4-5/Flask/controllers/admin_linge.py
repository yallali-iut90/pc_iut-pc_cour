#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
#from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_linge = Blueprint('admin_linge', __name__,
                          template_folder='templates')


@admin_linge.route('/admin/linge/show')
def show_linge():
    mycursor = get_db().cursor()
    # Récupérer tous les linges avec leur type et coloris
    # Adapter les noms pour correspondre au template show_linge.html
    sql = '''
        SELECT
            l.id_linge as id_linge,
            l.nom_linge as nom,
            l.prix_linge as prix,
            l.stock,
            l.image,
            tl.nom_type_linge as libelle,
            l.type_linge_id
        FROM linge l
        JOIN type_linge tl ON l.type_linge_id = tl.id_type_linge
        ORDER BY l.nom_linge ASC
    '''
    mycursor.execute(sql)
    linges = mycursor.fetchall()
    return render_template('admin/linge/show_linge.html', linges=linges)


@admin_linge.route('/admin/linge/add', methods=['GET'])
def add_linge():
    mycursor = get_db().cursor()

    # Récupérer tous les types de linge
    sql = '''
        SELECT id_type_linge, nom_type_linge as libelle
        FROM type_linge
        ORDER BY nom_type_linge ASC
    '''
    mycursor.execute(sql)
    types_linge = mycursor.fetchall()

    return render_template('admin/linge/add_linge.html',
                           types_linge=types_linge
                            )


@admin_linge.route('/admin/linge/add', methods=['POST'])
def valid_add_linge():
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    type_linge_id = request.form.get('type_linge_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')

    if image:
        filename = 'img_upload'+ str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        print("erreur")
        filename=None

    sql = ''' INSERT INTO linge(nom_linge, image, prix_linge, type_linge_id, description)
                VALUES(%s, %s, %s, %s, %s); '''

    tuple_add = (nom, filename, prix, type_linge_id, description)
    print(tuple_add)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    print(u'linge ajouté , nom: ', nom, ' - type_linge:', type_linge_id, ' - prix:', prix,
          ' - description:', description, ' - image:', image)
    message = u'linge ajouté , nom:' + nom + '- type_linge:' + type_linge_id + ' - prix:' + prix + ' - description:' + description + ' - image:' + str(
        image)
    flash(message, 'alert-success')
    return redirect('/admin/linge/show')


@admin_linge.route('/admin/linge/delete', methods=['GET'])
def delete_linge():
    id_linge = request.args.get('id_linge')
    mycursor = get_db().cursor()

    # Vérifier si le linge existe et récupérer son image
    sql = ''' SELECT image FROM linge WHERE id_linge = %s '''
    mycursor.execute(sql, (id_linge,))
    linge = mycursor.fetchone()

    if not linge:
        flash(u'Linge non trouvé', 'alert-warning')
        return redirect('/admin/linge/show')

    image = linge['image']

    # Vérifier si le linge est utilisé dans des commandes (ligne_commande)
    sql = ''' SELECT COUNT(*) as nb_commandes FROM ligne_commande WHERE linge_id = %s '''
    mycursor.execute(sql, (id_linge,))
    result = mycursor.fetchone()

    if result['nb_commandes'] > 0:
        message = u'Ce linge est utilisé dans des commandes : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        # Supprimer le linge
        sql = ''' DELETE FROM linge WHERE id_linge = %s '''
        mycursor.execute(sql, (id_linge,))
        get_db().commit()

        # Supprimer l'image si elle existe
        if image is not None and os.path.exists('static/images/' + image):
            os.remove('static/images/' + image)

        print("un linge supprimé, id :", id_linge)
        message = u'un linge supprimé, id : ' + str(id_linge)
        flash(message, 'alert-success')

    return redirect('/admin/linge/show')


@admin_linge.route('/admin/linge/edit', methods=['GET'])
def edit_linge():
    id_linge=request.args.get('id_linge')
    mycursor = get_db().cursor()

    # Récupérer le linge à modifier
    sql = '''
        SELECT
            l.id_linge,
            l.nom_linge as nom,
            l.prix_linge as prix,
            l.stock,
            l.image,
            l.description,
            l.type_linge_id
        FROM linge l
        WHERE l.id_linge = %s
    '''
    mycursor.execute(sql, (id_linge,))
    linge = mycursor.fetchone()
    print(linge)

    # Récupérer tous les types de linge
    sql = '''
        SELECT id_type_linge, nom_type_linge as libelle
        FROM type_linge
        ORDER BY nom_type_linge ASC
    '''
    mycursor.execute(sql)
    types_linge = mycursor.fetchall()

    return render_template('admin/linge/edit_linge.html'
                           ,linge=linge
                           ,types_linge=types_linge
                           )


@admin_linge.route('/admin/linge/edit', methods=['POST'])
def valid_edit_linge():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_linge = request.form.get('id_linge')
    image = request.files.get('image', '')
    type_linge_id = request.form.get('type_linge_id', '')
    prix = request.form.get('prix', '')
    stock = request.form.get('stock', '')
    description = request.form.get('description')

    # Récupérer l'image actuelle
    sql = 'SELECT image FROM linge WHERE id_linge = %s'
    mycursor.execute(sql, (id_linge,))
    result = mycursor.fetchone()
    image_nom = result['image'] if result else None

    # Gestion de la nouvelle image
    if image:
        if image_nom and image_nom != "" and os.path.exists(
                os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
        image_nom = filename

    # Mise à jour du linge (avec stock)
    sql = '''
        UPDATE linge
        SET nom_linge = %s,
            prix_linge = %s,
            stock = %s,
            image = %s,
            type_linge_id = %s,
            description = %s
        WHERE id_linge = %s
    '''
    mycursor.execute(sql, (nom, prix, stock, image_nom, type_linge_id, description, id_linge))

    get_db().commit()
    if image_nom is None:
        image_nom = ''
    message = u'linge modifié , nom:' + nom + ' - type_linge:' + type_linge_id + ' - prix:' + prix + ' - stock:' + stock + ' - image:' + image_nom
    flash(message, 'alert-success')
    return redirect('/admin/linge/show')







@admin_linge.route('/admin/linge/avis', methods=['GET'])
def admin_avis():
    mycursor = get_db().cursor()
    id = request.args.get('id', None)
    linge=[]
    commentaires = {}
    return render_template('admin/linge/show_avis.html'
                           , linge=linge
                           , commentaires=commentaires
                           )


@admin_linge.route('/admin/linge/stock/edit', methods=['POST'])
def edit_stock_linge():
    mycursor = get_db().cursor()
    id_linge = request.form.get('id_linge')
    nouveau_stock = request.form.get('stock')

    if id_linge and nouveau_stock is not None:
        nouveau_stock = int(nouveau_stock)
        if nouveau_stock < 0:
            flash('Le stock ne peut pas être négatif', 'alert-warning')
            return redirect('/admin/linge/show')

        sql = "UPDATE linge SET stock = %s WHERE id_linge = %s"
        mycursor.execute(sql, (nouveau_stock, id_linge))
        get_db().commit()
        flash('Stock mis à jour', 'alert-success')
    return redirect('/admin/linge/show')


@admin_linge.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    linge_id = request.form.get('idlinge', None)
    userId = request.form.get('idUser', None)

    return redirect('/admin/linge/avis?id=' + str(linge_id))
