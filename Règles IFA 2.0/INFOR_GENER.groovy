# Table / Couche : Informations générales (INFOR_GENER)

   - Territoire : pendant la saisie de la couche "Informations générales" et à la validation du formulaire de saisie

      si territoire faunique à la valeur "LIBRE - Territoire Libre"
         → Alors Territoire doit avoir la valeur "Territoire Libre"


   -  No du plan d''eau officiel (ING_NO_PLAN_EAU_OFFIC) : pendant la saisie de la couche "Informations générales" et à la validation du formulaire de saisie

    À la saisie de la variable "Information général.No du plan d'eau officiel" vérifie dans les fichiers CSV "lac_LCE.txt" ou 
    "cours_eau_LCE.txt" selon le cas si cette valeur existe. Les numéros à 5 caractères font référence à des lacs "lac_LCE.txt" 
    et le numéro à 8 caractères font référence à des cours d'eau (rivières) et se retrouvent dans le fichier "cours_eau_LCE.txt"
    Si elle n'est pas présente, en avertir l'utilisateur avec un message d'erreur. 
    Si la valeur est présente on l'assigne aux variables correspondantes dans le cas où la variable est vide. Si elle n'est pas
    vide aucune assignation est faite, l'ancienne valeur demeure.
    Lorsque les champs Superficie, Profondeur max, Altitude et Perimètre contiennent la valeur -99 ou -999, le champs correspondant est laissé vide.

   - Nom du plan d'eau (affichage) (ING_NOM_PLAN_EAU_AFFIC) :
      si Nom du plan d'eau officiel (ING_NOM_PLAN_EAU_OFFIC) est saisi Alors assigné sa valeur à Nom du plan d'eau (affichage) (ING_NOM_PLAN_EAU_AFFIC)
      sinon si Nom du plan d'eau régional (ING_NOM_PLAN_EAU) est saisi Alors assigné sa valeur à Nom du plan d'eau (affichage) (ING_NOM_PLAN_EAU_AFFIC)

   - Au moins une coordonnées saisie : 
      si les champs suivants ne sont pas saisis :  Latitude du plan d'eau - BD LCE (DD.déc.) (ING_LATIT_BD_LCE), Longitude du plan d'eau - BD LCE (DD.déc.) (ING_LONGI_BD_LCE), Latitude du centre du plan d'eau (degré,décimales) (ING_LATIT_CENTR) et Longitude du centre du plan d'eau (degré,décimales) (ING_LONGI_CENTR)
      ALORS Latitude du centre du plan d'eau (degré,décimales) (ING_LATIT_CENTR) et Longitude du centre du plan d'eau (degré,décimales) (ING_LONGI_CENTR) doivent être saisis. Si ces champs ne sont pas saisis, un message d'erreur est affiché à l'utilisateur.

   - indicateur allopatrie vs indicateur sans poisson
      si Indicateur allopatrie (ING_IND_ALLOP) est égal a 'oui'
      Alors Indicateur de lac ou cours d'eau sans poisson (ING_IND_LAC_SANS_POISS) doit être égal à 'non'
   
   - date de début et de fin d'inventaire
      si Date du début de l'inventaire (ING_DATE_DEBUT_INVEN) et Date de fin de l'inventaire (ING_DATE_FIN_INVEN) sont saisies
      Alors Date du début de l'inventaire (ING_DATE_DEBUT_INVEN) doit être inférieur ou égal à Date de fin de l'inventaire (ING_DATE_FIN_INVEN). Si ce n'est pas le cas, un message d'erreur est affiché à l'utilisateur.

   - Année d''inventaire (ING_AN_INVEN) : 
      Vérifier que Année d''inventaire est comprise entre 1900 et 2100 

   - Filtre territoire faunique selon la région administrative du projet

   - Territoire faunique (ING_NOM_TERRI_FAUNI) : 
      si type de plan d'eau (TPL_CODE) de Information générale à la valeur L (lac)
        Alors ne pas mesurer territoire faunique de Habitat, sinon le mesurer

   - variables obligatoires : 
      * date de debut d'inventaire (ING_DATE_DEBUT_INVEN)
      * date de fin d'inventaire (ING_DATE_FIN_INVEN)
      * No du plan d'eau officiel (ING_NO_PLAN_EAU_OFFIC) ou  No du plan d'eau régional (ING_NO_PLAN_EAU)
      * Type de plan d'eau (TPL_CODE)
      * Latitude du centre du plan d'eau (degré,décimales) (ING_LATIT_CENTR)
      * Longitude du centre du plan d'eau (degré,décimales) (ING_LONGI_CENTR)
      * 
   
   - 


   
