%Affectation
∃ ch ∊ ϩ. % On déclare...
ch ≔ "Hello World !". %Puis on affecte.
%quand on execute ce bout de code seul, on se rend compte que l'interpreteur nous affiche des messages...
%"Variable ch created with type ϩ"
%"Variable ch has recieved the value : Hello World !"
%Ces messages peuvent être bien utiles pour le developpeur, mais peuvent être inutiles voire génants lors de l'utilisation
%Pour enlever ces messages, il suffit d'ajouter l'instruction @HIDE. au début du code.

%On peut vouloir afficher notre message, on utilise pour cela : echo
echo$ch.

%On peut demander à l'utilisateur une valeur
%Pour cela on crée la variable qui contiendra la valeur:
∃ ANS ∊ ℕ.
%On définit le message à afficher :
ch ≔ "Donnez un entier positif ou nul : ".
%Puis on pose la question en spécifiant le type souhaité :
ANS ≔ ask$ℕ$ch.
%Et le tour est joué !

