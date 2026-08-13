

# Table / Couche Habitat (HABITAT) 

    - Profondeur de la prise de données de vitesse du courant en m (HAB_PRFD_VITES_COURA)
        si Vitesse courant avec profondeur en m/s (HAB_VAL_VITES_COURA) est saisi et Profondeur de la prise de données de vitesse du courant en m (HAB_PRFD_VITES_COURA) n'est pas saisi 
        Alors assigné à Profondeur de la prise de données de vitesse du courant la valeur 0
    
    - Date d'observation (HAB_DATE_OBSER)
        si Date d'observation n'est pas mesuré Alors lui assigner la valeur de date de début d'inventaire de la table "Informations générales"
    
    - Superficie (m2) (HAB_SUPRF_M2)
        si longueur (HAB_LONG_M) est mesurée et largeur (HAB_LARG_M) est mesurée 
        Alors assigner à  Superficie la valeur longueur x largeur 
        verifier que Superficie en m2 / 10000 est inférieur ou égal à superficie plan d'eau en ha (ING_SUPRF_PLAN_EAU_M) de Information générale 

    - Commentaires (HAB_COM) 
        si Type d'habitat (TYH_CODE) a la valeur AU (Autre) 
        Alors le champ Commentaires est requis

     - cohérence des dates 
        la date d'observation doit être supérieur ou égale à la date de début d'inventaire de Information générale et doit être inférieur à la date de fin d'inventaire

    - filtrer le territoire faunique selon la région administrative

    - si type de plan d'eau de Information générale à la valeur L (lac)
        Alors ne pas mesurer territoire faunique de Habitat, sinon le mesurer

    - variables obligatoires 
        No (HAB_NO)
        Date d'observation (HAB_DATE_OBSER)
        Type d'habitat (TYH_CODE)
        Latitude (HAB_LATIT)
        Longitude (HAB_LONGI)

    - cohérence des coordonnées X et Y selon le type de coordonnées projetées (TCP_CODE)
        si Type de coordonnées projetées (TCP_CODE) est mesuré et contient l'une des valeurs suivantes : ['MTM_NAD27', 'MTM_NAD83', 'UTM_ABREGE', 'UTM_NAD27', 'UTM_NAD83']
            Alors les champs suivants sont requis : Zone (ZON_CODE) Coordonnées X (HAB_VAL_COORD_X) et Coordonnées Y (HAB_VAL_COORD_Y)
            si Type de coordonnées projetées contient l'une des valeurs suivantes : ['MTM_NAD27', 'MTM_NAD83']
                Alors coordoonées X doit être compris entre 185000 et 425000 (MTM) et coordonnées Y doit être compris entre 4800000 et 6900000 (MTM)
            sinon si Type de coordonnées projetées contient l'une des valeurs suivantes : ['UTM_ABREGE', 'UTM_NAD27', 'UTM_NAD83']
                Alors coordoonées X doit être compris entre 260000 et 740000 (UTM) et coordonnées Y doit être compris entre 4960000 et 7000000 (UTM)
            sinon 
                Alors coordoonées X doit être compris entre 0 et 9999 et coordonnées Y doit être compris entre 0 et 9999
        sinon si type de coordonnées projetées (TCP_CODE) est mesuré et contient l'une des valeurs suivantes ['GEO_NAD27', 'GEO_NAD83']
            Alors les champs suivants sont requis : Latitude (DDMMSS.déc) (HAB_LATIT_DMS) et Longitude (DDMMSS.déc) (HAB_LONGI_DMS)
            et les champs Zone (ZON_CODE), Coordonnées X (HAB_VAL_COORD_X) et Coordonnées Y (HAB_VAL_COORD_Y) ne doivent pas être mesurés

    - filtre sur zone 
    si Type de coordonnées projetées (TCP_CODE) est mesuré et contient l'une des valeurs suivantes : ['MTM_NAD27', 'MTM_NAD83']
        Alors filtrer Zone avec Zone MTM
    sinon si Type de coordonnées projetées (TCP_CODE) est mesuré et contient l'une des valeurs suivantes : ['UTM_ABREGE', 'UTM_NAD27', 'UTM_NAD83']
        Alors filtrer Zone avec Zone UTM
    sinon
        Alors filtrer Zone avec Zone UTM abrégé

    