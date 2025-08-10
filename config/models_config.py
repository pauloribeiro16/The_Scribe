# config/models_config.py
import json

# O modelo que vai atuar como Classificador/Router. Deve ser rápido e pequeno.
ROUTER_MODEL_NAME = "qwen3:4b" # Um modelo pequeno é ideal aqui

# A lista de modelos "Expert" que vão competir para dar a resposta.
EXPERT_MODEL_NAMES = [
    "qwen2.5:0.5b",
]
