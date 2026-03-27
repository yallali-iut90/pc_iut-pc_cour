#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, redirect
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__,
                          template_folder='templates')


@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()

    sql_commands = [
        # 1. On désactive les clés étrangères pour pouvoir DROP dans n'importe quel ordre
        "SET FOREIGN_KEY_CHECKS = 0",

        # 2. Suppression des tables (on ajoute commentaire et note qui manquaient)
        "DROP TABLE IF EXISTS note",
        "DROP TABLE IF EXISTS commentaire",
        "DROP TABLE IF EXISTS ligne_panier",
        "DROP TABLE IF EXISTS ligne_commande",
        "DROP TABLE IF EXISTS linge",
        "DROP TABLE IF EXISTS commande",
        "DROP TABLE IF EXISTS utilisateur",
        "DROP TABLE IF EXISTS etat",
        "DROP TABLE IF EXISTS type_linge",
        "DROP TABLE IF EXISTS coloris",


        "CREATE TABLE coloris (id_coloris INT AUTO_INCREMENT, nom_coloris VARCHAR(50) NOT NULL, PRIMARY KEY (id_coloris)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE type_linge (id_type_linge INT AUTO_INCREMENT, nom_type_linge VARCHAR(50) NOT NULL, PRIMARY KEY (id_type_linge)) CHARSET=utf8mb4",
        "CREATE TABLE etat (id_etat INT AUTO_INCREMENT, libelle VARCHAR(50) NOT NULL, PRIMARY KEY (id_etat)) CHARSET=utf8mb4",
        "CREATE TABLE utilisateur (id_utilisateur INT AUTO_INCREMENT, login VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, nom VARCHAR(255) NOT NULL, role VARCHAR(50) NOT NULL, PRIMARY KEY (id_utilisateur)) CHARSET=utf8mb4",


        "CREATE TABLE linge (id_linge INT AUTO_INCREMENT, nom_linge VARCHAR(100) NOT NULL, prix_linge DECIMAL(10,2) NOT NULL, dimension VARCHAR(50), matiere VARCHAR(50), description TEXT, fournisseur VARCHAR(100), marque VARCHAR(100), image VARCHAR(255), stock INT DEFAULT 0, coloris_id INT, type_linge_id INT, PRIMARY KEY (id_linge), CONSTRAINT fk_linge_coloris FOREIGN KEY (coloris_id) REFERENCES coloris(id_coloris), CONSTRAINT fk_linge_type FOREIGN KEY (type_linge_id) REFERENCES type_linge(id_type_linge)) CHARSET=utf8mb4",
        "CREATE TABLE commande (id_commande INT AUTO_INCREMENT, date_achat DATETIME NOT NULL, utilisateur_id INT, etat_id INT, PRIMARY KEY (id_commande), CONSTRAINT fk_commande_user FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur), CONSTRAINT fk_commande_etat FOREIGN KEY (etat_id) REFERENCES etat(id_etat)) CHARSET=utf8mb4",
        "CREATE TABLE ligne_panier (utilisateur_id INT, linge_id INT, quantite INT NOT NULL, date_ajout DATETIME NOT NULL, PRIMARY KEY (utilisateur_id, linge_id), CONSTRAINT fk_panier_user FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur), CONSTRAINT fk_panier_linge FOREIGN KEY (linge_id) REFERENCES linge(id_linge)) CHARSET=utf8mb4",
        "CREATE TABLE ligne_commande (commande_id INT, linge_id INT, quantite INT NOT NULL, prix DECIMAL(10,2) NOT NULL, PRIMARY KEY (commande_id, linge_id), CONSTRAINT fk_ligne_comm FOREIGN KEY (commande_id) REFERENCES commande(id_commande), CONSTRAINT fk_ligne_linge FOREIGN KEY (linge_id) REFERENCES linge(id_linge)) CHARSET=utf8mb4",


        "CREATE TABLE commentaire (id_commentaire INT AUTO_INCREMENT, contenu TEXT NOT NULL, date_publication DATETIME DEFAULT CURRENT_TIMESTAMP, valide TINYINT(1) DEFAULT 1, reponse_admin TEXT, utilisateur_id INT, linge_id INT, PRIMARY KEY (id_commentaire), CONSTRAINT fk_commentaire_user FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur), CONSTRAINT fk_commentaire_linge FOREIGN KEY (linge_id) REFERENCES linge(id_linge)) CHARSET=utf8mb4",
        "CREATE TABLE note (utilisateur_id INT, linge_id INT, valeur INT CHECK (valeur BETWEEN 1 AND 5), PRIMARY KEY (utilisateur_id, linge_id), CONSTRAINT fk_note_user FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur), CONSTRAINT fk_note_linge FOREIGN KEY (linge_id) REFERENCES linge(id_linge)) CHARSET=utf8mb4",


        "INSERT INTO coloris (nom_coloris) VALUES ('Blanc Pur'), ('Gris Anthracite'), ('Bleu Marine'), ('Vieux Rose'), ('Vert Sauge'), ('Jaune Moutarde')",
        "INSERT INTO type_linge (nom_type_linge) VALUES ('Linge de Lit'), ('Linge de Bain'), ('Linge de Table'), ('Décoration')",
        "INSERT INTO etat (libelle) VALUES ('En attente'), ('Expédié'), ('Validé'), ('Annulé')",
        "INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom) VALUES (1,'admin','admin@admin.fr','scrypt:32768:8:1$irSP6dJEjy1yXof2$56295be51bb989f467598b63ba6022405139656d6609df8a71768d42738995a21605c9acbac42058790d30fd3adaaec56df272d24bed8385e66229c81e71a4f4','ROLE_admin','admin'), (2,'client','client@client.fr','scrypt:32768:8:1$iFP1d8bdBmhW6Sgc$7950bf6d2336d6c9387fb610ddaec958469d42003fdff6f8cf5a39cf37301195d2e5cad195e6f588b3644d2a9116fa1636eb400b0cb5537603035d9016c15910','ROLE_client','client'), (3,'client2','client2@client2.fr','scrypt:32768:8:1$l3UTNxiLZGuBKGkg$ae3af0d19f0d16d4a495aa633a1cd31ac5ae18f98a06ace037c0f4fb228ed86a2b6abc64262316d0dac936eb72a67ae82cd4d4e4847ee0fb0b19686ee31194b3','ROLE_client','client2')",
        "INSERT INTO linge (nom_linge, prix_linge, dimension, matiere, description, fournisseur, marque, image, stock, coloris_id, type_linge_id) VALUES('Housse Percaline', 55.00, '240x220', 'Percaline de coton', 'Housse respirante et ultra-douce.', 'TextileFrance', 'Rêve d''Or', 'housse_blanc.jpg', 25, 1, 1),('Drap Housse Bio', 19.90, '140x190', 'Coton bio', 'Drap housse élastiqué maintien parfait.', 'BioHome', 'Naturelle', 'drap_gris.jpg', 40, 2, 1),('Taie Lin Lavé', 12.00, '65x65', 'Lin lavé', 'Taie d''oreiller style bohème.', 'Linum', 'Artisanal', 'taie_rose.jpg', 60, 4, 1),('Parure Satinée', 89.00, '260x240', 'Satin de coton', 'Finition luxueuse et soyeuse.', 'LuxTextile', 'Palace', 'parrure_marine.jpg', 15, 3, 1),('Drap de Douche', 14.50, '70x140', 'Éponge 600g', 'Séchage rapide et grand confort.', 'AquaSoft', 'BainDouceur', 'serviette_verte.jpg', 50, 5, 2),('Peignoir Mixte', 45.00, 'Taille L', 'Coton bouclette', 'Peignoir épais avec poches.', 'AquaSoft', 'BainDouceur', 'peignoir_gris.jpg', 20, 2, 2),('Gant de toilette', 3.50, '15x21', 'Éponge coton', 'Douceur garantie pour le visage.', 'AquaSoft', 'BainDouceur', 'gant_blanc.jpg', 100, 1, 2),('Tapis de Bain', 22.00, '50x80', 'Microfibre', 'Tapis ultra absorbant.', 'DecoBain', 'HomeDesign', 'tapis_jaune.jpg', 30, 6, 2),('Nappe Anti-tache', 35.00, '150x250', 'Polyester', 'Facile d''entretien, sans repassage.', 'TableZ', 'CookStyle', 'nappe_grise.jpg', 12, 2, 3),('Serviettes Table (x4)', 16.00, '40x40', 'Lin', 'Lot de 4 serviettes élégantes.', 'Linum', 'Artisanal', 'serviette_table.jpg', 25, 5, 3),('Chemin de Table', 18.00, '40x140', 'Coton tissé', 'Parfait pour vos repas de fête.', 'DecoTable', 'Bohème', 'chemin_table.jpg', 18, 4, 3),('Plaid Polaire XL', 29.90, '180x220', 'Polyester', 'Idéal pour vos soirées canapé.', 'SweetHome', 'Cocooning', 'plaid_marine.jpg', 35, 3, 4),('Coussin Velours', 15.00, '45x45', 'Velours', 'Coussin décoratif très doux.', 'SweetHome', 'Cocooning', 'coussin_jaune.jpg', 45, 6, 4),('Rideau Occultant', 39.00, '140x260', 'Tissage serré', 'Bloque la lumière et garde la chaleur.', 'DecoHome', 'TotalDark', 'rideau_gris.jpg', 10, 2, 4),('Torchon Cuisine', 5.50, '50x70', 'Nid d''abeille', 'Excellente absorption pour la vaisselle.', 'ChefLine', 'ProCook', 'torchon_blanc.jpg', 80, 1, 3)",
        "INSERT INTO commentaire (contenu, utilisateur_id, linge_id) VALUES ('Super qualité, je recommande !', 2, 1), ('Un peu déçu par la couleur.', 3, 1)",
        "INSERT INTO note (utilisateur_id, linge_id, valeur) VALUES (2, 1, 5), (3, 1, 3)",


        "SET FOREIGN_KEY_CHECKS = 1"
    ]

    for command in sql_commands:
        mycursor.execute(command)
    get_db().commit()
    return redirect('/')