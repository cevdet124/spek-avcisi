# Spek Avcısı V21 Pro — Walk-Forward

V20 dinamik backtest motoruna walk-forward optimizasyonu eklenmiştir.

## Neden walk-forward?
Ayarlar geçmiş verinin ilk bölümünde seçilir ve daha sonra hiç görülmemiş son bölümde test edilir. Böylece yalnızca geçmişe aşırı uyum sağlayan ayarların fark edilmesi kolaylaşır.

## Yeni dosya
- `optimizer.py`: parametre taraması, risk-ayarlı seçim ve görülmemiş dönem doğrulaması

## Dikkat
Tek bir hissede veya tek bir dönemde iyi sonuç yeterli değildir. Farklı hisseler, piyasa rejimleri ve dönemler üzerinde tutarlılık aranmalıdır. Geçmiş performans geleceği garanti etmez.
