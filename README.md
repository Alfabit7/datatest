crypto_data_collector/
├── config/
│   └── secrets.env          # Токены (добавлен в .gitignore)
├── src/
│   ├── api_clients/
│   │   ├── binance.py       # Публичные фьючерсы Binance
│   │   ├── bybit.py         # Публичные фьючерсы Bybit
│   │   └── coingecko.py     # CoinGecko API (с демо-токеном)
│   ├── data_handlers/
│   │   └── merger.py        # Объединение данных
│   └── main.py              # Главный скрипт
└── data/
    ├── raw/                 # Сырые ответы от API
    └── processed/           # Объединенный combined.json# datatest
