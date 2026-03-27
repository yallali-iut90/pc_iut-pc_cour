#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                        template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_linge = request.form.get('id_linge')
    quantite = int(request.form.get('quantite', 1))

    # Vérifier que la quantité est supérieure à zéro
    if quantite <= 0:
        flash('La quantité doit être supérieure à zéro', 'alert-warning')
        return redirect('/client/linge/show')

    # Vérifier le stock disponible
    sql_stock = "SELECT stock FROM linge WHERE id_linge = %s"
    mycursor.execute(sql_stock, (id_linge,))
    stock_result = mycursor.fetchone()

    if not stock_result or stock_result['stock'] < quantite:
        flash('Stock insuffisant pour cet linge', 'alert-warning')
        return redirect('/client/linge/show')

    # Vérifier si l'linge est déjà dans le panier
    sql_check = """
        SELECT quantite FROM ligne_panier
        WHERE utilisateur_id = %s AND linge_id = %s
    """
    mycursor.execute(sql_check, (id_client, id_linge))
    panier_existant = mycursor.fetchone()

    if panier_existant:
        # Article déjà dans le panier : mettre à jour la quantité
        nouvelle_quantite = panier_existant['quantite'] + quantite

        # Vérifier que le nouveau total ne dépasse pas le stock
        if nouvelle_quantite > stock_result['stock']:
            flash('Quantité totale demandée supérieure au stock disponible', 'alert-warning')
            return redirect('/client/linge/show')

        sql_update = """
            UPDATE ligne_panier
            SET quantite = %s, date_ajout = NOW()
            WHERE utilisateur_id = %s AND linge_id = %s
        """
        mycursor.execute(sql_update, (nouvelle_quantite, id_client, id_linge))
    else:
        # Nouvel linge dans le panier
        sql_insert = """
            INSERT INTO ligne_panier (utilisateur_id, linge_id, quantite, date_ajout)
            VALUES (%s, %s, %s, NOW())
        """
        mycursor.execute(sql_insert, (id_client, id_linge, quantite))

    # Décrémenter le stock
    sql_decrement = "UPDATE linge SET stock = stock - %s WHERE id_linge = %s"
    mycursor.execute(sql_decrement, (quantite, id_linge))

    get_db().commit()
    flash('Article ajouté au panier', 'alert-success')
    return redirect('/client/linge/show')

@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_linge = request.form.get('id_linge', '')

    # Vérifier si l'linge est dans le panier
    sql_check = """
        SELECT quantite FROM ligne_panier
        WHERE utilisateur_id = %s AND linge_id = %s
    """
    mycursor.execute(sql_check, (id_client, id_linge))
    panier_item = mycursor.fetchone()

    if not panier_item:
        flash('Article non trouvé dans le panier', 'alert-warning')
        return redirect('/client/linge/show')

    quantite_actuelle = panier_item['quantite']

    if quantite_actuelle > 1:
        # Quantité > 1 : décrémenter la quantité de 1
        sql_update = """
            UPDATE ligne_panier
            SET quantite = quantite - 1
            WHERE utilisateur_id = %s AND linge_id = %s
        """
        mycursor.execute(sql_update, (id_client, id_linge))
    else:
        # Quantité = 1 : supprimer la ligne du panier
        sql_delete = """
            DELETE FROM ligne_panier
            WHERE utilisateur_id = %s AND linge_id = %s
        """
        mycursor.execute(sql_delete, (id_client, id_linge))

    # Ré-incrémenter le stock
    sql_increment = "UPDATE linge SET stock = stock + 1 WHERE id_linge = %s"
    mycursor.execute(sql_increment, (id_linge,))

    get_db().commit()
    flash('Article retiré du panier', 'alert-success')
    return redirect('/client/linge/show')





@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']

    # Récupérer toutes les lignes du panier pour réincréménter les stocks
    sql_select = """
        SELECT linge_id, quantite FROM ligne_panier
        WHERE utilisateur_id = %s
    """
    mycursor.execute(sql_select, (client_id,))
    items_panier = mycursor.fetchall()

    # Pour chaque linge, réincréménter le stock
    for item in items_panier:
        sql_increment = "UPDATE linge SET stock = stock + %s WHERE id_linge = %s"
        mycursor.execute(sql_increment, (item['quantite'], item['linge_id']))

    # Supprimer toutes les lignes du panier
    sql_delete = "DELETE FROM ligne_panier WHERE utilisateur_id = %s"
    mycursor.execute(sql_delete, (client_id,))

    get_db().commit()
    flash('Panier vidé', 'alert-success')
    return redirect('/client/linge/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_linge = request.form.get('id_linge')

    # Récupérer la quantité avant suppression pour réincréménter le stock
    sql_quantite = """
        SELECT quantite FROM ligne_panier
        WHERE utilisateur_id = %s AND linge_id = %s
    """
    mycursor.execute(sql_quantite, (id_client, id_linge))
    result = mycursor.fetchone()

    if not result:
        flash('Article non trouvé dans le panier', 'alert-warning')
        return redirect('/client/linge/show')

    quantite = result['quantite']

    # Supprimer la ligne complète du panier
    sql_delete = """
        DELETE FROM ligne_panier
        WHERE utilisateur_id = %s AND linge_id = %s
    """
    mycursor.execute(sql_delete, (id_client, id_linge))

    # Ré-incrémenter le stock du montant supprimé
    sql_increment = "UPDATE linge SET stock = stock + %s WHERE id_linge = %s"
    mycursor.execute(sql_increment, (quantite, id_linge))

    get_db().commit()
    flash('Ligne supprimée du panier', 'alert-success')
    return redirect('/client/linge/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    filter_types = request.form.getlist('filter_types')
    filter_word = request.form.get('filter_word', '').strip()
    filter_prix_min = request.form.get('filter_prix_min', '').strip()
    filter_prix_max = request.form.get('filter_prix_max', '').strip()

    # Stockage des filtres en session
    if filter_types:
        session['filter_types'] = filter_types
    else:
        session.pop('filter_types', None)

    if filter_word:
        session['filter_word'] = filter_word
    else:
        session.pop('filter_word', None)

    if filter_prix_min:
        session['filter_prix_min'] = filter_prix_min
    else:
        session.pop('filter_prix_min', None)

    if filter_prix_max:
        session['filter_prix_max'] = filter_prix_max
    else:
        session.pop('filter_prix_max', None)

    return redirect('/client/linge/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    # suppression des variables de filtre en session
    session.pop('filter_types', None)
    session.pop('filter_word', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    flash('Filtre supprimé', 'alert-success')
    return redirect('/client/linge/show')
