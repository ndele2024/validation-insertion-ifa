# Table / Couche : profil de mesures phisico-chimie (PROFI_MESUR) 

   - Profondeur (PME_PROFD_M) : à l'ouverture du formulaire de saisie de la couche 

      si le nombre d'occurrence de la couche "Profil de mesures physico-chimie" est égal à 0
      → Alors Selon la profondeur maximale du plan d'eau (ING_PROFD_MAX_M) saisie dans information générale, générer toutes les occurrences pour se rendre jusqu'à cette profondeur en respectant les règles suivantes : 
         /// - à 0,5 mètre;
         /// - à tous les mètres de 1 à 14 mètres inclusivement;
         /// - à tous les deux mètres de 16 à 20 mètres inclusivement;
         /// - à tous les quatre mètres à partir de 24 mètres,
         /// et ce, jusqu'au fond (profondeur maximale). Si la profondeur max est absente → 20 m

         0.5 m                          → toujours (premier point)
         1, 2, 3, ... 14 m             → tous les 1 m
         16, 18, 20 m                  → tous les 2 m  (i % 2 == 0)
         24, 28, 32, ... jusqu'au fond → tous les 4 m  (i % 4 == 0)
      
      la liste des valeurs de profondeur générées va être utilisée comme liste de chois pour le champ "Profondeur" du formulaire de saisie de la couche "Profil de mesures physico-chimie" et l'utilisateur peut les modifier si nécessaire avant de valider.

   - PH (PME_VAL_PH) : 
     si le PH (PME_VAL_PH) est renseigné, alors vérifier que la valeur est comprise entre 5 et 8.

   - valeurs obligatoires :
      * Profondeur (PME_PROFD_M)
      * Oxygiène (PME_VAL_OXYGE) ou PH (PME_VAL_PH) ou Température (PME_VAL_TEMPE_CEL) ; au moins une de ces trois variables doit être renseignée

      