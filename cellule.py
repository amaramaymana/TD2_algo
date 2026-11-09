
import random

# 1. Données du problème
CAPACITE = [20, 15, 35, 40, 15, 15, 10]      # MW par unité
DUREE    = [2, 2, 1, 1, 1, 1, 1]             # nb d'intervalles de maintenance
DEMANDE  = [80, 90, 65, 70]                  # MW par intervalle
N_UNITES = len(CAPACITE)
N_INT    = len(DEMANDE)
CAP_TOT  = sum(CAPACITE)                     # 150 MW


def patterns_possibles(duree, n=N_INT):
    """Maintenance sur `duree` intervalles CONSÉCUTIFS (ex: 1100, 0110, 0011)."""
    res = []
    for debut in range(n - duree + 1):
        bits = [0] * n
        for k in range(duree):
            bits[debut + k] = 1
        res.append(tuple(bits))
    return res


PATTERNS = [patterns_possibles(d) for d in DUREE]   # gènes admissibles par unité

# 2. Chromosome et fonction objective
def creer_chromosome():
    return [random.choice(PATTERNS[u]) for u in range(N_UNITES)]


def reserves(chromo):
    """Réserve par intervalle = capacité totale - puissance en maintenance - demande."""
    res = []
    for t in range(N_INT):
        perdue = sum(CAPACITE[u] * chromo[u][t] for u in range(N_UNITES))
        res.append(CAP_TOT - perdue - DEMANDE[t])
    return res


def fitness(chromo):
    """Performance = plus petite réserve (0 si négative). À MAXIMISER."""
    return max(0, min(reserves(chromo)))


def affiche(chromo):
    return " ".join("".join(map(str, g)) for g in chromo)

# 3. Opérateurs génétiques
def selection_loterie(pop, fits):
    """Roulette : probabilité de sélection proportionnelle à la performance."""
    total = sum(fits)
    if total == 0:                       # population entièrement nulle
        return random.choice(pop)
    tirage = random.uniform(0, total)
    cumul = 0
    for ind, f in zip(pop, fits):
        cumul += f
        if cumul >= tirage:
            return ind
    return pop[-1]


def croisement(p1, p2, pc):
    """Croisement à un point, uniquement entre deux gènes (blocs de 4 bits)."""
    if random.random() < pc:
        pt = random.randint(1, N_UNITES - 1)
        return p1[:pt] + p2[pt:], p2[:pt] + p1[pt:]
    return p1[:], p2[:]


def mutation_inversion(chromo, pm):
    """Pour chaque gène, avec proba pm, on inverse l'ordre de ses bits
    (1100 -> 0011, 1000 -> 0001, 0110 -> 0110).
    Le résultat reste toujours une maintenance valide (consécutive)."""
    return [tuple(reversed(g)) if random.random() < pm else g for g in chromo]


def mutation_remplacement(chromo, pm):
    """Variante : le gène est remplacé par un autre motif admissible de l'unité."""
    nouveau = []
    for u, g in enumerate(chromo):
        if random.random() < pm:
            g = random.choice(PATTERNS[u])
        nouveau.append(g)
    return nouveau

# 4. Algorithme génétique
def ag(taille_pop=None, n_gen=60, pc=0.8, pm=0.1,
       mutation=mutation_inversion, elitisme=True, seed=None, verbose=True):
    if seed is not None:
        random.seed(seed)
    if taille_pop is None:
        taille_pop = 6 * N_UNITES            # règle du cours : 6 à 7 x nb de variables
    pop = [creer_chromosome() for _ in range(taille_pop)]
    meilleur, historique = None, []

    for gen in range(n_gen):
        fits = [fitness(c) for c in pop]
        i_best = max(range(taille_pop), key=lambda i: fits[i])
        if meilleur is None or fits[i_best] > fitness(meilleur):
            meilleur = pop[i_best][:]
        historique.append(max(fits))
        if verbose and (gen % 10 == 0 or gen == n_gen - 1):
            print(f"Gén {gen:3d} | meilleure = {max(fits):3d} | moyenne = {sum(fits)/len(fits):5.1f}")

        nouvelle = [meilleur[:]] if elitisme else []
        while len(nouvelle) < taille_pop:
            p1 = selection_loterie(pop, fits)
            p2 = selection_loterie(pop, fits)
            e1, e2 = croisement(p1, p2, pc)
            nouvelle.append(mutation(e1, pm))
            if len(nouvelle) < taille_pop:
                nouvelle.append(mutation(e2, pm))
        pop = nouvelle

    return meilleur, historique


if __name__ == "__main__":
    for nom, mut in [("INVERSION", mutation_inversion),
                     ("REMPLACEMENT", mutation_remplacement)]:
        print(f"\nMutation par {nom}")
        best, hist = ag(mutation=mut, seed=42)
        print("Meilleure cédule :", affiche(best))
        print("Réserves par intervalle :", reserves(best))
        print("Performance (réserve minimale) :", fitness(best))