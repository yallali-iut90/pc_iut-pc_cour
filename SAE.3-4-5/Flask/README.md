# SAE.3-4-5-
C'est la création d'un site de vente en ligne complet (E-commerce) spécialisé dans le linge de maison.
SAE 2.04 : Création d'une application Web de vente de linge

Description du projet : Cette SAE consiste à développer une application web complète (e-commerce) pour un magasin de linge de maison. L'objectif est de lier une interface utilisateur, une logique de serveur et une base de données relationnelle.

Ce que l'application permet de faire :

    Gestion des utilisateurs : Inscription et connexion sécurisées avec hachage des mots de passe (méthode scrypt).

    Catalogue de produits : Affichage dynamique de 15 articles de linge (couettes, oreillers, draps) récupérés directement depuis la base de données.

    Filtres de recherche : Organisation des articles par types (catégories) pour faciliter la navigation.

    Initialisation automatisée : Une route /base/init qui permet de réinitialiser toute la structure de la base de données et les données de test en un clic.

Technologies utilisées :

    Langage : Python 3

    Framework Web : Flask

    Base de données : MariaDB / MySQL

    Sécurité : python-dotenv pour protéger les accès et werkzeug.security pour les mots de passe.
