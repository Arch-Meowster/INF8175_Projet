
# Plan du projet

> Dernière mise à jour : 2026/10/28

# 1. Présentation du projet

Créé un agent capable de jouer au jeux Quoridor. 

# 2. Plan de travail

- [ ] Compléter l'heuristique
  - [ ] Définir les paramètre à utiliser et leur poid
- [ ] Définir des ouvertures (pt regarder dans la littérature, j'ai vu que y'avais des ouverture commune)
- [ ] Amélioré le pruning
- [ ] Définir la profondeur qu'on peutr allé après avoir optimiser

# 3. Idées 

## Heuristique 

Ce que je pensais qu'on pourrait utilisé pour le calcul de l'heuristique:
- Qui joue en premier, donc avoir un poid pour le tour de jeux, car si pour les deux personnes c'est la même distance, mais que l'adverse joue en premier, alors c'est lui qui va gagner. Donc soit additionner une valeur pour le tour que c'est la personne ou multiplier par 0,5 pour la personne que ce n'Est pas le tour. À déterminer encore. 
- Mettre les murs restant dans l'heuristique à considérer. Donc avoir quelque chose comme ``` score = ... + α × (murs_moi − murs_adv)``` où alpha est à déterminer. Souvent cela fait perdre 2 déplacement à une perosnne donc pt faire x2, mais tout dépendant où le mur est placé et quand. Si le mur est placé en début de partie, ca déranger vraiment que en milieu ou en fin de partie. Donc, pt faire varier alpha durant la partie. 
- Faire en sorte que lorsqu'il ne reste plus de mur, il calcul directement le chemin le plus court et ne perd pas de temps avec le calcul du mur. 
- Mettre un poid sur le positionnement des murs en fonction des chemins. Genre si on a un chemin d'une case de large, alors c'est beaucoup plus d'engeureux d'aller là car on peux ce faire bloqué facilement. Genre, essaie de mettre un poid sur à quel point on est vulnérable à ce faire bloqué.
- Regarder le chemin le plus cours de l'adversaire aussi. Voir si on peux le bloqué. 


## Algorithme — Minmax

Explication du fonctionnement:

Amélioratiojn possible:
- Pour le alpha-bêta prunnning: Calculer si un mur rallonge aussi notre chemin, genre pour trier en fonctione des meilleur au pire. Si ca rallonge aussi notre chemin alors on le trie pour qu'il soit a la fin ou je sais pas. 
- 


# 4. Explication des versions

## 4.3 - Version 3

### Explication des changements 


## 4.2 - Version 2



## 4.1 - Version 1



