# Table / Couche : Pose et levée (POSE_LEVEE_FILET)

    - Date de pose du filet (PLF_DATE_POSE) & Date de levée du filet (PLF_DATE_LEVEE) : pendant la saisie de la couche "Pêche expérimentale"
    
      Lors de la saisie de la variable "Date de pose du filet", assigne automatiquement la date
      du lendemain à la variable "Date de levée du filet".

      date de pose du filet (PLF_DATE_POSE) doit être inférieure à la date de levée du filet (PLF_DATE_LEVEE).
      si date de pose est égale à la date de levée, alors vérifier que l''heure de pose (PLF_VAL_HRE_POSE) est inférieure à l''heure de levée (PLF_VAL_HRE_LEVEE).
      si heure de pose est égale à l''heure de levée, alors vérifier que la minute de pose (PLF_VAL_MI_POSE) est inférieure à la minute de levée (PLF_VAL_MI_LEVEE).


    - Date de pose du filet (PLF_DATE_POSE) : 
      si date de pose du filet (PLF_DATE_POSE) n''est pas renseignée, alors lui assigner la Date du début de l''inventaire (ING_DATE_DEBUT_INVEN) de Information générale (INFOR_GENER).

      la date de pose du filet (PLF_DATE_POSE) doit être supérieure ou égale à la date du début de l''inventaire (ING_DATE_DEBUT_INVEN) de Information générale (INFOR_GENER) et doit être inférieure ou égale à la date de fin de l''inventaire (ING_DATE_FIN_INVEN) de Information générale (INFOR_GENER).

    - Effort de la pêche (IFD_EFFORT) : table pose levée filet
    si Superficie du plan d''eau (ING_SUPRF_PLAN_EAU_M) de information générale est renseignée ET type de pêche (TPC_CODE) de Pêche expérimentale (PECHE_EXPER) à la valeur "PENT"
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


    - Filtre territoire faunique selon la région administrative du projet

    - Territoire faunique (PER_NOM_TERRI_FAUNI) : 
      si type de plan d''eau (TPL_CODE) de Information générale à la valeur L (lac)
        Alors ne pas mesurer territoire faunique de Habitat, sinon le mesurer

    - valeurs obligatoires :
      * Numéro pose et levée (PLF_NO_POSE_LEVEE)
      * Numéro de station (PLF_NO_STATI)
      * Date de pose du filet (PLF_DATE_POSE)
      * Latitude (PLF_LATIT)
      * Longitude (PLF_LONGI)

    
