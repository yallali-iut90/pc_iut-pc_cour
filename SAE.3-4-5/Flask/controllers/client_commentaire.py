#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, url_for, abort, flash, session
from connexion_db import get_db

client_commentaire = Blueprint('client_commentaire', __name__,
                               template_folder='templates')


@client_commentaire.route('/client/linge/details', methods=['GET'])
def client_linge_details():
    mycursor = get_db().cursor()
    id_linge = request.args.get('id_linge', None)
    id_client = session.get('id_user')  # ID de l'utilisateur connecté

    # 1. Détails du linge
    sql_linge = "SELECT id_linge, nom_linge as nom, prix_linge as prix, image, description FROM linge WHERE id_linge = %s"
    mycursor.execute(sql_linge, (id_linge,))
    linge = mycursor.fetchone()

    if linge is None:
        abort(404, "Article introuvable")

    # Stats des notes globales
    sql_stats = "SELECT ROUND(AVG(valeur),1) as moyenne_notes, COUNT(valeur) as nb_notes FROM note WHERE linge_id = %s"
    mycursor.execute(sql_stats, (id_linge,))
    stats = mycursor.fetchone()

    linge['moyenne_notes'] = stats['moyenne_notes'] if stats['moyenne_notes'] else 0
    linge['nb_notes'] = stats['nb_notes'] if stats['nb_notes'] else 0

    # 2. Commentaires et Réponses (Correction SQL)
    # On sélectionne les commentaires validés OU ceux appartenant à l'utilisateur connecté
    sql_comms = '''
        SELECT c.id_commentaire, c.contenu, c.date_publication, c.utilisateur_id, 
               u.login as nom, c.reponse_admin, c.valide
        FROM commentaire c 
        JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
        WHERE c.linge_id = %s 
        AND (c.valide = 1 OR c.utilisateur_id = %s)
        ORDER BY c.date_publication DESC
    '''
    mycursor.execute(sql_comms, (id_linge, id_client))
    commentaires = mycursor.fetchall()

    # 3. Compteurs pour l'interface
    sql_counts = """
        SELECT 
            COUNT(*) AS total,
            SUM(CASE WHEN utilisateur_id = %s THEN 1 ELSE 0 END) AS utilisateur,
            SUM(CASE WHEN valide = 1 THEN 1 ELSE 0 END) AS total_valide
        FROM commentaire
        WHERE linge_id = %s
    """
    mycursor.execute(sql_counts, (id_client, id_linge))
    res_counts = mycursor.fetchone()

    nb_commentaires = {
        'total': res_counts['total'] if res_counts['total'] else 0,
        'utilisateur': res_counts['utilisateur'] if res_counts['utilisateur'] else 0,
        'total_valide': res_counts['total_valide'] if res_counts['total_valide'] else 0
    }

    # 4. Vérification achat et Note personnelle
    commandes_linges = {'nb_commandes_linge': 0}
    note = None
    if id_client:
        sql_achat = '''
            SELECT COUNT(*) as nb_commandes_linge FROM ligne_commande lc
            JOIN commande c ON lc.commande_id = c.id_commande
            WHERE c.utilisateur_id = %s AND lc.linge_id = %s
        '''
        mycursor.execute(sql_achat, (id_client, id_linge))
        commandes_linges = mycursor.fetchone()

        sql_note = "SELECT valeur FROM note WHERE utilisateur_id = %s AND linge_id = %s"
        mycursor.execute(sql_note, (id_client, id_linge))
        note_res = mycursor.fetchone()
        note = note_res['valeur'] if note_res else None

    return render_template('client/linge_info/linge_details.html',
                           linge=linge,
                           commentaires=commentaires,
                           commandes_linges=commandes_linges,
                           note=note,
                           nb_commentaires=nb_commentaires)


@client_commentaire.route('/client/commentaire/add', methods=['POST'])
def client_comment_add():
    mycursor = get_db().cursor()
    id_client = session.get('id_user')
    id_linge = request.form.get('id_linge', None)
    commentaire = request.form.get('commentaire', '').strip()

    # Quota de 3 commentaires
    sql_quota = "SELECT COUNT(*) as nb_com FROM commentaire WHERE utilisateur_id = %s AND linge_id = %s"
    mycursor.execute(sql_quota, (id_client, id_linge))
    res_quota = mycursor.fetchone()

    if res_quota and res_quota['nb_com'] >= 3:
        flash(u"Vous avez déjà posté 3 commentaires pour cet article.", 'alert-danger')
        return redirect('/client/linge/details?id_linge=' + id_linge)

    if len(commentaire) < 3:
        flash(u'Message trop court.', 'alert-warning')
        return redirect('/client/linge/details?id_linge=' + id_linge)

    # Insertion avec valide=0 (attente modération)
    sql = "INSERT INTO commentaire (contenu, utilisateur_id, linge_id, date_publication, valide) VALUES (%s, %s, %s, NOW(), 0)"
    mycursor.execute(sql, (commentaire, id_client, id_linge))
    get_db().commit()

    flash(u'Commentaire envoyé ! Il sera visible après validation.', 'alert-success')
    return redirect('/client/linge/details?id_linge=' + id_linge)


@client_commentaire.route('/client/commentaire/delete', methods=['POST'])
def client_comment_delete():
    mycursor = get_db().cursor()
    id_client = session.get('id_user')
    id_linge = request.form.get('id_linge', None)
    id_comm = request.form.get('id_commentaire', None)

    sql = "DELETE FROM commentaire WHERE id_commentaire = %s AND utilisateur_id = %s"
    mycursor.execute(sql, (id_comm, id_client))
    get_db().commit()

    flash(u'Commentaire supprimé.', 'alert-info')
    return redirect('/client/linge/details?id_linge=' + id_linge)


@client_commentaire.route('/client/note/save', methods=['POST'])
def client_note_save():
    mycursor = get_db().cursor()
    id_client = session.get('id_user')
    id_linge = request.form.get('id_linge', None)
    valeur_note = request.form.get('note', None)

    sql = """
        INSERT INTO note (utilisateur_id, linge_id, valeur) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE valeur = VALUES(valeur)
    """
    mycursor.execute(sql, (id_client, id_linge, valeur_note))
    get_db().commit()

    flash(u'Note mise à jour.', 'alert-success')
    return redirect('/client/linge/details?id_linge=' + id_linge)


@client_commentaire.route('/client/note/delete', methods=['POST'])
def client_note_delete():
    mycursor = get_db().cursor()
    id_client = session.get('id_user')
    id_linge = request.form.get('id_linge', None)

    sql = "DELETE FROM note WHERE utilisateur_id = %s AND linge_id = %s"
    mycursor.execute(sql, (id_client, id_linge))
    get_db().commit()

    flash(u'Note supprimée.', 'alert-info')
    return redirect('/client/linge/details?id_linge=' + id_linge)