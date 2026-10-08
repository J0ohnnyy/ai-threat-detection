# Architecture & design

## Principe directeur : **tout en local**

Aucune donnée (flux réseau, prompts) ne quitte la machine. Les LLM tournent via **Ollama**
(localhost) et les embeddings via des modèles **HuggingFace** téléchargés localement. C'est un
argument de **souveraineté** et de **confidentialité** clé pour un contexte bancaire/santé.

## Module A — Botnet / C2

```
flows.csv ─▶ features.py ──▶ X (features de beaconing) ─▶ RandomForest ─▶ verdict
                                                                │
                                              alerte ─▶ llm_triage.py (Ollama) ─▶ explication
```
- **Feature engineering** centré sur le *beaconing* : régularité des intervalles (`iat_cv`,
  `beacon_score`), ratio d'octets, répétition vers une même destination.
- **Modèle** : RandomForest `class_weight="balanced"` (classes déséquilibrées).
- **Explicabilité** : importances de features + triage LLM en langage clair.

## Module B — Jailbreak / Prompt-Injection

```
prompt ─▶ detector.py (embeddings + LogisticRegression) ─▶ score
   │                                                         │
   └── si incertain ──▶ guardrail.py (LLM-judge Ollama) ─▶ verdict + raison
```
- **Défense en profondeur** : un classifieur rapide filtre la masse, un LLM-judge tranche les
  cas ambigus.
- **Sécurité du guardrail** : le prompt est traité comme **donnée à classer**, jamais comme
  instruction (le système le dit explicitement) — on ne se fait pas injecter par ce qu'on analyse.

## Évaluation

Les deux modules privilégient le **recall sur la classe malveillante** (ne pas rater une menace)
tout en gardant une **précision** correcte (limiter les faux positifs). Métriques : precision /
recall / F1 par classe, matrice de confusion, ROC-AUC.

## Référentiels

- Botnet → MITRE ATT&CK **T1071 / T1102**, patterns de beaconing
- Jailbreak → **OWASP LLM Top 10 (LLM01:2025)**, MITRE **ATLAS**
