# race
Tennis fantasy race folder with Tristan, Remy, François, and Jules. THE RACE — ligue de fantasy tennis entre amis : classements, duels entre équipes et statistiques des joueurs, saison par saison. Saison 2026 en cours, mise à jour chaque lundi ; saisons précédentes à venir.

**Site :** https://peozenou.github.io/race/ · saison 2026 : https://peozenou.github.io/race/2026/

## Organisation

| Dossier | Contenu |
|---|---|
| `index.html` | Page d'accueil : liste des saisons |
| `2026/` | Tableau de bord de la saison 2026 (même code que la version maîtresse tenue dans Claude) |
| `2026/data/` | Données de la semaine : totaux d'équipe (HEBDO), points Race des joueurs (JOUEURS), statistiques des joueurs, matchs, calendrier, couleurs |
| `2026/source/dashboard.html` | Code de la page exporté du tableau de bord Claude |
| `2026/assets/` | Petit moteur qui charge les données (`runtime.js`), thème (`theme.css`), d3 v7.9.0 (licence ISC, © Mike Bostock) |
| `2026/tutoriel.mp4` | Vidéo de 1 min 30 : comment naviguer dans le tableau de bord 2026 |
| `2026/tools/` | `build.py` reconstruit `2026/index.html` ; `preview.py` régénère l'image d'aperçu WhatsApp ; `tutorial.py` réenregistre la vidéo |

Une saison précédente s'ajoute dans son propre dossier (`2025/`, `2024/`…) et une carte sur la page d'accueil.

## Mise à jour hebdomadaire

Après validation de la mise à jour du lundi :

1. Remplacer les fichiers de `2026/data/` par le nouvel instantané (mêmes noms).
2. Si la page a changé dans Claude, remplacer `2026/source/dashboard.html`.
3. `python3 2026/tools/build.py` (et `2026/tools/preview.py` sur un serveur local pour une nouvelle image d'aperçu).
4. Commit et push sur `main` : GitHub Pages republie en une à deux minutes.

Sources : Tennis Abstract (matchs, bilans, Elo/yElo) et Tennis Explorer (classements et points ATP et Race).
