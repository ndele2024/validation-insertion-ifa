# Table / Couche : Aménagement (AMENAGEMENT)

    - superficie (AME_SUPRF_M2) : 
      si longueur (AME_LONG_M) est renseignée et largeur (AME_LARG_M) est renseignée, Alors 
        Assigner à Superficie la valeur longueur * largeur 

    - filtre sur Type d''activité (AAM_CODE)
      si Type d''aménagement (TAM_CODE) à la valeur "IP" Alors 
        filtrer type d''activité avec ["C", "CC", "CNC", "CP", "CV", "DBC", "EC", "N", "NG", "RR"]
      sinon
        filtrer type d''activité avec ["CO", "EN", "N", "R", "V"]

    - Variable obligatoire 
      * Type d''aménagement (TAM_CODE) 
      * Type d''activité (AAM_CODE)
      * Date d''activité (AME_DATE_ACTIV)

    - consultation de l''historique des activités : lorsqu''on clique sur le bouton dédié dans le formulaire
        Permet de consulter les activités déjà réalisées antérieurement sur un aménagement. Les informations sont 
        affichés dans une fenêtre. 
        Les variables qui sont affichés sont:
            - Date de l'activité
            - Nom de l'activité
            - Commentaire

    - valider date aménagement 
        Vérifie que l'année indiquée dans la date d'activité du formulaire "aménagement" est bien la même que l''année indiquée dans date de debut d''inventaire de "Information générale" pour cet inventaire.
        Il est déclenché automatiquement sur un changement de valeur de la variable Date d'activité
