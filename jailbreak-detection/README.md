# Module B — Détection de Jailbreak / Prompt-Injection

Détecter si un prompt utilisateur tente de **contourner les garde-fous** d'un LLM.
Aligné **OWASP LLM Top 10 — LLM01:2025 (Prompt Injection)** et MITRE **ATLAS**.

## Deux approches (complémentaires)

1. **Classifieur par embeddings** (`detector.py`) — on encode le prompt avec un modèle
   HuggingFace (`sentence-transformers`, local), puis un classifieur (régression logistique)
   décide *jailbreak* vs *bénin*. Rapide, offline, explicable, ré-entraînable.
2. **LLM-judge / guardrail** (`guardrail.py`) — un LLM local (Ollama) juge le prompt et
   renvoie un verdict + la raison. Plus souple sur les attaques jamais vues.

## Datasets (publics, recherche)

| Dataset | Contenu |
|---|---|
| **JailbreakBench (JBB-Behaviors)** | prompts de jailbreak + refus/benign |
| **In-the-wild jailbreak prompts** | prompts collectés sur Reddit/Discord |
| Prompts **bénins** | questions normales (pour la classe négative) |

> Place un CSV `data/prompts.csv` avec colonnes `text,label` (`label` = 1 jailbreak, 0 bénin).

## Utilisation

```bash
# 1) Entraîner + évaluer le classifieur par embeddings
python src/evaluate.py --data data/prompts.csv

# 2) Tester le guardrail LLM local
ollama pull llama3.1:8b
python src/guardrail.py --model llama3.1:8b
```

## Métriques qui comptent

- **Recall sur la classe jailbreak** (ne pas laisser passer une attaque)
- **Précision** (ne pas bloquer des utilisateurs légitimes → faux positifs)
- **ROC-AUC**, matrice de confusion, et robustesse aux variantes (obfuscation, langues).

## Pour aller plus loin

- Red-team ton propre détecteur avec des outils comme **garak** / **promptfoo**.
- Tester l'**injection indirecte** (charge utile cachée dans un document fourni au LLM).
