#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                        template_folder='templates')


# validation de la commande : partie 2 -- vue pour choisir les adresses (livraision et facturation)
@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Récupérer les linges du panier
    sql_panier = '''
        SELECT
            lp.linge_id,
            l.nom_linge,
            lp.quantite,
            l.prix_linge as prix
        FROM ligne_panier lp
        JOIN linge l ON lp.linge_id = l.id_linge
        WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql_panier, (id_client,))
    linges_panier = mycursor.fetchall()

    if len(linges_panier) < 1:
        flash('Votre panier est vide', 'alert-warning')
        return redirect('/client/linge/show')

    # Calcul du prix total
    sql_prix_total = '''
        SELECT SUM(lp.quantite * l.prix_linge) as total
        FROM ligne_panier lp
        JOIN linge l ON lp.linge_id = l.id_linge
        WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql_prix_total, (id_client,))
    result = mycursor.fetchone()
    prix_total = result['total'] if result and result['total'] else 0

    return render_template('client/boutique/panier_validation_adresses.html',
                           linges_panier=linges_panier,
                           prix_total=prix_total,
                           validation=1
                           )


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Récupérer le contenu du panier
    sql_panier = '''
        SELECT lp.linge_id, lp.quantite, l.prix_linge
        FROM ligne_panier lp
        JOIN linge l ON lp.linge_id = l.id_linge
        WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql_panier, (id_client,))
    items_ligne_panier = mycursor.fetchall()

    if not items_ligne_panier or len(items_ligne_panier) < 1:
        flash('Pas d\'linges dans le panier', 'alert-warning')
        return redirect('/client/linge/show')

    # Création de la commande (état 1 = "En attente")
    sql_commande = '''
        INSERT INTO commande (date_achat, utilisateur_id, etat_id)
        VALUES (NOW(), %s, 1)
    '''
    mycursor.execute(sql_commande, (id_client,))

    # Récupérer l'id de la commande créée
    sql_last_id = "SELECT LAST_INSERT_ID() as last_insert_id"
    mycursor.execute(sql_last_id)
    result = mycursor.fetchone()
    id_commande = result['last_insert_id']

    # Ajouter les lignes de commande
    for item in items_ligne_panier:
        sql_ligne = '''
            INSERT INTO ligne_commande (commande_id, linge_id, quantite, prix)
            VALUES (%s, %s, %s, %s)
        '''
        mycursor.execute(sql_ligne, (id_commande, item['linge_id'], item['quantite'], item['prix_linge']))

    # Vider le panier
    sql_delete_panier = "DELETE FROM ligne_panier WHERE utilisateur_id = %s"
    mycursor.execute(sql_delete_panier, (id_client,))

    get_db().commit()
    flash('Commande créée avec succès', 'alert-success')
    return redirect('/client/commande/show')




@client_commande.route('/client/commande/show', methods=['get','post'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Récupérer les commandes du client
    sql_commandes = '''
        SELECT
            c.id_commande,
            c.date_achat,
            c.etat_id,
            e.libelle,
            SUM(lc.quantite) as nbr_linge,
            SUM(lc.quantite * lc.prix) as prix_total
        FROM commande c
        JOIN etat e ON c.etat_id = e.id_etat
        LEFT JOIN ligne_commande lc ON c.id_commande = lc.commande_id
        WHERE c.utilisateur_id = %s
        GROUP BY c.id_commande, c.date_achat, c.etat_id, e.libelle
        ORDER BY c.etat_id ASC, c.date_achat DESC
    '''
    mycursor.execute(sql_commandes, (id_client,))
    commandes = mycursor.fetchall()

    linge_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)

    if id_commande:
        # Détails d'une commande spécifique
        sql_details = '''
            SELECT
                lc.linge_id,
                l.nom_linge as nom,
                lc.quantite,
                lc.prix,
                (lc.quantite * lc.prix) as prix_ligne
            FROM ligne_commande lc
            JOIN linge l ON lc.linge_id = l.id_linge
            WHERE lc.commande_id = %s
        '''
        mycursor.execute(sql_details, (id_commande,))
        linge_commande = mycursor.fetchall()

    return render_template('client/commandes/show.html',
                           commandes=commandes,
                           linge_commande=linge_commande,
                           commande_adresses=commande_adresses
                           )

