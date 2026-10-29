"""Katman katman parametre dökümü.

Her tensör için bir satır yazar: model, tensör adı, katman no, grup, şekil, eleman sayısı.
Tied embedding (embed_tokens == lm_head) bir kez sayılır.

Kullanım:
    python eval/param_breakdown.py --out results/param_breakdown.csv
"""
import argparse
import csv
from collections import defaultdict

import torch
from transformers import AutoModelForCausalLM

MODELS = ["HuggingFaceTB/SmolLM2-135M-Instruct", "HuggingFaceTB/SmolLM2-360M-Instruct"]


def group_of(name):
    if "embed_tokens" in name or "lm_head" in name:
        return "embedding"
    if "self_attn" in name:
        return "attention"
    if "mlp" in name:
        return "mlp"
    if "norm" in name:
        return "norm"
    return "other"


def layer_of(name):
    parts = name.split(".")
    if "layers" in parts:
        return int(parts[parts.index("layers") + 1])
    return -1  # katman dışı (embedding, final norm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/param_breakdown.csv")
    args = ap.parse_args()

    rows = []
    for model_id in MODELS:
        model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
        # named_parameters() paylaşılan tensörleri varsayılan olarak bir kez döndürür
        for name, p in model.named_parameters():
            rows.append({
                "model": model_id.split("/")[-1],
                "name": name,
                "layer": layer_of(name),
                "group": group_of(name),
                "shape": "x".join(map(str, p.shape)),
                "numel": p.numel(),
            })

        total = sum(r["numel"] for r in rows if r["model"] == model_id.split("/")[-1])
        by_group = defaultdict(int)
        for r in rows:
            if r["model"] == model_id.split("/")[-1]:
                by_group[r["group"]] += r["numel"]
        print(f"\n{model_id}  (tied embeddings: {model.config.tie_word_embeddings})")
        print(f"  toplam: {total:,}")
        for g, n in sorted(by_group.items(), key=lambda x: -x[1]):
            print(f"  {g:10s} {n:>12,}  ({100 * n / total:5.1f}%)")
        per_layer = sum(r["numel"] for r in rows
                        if r["model"] == model_id.split("/")[-1] and r["layer"] == 0)
        print(f"  tek blok: {per_layer:,}  x {model.config.num_hidden_layers} katman")

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)} satır -> {args.out}")


if __name__ == "__main__":
    main()
