"""Market configurations for different stock exchanges."""

from typing import Any, Dict, List

# Market identifiers
Market = str  # "UK" or "MY" (Malaysia)

# UK Stock Exchange (LSE) - Top 50
UK_TICKERS: List[str] = [
    # Top 50 LSE stocks by market cap
    "AZN.L",      # AstraZeneca PLC
    "SHEL.L",     # Shell plc
    "HSBA.L",     # HSBC Holdings plc
    "ULVR.L",     # Unilever PLC
    "BATS.L",     # British American Tobacco p.l.c.
    "RR.L",       # Rolls-Royce Holdings plc
    "REL.L",      # RELX PLC
    "GSK.L",      # GSK plc
    "LSEG.L",     # London Stock Exchange Group plc
    "BA.L",       # BAE Systems plc
    "RIO.L",      # Rio Tinto Group
    "NG.L",       # National Grid plc
    "BARC.L",     # Barclays PLC
    "LLOY.L",     # Lloyds Banking Group plc
    "DGE.L",      # Diageo plc
    "GLEN.L",     # Glencore plc
    "PRU.L",      # Prudential plc
    "AAL.L",      # Anglo American plc
    "STAN.L",     # Standard Chartered PLC
    "VOD.L",      # Vodafone Group plc
    "BP.L",       # BP p.l.c.
    "BHP.L",      # BHP Group
    "AV.L",       # Aviva plc
    "LGEN.L",     # Legal & General Group plc
    "IMB.L",      # Imperial Brands PLC
    "BT-A.L",     # BT Group plc
    "SSE.L",      # SSE plc
    "EXPN.L",     # Experian plc
    "ANTO.L",     # Antofagasta plc
    "SMIN.L",     # Smiths Group plc
    "SPX.L",      # Spirax-Sarco Engineering plc
    "HLMA.L",     # Halma plc
    "ADM.L",      # Admiral Group plc
    "ABF.L",      # Associated British Foods plc
    "PSON.L",     # Pearson plc
    "RKT.L",      # Reckitt Benckiser Group plc
    "IAG.L",      # International Consolidated Airlines Group S.A.
    "WPP.L",      # WPP plc
    "CRDA.L",     # Croda International plc
    "FERG.L",     # Ferguson plc
    "BRBY.L",     # Burberry Group plc
    "AUTO.L",     # Auto Trader Group plc
    "ENT.L",      # Entain plc
    "MNG.L",      # M&G plc
    "JD.L",       # JD Sports Fashion plc
    "SBRY.L",     # J Sainsbury plc
    "TSCO.L",     # Tesco PLC
    "MKS.L",      # Marks and Spencer Group plc
    "EZJ.L",      # easyJet plc
    "SMT.L",      # Scottish Mortgage Investment Trust plc
]

# Bursa Malaysia (KLSE) - FTSE Bursa Malaysia Top 100
# Note: Malaysian tickers use .KL suffix for Yahoo Finance
MY_TICKERS: List[str] = [
    # Major constituents of FTSE Bursa Malaysia Top 100 Index
    "MAYBANK.KL",      # Malayan Banking Berhad
    "PUBLICBANK.KL",   # Public Bank Berhad
    "CIMB.KL",        # CIMB Group Holdings Berhad
    "RHB.KL",         # RHB Bank Berhad
    "HLBANK.KL",      # Hong Leong Bank Berhad
    "PCHEM.KL",       # Petronas Chemicals Group Berhad
    "IOICORP.KL",     # IOI Corporation Berhad
    "SIME.KL",        # Sime Darby Berhad
    "GENTING.KL",     # Genting Berhad
    "GENM.KL",        # Genting Malaysia Berhad
    "AMMB.KL",        # AMMB Holdings Berhad
    "UEMS.KL",        # UEM Sunrise Berhad
    "TENAGA.KL",      # Tenaga Nasional Berhad
    "MAXIS.KL",       # Maxis Berhad
    "DIGI.KL",        # Digi.Com Berhad (Axiata)
    "AXIATA.KL",      # Axiata Group Berhad
    "TM.KL",          # Telekom Malaysia Berhad
    "PPB.KL",         # PPB Group Berhad
    "FGV.KL",         # FGV Holdings Berhad
    "KLK.KL",         # Kuala Lumpur Kepong Berhad
    "IOIPG.KL",       # IOI Properties Group Berhad
    "UMW.KL",         # UMW Holdings Berhad
    "MISC.KL",        # MISC Berhad
    "DIALOG.KL",      # Dialog Group Berhad
    "PETDAG.KL",      # Petronas Dagangan Berhad
    "PETGAS.KL",      # Petronas Gas Berhad
    "SAPNRG.KL",      # Sapura Energy Berhad
    "AIRPORT.KL",     # Malaysia Airports Holdings Berhad
    "IHH.KL",         # IHH Healthcare Berhad
    "KPJ.KL",         # KPJ Healthcare Berhad
    "TOPGLOV.KL",     # Top Glove Corporation Berhad
    "HARTALEGA.KL",   # Hartalega Holdings Berhad
    "SUPERMX.KL",     # Supermax Corporation Berhad
    "SCIENTX.KL",     # Scientex Berhad
    "NESTLE.KL",      # Nestle Malaysia Berhad
    "F&N.KL",         # Fraser & Neave Holdings Berhad
    "DLADY.KL",       # Dutch Lady Milk Industries Berhad
    "YTL.KL",         # YTL Corporation Berhad
    "YTLPOWR.KL",     # YTL Power International Berhad
    "GAMUDA.KL",      # Gamuda Berhad
    "IJM.KL",         # IJM Corporation Berhad
    "WPRTS.KL",       # Westports Holdings Berhad
    "MMCCORP.KL",     # MMC Corporation Berhad
    "MALAYSIAN.KL",   # Malaysian Resources Corporation Berhad
    "SUNWAY.KL",      # Sunway Berhad
    "SP SETIA.KL",    # SP Setia Berhad
    "MAHSING.KL",    # Mah Sing Group Berhad
    "ECOWLD.KL",     # Eco World Development Group Berhad
    "HAPSENG.KL",    # Hap Seng Consolidated Berhad
    "LPI.KL",        # LPI Capital Berhad
    "ALLIANZ.KL",    # Allianz Malaysia Berhad
    "STMB.KL",       # SAM Engineering & Equipment Berhad
    "VS.KL",         # VS Industry Berhad
    "INARI.KL",      # Inari Amertron Berhad
    "FRONTKN.KL",    # Frontken Corporation Berhad
    "GLOBETEC.KL",   # Globetronics Technology Berhad
    "UNISEM.KL",     # Unisem Berhad
    "KESM.KL",       # KESM Industries Berhad
    "MALAKOFF.KL",   # Malakoff Corporation Berhad
    "YINSON.KL",     # Yinson Holdings Berhad
    "VELESTO.KL",    # Velesto Energy Berhad
    "SKPETRO.KL",    # SK Petrochemicals Berhad
    "SHANG.KL",      # Shangri-La Hotels Malaysia Berhad
    "LION.KL",       # Lion Industries Corporation Berhad
    "MEDIA.KL",      # Media Prima Berhad
    "ASTRO.KL",      # Astro Malaysia Holdings Berhad
    "PADINI.KL",     # Padini Holdings Berhad
    "BAT.KL",        # British American Tobacco Malaysia Berhad
    "HEIM.KL",       # Heineken Malaysia Berhad
    "CARLSBG.KL",    # Carlsberg Brewery Malaysia Berhad
    "PBBANK.KL",     # Public Bank Berhad (alternative ticker)
    "RHBBANK.KL",    # RHB Bank Berhad (alternative ticker)
    "HLFG.KL",       # Hong Leong Financial Group Berhad
    "HLIND.KL",      # Hong Leong Industries Berhad
    "HARTA.KL",      # Hartalega Holdings Berhad (alternative)
    "MFCB.KL",       # Malaysian Food Industries Berhad
    "KLCC.KL",       # KLCC Real Estate Investment Trust
    "ALAQAR.KL",     # Al-Aqar Healthcare REIT
    "PAVREIT.KL",    # Pavilion Real Estate Investment Trust
    "SUNREIT.KL",    # Sunway Real Estate Investment Trust
    "YTREIT.KL",     # YTL Real Estate Investment Trust
    "STARREIT.KL",   # Star Real Estate Investment Trust
    "AXREIT.KL",     # Axis Real Estate Investment Trust
]

# Market configurations
MARKET_CONFIGS: Dict[Market, Dict[str, Any]] = {
    "UK": {
        "name": "London Stock Exchange",
        "index_name": "FTSE 100",
        "tickers": UK_TICKERS,
        "currency": "GBP",
        "currency_symbol": "£",
        "ticker_suffix": ".L",
    },
    "MY": {
        "name": "Bursa Malaysia",
        "index_name": "FTSE Bursa Malaysia Top 100",
        "tickers": MY_TICKERS,
        "currency": "MYR",
        "currency_symbol": "RM",
        "ticker_suffix": ".KL",
    },
}

