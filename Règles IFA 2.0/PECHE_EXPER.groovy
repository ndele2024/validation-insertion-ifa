# Table / Couche : Pêche expérimentale (PECHE_EXPER)

    
    - Subdivision (SUB_CODE) 
        si Type de pêche (TPC_CODE) à la valeur "PENDJ" 
        Alors subdivision (SUB_CODE) doit avoir l''une des valeurs suivantes : "1ÈRE" (1ére partie de 2), "2E" (2éme partie de 2) ou "COMPLÈTE" (Pêche complétée en une partie)


    - Effort de la pêche (IFD_EFFORT) : table pose levée filet
    si Superficie du plan d''eau (ING_SUPRF_PLAN_EAU_M) de information générale ET type de pêche (TPC_CODE) à la valeur "PENT"
        si superficie du plan d''eau (ING_SUPRF_PLAN_EAU_M) est inférieure ou égal à 150 
            Alors Effort de la pêche (IFD_EFFORT) doit être supérieur à 5
        sinon si superficie du plan d''eau (ING_SUPRF_PLAN_EAU_M) est supérieure à 150 et inférieure ou égal à 300
            Alors Effort de la pêche (IFD_EFFORT) doit être supérieur ou égal à 8
        sinon si superficie du plan d''eau (ING_SUPRF_PLAN_EAU_M) est supérieure à 300 et inférieure ou égal à 1000
            Alors Effort de la pêche (IFD_EFFORT) doit être supérieur ou égal à 10
        sinon si superficie du plan d''eau (ING_SUPRF_PLAN_EAU_M) est supérieure à 1000 et inférieure ou égal à 5000
            Alors Effort de la pêche (IFD_EFFORT) doit être compris entre 10 et 50
        sinon 
            Alors Effort de la pêche (IFD_EFFORT) doit être supérieur ou égal à 50

    - Caractéristiques de l''engin (PEX_DESCR_CARAC)
        si Type de pêche (TPC_CODE) à la valeur "PENDJ"
            Alors Caractéristiques de l''engin = "8 panneaux, 7,6m X 1,8m, 25-38-51-64-76-102-127-152mm"
                  Espèce visée (EFA_CODE) = "SAVI"
                  Type d'engin utilisé (TEG_CODE) = "FX"
        sinon si Type de pêche (TPC_CODE) à la valeur "PENOC"
            Alors Caractéristiques de l''engin = "6 panneaux, 3,8m X 1,8, 25-32-38-51-64-76mm"
                  Espèce visée (EFA_CODE) = "SAAL"
                  Type d'engin utilisé (TEG_CODE) = "FX"
        sinon si Type de pêche (TPC_CODE) à la valeur "PENOF"
            Alors Caractéristiques de l''engin = "6 panneaux, 3,8m X 1,8, 25-32-38-51-64-76mm"
                  Espèce visée (EFA_CODE) = "SAFO"
                  Type d'engin utilisé (TEG_CODE) = "FX"
        sinon si Type de pêche (TPC_CODE) à la valeur "PENT"
            Alors Caractéristiques de l''engin = "8 panneaux, 7,6m X 1,8m, 25-38-51-64-76-102-127-152mm"
                  Espèce visée (EFA_CODE) = "SANA"
                  Type d'engin utilisé (TEG_CODE) = "FX"
        sinon si Type de pêche (TPC_CODE) à la valeur "PECPM"
            Alors Caractéristiques de l''engin = "2 bandes de filets à petites mailles de 5 panneaux. 2,5 x 1,8. 13-19-25-32-38"
                  Espèce visée (EFA_CODE) = "MULTI"
                  Type d'engin utilisé (TEG_CODE) = "FX"

    - si Type d''engin utilisé (TEG_CODE) à la valeur "AU"
        Alors caractéristiques de l''engin (PEX_DESCR_CARAC) doit être renseigné

    - Espèce visée (EFA_CODE) ne doit pas contenir les valeurs suivantes : "AU", "RIEN", "NI", "POIS"

    - valeurs obligatoires 
        * Numéro pêche (PEX_NO_PECHE)
        * Type de pêche (TPC_CODE)
        * espèce visée (EFA_CODE)
        * Type d''engin utilisé (TEG_CODE)

    - 
