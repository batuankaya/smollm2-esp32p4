"""Bellek bütçesi tablosu: farklı formatlarda, vocab ve katman sayılarında model boyutu.

Boyutlar model config'inden hesaplanır (ağırlık yüklenmez). Birim MiB (2^20 bayt).

Formatlar (tied embedding tek kopya sayılır, norm ağırlıkları her zaman fp32):
  fp16    : her ağırlık 2 bayt
  int8    : 1 bayt/ağırlık + 64'lük grup başına fp32 ölçek (llama2.c runq.c düzeni)
  int4    : 0.5 bayt/ağırlık + 32'lik grup başına fp16 ölçek
  ternary : gövde lineer katmanları 2 bit/ağırlık (4 ağırlık/bayt) + tensör başına fp32 ölçek
            (BitNet b1.58 absmean); embedding int8 (64'lük grup, fp32 ölçek)

KV cache llama2.c'deki gibi fp32 tutulur: 2 (K,V) x katman x bağlam x kv_dim x 4 bayt.

Kullanım:
    python eval/memory_budget.py --out results/memory_budget.csv
"""
import argparse
import csv

from transformers import AutoConfig

MIB = 2 ** 20
CTX = [256, 512]

# (model, vocab boyutları, katman sayıları)
SCENARIOS = [
    ("HuggingFaceTB/SmolLM2-135M-Instruct", [49152, 16384], [30, 24, 20, 15]),
    ("HuggingFaceTB/SmolLM2-360M-Instruct", [49152], [32]),
]


def int8_bytes(n, gs=64):
    return n + (n // gs) * 4


def int4_bytes(n, gs=32):
    return n / 2 + (n // gs) * 2


def sizes(cfg, vocab, n_layers):
    d, ff = cfg.hidden_size, cfg.intermediate_size
    kv_dim = d * cfg.num_key_value_heads // cfg.num_attention_heads
    emb = vocab * d
    # her blok: q,o (d x d), k,v (kv_dim x d), gate,up,down (ff x d)
    lin_per_layer = [d * d, kv_dim * d, kv_dim * d, d * d, ff * d, ff * d, ff * d]
    body = sum(lin_per_layer) * n_layers
    norm = (2 * n_layers + 1) * d
    return d, kv_dim, emb, lin_per_layer, body, norm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/memory_budget.csv")
    args = ap.parse_args()

    rows = []
    for model_id, vocabs, layer_counts in SCENARIOS:
        cfg = AutoConfig.from_pretrained(model_id)
        for vocab in vocabs:
            for L in layer_counts:
                d, kv_dim, emb, lin, body, norm = sizes(cfg, vocab, L)
                n_tensors = len(lin) * L
                fmt_bytes = {
                    "fp16": (emb * 2, body * 2),
                    "int8": (int8_bytes(emb), sum(int8_bytes(x) for x in lin) * L),
                    "int4": (int4_bytes(emb), sum(int4_bytes(x) for x in lin) * L),
                    "ternary": (int8_bytes(emb), body / 4 + n_tensors * 4),
                }
                for fmt, (emb_b, body_b) in fmt_bytes.items():
                    norm_b = norm * 4
                    weights = emb_b + body_b + norm_b
                    row = {
                        "model": model_id.split("/")[-1],
                        "format": fmt,
                        "vocab": vocab,
                        "n_layers": L,
                        "params": emb + body + norm,
                        "embedding_MiB": round(emb_b / MIB, 2),
                        "body_MiB": round(body_b / MIB, 2),
                        "norm_MiB": round(norm_b / MIB, 3),
                        "weights_MiB": round(weights / MIB, 2),
                        "logits_buf_MiB": round(vocab * 4 / MIB, 3),
                    }
                    for c in CTX:
                        kv = 2 * L * c * kv_dim * 4
                        row[f"kv_fp32_ctx{c}_MiB"] = round(kv / MIB, 2)
                        row[f"total_ctx{c}_MiB"] = round((weights + kv + vocab * 4) / MIB, 2)
                    rows.append(row)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    cols = ["model", "format", "vocab", "n_layers", "embedding_MiB", "body_MiB",
            "weights_MiB", "kv_fp32_ctx512_MiB", "total_ctx512_MiB"]
    print("  ".join(f"{c[:14]:>14s}" for c in cols))
    for r in rows:
        print("  ".join(f"{str(r[c])[:14]:>14s}" for c in cols))
    print(f"\n{len(rows)} satır -> {args.out}")


if __name__ == "__main__":
    main()
