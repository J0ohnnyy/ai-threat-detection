# Module A — Détection de Botnet / C2

Classifier un flux réseau comme **botnet (C2)** ou **bénin** à partir de features de flux,
puis **expliquer** une alerte en langage clair via un LLM local.

## Datasets (publics, recherche)

| Dataset | Contenu | Lien |
|---|---|---|
| **CTU-13** | 13 captures de botnets réels + trafic normal | stratosphereips.org |
| **IoT-23** | trafic IoT malveillant/bénin labellisé | stratosphereips.org |
| **CIC-IDS2017** | flux labellisés (dont botnet Ares) | unb.ca/cic/datasets |

> Télécharge un dataset dans `data/` (ignoré par git). Les CSV de flux exposent typiquement :
> `src_ip, dst_ip, dst_port, proto, duration, bytes_out, bytes_in, packets, timestamp, label`.

## Pipeline

```
data/flows.csv ─▶ features.py (agrégation + beaconing) ─▶ train.py (RandomForest)
                                                              └─▶ model.joblib
alerte ─▶ llm_triage.py (Ollama) ─▶ explication + recommandation
```

## Utilisation

```bash
# 1) Entraîner (dataset labellisé dans data/)
python src/train.py --data data/flows.csv --label-col label --out models/botnet_rf.joblib

# 2) Expliquer une alerte avec le LLM local
python src/llm_triage.py --model llama3.1:8b
```

## Idée clé — le beaconing

Un botnet « bat » vers son C2 à intervalles réguliers. Les features les plus discriminantes
sont donc la **régularité temporelle** (faible écart-type des intervalles), le **ratio
bytes_out/bytes_in**, et la **répétition** des connexions vers une même destination. Voir
[`src/features.py`](src/features.py).

## Évaluation attendue

Precision / Recall / F1 par classe + matrice de confusion. Sur CTU-13, viser un **recall élevé
sur la classe botnet** (ne pas rater de C2) tout en maîtrisant les faux positifs.
