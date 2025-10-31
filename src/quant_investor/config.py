from typing import List, Literal, Union

# API Provider Options
DataProvider = Literal["yahoo", "alpha_vantage"]

# Default API provider (can be overridden via environment variable or dashboard)
DEFAULT_DATA_PROVIDER: DataProvider = "yahoo"

# Alpha Vantage API Key (set via ALPHA_VANTAGE_API_KEY environment variable)
# Get your free API key at: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY: Union[str, None] = None

DEFAULT_TICKERS: List[str] = [
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
    "BT-A.L",     # BT Group plc (alternative: BT.L might work too)
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
    "SMT.L",      # Scottish Mortgage Investment Trust plc (major FTSE 100 component)
]

DEFAULT_PERIOD: str = "1y"
DEFAULT_MOMENTUM_WINDOW: int = 30
TOP_N: int = 5

