# Table / Couche : Pertubation (PERTUBATION)

   - Historique des Pertubations : lorsqu''on clique sur le bouton "Consulter l'historique des Pertubations" dans la couche "Pertubation"

      Permet de consulter sous forme de rapport, l'historique de toutes les
      perturbations de cette unité d'échantillonnage, pour tous les mesurages.
.

         les champs suivants :   DATE      |    TYPE    |    LATITUDE    |    LONGITUDE    |    SUPERFICIE    |    CORRECTIF 

      La liste doit être triée par date de début de mesurage, du plus récent au plus ancien.

   - Date d''observation (PER_DATE_OBSER) : 
      si date d''observation (PER_DATE_OBSER) n''est pas renseignée, alors lui assigner la Date du début de l''inventaire (ING_DATE_DEBUT_INVEN) de Information générale (INFOR_GENER).

      la date d''observation (PER_DATE_OBSER) doit être supérieure à la date du début de l''inventaire (ING_DATE_DEBUT_INVEN) de Information générale (INFOR_GENER) et doit être inférieure à la date de fin de l''inventaire (ING_DATE_FIN_INVEN) de Information générale (INFOR_GENER).

   - Superficie (PER_SUPRF_M) : 
      si superficie (PER_SUPRF_M) n''est pas renseignée, alors lui assigner la valeur 
      longueur (PER_LONG_M) * largeur (PER_LARG_M) de la perturbation.

   - Commentaire (PER_COMMENTAIRE) : 
      si Type de perturbation (TPE_CODE) à la valeur "AU" alors le commentaire (PER_COMMENTAIRE) doit être renseigné.

   - Filtre territoire faunique selon la région administrative du projet

   - Territoire faunique (PER_NOM_TERRI_FAUNI) : 
      si type de plan d''eau (TPL_CODE) de Information générale à la valeur L (lac)
        Alors ne pas mesurer territoire faunique de Habitat, sinon le mesurer

   - valeurs obligatoires :
      * No perturbation (PER_NO_STATI)
      * Date d''observation (PER_DATE_OBSER)
      * Type de perturbation (TPE_CODE)
      * latitude (PER_LATIT)
      * Longitude (PER_LONGI)

   