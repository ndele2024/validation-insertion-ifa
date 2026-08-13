# Table / Couche : Résultat d''analyse physico-chimique (RESUL_ANALY_PHYSI_CHIMI)

    - Appareil & Autre appareil :

      Si Appareil (APP_CODE) est vide ET Autre appareil (RPC_NOM_AUTRE_APPAR) est renseigné
      → Alors Appareil = "AUTRE"
      dans ce cas autre appareil doit spécifier la marque le modéle et la précision de cet autre appareil sinon indiquer "inconnu"
      
      quand un utilisateur saisit quelque chose dans le champ "Autre appareil" sans avoir choisi un appareil standard, la règle remplit automatiquement le champ "Appareil" avec la valeur générique 'AUTRE', pour assurer la cohérence des données.

    - Nom du laboratoire (LAB_CODE) & Nom autre laboratoire (RPC_NOM_AUTRE_LABOR) 
    
      Si Nom du laboratoire (LAB_CODE) est vide ET Nom autre laboratoire (RPC_NOM_AUTRE_LABOR) est renseigné
      → Alors Nom du laboratoire = "AUTRE"
      si Nom du laboratoire = "AUTRE" alors Nom autre laboratoire doit spécifier le nom du laboratoire
      
      quand un utilisateur saisit quelque chose dans le champ "Nom autre laboratoire" sans avoir choisi un laboratoire standard, la règle remplit automatiquement le champ "Nom du laboratoire" avec la valeur générique 'AUTRE', pour assurer la cohérence des données.

    - Indicateur analyse laboratoire (RPC_IND_ANALY_LABOR) 
      si Numéro d''échantillon laboratoire (RPC_NO_ECHAN_LABOR) est renseigné, alors attribuer à Indicateur analyse laboratoire (RPC_IND_ANALY_LABOR) la valeur "OUI".

    - Commentaires (RPC_COM) 
      si Paramètre physico-chimique (PPC_CODE) à la valeur "AU" alors le commentaire (RPC_COM) doit être renseigné.

    - Paramètre physico-chimique (PPC_CODE) vs Profondeur de la prise de l''échantillon (RPC_PROFD_ECHAN_M) & Resultat (RPC_VAL_RESUL)
      si Paramètre physico-chimique (PPC_CODE) à la valeur "TR" Alors profondeur de la prise de l''échantillon (RPC_PROFD_ECHAN_M) ne doit pas être renseignée. Et si profondeur est renseignée, sa valeur doit être assignée à résultat (RPC_VAL_RESUL).

    - Profondeur 2 (RPC_VAL_PROFD_2_M)
      si Paramètre physico-chimique (PPC_CODE) à la valeur "CD" Alors 
        si Profondeur de la prise de l''échantillon (RPC_PROFD_ECHAN_M) n''est pas renseignée et Profondeur 2 (RPC_VAL_PROFD_2_M) n''est pas renseignée, alors 
            assigner à Profondeur de la prise de l''échantillon (RPC_PROFD_ECHAN_M) la valeur 0 et à Profondeur 2 (RPC_VAL_PROFD_2_M) la valeur 5
      sinon si Profondeur de la prise de l''échantillon (RPC_PROFD_ECHAN_M) est renseignée et Profondeur 2 (RPC_VAL_PROFD_2_M) n''est pas renseignée, alors assigner à Profondeur 2 (RPC_VAL_PROFD_2_M) la valeur Profondeur de la prise de l''échantillon (RPC_PROFD_ECHAN_M)

    
    - Resultat (RPC_VAL_RESUL) & Teinte de l''eau (RES_CODE)
      si Paramètre physico-chimique (PPC_CODE) à la valeur "TI" Alors   
        Ne pas renseigner résultat (RPC_VAL_RESUL) et renseigner teinte de l''eau (RES_CODE)
      sinon Ne pas renseigner teinte de l''eau (RES_CODE) et renseigner résultat (RPC_VAL_RESUL)

    - Resultat (RPC_VAL_RESUL) 
      si Profondeur maximum du plan d''eau de la couche informations générales est renseignée et Résultat est mesuré et paramètre physico-chimique (PPC_CODE) à la valeur "TR" Alors 
        vérifier que Resultat (RPC_VAL_RESUL) est inférieur ou égal à Profondeur max plan d''eau de information générale (ING_PROFD_MAX_M)
    - unicité des paramètres: 
      Vérifier que pour un même numéro de station (PHC_NO_STATI), une même Date de prise de l''échantillon (RPC_DATE_ECHAN) et une même Profondeur de la prise de l''échantillon (RPC_PROFD_ECHAN_M), on ne peut avoir qu''une seule occurrence pour un même paramètre ; autrement dit le tuple (PHC_NO_STATI, RPC_DATE_ECHAN, RPC_PROFD_ECHAN_M, PPC_CODE) doit être unique.

    - le Numéro d''échantillon laboratoire (RPC_NO_ECHAN_LABOR) doit être unique.

    - Date de prise de l''échantillon (RPC_DATE_ECHAN) : 
    la date de prise de l''échantillon (RPC_DATE_ECHAN) doit être supérieure ou égale à la date du début de l''inventaire (ING_DATE_DEBUT_INVEN) de Information générale (INFOR_GENER) et doit être inférieure ou égale à la date de fin de l''inventaire (ING_DATE_FIN_INVEN) de Information générale (INFOR_GENER).
       

    - Cohérence du PH
      si Paramètre physico-chimique (PPC_CODE) à la valeur "PH" Alors vérifier que le résultat (RPC_VAL_RESUL) est compris entre 5 et 8.

    - Cohérence des profondeurs 
      si Profondeur de la prise de l''échantillon (RPC_PROFD_ECHAN_M) est renseignée et Profondeur 2 (RPC_VAL_PROFD_2_M) est renseignée, alors vérifier que Profondeur de la prise de l''échantillon (RPC_PROFD_ECHAN_M) est inférieure ou égale à Profondeur 2 (RPC_VAL_PROFD_2_M).

    - Variables obligatoires : 
      * Numéro (RPC_NO)
      * Paramètre physico-chimique (PPC_CODE)
      * Appareil (APP_CODE) ou Autre appareil (RPC_NOM_AUTRE_APPAR)
      * Résultat (RPC_VAL_RESUL) ou Teinte de l''eau (RES_CODE) si Indicateur analyse laboratoire (RPC_IND_ANALY_LABOR) à la valeur "NON"
      * Numéro d''échantillon laboratoire (RPC_NO_ECHAN_LABOR) et Nom du laboratoire (LAB_CODE) ou Nom autre laboratoire (RPC_NOM_AUTRE_LABOR) si Indicateur analyse laboratoire (RPC_IND_ANALY_LABOR) à la valeur "OUI"