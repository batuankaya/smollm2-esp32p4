# SmolLM2-135M → ESP32-P4

SmolLM2-135M-Instruct modelini vocab küçültme, katman budama, distillation ve ternary quantization ile sıkıştırıp ESP32-P4 üzerinde internetsiz çalıştırma projesi. Görev: doğal dildeki komutları (alarm, zamanlayıcı, ışık…) JSON'a çevirmek.

- Plan: [PLAN.md](PLAN.md)
- Klasörler: `train/` (SFT, distillation, QAT), `eval/`, `export/`, `firmware/` (ESP-IDF), `results/` (ölçüm CSV'leri)
