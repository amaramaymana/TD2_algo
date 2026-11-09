# Ordonnancement de la maintenance de centrales électriques par algorithme génétique

Résolution par algorithme génétique (AG) du problème de la cédule de maintenance : planifier l'arrêt de 7 unités de production sur 4 intervalles de l'année afin de **maximiser la plus petite réserve de puissance**.

## Contenu

| Fichier | Description |
|---|---|
| `ag_maintenance.py` | Implémentation complète de l'AG (Python 3, bibliothèque standard uniquement) |
| `README.md` | Ce document |

## Énoncé

| Unité | Capacité (MW) | Intervalles de maintenance requis |
|---|---|---|
| 1 | 20 | 2 |
| 2 | 15 | 2 |
| 3 | 35 | 1 |
| 4 | 40 | 1 |
| 5 | 15 | 1 |
| 6 | 15 | 1 |
| 7 | 10 | 1 |

- Capacité totale : 150 MW
- 4 intervalles, demande : 80, 90, 65 et 70 MW
- La maintenance d'une unité commence au début d'un intervalle et se termine à la fin d'un intervalle ; pour les unités à 2 intervalles, ceux-ci sont consécutifs.
- La réserve de chaque intervalle doit rester supérieure à zéro.

## Formulation

**Variables** : x(u,t) ∈ {0,1}, égal à 1 si l'unité *u* est en maintenance à l'intervalle *t*.

**Réserve** à l'intervalle *t* :

```
R(t) = Capacité_totale − Σ_u ( C(u) · x(u,t) ) − D(t)
```

**Fonction objective (à maximiser)** :

```
f = max( 0 , min_t R(t) )
```

**Contraintes** :
- Σ_t x(u,t) = d(u) pour chaque unité (durée de maintenance)
- intervalles consécutifs pour les unités 1 et 2
- R(t) ≥ 0

## Codage

Un chromosome est composé de **7 gènes de 4 bits** (un gène par unité, un bit par intervalle ; `1` = maintenance, `0` = en service).

- Unités 1 et 2 : `1100`, `0110`, `0011`
- Unités 3 à 7 : `1000`, `0100`, `0010`, `0001`

Exemple : `0110 0011 0001 1000 0100 0010 1000`

La population initiale n'utilise que des motifs admissibles : aucune cédule illogique n'est générée.

## Opérateurs génétiques

- **Sélection par loterie (roulette)** : probabilité de sélection proportionnelle à la performance.
- **Croisement à un point**, uniquement aux frontières de gènes (blocs de 4 bits).
- **Mutation par inversion** : pour chaque gène, avec probabilité `pm`, l'ordre des bits est inversé (`1100 → 0011`, `1000 → 0001`, `0110 → 0110`). L'ensemble des motifs admissibles étant stable par inversion, le chromosome reste toujours valide.
- **Mutation par remplacement** (variante de comparaison) : le gène est remplacé par un autre motif admissible de la même unité.
- **Élitisme** : le meilleur individu est conservé à chaque génération.

## Utilisation

Prérequis : Python 3.8 ou plus récent.

```bash
python ag_maintenance.py
```

Le script lance l'AG avec les deux types de mutation et affiche, pour chacun, l'évolution de la performance, la meilleure cédule, les réserves par intervalle et la performance finale.

### Utilisation comme module

```python
from ag_maintenance import ag, mutation_inversion, reserves, fitness, affiche

meilleur, historique = ag(
    taille_pop=42,   # 6 à 7 fois le nombre de variables
    n_gen=60,
    pc=0.8,          # probabilité de croisement
    pm=0.1,          # probabilité de mutation par gène
    mutation=mutation_inversion,
    elitisme=True,
    seed=42,         # reproductibilité
)
print(affiche(meilleur), reserves(meilleur), fitness(meilleur))
```

### Paramètres principaux

| Paramètre | Valeur par défaut | Rôle |
|---|---|---|
| `taille_pop` | 42 | Taille de la population |
| `n_gen` | 60 | Nombre de générations |
| `pc` | 0,8 | Probabilité de croisement |
| `pm` | 0,1 | Probabilité de mutation par gène |
| `mutation` | `mutation_inversion` | Opérateur de mutation |
| `elitisme` | `True` | Conservation du meilleur individu |
| `seed` | `None` | Graine aléatoire |

## Résultats (seed = 42)

| Mutation | Meilleure cédule | Réserves (MW) | Performance |
|---|---|---|---|
| Inversion | `1100 0110 0010 0001 0001 1000 1000` | 25, 25, 35, 25 | **25** |
| Remplacement | `1100 1100 0001 0010 0001 0010 1000` | 25, 25, 30, 30 | **25** |

**25 MW est l'optimum.** La maintenance totale représente 185 MW·intervalle, donc la somme des réserves vaut 4 × 150 − 185 − 305 = 110 MW. La plus petite réserve ne peut donc pas dépasser 27,5 MW, et comme toutes les capacités sont des multiples de 5, la meilleure valeur atteignable est 25.

## Pistes d'expérimentation

- Faire varier `pc`, `pm` et `taille_pop`, puis comparer les courbes de convergence (l'historique est renvoyé par `ag()`).
- Comparer avec et sans élitisme.
- Comparer les deux mutations sur plusieurs graines et calculer la performance moyenne.
- Ajouter d'autres contraintes (délais d'équipement, interruptions de service) dans `fitness`.