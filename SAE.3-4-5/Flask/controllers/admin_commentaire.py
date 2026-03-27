#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, flash, session
from connexion_db import get_db

admin_commentaire = Blueprint('admin_commentaire', __name__,
                              template_folder='templates')


@admin_commentaire.route('/admin/linge/commentaires', methods=['GET'])
def admin_linge_details():
    mycursor = get_db().cursor()
    id_linge = request.args.get('id_linge', None)

    # 1. Infos du linge avec calculs SQL (Moyenne et Count)
    sql_linge = ''' 
        SELECT id_linge, nom_linge AS nom, prix_linge AS prix, image,
               (SELECT ROUND(AVG(valeur),1) FROM note WHERE linge_id = %s) AS moyenne_notes,
               (SELECT COUNT(valeur) FROM note WHERE linge_id = %s) AS nb_notes
        FROM linge WHERE id_linge = %s
    '''
    mycursor.execute(sql_linge, (id_linge, id_linge, id_linge))
    linge = mycursor.fetchone()

    # 2. Compteurs de commentaires (Calculs SQL)
    sql_counts = '''
        SELECT COUNT(*) AS nb_commentaires_total,
               SUM(CASE WHEN valide = 1 THEN 1 ELSE 0 END) AS nb_commentaires_valider
        FROM commentaire WHERE linge_id = %s
    '''
    mycursor.execute(sql_counts, (id_linge,))
    nb_commentaires = mycursor.fetchone()

    # 3. Liste des commentaires
    sql_coms = '''
        SELECT c.id_commentaire, c.contenu AS commentaire, c.valide, c.date_publication, 
               c.reponse_admin, u.login AS nom, u.id_utilisateur,
               (SELECT valeur FROM note WHERE linge_id = c.linge_id AND utilisateur_id = c.utilisateur_id) AS note
        FROM commentaire c
        JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
        WHERE c.linge_id = %s
        ORDER BY c.date_publication DESC
    '''
    mycursor.execute(sql_coms, (id_linge,))
    commentaires = mycursor.fetchall()

    return render_template('admin/linge/show_linge_commentaires.html',
                           commentaires=commentaires,
                           linge=linge,
                           nb_commentaires=nb_commentaires)


@admin_commentaire.route('/admin/linge/commentaires/delete', methods=['POST'])
def admin_comment_delete():
    mycursor = get_db().cursor()
    id_utilisateur = request.form.get('id_utilisateur', None)
    id_linge = request.form.get('id_linge', None)
    date_publication = request.form.get('date_publication', None)

    sql = "DELETE FROM commentaire WHERE utilisateur_id = %s AND linge_id = %s AND date_publication = %s"
    mycursor.execute(sql, (id_utilisateur, id_linge, date_publication))

    get_db().commit()
    flash("Commentaire supprimé", "alert-success")
    # Redirection avec paramètre GET (pas d'url_for)
    return redirect('/admin/linge/commentaires?id_linge=' + str(id_linge))


@admin_commentaire.route('/admin/linge/commentaires/repondre', methods=['POST', 'GET'])
def admin_comment_add():
    if request.method == 'GET':
        id_utilisateur = request.args.get('id_utilisateur', None)
        id_linge = request.args.get('id_linge', None)
        date_publication = request.args.get('date_publication', None)

        # On récupère le texte original pour l'afficher à l'admin pendant qu'il répond
        mycursor = get_db().cursor()
        sql_original = "SELECT contenu FROM commentaire WHERE utilisateur_id=%s AND linge_id=%s AND date_publication=%s"
        mycursor.execute(sql_original, (id_utilisateur, id_linge, date_publication))
        res = mycursor.fetchone()
        commentaire_client = res['contenu'] if res else ""

        return render_template('admin/linge/add_commentaire.html',
                               id_utilisateur=id_utilisateur,
                               id_linge=id_linge,
                               date_publication=date_publication,
                               commentaire_client=commentaire_client)

    mycursor = get_db().cursor()
    # Récupération des données du formulaire
    id_user_client = request.form.get('id_utilisateur', None)
    id_linge = request.form.get('id_linge', None)
    date_publication = request.form.get('date_publication', None)


    reponse = request.form.get('reponse_admin', None)

    # Mise à jour : On enregistre la réponse ET on valide (valide=1)
    sql = '''
        UPDATE commentaire 
        SET reponse_admin = %s, valide = 1 
        WHERE utilisateur_id = %s AND linge_id = %s AND date_publication = %s
    '''
    mycursor.execute(sql, (reponse, id_user_client, id_linge, date_publication))

    get_db().commit()
    flash("Votre réponse a été publiée et le commentaire est validé", "alert-success")
    return redirect('/admin/linge/commentaires?id_linge=' + str(id_linge))


@admin_commentaire.route('/admin/linge/commentaires/valider', methods=['POST', 'GET'])
def admin_comment_valider():
    id_linge = request.args.get('id_linge') or request.form.get('id_linge')

    if id_linge:
        mycursor = get_db().cursor()
        sql = "UPDATE commentaire SET valide = 1 WHERE linge_id = %s"
        mycursor.execute(sql, (id_linge,))
        get_db().commit()
        flash("Tous les commentaires sont validés", "alert-success")

    return redirect('/admin/linge/commentaires?id_linge=' + str(id_linge))