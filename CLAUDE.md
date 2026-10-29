# Proje: SmolLM2-135M'i sıkıştırıp ESP32-P4'te çalıştırma

Derin öğrenme dersi projesi. Hazır bir dil modelini (SmolLM2-135M-Instruct) vocab küçültme, katman budama, distillation ve quantization ile küçültüp ESP32-P4'te internetsiz çalıştırıyoruz. Görev: doğal dildeki komutları (alarm, zamanlayıcı, ışık…) JSON'a çevirip sunucuya iletmek. Haftalık plan PLAN.md'de; o gün çalıştığımız haftanın bölümünü oku.

## Temel kararlar
- Öğrenci model: `HuggingFaceTB/SmolLM2-135M-Instruct`
- Öğretmen model: `HuggingFaceTB/SmolLM2-360M-Instruct` (aynı tokenizer; komut verisiyle o da ince ayarlanacak)
- Hedef format: gövde ternary (1.58-bit, BitNet b1.58 absmean + STE), embedding int8
- Vocab hedefi: 49152 → ~16k
- Donanım: Waveshare ESP32-P4-WIFI6 (32MB PSRAM, 32MB flash, microSD). Çip v3.x olabilir, bu yüzden ESP-IDF v5.5.3 veya üstü gerekli
- Çıkarım motoru: llama2.c tabanlı (run.c / runq.c), ESP-IDF ile derlenecek
- Eğitim donanımı: tek bir 12GB GPU; batch boyutu ve bellek kullanımını buna göre seç

## Klasörler
- `train/`: SFT, distillation, QAT
- `eval/`: değerlendirme scriptleri
- `export/`: ESP formatına dönüştürme
- `firmware/`: ESP-IDF projesi
- `results/`: ölçüm CSV'leri (git'e girer)
- `data/`, `checkpoints/`: büyük dosyalar (git'e girmez)

## Komutlar
- Proje konumu: `C:\Users\user\projects\smollm2-esp32p4` (OneDrive dışında)
- Python ortamı (repo dışında): `C:\Users\user\.venvs\smollm-esp` (Python 3.11, torch 2.11+cu128, transformers 5.22, datasets 5.1)
  - Aktifleştirme (PowerShell): `C:\Users\user\.venvs\smollm-esp\Scripts\Activate.ps1`
  - Doğrudan çalıştırma: `C:/Users/user/.venvs/smollm-esp/Scripts/python.exe <script>`
  - Paket ekleme: `$env:VIRTUAL_ENV='C:\Users\user\.venvs\smollm-esp'; uv pip install <paket>`
- (Eval ve ESP-IDF build/flash komutları eklenecek.)

## Kurallar
- Her ölçümü bir script `results/` altındaki bir CSV'ye yazar. Sonuç rakamlarını asla elle yazma ya da tahmin etme; her sonucu çalıştırdığın komut ve çıktısıyla göster.
- Perplexity'yi bits-per-byte olarak raporla; vocab değişince token sayısı da değişiyor.
- Vocab küçültürken sohbet şablonu token'larını (`<|im_start|>`, `<|im_end|>`) ve JSON karakterlerini her zaman koru.
- 10 dakikadan uzun sürecek eğitimleri kendin başlatma. Önce birkaç adımlık bir deneme çalıştır, sonra tam eğitim komutunu bana ver; ben ayrı bir terminalde başlatırım. Eğitimi log dosyasını okuyarak takip et.
- ESP tarafında her değişiklikten sonra PC ile karşılaştırma testini çalıştır: aynı prompt, greedy decoding, aynı token'lar çıkmalı.
- Önemli bir parçayı (STE, vocab yeniden eşleme, ternary paketleme gibi) yazdıktan sonra bana kısaca açıkla. Bu bir ders projesi; kodu sunumda açıklayabilmem gerekiyor.
- Model ağırlıklarını ve veri setlerini git'e ekleme.
- Her çalışan adımdan sonra açıklayıcı bir mesajla commit at.
