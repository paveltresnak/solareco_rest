# SolarEco REST – Home Assistant Integration
Integrace pro připojení a monitorování solárního regulátoru SolarEco OPL 9AC v systému Home Assistant.
Umožňuje načítat provozní data přes rozhraní SolarEco REST API a zobrazovat je jako senzory v Home Assistantu.

[Repozitář na GitHubu](https://github.com/paveltresnak/solareco_rest)

O projektu
Tato integrace vznikla ve spolupráci s Claude.AI, která vytvořila počáteční implementaci modulu.
Následně byla testována a rozšířena o požadavky zadavatele (měření výkonu, teploty, relé atd.).
Cílem je snadné a spolehlivé připojení regulátoru OPL 9AC k Home Assistantu přes lokální REST API nebo LAN modul SolarEco.

## Podporované funkce
Integrace aktuálně podporuje čtení provozních hodnot z vašeho regulátoru:
* Napětí (Voltage)
* Proud (Current)
* Výkon (Power)
* Denní energie (Energy of Day)
* Teplota chladiče (Cooler Temperature)

Autoři a přispěvatelé
Claude.AI – počáteční návrh integrace
Pavel Třešňák – testování, zpětná vazba, vylepšení funkcí

Licence
Projekt je dostupný pod licencí MIT.
Použití na vlastní riziko, bez jakýchkoliv záruk.
