# AI Threat Detection — ML & LLMs for Security

> Deux détecteurs open-source et **100 % locaux** (Ollama / HuggingFace, aucune donnée envoyée au cloud) :
> **(A) détection de botnet / C2** par ML sur flux réseau, et **(B) détection de jailbreak / prompt-injection** contre un LLM (OWASP LLM01).

**Auteur :** Karim EL HAOURATI · M.Sc. Cybersécurité
**Stack :** Python · scikit-learn · HuggingFace `sentence-transformers` · **Ollama** (LLM local) · pandas

![status](https://img.shields.io/badge/status-in%20progress-orange) ![ml](https://img.shields.io/badge/ML-scikit--learn-f7931e) ![llm](https://img.shields.io/badge/LLM-local%20(Ollama)-000000) ![owasp](https://img.shields.io/badge/aligned-OWASP%20LLM%20Top%2010-5a2a82)

---

## 🎯 Pourquoi ce projet

Il couvre **deux menaces très actuelles** avec la même colonne vertébrale (ML + LLM) :

| Module | Menace | Approche |
|---|---|---|
| **A — Botnet / C2** | Trafic de command & control, beaconing | Features de flux → classifieur ML + **triage LLM** explicatif |
| **B — Jailbreak / Prompt-Injection** | Contournement des garde-fous d'un LLM | Embeddings + classifieur **ou** LLM-judge local (guardrail) |

**Tout tourne en local** (Ollama + modèles HuggingFace) → pas de clé API, pas de fuite de données.

## 🧩 Architecture

```
                 ┌───────────────────────────────────────────┐
                 │              ai-threat-detection           │
   flux réseau ─▶│  A) features.py → train.py (ML)            │─▶ botnet / bénin
   (CSV flows)   │        └─ llm_triage.py (Ollama) ──────────│─▶ explication en clair
                 │                                            │
   prompts  ────▶│  B) detector.py (embeddings + classifieur) │─▶ jailbreak / bénin
   (texte)       │        └─ guardrail.py (LLM-judge Ollama)  │─▶ verdict + raison
                 └───────────────────────────────────────────┘
```

## 📁 Structure

```
ai-threat-detection/
├── botnet-detection/
│   ├── src/ features.py · train.py · llm_triage.py
│   └── README.md            # datasets (CTU-13 / IoT-23 / CIC-IDS2017), pipeline
├── jailbreak-detection/
│   ├── src/ detector.py · evaluate.py · guardrail.py
│   └── README.md            # datasets (JailbreakBench…), OWASP LLM01
├── docs/ architecture.md
├── requirements.txt
└── README.md
```

## 🚀 Démarrage rapide

```bash
python -m venv .venv && source .venv/bin/activate   # (Windows : .venv\Scripts\activate)
pip install -r requirements.txt

# LLM local
curl -fsSL https://ollama.com/install.sh | sh        # ou installeur Windows
ollama pull llama3.1:8b                               # modèle local
```
Puis suis le README de chaque module.

## 🗺️ Roadmap

| Phase | Botnet (A) | Jailbreak (B) |
|---|---|---|
| 1. Données | Charger CTU-13 / IoT-23, nettoyer | Charger JailbreakBench + prompts bénins |
| 2. Features / embeddings | Extraction de features de flux | Embeddings `sentence-transformers` |
| 3. Modèle | Entraîner RandomForest, évaluer | Classifieur + option LLM-judge |
| 4. Explicabilité | Triage LLM (Ollama) d'une alerte | Raison du verdict (guardrail) |
| 5. Évaluation | Precision/Recall/F1, matrice | ROC-AUC, FP/FN, robustesse |

## 🧠 Compétences démontrées

`Python` · `Machine Learning (scikit-learn)` · `Feature engineering réseau` · `NLP / embeddings (HuggingFace)` · `LLM local (Ollama)` · `AI security (OWASP LLM Top 10)` · `Détection C2 / beaconing` · `Évaluation de modèles` · `MLOps léger`

## 🧭 Référentiels

- **Botnet / C2** → MITRE ATT&CK **T1071** (C2 Application Layer), **T1102** (Web Service), beaconing
- **Jailbreak / Prompt-Injection** → **OWASP LLM Top 10 — LLM01:2025 Prompt Injection** · MITRE **ATLAS**

---

> ⚠️ **Cadre.** Les données offensives (prompts de jailbreak, captures de botnet) proviennent de **datasets publics de recherche** et sont utilisées **uniquement pour entraîner des défenses**. Lab isolé, finalité défensive.
