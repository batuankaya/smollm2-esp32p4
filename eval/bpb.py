"""WikiText-2 test setinde bits-per-byte (BPB) ölçümü.

Neden BPB: perplexity token başına; vocab küçülünce aynı metin daha fazla token'a
bölünür ve perplexity'ler karşılaştırılamaz hale gelir. BPB ise toplam kaybı metnin
UTF-8 bayt sayısına böler, tokenizer'dan bağımsızdır:

    BPB = (toplam NLL, nat) / ln(2) / (metnin bayt sayısı)

Metin: wikitext-2-raw-v1 test satırları "".join ile birleştirilir (satırlar zaten '\n'
ile bitiyor, böylece orijinal dosya geri elde edilir).
İlk token'ın da tahmin edilmesi için başa <|endoftext|> konur; böylece tüm baytlar puanlanır.
Uzun metin kayan pencereyle işlenir: her pencere `ctx` token, her adımda `stride` yeni
token puanlanır, geri kalanı bağlam olarak kullanılır.

Kullanım:
    python eval/bpb.py --model HuggingFaceTB/SmolLM2-135M-Instruct --out results/baseline.csv
"""
import argparse
import csv
import math
import os
import time

import torch
import torch.nn.functional as F
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

DTYPES = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}


@torch.no_grad()
def compute_bpb(model, tok, text, ctx, stride, device):
    ids = tok(text, add_special_tokens=False)["input_ids"]
    ids = torch.tensor([tok.eos_token_id] + ids, device=device)
    n = len(ids)

    total_nll = 0.0
    scored = 0
    prev_end = 1  # 0. pozisyon (<|endoftext|>) puanlanmaz
    for begin in range(0, n - 1, stride):
        end = min(begin + ctx, n)
        window = ids[begin:end].unsqueeze(0)
        logits = model(window).logits[0].float()
        # pozisyon i'deki logit, i+1'deki token'ı tahmin eder
        targets = window[0, 1:]
        nll = F.cross_entropy(logits[:-1], targets, reduction="none")
        # sadece daha önce puanlanmamış hedefleri say
        new_from = prev_end - begin - 1
        total_nll += nll[new_from:].sum().item()
        scored += nll[new_from:].numel()
        prev_end = end
        if end == n:
            break

    assert scored == n - 1, (scored, n - 1)
    return total_nll, scored


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dtype", default="fp32", choices=DTYPES)
    ap.add_argument("--ctx", type=int, default=2048)
    ap.add_argument("--stride", type=int, default=1024)
    ap.add_argument("--out", default="results/baseline.csv")
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=DTYPES[args.dtype]).to(device).eval()

    ds = load_dataset("Salesforce/wikitext", "wikitext-2-raw-v1", split="test")
    text = "".join(ds["text"])
    n_bytes = len(text.encode("utf-8"))

    t0 = time.time()
    nll, n_tok = compute_bpb(model, tok, text, args.ctx, args.stride, device)
    secs = time.time() - t0

    bpb = nll / math.log(2) / n_bytes
    row = {
        "model": args.model.rstrip("/").split("/")[-1],
        "dtype": args.dtype,
        "dataset": "wikitext-2-raw-v1/test",
        "vocab_size": len(tok),
        "params": sum(p.numel() for p in model.parameters()),
        "ctx": args.ctx,
        "stride": args.stride,
        "n_tokens": n_tok,
        "n_bytes": n_bytes,
        "tokens_per_byte": round(n_tok / n_bytes, 5),
        "bpb": round(bpb, 5),
        "token_ppl": round(math.exp(nll / n_tok), 3),
        "seconds": round(secs, 1),
        "note": args.note,
    }
    for k, v in row.items():
        print(f"{k:16s} {v}")

    new = not os.path.exists(args.out) or os.path.getsize(args.out) == 0
    with open(args.out, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if new:
            w.writeheader()
        w.writerow(row)
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
