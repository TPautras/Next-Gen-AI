# TD 2 — Partie A : le vote k sur n (quorum)

**Partie A :** Arthur Belloc (seul)
**Données :** traces réelles du TD 1 (`traces-td1.csv`, batch du 2026-10-21), références `reference-td1.csv`. Aucun nouvel appel réseau.
**Code :** `skeleton-multi-llm-en.py` (`Orchestrateur.vote_k_sur_n`), `td2/A-quorum/comparaisons.py`.

## 1. Objectif

Un seul modèle peut se tromper sans qu'on le voie. On fait voter plusieurs modèles de familles différentes : une valeur n'est publiée que si une **majorité stricte** est d'accord, sinon on s'abstient. On compare deux réglages sur les traces du TD 1 : le panel fixe **2 sur 3** et un quorum **3 sur 5** sur les cinq modèles.

## 2. Le vote `vote_k_sur_n`

### 2.1 Le contrat, et comment le code le respecte

| Règle du contrat | Comment c'est fait dans le code |
|---|---|
| Seules les propositions `executed` avec une valeur votent ; un membre en erreur reste dans `n` | `n = len(traces_question)` compte tout le monde ; seules les propositions `verdict == "executed"` et `value is not None` entrent dans le dictionnaire des voix |
| `k` est une majorité stricte : `n // 2 < k <= n`, sinon `ValueError` | clause de garde en tête : `if not n // 2 < k <= n: raise ValueError` |
| Un doublon (même fournisseur et même modèle) est refusé avec `ValueError` | un `set` des couples `(provider, model_requested)` déjà vus ; couple déjà présent → `ValueError` |
| Une valeur qui atteint `k` voix → consensus | dictionnaire `valeur → membres` ; `len(membres) >= k` → `return` du consensus |
| Sinon abstention, avec le plus grand nombre de voix, sans jamais inventer de valeur | `return` **après** la boucle : `value: None`, `models: []`, `votes` = max des `len(membres)` (0 si personne n'a voté) |

**Arrêt au premier consensus.** `k > n/2` : deux valeurs à `k` voix demanderaient `2k > n` votants. Au plus une valeur atteint `k`, donc la première trouvée est la seule.

**Abstention après la boucle.** Une valeur sous `k` ne prouve rien : la suivante peut l'atteindre. Avec `[0, 100, 100]` et `k = 2`, un `return` dans un `else` s'arrêtait sur 0 et ratait le consensus sur 100. On ne conclut à l'abstention qu'une fois toutes les valeurs vues.

### 2.2 Tests du contrat : 12/12

`python3 td2/A-quorum/vote_tests.py` → `td2/A-quorum/voting-tests.csv` (exemples **synthétiques**, nature `simulation`).

| Test | n | k | Valeurs proposées | Indisponibles | Résultat obtenu | Passe |
|---|---|---|---|---|---|---|
| T1-agreement | 3 | 2 | 100 100 120 | 0 | consensus 100 (2 voix) | yes |
| T2-unanimity | 3 | 3 | 100 100 100 | 0 | consensus 100 (3 voix) | yes |
| T3-disagreement | 3 | 2 | 100 110 120 | 0 | abstention (1 voix max) | yes |
| T4-one-unavailable-agree | 3 | 2 | 100 None 100 | 1 | consensus 100 (2 voix) | yes |
| T5-two-unavailable | 3 | 2 | 100 None None | 2 | abstention (1 voix max) | yes |
| T6-all-unavailable | 3 | 2 | None None None | 3 | abstention (0 voix max) | yes |
| T7-wrong-consensus | 3 | 2 | 0 0 100 | 0 | consensus 0 (2 voix) | yes |
| T8-3of5-unavailable-in-n | 5 | 3 | 100 100 None None 120 | 2 | abstention (2 voix max) | yes |
| T9-3of5-agreement | 5 | 3 | 100 100 90 100 None | 1 | consensus 100 (3 voix) | yes |
| T10-duplicate-route | 3 | 2 | 100 100 120 | 0 | ValueError: doublon : groq:openai/gpt-oss-120b | yes |
| T11-k-not-majority | 3 | 1 | 100 110 120 | 0 | ValueError: Seuil n'est pas une majorité stricte. | yes |
| T12-k-above-n | 3 | 4 | 100 100 100 | 0 | ValueError: Seuil n'est pas une majorité stricte. | yes |

- **T6** : tous les membres indisponibles. Personne ne vote, `votes = 0`, abstention ; pas de plantage sur un `max` vide.
- **T8** : 3 sur 5 avec des membres indisponibles. Ils restent dans `n = 5`, donc il faut toujours 3 voix ; 2 voix ne suffisent pas.

### 2.3 Les quatre exemples de l'atelier

`python3 atelier-vote.py` (exemples **synthétiques** fournis par l'énoncé).

| Exemple | n | k | Décision | Référence | Accord |
|---|---|---|---|---|---|
| agreement | 3 | 2 | consensus 100 (2 voix) | 100 | oui |
| disagreement | 3 | 2 | abstention (1 voix max) | 100 | — |
| unavailable | 3 | 2 | abstention (1 voix max) | 100 | — |
| wrong consensus | 3 | 2 | consensus 0 (2 voix) | 100 | non |

Pas de bug : deux membres sur trois proposent 0, donc `k = 2` est atteint et le contrat impose de publier. Le vote ne voit jamais la référence. **Un consensus prouve un accord, pas une vérité** : des modèles proches peuvent partager la même erreur (voir partie B).

## 3. Panel 2 sur 3 contre quorum 3 sur 5 sur les 20 questions

- **Panel 2 sur 3** (fixe, `atelier-vote.py`) : `groq:openai/gpt-oss-120b`, `openrouter:cohere/north-mini-code:free`, `groq:qwen/qwen3.8-27b`, `k = 2`.
- **Quorum 3 sur 5** : les cinq modèles du TD 1 (le panel + `groq:openai/gpt-oss-20b` et `openrouter:dots-studio/dots-3-note-preview:free`), `k = 3`.
- Pour chaque membre : sa **dernière tentative** sur la question ; un membre sans réponse exploitable reste dans `n` sans voter.
- La référence n'est utilisée qu'**après** la décision, pour la colonne « Accord ».

Reproduire : `python3 td2/A-quorum/comparaisons.py`

| Question | Référence | 2 sur 3 (panel fixe) | Accord | 3 sur 5 (5 modèles) | Accord | Change ? |
|---|---|---|---|---|---|---|
| C01 | 792800 | consensus 792800 (3 voix) | oui | consensus 792800 (5 voix) | oui |  |
| C02 | 590320 | consensus 590320 (2 voix) | oui | abstention (2 voix max) | — | **décision** |
| C03 | 936350 | consensus 936350 (3 voix) | oui | consensus 936350 (5 voix) | oui |  |
| C04 | 2826250 | consensus 2826250 (3 voix) | oui | consensus 2826250 (5 voix) | oui |  |
| C05 | 38480 | consensus 38480 (3 voix) | oui | consensus 38480 (5 voix) | oui |  |
| C06 | 0 | consensus 0 (3 voix) | oui | consensus 0 (5 voix) | oui |  |
| C07 | 13970 | consensus 13970 (3 voix) | oui | consensus 13970 (5 voix) | oui |  |
| C08 | 605580 | consensus 605580 (2 voix) | oui | abstention (2 voix max) | — | **décision** |
| C09 | 487980 | consensus 487980 (2 voix) | oui | consensus 487980 (4 voix) | oui |  |
| C10 | 558980 | abstention (1 voix max) | — | abstention (2 voix max) | — | marge |
| C11 | 446690 | consensus 446690 (2 voix) | oui | consensus 446690 (3 voix) | oui |  |
| C12 | 1666490 | consensus 1666490 (3 voix) | oui | consensus 1666490 (5 voix) | oui |  |
| C13 | 107740 | consensus 107740 (3 voix) | oui | consensus 107740 (5 voix) | oui |  |
| C14 | 0 | consensus 0 (3 voix) | oui | consensus 0 (5 voix) | oui |  |
| C15 | 168680 | consensus 168680 (2 voix) | oui | consensus 168680 (3 voix) | oui |  |
| C16 | 376740 | consensus 376740 (3 voix) | oui | consensus 376740 (4 voix) | oui |  |
| C17 | 258180 | abstention (1 voix max) | — | abstention (2 voix max) | — | marge |
| C18 | 62480 | consensus 62480 (3 voix) | oui | consensus 62480 (4 voix) | oui |  |
| C19 | 1990 | consensus 1990 (2 voix) | oui | consensus 1990 (4 voix) | oui |  |
| C20 | 1106090 | consensus 1106090 (3 voix) | oui | consensus 1106090 (5 voix) | oui |  |

« **décision** » : l'un des votes publie, l'autre s'abstient. « marge » : les deux s'abstiennent, mais le nombre maximal de voix diffère.

| | 2 sur 3 | 3 sur 5 |
|---|---|---|
| Consensus justes | 18 | 16 |
| Consensus faux | **0** | **0** |
| Abstentions | 2 (C10, C17) | 4 (C02, C08, C10, C17) |

## 4. Les questions où le passage de 2 sur 3 à 3 sur 5 change le résultat

### C02 — la décision change (référence 590320)

| Modèle | Dans le panel 2 sur 3 ? | Valeur | Verdict de la trace | Juste ? |
|---|---|---|---|---|
| `groq:openai/gpt-oss-120b` | oui | 590320 | correct | oui |
| `openrouter:cohere/north-mini-code:free` | oui | 0 | incorrect | non |
| `groq:qwen/qwen3.8-27b` | oui | 590320 | correct | oui |
| `groq:openai/gpt-oss-20b` | non | 321340 | incorrect | non |
| `openrouter:dots-studio/dots-3-note-preview:free` | non | 135000 | incorrect | non |

- **2 sur 3** : 120b et qwen donnent 590320 → 2 voix = `k`, **consensus juste**.
- **3 sur 5** : la bonne valeur garde 2 voix, il en faut 3. north (0), 20b (321340) et dots (135000) se trompent **chacun différemment** : aucune autre valeur n'a plus d'une voix → **abstention**.
- Les deux modèles ajoutés ne votent pas pour la bonne valeur : ils diluent la majorité.

### C08 — la décision change (référence 605580)

| Modèle | Dans le panel 2 sur 3 ? | Valeur | Verdict de la trace | Juste ? |
|---|---|---|---|---|
| `groq:openai/gpt-oss-120b` | oui | 605580 | correct | oui |
| `openrouter:cohere/north-mini-code:free` | oui | 1553040 | incorrect | non |
| `groq:qwen/qwen3.8-27b` | oui | 605580 | correct | oui |
| `groq:openai/gpt-oss-20b` | non | 25920 | incorrect | non |
| `openrouter:dots-studio/dots-3-note-preview:free` | non | 186340 | incorrect | non |

Même mécanisme : 120b et qwen justes (605580), north, 20b et dots faux et dispersés (1553040, 25920, 186340). Consensus juste en 2 sur 3, abstention en 3 sur 5.

**Commun à C02 et C08** : questions d'**âge à une date** ; seuls 120b et qwen sont justes. Le quorum 3 sur 5 refuse de publier une valeur juste.

### C10 — la marge change (référence 558980)

| Modèle | Dans le panel 2 sur 3 ? | Valeur | Verdict de la trace | Juste ? |
|---|---|---|---|---|
| `groq:openai/gpt-oss-120b` | oui | 558980 | correct | oui |
| `openrouter:cohere/north-mini-code:free` | oui | 0 | incorrect | non |
| `groq:qwen/qwen3.8-27b` | oui | 119410 | incorrect | non |
| `groq:openai/gpt-oss-20b` | non | 558980 | correct | oui |
| `openrouter:dots-studio/dots-3-note-preview:free` | non | 119410 | incorrect | non |

- **2 sur 3** : 558980 (120b), 0 (north), 119410 (qwen) → 1 voix max, **abstention**.
- **3 sur 5** : 558980 (120b, 20b) et **119410 (qwen, dots)** → 2 voix chacune, il en faut 3, **abstention**.
- La valeur **fausse** 119410 fait jeu égal avec la bonne. Un panel north + qwen + dots en 2 sur 3 l'aurait publiée : c'est le **faux consensus** de la partie B.

### C17 — la marge change (référence 258180)

| Modèle | Dans le panel 2 sur 3 ? | Valeur | Verdict de la trace | Juste ? |
|---|---|---|---|---|
| `groq:openai/gpt-oss-120b` | oui | 258180 | correct | oui |
| `openrouter:cohere/north-mini-code:free` | oui | 197080 | incorrect | non |
| `groq:qwen/qwen3.8-27b` | oui | — | not_executed (2 tentatives, HTTP 429) | — |
| `groq:openai/gpt-oss-20b` | non | 258180 | correct | oui |
| `openrouter:dots-studio/dots-3-note-preview:free` | non | 152730 | incorrect | non |

- qwen prend **deux HTTP 429** (`not_executed`) : il reste dans `n = 3` mais **ne vote pas**.
- **2 sur 3** : 120b (258180) contre north (197080) → 1 voix max, **abstention**. Le 429 coûte la décision : il ne reste que deux votants en désaccord.
- **3 sur 5** : 20b rejoint 120b sur 258180 → 2 voix, il en faut 3 (`n = 5` malgré le 429), **abstention**.

## 5. Bilan

- **Erreurs publiées** : 0 dans les deux cas sur ce batch. Le 3 sur 5 n'en évite aucune de plus ici.
- **Prix du 3 sur 5** : 2 abstentions de plus (C02, C08) sur des valeurs **justes**, et 5 appels au lieu de 3.
- **Plus de modèles ≠ plus de décisions** : des modèles faibles qui se trompent chacun à leur façon diluent la bonne réponse.
- **Usage** : 2 sur 3 pour un chiffre montré au client (publie plus, reste majoritaire) ; 3 sur 5, plus des contrôles déterministes, pour un montant versé, où une abstention coûte moins qu'une erreur.

## 6. Limites

- **Un tirage par cellule** : un autre tirage peut changer C10 ou C17.
- **20 questions** : une hypothèse sur ce batch, pas un taux d'erreur général ni une garantie du quorum.
- **Familles proches** : un quorum ne protège pas contre une erreur partagée (C10, partie B).
- **Indisponibilités** : un 429 réduit le nombre de votants sans réduire `n`, donc rend l'abstention plus probable.

## 7. Reproduire

```
python3 td2/A-quorum/vote_tests.py          # 12 tests du contrat -> td2/A-quorum/voting-tests.csv
python3 atelier-vote.py            # 4 exemples synthétiques
python3 atelier-vote.py --traces traces-td1.csv --case C02   # une question réelle, panel fixe
python3 td2/A-quorum/comparaisons.py        # tableau 2 sur 3 contre 3 sur 5
```

## 8. Contribution

- **Arthur Belloc** (seul sur la partie A) : réécriture de `vote_k_sur_n`, `td2/A-quorum/comparaisons.py` (tableau 2 sur 3 / 3 sur 5), ce rapport.
- **Relecture** : indentation et propreté du code vérifiées (`vote_k_sur_n`, `td2/A-quorum/comparaisons.py`).
