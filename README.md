# Projet-L1-Informatique-1er-semestre

## Branchements

Capteur Sonore [(wiki)](https://wiki.seeedstudio.com/Grove-Sound_Sensor/): A0 <br>
LED [(wiki)](https://wiki.seeedstudio.com/Grove-Red_LED/): 12

## Analyse fonctionnelle

Introduction

L’idée générale de Sing On Light est de divertir des plus jeunes aux plus vieux en créant un mini-jeu amusant et compétitif afin d’atteindre un public large et universel afin de les amuser avec un jeu de rythme, compréhensible par tous. 

Cette idée s’inspire de multiples mini-jeux créés par la société Nintendo, dont l’influence est mondiale et qui a pu rapprocher enfants et adultes autour de jeux basés sur le son. Le projet fait appel à une Raspberry Pi ainsi que deux capteurs sonores Grove et une LED. 

Le but est simple, la LED clignotera selon un rythme déterminé aléatoirement pendant un certain temps, puis pendant ce même lapse de temps l'utilisateur devra reproduire le rythme de la LED à l'aide de sa voix. 

À la fin de chaque session, l'utilisateur sera informé du pourcentage de réussite qu'il a obtenu; si ce dernier est en dessous d'un pourcentage choisi en paramètre alors c'est perdu. Le score total est alors renvoyé sur le site web associé à notre mini-jeu (à savoir le nombre de sessions réussies et le taux moyen de réussite).

Ce site mettra en avant les sections “Jouer”, “Calibration” et “Données”. Cela permettra notamment de consulter son meilleur score actuel, à l’aide d’un tableau des scores et de lancer une partie, avec un choix sur la difficulté désirée.

Une information importante est qu'avant chaque partie, un paramètre et un calibrage seront mis en place dans la section “Calibration”: 

Le taux barrière (pourcentage au dessus duquel il faut avoir pour gagner une session)
Le calibrage consistera à enregistrer le bruit ambiant pour déterminer l'intensité du son nécessaire pour jouer.

Le produit est alors un pur divertissement destiné à n'importe quelle personne avec une vue active et a pour objectif d'amuser l'utilisateur.
Schéma général du projet

Le dispositif sera composé de :

- Deux capteurs sons (Grove sound sensor)
- Un Raspberry Pi 4 Computer Model B, 2 GB de RAM
- Une LED Rouge

Les données recueillies seront stockées dans une base de données. Ces données seront notamment accessibles depuis notre site, dans l’onglet “Données”. L’humain utilisera notre site comme intermédiaire, notamment afin de lancer une nouvelle partie et inspecter les données relatives au jeu mais interviendra aussi en utilisant un système sonore pour pouvoir jouer au mini-jeu.


Scénarios d’usages

Scénario 1: 

L’utilisateur joue en mode solo. Le Raspberry Pi déclenche la LCD à un rythme aléatoire. Puis, il lit les données des deux capteurs sonores, et les filtre afin de comparer le signal reçu et celui attendu. Selon la précision de la comparaison, un score s'affiche à la fin et permet ou pas à l’utilisateur de continuer sa partie.

Scénario 2: 

Les utilisateurs jouent en mode multijoueur (à deux joueurs). Lors du tour du premier utilisateur, le Raspberry Pi déclenche la LCD à un rythme aléatoire. Puis lit les données des deux capteurs sonores, et les filtres afin de comparer le signal reçu et celui attendu, selon la précision de la comparaison un score s'affiche à la fin de la session du premier utilisateur. Puis le Raspberry Pi refait de même pour le deuxième utilisateur, et affiche à la fin les scores des deux utilisateurs.
