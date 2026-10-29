# Haftalık Plan

Model tarafı (PC) ve ESP tarafı paralel ilerliyor. Ara hedef 9. hafta: sıkıştırılmış model ESP'de çalışıyor. Son hedef 12. hafta: uçtan uca demo.

## Hafta 1: Kurulum ve başlangıç ölçümleri
- Model: Repo ve Python ortamının kurulumu; 135M ve 360M Instruct modellerinin indirilmesi; katman katman parametre dökümü; WikiText-2 test setinde bits-per-byte ölçümü; FP16, int8, 4-bit ve ternary için bellek bütçesi tablosu
- ESP: Kart ve microSD siparişi
- Çıktı: `results/param_breakdown.csv`, `results/baseline.csv`, `results/memory_budget.csv`

## Hafta 2: Görev verisi ve SFT
- Model: Komut şeması (5–8 komut + `unknown`, eksik bilgi durumu); yerel büyük LLM ile birkaç bin "cümle → JSON" örneği; elle yazılmış 200 komutluk test seti; 50–100 soruluk soru-cevap seti; 135M ve 360M modellerine komut SFT'si
- ESP: ESP-IDF v5.5.3+ kurulumu
- Çıktı: Sıkıştırılmamış görev başarısı (öğrenci ve öğretmen)

## Hafta 3: Vocab küçültme
- Model: 49k → ~16k (sohbet şablonu token'ları ve JSON karakterleri korunur)
- ESP: llama2.c'nin 260K modelini kartta çalıştırma
- Çıktı: Vocab ölçümleri; kartta ilk çalışan model

## Hafta 4: Katman budama
- Model: Block Influence (BI) skorları; 6, 10 ve 15 katman silme; iyileştirme öncesi ölçüm
- ESP: SD karttan model yükleme, PSRAM yerleşimi
- Çıktı: Budama ölçümleri

## Hafta 5: Distillation altyapısı
- Model: Öğretmen çıktısını korunan vocab'a göre yeniden normalize etme; KL + CE kaybı; kısa denemeler
- ESP: int8 çıkarımın (runq.c) portu; stories15M ve 42M ile hız ölçümü
- Çıktı: Çalışan distillation hattı; bant genişliği referansı

## Hafta 6: Ana distillation eğitimi
- Model: Birkaç yüz milyon token'lık distillation (uzun eğitim, ayrı terminalde)
- ESP: Kendi modelinin llama2.c formatına dışa aktarılması ve doğrulanması; PC ile ESP karşılaştırma testi
- Çıktı: Dışa aktarma hattı hazır

## Hafta 7: PTQ
- Model: Distillation'ın tamamlanması; PTQ ile int8 ve 4-bit ölçümleri
- ESP: Ternary veri formatı (2-bit paketleme) ve skaler ternary çekirdek
- Çıktı: Distill edilmiş model; PTQ ölçümleri

## Hafta 8: Ternary QAT
- Model: Ternary QAT (absmean + STE, distillation kaybıyla)
- ESP: Ternary çekirdeğin PC çıktısıyla karşılaştırmalı doğruluk testi
- Çıktı: Doğrulanmış ternary çekirdek

## Hafta 9: Ternary model ESP'de
- Model: QAT'nin tamamlanması ve ölçümler
- ESP: Ternary modeli kartta çalıştırma
- Çıktı: Sıkıştırılmış model ESP'de çalışıyor

## Hafta 10: Hızlandırma
- Model: Eksik ölçümler; ana tablonun tamamlanması
- ESP: Çift çekirdek ve PIE vektör komutlarıyla hızlandırma; token/s ve bellek ölçümü
- Çıktı: Ana karşılaştırma tablosu

## Hafta 11: Kısıtlı çözümleme
- Model: ESP'deki modelin test setinde değerlendirilmesi (PC sonuçlarıyla tutarlılık)
- ESP: JSON grameriyle kısıtlı çözümleme
- Çıktı: Geçersiz JSON üretmeyen model

## Hafta 12: Uygulama katmanı
- ESP: C6 üzerinden Wi-Fi, MQTT ile sunucuya komut; sunucuda Python servisi; uçtan uca süre ölçümü
- Çıktı: Uçtan uca çalışan demo

## Hafta 13–14: Rapor ve sunum
- Tablolar, grafikler, PFor ile karşılaştırma; sunum ve demo provası

## Zaman kalırsa
- 3.5 inç SPI ekran + USB klavye
- Uyandırma kelimesi (ESP-SR WakeNet)
- 4-bit + flash hibrit yerleşim deneyi
- 8k / 16k / 32k vocab karşılaştırması
