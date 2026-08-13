# Table / couche : Détails des spécimens (DETAIL_SPECI)

   - Panneau du filet (CDE_CODE) : pendant la saisie de la couche "Détails des spécimens" et à la validation du formulaire de saisie

      La valeur du champ "Panneau du filet" est assignée en fonction de la valeur des champs : 
         Type de pêche de pêche expérimentale 
         Grandeur de maille de Détail des spécimens
         si type de pêche est contient les valeurs ["PENDJ", "PENT"] alors
            si detail des spécimens contient 25 
               → Alors Panneau du filet = "PAN1"
            sinon si detail des spécimens contient 38
               → Alors Panneau du filet = "PAN2"
            sinon si detail des spécimens contient 51
               → Alors Panneau du filet = "PAN3"
            sinon si detail des spécimens contient 64
               → Alors Panneau du filet = "PAN4"
            sinon si detail des spécimens contient 76
               → Alors Panneau du filet = "PAN5"
            sinon si detail des spécimens contient 102
               → Alors Panneau du filet = "PAN6"
            sinon si detail des spécimens contient 127
               → Alors Panneau du filet = "PAN7"
            sinon si detail des spécimens contient 152
               → Alors Panneau du filet = "PAN8"
         sinon si type de pêche est contient les valeurs ["PENOC", "PENOF"] alors
            si detail des spécimens contient 25 
               → Alors Panneau du filet = "PAN1"
            sinon si detail des spécimens contient 32
               → Alors Panneau du filet = "PAN2"
            sinon si detail des spécimens contient 38
               → Alors Panneau du filet = "PAN3"
            sinon si detail des spécimens contient 51
               → Alors Panneau du filet = "PAN4"
            sinon si detail des spécimens contient 64
               → Alors Panneau du filet = "PAN5"
            sinon si detail des spécimens contient 76
               → Alors Panneau du filet = "PAN6"
         sinon si type de pêche est contient les valeurs ["PECPM"] alors
            si detail des spécimens contient 32
               → Alors Panneau du filet = "PAN1"
            sinon si detail des spécimens contient 19
               → Alors Panneau du filet = "PAN2"
            sinon si detail des spécimens contient 38
               → Alors Panneau du filet = "PAN3"
            sinon si detail des spécimens contient 13
               → Alors Panneau du filet = "PAN4"
            sinon si detail des spécimens contient 25
               → Alors Panneau du filet = "PAN5"
         sinon si type de pêche est contient les valeurs ["PECGM"] alors
            si detail des spécimens contient 76
               → Alors Panneau du filet = "PAN1"
            sinon si detail des spécimens contient 114
               → Alors Panneau du filet = "PAN2"
            sinon si detail des spécimens contient 51
               → Alors Panneau du filet = "PAN3"
            sinon si detail des spécimens contient 89
               → Alors Panneau du filet = "PAN4"
            sinon si detail des spécimens contient 38
               → Alors Panneau du filet = "PAN5"
            sinon si detail des spécimens contient 127
               → Alors Panneau du filet = "PAN6"
            sinon si detail des spécimens contient 64
               → Alors Panneau du filet = "PAN7"
            sinon si detail des spécimens contient 102
               → Alors Panneau du filet = "PAN8"

   - Numéro échantillon laboratoire 1 (DSP_NO_ECHAN_LABOR_1) & Numéro échantillon laboratoire 2 (DSP_NO_ECHAN_LABOR_2) : Aprés l'ajout d'une occurence dans la couche "Détails des spécimens"
      
      si Type de structure conservée pour déterminer l'âge 1 (TSA_CODE_1) = ["OT - Otolithe", "EC - Ecaille", "OP - Opercule", "RE - Rayon épineux"] 
         → Parcourir tous les spécimens existants
         → Trouver le plus grand numéro parmi Échantillon 1 et Échantillon 2 (Le numéro d'échantillon peut être un caractère suivit  d'un entier, dans ce cas on considère seulement la partie entière pour trouver le plus grand numéro)
         → Incrémenter de 1
         → Assigner le nouveau numéro à Échantillon 1 pour le spécimen en cours de saisie (garder le caractère dans le numéro si existant)
      
      Même logique pour Type de structure conservée pour déterminer l'âge 2 (TSA_CODE_2) et Échantillon 2

            
   - Numéro de spécimen (DSP_NO_SPECI) : Après l'ajout d'une occurence dans la couche "Détails des spécimens"

      Un numéro de spécimen unique est généré par unité d'échantillonnage et l'espèce du spécimen précédent est copié vers le nouveau spécimen ajouté

    

   - Validation des données saisies Masse totale (g), Nombre pesé, Nombre capturé : à la validation du formulaire de saisie de la couche "Détails des spécimens"

      Description:
      Fait la somme des enregistrements par "Détail spécimen.No pêche" + "Détail spécimen.No pose et levée" + "Détail spécimen.Espèce" + 
      "Détail spécimen.Panneau", fait aussi la somme pour le même groupe de toutes des enregistrements pour lesquels la variable 
      "Détail spécimens.Masse (g)" a été saisie. Pour chaque occurrence on vérifie si un enregistrement correspond dans le groupe 
      "Dénombrement par espèce.No pêche" + "Dénombrement par espèce.No pose et levée" + "Dénombrement par espèce.Espèce" + 
      "Dénombrement par espèce. Catégorie de dénombrement" et vérifie si la variable "Dénombrement par espèce.Nbre capturé" existe. 
      Si c'est le cas, vérifie si le nombre inscrit est inférieur au nombre d'enregistrement de l'espèce, si c'est le cas l'utilisateur 
      est averti à l'aide d'un message d'erreur et d'une pastille. Si le nombre capturé n'est pas mesuré, on assigne le nombre 
      d'enregistrement à cette variable. Pour la même occurrence de Détail de spécimen, vérifie si la variable
      "Dénombrement par espèce.Nbre pesé" est mesurée. Si ce n'est pas le cas, assigne à cette variable le nombre d'enregistrements 
      trouvés qui ont une masse de mesurée. Si elle est mesurée et que la valeur diffère de celle calculée, indique un avertissement 
      avec la valeur qui a été calculée. Même procédé par la variable "Dénombrement par espèce.Masse totale (g)" si la valeur n'existe 
      pas, assigne la sommation de tous les spécimens de la même espèce. Si elle existe et que la valeur est différente de celle 
      calculée, indique un avertissement avec la valeur calculée.

   - Validation des occurrences entre Détail des spécimens et Dénombrement par espèce : à la validation du formulaire

      Valide que toutes les "Espèce" présente dans le groupe de variable "Détail spécimens" se retrouvent dans le groupe de 
      variable "Dénombrement par espèce" Et ce pour un même "No pêche" et "No pose et levée"

   - Cohérence des indicateurs contenu stomacal
      si Indicateur contenu stomacal vide (DSP_IND_CONTE_STOMA_VIDE) est coché (oui) 
       Alors les autres indicateurs de contenu stomacal ne devraient pas être coché à savoir 
         Indicateur contenu stomacal insecte (DSP_IND_CONTE_STOMA_INSEC)
         Indicateur contenu stomacal benthos (DSP_IND_CONTE_STOMA_BENTH)
         Indicateur contenu stomacal plancton (DSP_IND_CONTE_STOMA_PLANC)
         Indicateur contenu stomacal chyme (DSP_IND_CONTE_STOMA_CHYME)
         Indicateur contenu stomacal poisson (DSP_IND_CONTE_STOMA_POISS)

   - Cohérence des longueurs : Longueur à la fourche (DSP_LONG_FOURC_MM) et Longueur totale maximale (DSP_LONG_TOT_MAX_M)
      la longueur de la fourche doit être inférieur à la longueur totale maximale
   
   - Valeur obligatoire si espèce est mesuré : 
      si espéce (EFA_CODE) est saisi 
       Alors au moins une de ces valeurs : 
       Longueur totale maximale ; Longueur à la fourche ; Masse ; Sexe ; Maturité sexuelle ; doit être saisi

   - Contenu stomacal - Espèce de poisson 1 (EPO_CODE_STOMA_1) VS Contenu stomacal - Espèce de poisson 2 (EPO_CODE_STOMA_2)
      si les deux valeurs sont saisies elles doivent être différentes 
      Si une seule des deux valeur est sasie alors elle doit être dans Contenu stomacal - Espèce de poisson 1 (donc Contenu stomacal - Espèce de poisson 2 ne peut pas être renseignée lorsque Contenu stomacal - Espèce de poisson 1 est vide)
   
   - Valeur interdite pour le champ Espèce : 
      Espèce ne doit pas contenir les valeurs : RIEN (Aucune espèce), AU (Autre espèce), MULTI (Multi espèces), NI (Espèce non identifiée)

   - si Contenu stomacal - Espèce de poisson 1 ou Contenu stomacal - Espèce de poisson 2 
      si Indicateur contenu stomacal poisson à la valeur non (faux) 
         Alors lui assigner la valeur oui (vrai)
   
   - si Indicateur informations supplémentaires disponibles (DSP_IND_INFOR_SUPPL_DISPO) a la valeur oui (vrai) 
      Alors Emplacement (DSP_VAL_EMPLA) doit aussi avoir une valeur
     si Emplacement (DSP_VAL_EMPLA) est saisit Alors Indicateur informations supplémentaires disponibles (DSP_IND_INFOR_SUPPL_DISPO) doit avoir la valeur oui (vrai) 

   - cohérence TypeType de structure conservée pour déterminer l'âge 1 et Type de structure conservée pour déterminer l'âge 2
      si type structure 1 a une valeur différente de AS (Aucune) et type structure 2 a une valeur différente de AS (Aucune) 
         Alors type structure 1  doit être différent de type structure 1
      
      Type structure 2 ne peut pas avoir une valeur lorsque type structure 1 est vide

   - si Numéro échantillon laboratoire 1 est saisi et Age 1 est saisit 
      Alors Type structure 1 doit avoir une valeur et elle doit être différente de AS (Aucune) 

   - si Numéro échantillon laboratoire 2 est saisi et Age 2 est saisit 
      Alors Type structure 2 doit avoir une valeur et elle doit être différente de AS (Aucune) 

   - Valeurs obligatoires : les champs suivants sont obligatoires
      * Numéro de spécimen (DSP_NO_SPECI)
      * Espèce (EFA_CODE) 
      * Longueur totale maximale ou Longueur à la fourche (au moins une longueur est obligatoire)
      * Masse 
      * Sexe
      * Maturité sexuelle
      * Statut du marquage est obligatoire si Type de marquage est saisi 

   - si Type de marquage a l'une des valeurs : "ABNAG", "AUTRE", "CHIM", "COLOR", "CRYO", "EMETT", "MAGN_C", "MAGN_NC", "PIT_TAG", "THERMI", "THERMO", 
      Alors Description de l'étiquette de marquage (DSP_DESCR_ETIQU_MARQU) doit être saisi
     sinon si Type de marquage a l'une des valeurs : "CARLIN", "EXT_AUT", "SPAGH"
         Alors Couleur de l'étiquette (COU_CODE) et Numéro d'étiquette de marquage (DSP_NO_ETIQU_MARQU) doivent être saisis
   
   - Filtre Type de structure selon espèce 
      si Espèce a l'une des valeurs : "ACFU", "ACOX", "ACSP" Alors type structure = ["AU", "AS", "NP"]
      si Espèce a l'une des valeurs : "ESLU", "ESMA" Alors type structure = ["AU", "AS", "CL", "EC"]
      si Espèce a l'une des valeurs : "MIDO", "MISA" Alors type structure = ["AU", "AS", "OP"]
      si Espèce a l'une des valeurs : "PEFL", "SACA" Alors type structure = ["AU", "AS", "ND", "OP", "OT"]
      si Espèce a l'une des valeurs : "SANA", "SAVI" Alors type structure = ["AU", "AS", "OT"]
      si Espèce a l'une des valeurs : "SAAL", "SAFO" Alors type structure = ["AU", "AS", "OT", "EC"]

   - valeurs obligatoires des couches parents  
      . couche / table Pêche expérimentale : vérifier que les valeurs suivantes sont saisies (Aucun spécimen ne peut être créé tant que toutes les caractéristiques de la pêche ne sont pas saisies) 
         * Type de pêche (TPC_CODE)
         * Espèce visée (EFA_CODE)
         * Type d'engin utilisé (TEG_CODE)
      . couche / table Pose et levée
         * Date de pose (PLF_DATE_POSE)
         * Date de levée (PLF_DATE_LEVEE)
   
   - Numéro d'étiquette - échantillon tissus génétique (DSP_NO_ETIQU_GENET) et Numéro d'étiquette - échantillon tissu contamination (DSP_NO_ETIQU_CONTA)
      Attribuer à ces champs la valeur de Numéro échantillon laboratoire 1 (DSP_NO_ECHAN_LABOR_1)

   - si Espèce a la valeur "CACA" (Meunier rouge) et Longueur totale maximale est saisi et Masse est saisi 
      Alors on calcul 
         coeficient1 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être suppérieur ou égal à 0.8
         coeficient2 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être inférieur ou égal à 1.3

   - si Espèce a la valeur "COAR" (Cisco de lac) et Longueur totale maximale est saisi et Masse est saisi 
      Alors on calcul 
         coeficient1 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être suppérieur ou égal à 0.6
         coeficient2 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être inférieur ou égal à 1.1

   - si Espèce a la valeur "COCL" (Grand corégone) et Longueur totale maximale est saisi et Masse est saisi 
      Alors on calcul 
         coeficient1 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être suppérieur ou égal à 0.6
         coeficient2 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être inférieur ou égal à 1.4

    - si Espèce a la valeur "ESLU" (Grand brochet) et Longueur totale maximale est saisi et Masse est saisi 
      Alors on calcul 
         coeficient1 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être suppérieur ou égal à 0.5
         coeficient2 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être inférieur ou égal à 0.9

    - si Espèce a l'une des valeurs "PEFL" (Perchaude), "SAFO" (Omble de fontaine), "CACO" (Meunier noir), et Longueur totale maximale est saisi et Masse est saisi 
      Alors on calcul 
         coeficient1 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être suppérieur ou égal à 0.8
         coeficient2 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être inférieur ou égal à 1.4

    - si Espèce a la valeur "SANA" (Touladi) et Longueur totale maximale est saisi et Masse est saisi 
      Alors on calcul 
         coeficient1 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être suppérieur ou égal à 0.6
         coeficient2 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être inférieur ou égal à 1.2

    - si Espèce a la valeur "SASA" (Saumon atlantique) et Longueur totale maximale est saisi et Masse est saisi 
      Alors on calcul 
         coeficient1 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être suppérieur ou égal à 0.7
         coeficient2 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être inférieur ou égal à 1.4

    - si Espèce a l'une des valeurs "SAAL" (Omble chevalier), "SAVI" (Doré jaune), et Longueur totale maximale est saisi et Masse est saisi 
      Alors on calcul 
         coeficient1 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être suppérieur ou égal à 0.5
         coeficient2 = Masse * 100000 / (longueur totale maximale ^ 3) -> doit être inférieur ou égal à 0.9
