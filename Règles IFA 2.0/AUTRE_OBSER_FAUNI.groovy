# Table / Couche : Autres observations fauniques (AUTRE_OBSER_FAUNI)

   - Territoire faunique vs Région administrative du projet : à l'ouverture du formulaire de saisie de la couche "Autres observations fauniques"
   
      Filtrer le champ "Territoire faunique" pour n'afficher que les territoires fauniques situés dans la région administrative du projet. (cas particulier : pour la région 04 - Mauricie, filtrer les territoires fauniques avec 04 - Mauricie et 17 - Centre-du-Québecc)

      à la validation du formulaire de saisie de la couche "Autres observations fauniques" :

      si Type de plan d'eau de "information générales" à la valeur 'L-lac'
      → Alors ne pas mesurer territoire faunique (on le désactive du formulaire)
      sinon mesurer (on laisse activer le champ territoire faunique)


   - Date de l'observation : pendant la saisie de la couche "Autres observations fauniques" et à la validation du formulaire de saisie
      si la date n'est pas renseignée
      → Alors lui assigner la valeur de date de début d'inventaire de la table "Informations générales"

      La date de l'observation doit être supérieure à la date de debut d'inventaire et inférieure à la date de fin d'inventaire de la table/couche "Informations générales". Si ce n'est pas le cas, un message d'erreur doit être affiché pour informer l'utilisateur de corriger la date.

      la date de l'observation est obligatoire si elle n'est pas renseignée, la valeur par défaut est la date de début d'inventaire de la table "Informations générales"

   - Espèce visée (EFA_CODE) : pendant la saisie de la couche "Autres observations fauniques" et à la validation du formulaire de saisie
      
      Valeur obligatoire

      si catégorie d'espèce est mesurée 
         si espèce visée est à la valeur "A - Amphibien"
            filtrer le champ "Espèce visée" avec "A - Amphibien"
         sinon si espèce visée est à la valeur "C - Crustacé"
            filtrer le champ "Espèce visée" avec "C - Crustacé"
         sinon si espèce visée est à la valeur "MA - Mammifère"
            filtrer le champ "Espèce visée" avec "MA - Mammifère"
         sinon si espèce visée est à la valeur "MO - Mollusque"
            filtrer le champ "Espèce visée" avec "MO - Mollusque"
         sinon si espèce visée est à la valeur "O - Oiseau"
            filtrer le champ "Espèce visée" avec "O - Oiseau"
         sinon si espèce visée est à la valeur "R - Reptile"
            filtrer le champ "Espèce visée" avec "R - Reptile"
         sinon si espèce visée est à la valeur "PP - Plantes Précaires"
            filtrer le champ "Espèce visée" avec "PP - Plantes Précaires"
         sinon aucun filtre n'est appliqué sur le champ "Espèce visée" (on affiche toutes les espèces)
      sinon aucun filtre n'est appliqué sur le champ "Espèce visée" (on affiche toutes les espèces)
   
   - Catégorie d'espèce (CEF_CODE)
      Valeur obligatoire 

   - Latitude (AOF_LATIT) et Longitude (AOF_LONGIT)
      Valeurs obligatoires
