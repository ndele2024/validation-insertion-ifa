# Table / Couche : Analyse physico-chimique (ANALY_PHYSI_CHIMI)

   - Numéro de station (PHC_NO_STATI) : à la validation du formulaire de saisie de la couche "Analyse physico-chimique"
      valeur obligatoire

   - Appareil & Autre appareil : lors de la saisie et à la validation du formulaire de saisie de la couche "Analyse physico-chimique"

      Si (Appareil est vide) ET (Autre appareil est renseigné)
      → Alors Appareil = "AUTRE - Autre appareil"
         dans ce cas autre appareil doit spécifier la marque le modéle et la précision de cet autre appareil sinon indiquer "inconnu"
      
      quand un utilisateur saisit quelque chose dans le champ "Autre appareil" sans avoir choisi un appareil standard, la règle remplit automatiquement le champ "Appareil" avec la valeur générique 'AUTRE', pour assurer la cohérence des données.

      si on a renseigné au moin un profil de mesures (PROFI_MESUR) 
         alors "Appareil" doit être renseigné (ne peut pas être vide)



   - Territoire faunique vs Région administrative du projet : à l'ouverture et à la validation du formulaire de saisie de la couche "Analyse physico-chimique"

      Si le projet n'a pas de région administrative 
      → Alors aucun filtre n'est appliqué sur le champ "Territoire faunique"
      Sinon 
      → Alors le champ "Territoire faunique" est filtré pour n'afficher que les territoires fauniques situés dans la région administrative du projet. (cas particulier : pour la région 04 - Mauricie, filtrer les territoires fauniques avec 04 - Mauricie et 17 - Centre-du-Québecc)

      si Type de plan d''eau de "information générales" à la valeur 'L-lac'
      → Alors ne pas mesurer territoire faunique (on le désactive du formulaire)
      sinon mesurer (on laisse activer le champ territoire faunique)


   - Date de visite de la station : pendant la saisie de la couche "Analyse physico-chimique" et à la validation du formulaire de saisie

      si la date n'est pas renseignée
      → Alors lui assigner la valeur de date de début d'inventaire de la table "Informations générales"

      La date de visite doit être suppérieure à la date de debut d'inventaire et inférieure à la date de fin d'inventaire de la table/couche "Informations générales". Si ce n'est pas le cas, un message d'erreur doit être affiché pour informer l'utilisateur de corriger la date.

      la date de visite de la sation est obligatoire




      