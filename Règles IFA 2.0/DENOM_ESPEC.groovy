# Table / Couche : Dénombrement par espèce (DENOM_ESPEC)

   - Nombre capturé (DES_NB_CAPTU) selon Espèce visée (EFA_CODE) : pendant la saisie de la couche "Dénombrement par espèce" et à la validation du formulaire de saisie

      si Espèce visée (EFA_CODE) est à la valeur "RIEN - Aucune espèce de poisson"
         → Alors Nombre capturé doit être égal à 0 (on assigne automatiquement la valeur 0 à cette variable)
   
   - Longueur minimale (mm) (DES_LONG_MIN_MM) vs Longueur maximale (mm) (DES_LONG_MAX_MM) : pendant la saisie de la couche "Dénombrement par espèce" et à la validation du formulaire de saisie

      si Longueur minimale (mm) est supérieure à Longueur maximale (mm)
      → Alors afficher un message d'erreur pour informer l'utilisateur de corriger les valeurs

   - Nombre capturé (DES_NB_CAPTU) vs Nombre pesé (DES_NB_PESE) : pendant la saisie de la couche "Dénombrement par espèce" et à la validation du formulaire de saisie

      si Nombre pesé est supérieur à Nombre capturé
      → Alors afficher un message d'erreur pour informer l'utilisateur de corriger les valeurs

   
   - Variables obligatoires : A la validation du formulaire de saisie de la couche "Dénombrement par espèce", et pendant la saisie des données
      si Espèce visée (EFA_CODE) a une valeur (différente de "RIEN - Aucune espèce de poisson")
      → Alors Nombre capturé (DES_NB_CAPTU) doit être renseigné (valeur obligatoire)

         si Masse totale (DES_VAL_MASSE_TOTAL_G) est saisi 
         → Alors Nombre pesé (DES_NB_PESE) doit être saisi (valeur obligatoire)
          
         si Nombre pesé (DES_NB_PESE) est saisi 
         → Alors Masse totale (DES_VAL_MASSE_TOTAL_G) doit être saisi (valeur obligatoire)

   - Catégorie de dénombrement (CDE_CODE) : controle de la valeur saisie
      si Catégorie de dénombrement (CDE_CODE) n'est pas saisi, 
       Alors lui attribuer la valeur '-' (Aucune catégorie)
       

   - cohérence Nombre capturé (DES_NB_CAPTU)  
      si Espèce visée (EFA_CODE) n'a pas les valeurs suivantes : NILAB1, NILAB2, NILAB3, RIEN
      → Alors Nombre capturé (DES_NB_CAPTU) doit être supérieur à 0