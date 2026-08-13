# Table / Couche : Description de l'habitat (DESCR_HABIT)

   - Date (DHA_DATE) : A la validation du formulaire 
      La date est obligatoire

      si la date n'est pas renseignée
      → Alors lui assigner la valeur de date de début d'inventaire de la table "Informations générales"

   - Profondeur de la prise de données de vitesse du courant (DHA_PRFD_VITES_COURA) : A la validation du formulaire 
      si Vitesse courant avec profondeur (DHA_VAL_VITES_COURA) est saisie et Profondeur donnée courant n'est pas renseigée
      → Alors assigner à Profondeur donnée courant la valeur 0
   
   - Superficie (DHA_SUPRF) : A la validation et pendant la saisie du formulaire
      si longueur est saisie et largeur est saisie 
      → Alors assigner à Superficie la valeur longueur x largeur 
   
   - Territoire faunique (DHA_NOM_TERRI_FAUNI) : pendant la saisie et à la validation
      Filtrer les valeurs du territoire faunique en fonction de la région administrative (même algorithme que pour la couche Analyse-physico-chimique)
      si Type de plan d'eau de "information générales" à la valeur 'L-lac'
      → Alors ne pas mesurer territoire faunique (on le désactive du formulaire)
      sinon mesurer (on laisse activer le champ territoire faunique)
 