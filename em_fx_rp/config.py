"""
Configuration and metadata for FX universes, tickers, and Bloomberg conventions.
Supports 57 currencies across 6 categories:
1) DM: EUR, GBP, CHF, AUD, NZD, CAD, SEK, NOK, DKK
2) CEEMEA: CZK, PLN, HUF, RON, TRY, ILS, EGP, ZAR, SAR, AED, QAR, RUB, UAH
3) LatAM: MXN, BRL, CLP, COP, PEN, ARS
4) SSA: NGN, KES, GHS, UGX, ZMW, TZS, AOA, XOF
5) Asia: CNY, CNH, HKD, SGD, TWD, KRW, INR, IDR, PHP, THB, MYR, VND, PKR
6) Edge: KZT, UZS, TJS, KGS, MNT, GEL, AZN, AMD
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CurrencyMeta:
    code: str                     # e.g., 'MXN'
    name: str                     # e.g., 'Mexican Peso'
    region: str                   # 'DM', 'CEEMEA', 'LatAm', 'SSA', 'Asia', 'Edge'
    market_quote: str             # e.g., 'USDMXN' or 'EURUSD'
    is_usd_base: bool             # True if market quote is USD/CCY (e.g. USDMXN), False if CCY/USD (e.g. EURUSD)
    spot_ticker: str              # e.g. 'USDMXN Curncy'
    fwd_1m_ticker: str            # e.g. 'USDMXN1M Curncy'
    fwd_3m_ticker: str            # e.g. 'USDMXN3M Curncy'
    fwd_12m_ticker: str           # e.g. 'USDMXN12M Curncy'
    vol_1m_ticker: str            # e.g. 'USDMXNV1M Curncy'
    vol_3m_ticker: str            # e.g. 'USDMXNV3M Curncy'
    rr_25d_1m_ticker: str         # e.g. 'USDMXN25R1M Curncy'
    rr_25d_3m_ticker: str         # e.g. 'USDMXN25R3M Curncy'
    bf_25d_1m_ticker: str         # e.g. 'USDMXN25B1M Curncy'
    bf_25d_3m_ticker: str         # e.g. 'USDMXN25B3M Curncy'
    cpi_yoy_ticker: str           # e.g. 'MXPCYOY Index'
    policy_rate_ticker: str       # e.g. 'MXONBR Index'


def _build_meta(
    code: str,
    name: str,
    region: str,
    is_usd_base: bool = True,
    market_quote: Optional[str] = None,
    cpi_ticker: Optional[str] = None,
    policy_ticker: Optional[str] = None
) -> CurrencyMeta:
    quote = market_quote or (f"USD{code}" if is_usd_base else f"{code}USD")
    return CurrencyMeta(
        code=code,
        name=name,
        region=region,
        market_quote=quote,
        is_usd_base=is_usd_base,
        spot_ticker=f"{quote} Curncy",
        fwd_1m_ticker=f"{quote}1M Curncy",
        fwd_3m_ticker=f"{quote}3M Curncy",
        fwd_12m_ticker=f"{quote}12M Curncy",
        vol_1m_ticker=f"{quote}V1M Curncy",
        vol_3m_ticker=f"{quote}V3M Curncy",
        rr_25d_1m_ticker=f"{quote}25R1M Curncy",
        rr_25d_3m_ticker=f"{quote}25R3M Curncy",
        bf_25d_1m_ticker=f"{quote}25B1M Curncy",
        bf_25d_3m_ticker=f"{quote}25B3M Curncy",
        cpi_yoy_ticker=cpi_ticker or f"{code}CPI Index",
        policy_rate_ticker=policy_ticker or f"{code}RATE Index"
    )


# -----------------------------------------------------------------------------
# Complete 57-Currency Master Metadata Directory
# -----------------------------------------------------------------------------
CURRENCIES: Dict[str, CurrencyMeta] = {
    # 1) DM: Developed Markets (9)
    "EUR": _build_meta("EUR", "Euro", "DM", is_usd_base=False, cpi_ticker="ECCPEST Index", policy_ticker="EURR002W Index"),
    "GBP": _build_meta("GBP", "British Pound", "DM", is_usd_base=False, cpi_ticker="UKRPCI Index", policy_ticker="UKBRBASE Index"),
    "CHF": _build_meta("CHF", "Swiss Franc", "DM", is_usd_base=True, cpi_ticker="SZCPIYOY Index", policy_ticker="SZLTTR Index"),
    "AUD": _build_meta("AUD", "Australian Dollar", "DM", is_usd_base=False, cpi_ticker="AUCPIYOY Index", policy_ticker="RBACOR Index"),
    "NZD": _build_meta("NZD", "New Zealand Dollar", "DM", is_usd_base=False, cpi_ticker="NZCPIYOY Index", policy_ticker="NZOCR Index"),
    "CAD": _build_meta("CAD", "Canadian Dollar", "DM", is_usd_base=True, cpi_ticker="CACPIYOY Index", policy_ticker="BOCONBR Index"),
    "SEK": _build_meta("SEK", "Swedish Krona", "DM", is_usd_base=True, cpi_ticker="SWCPYOY Index", policy_ticker="SWRRATEI Index"),
    "NOK": _build_meta("NOK", "Norwegian Krone", "DM", is_usd_base=True, cpi_ticker="NWCPYOY Index", policy_ticker="NOWCBR Index"),
    "DKK": _build_meta("DKK", "Danish Krone", "DM", is_usd_base=True, cpi_ticker="DKCPYOY Index", policy_ticker="DKLNDR Index"),

    # 2) CEEMEA: Central & Eastern Europe, Middle East, Africa (13)
    "CZK": _build_meta("CZK", "Czech Koruna", "CEEMEA", is_usd_base=True, cpi_ticker="CZCPYOY Index", policy_ticker="CZRP2W Index"),
    "PLN": _build_meta("PLN", "Polish Zloty", "CEEMEA", is_usd_base=True, cpi_ticker="POCPIYOY Index", policy_ticker="POLBFREF Index"),
    "HUF": _build_meta("HUF", "Hungarian Forint", "CEEMEA", is_usd_base=True, cpi_ticker="HNCPIY Index", policy_ticker="MNBBRATE Index"),
    "RON": _build_meta("RON", "Romanian Leu", "CEEMEA", is_usd_base=True, cpi_ticker="ROCPIYOY Index", policy_ticker="ROBRPOL Index"),
    "TRY": _build_meta("TRY", "Turkish Lira", "CEEMEA", is_usd_base=True, cpi_ticker="TUTIYOY Index", policy_ticker="TRONR Index"),
    "ILS": _build_meta("ILS", "Israeli Shekel", "CEEMEA", is_usd_base=True, cpi_ticker="ISCPIYOY Index", policy_ticker="ILBRBASE Index"),
    "EGP": _build_meta("EGP", "Egyptian Pound", "CEEMEA", is_usd_base=True, cpi_ticker="ECCPIYOY Index", policy_ticker="EGCBODR Index"),
    "ZAR": _build_meta("ZAR", "South African Rand", "CEEMEA", is_usd_base=True, cpi_ticker="SACPIY Index", policy_ticker="SARRP Index"),
    "SAR": _build_meta("SAR", "Saudi Riyal", "CEEMEA", is_usd_base=True, cpi_ticker="SACPIYOY Index", policy_ticker="SARREPO Index"),
    "AED": _build_meta("AED", "UAE Dirham", "CEEMEA", is_usd_base=True, cpi_ticker="AECPIYOY Index", policy_ticker="AECBRATE Index"),
    "QAR": _build_meta("QAR", "Qatari Riyal", "CEEMEA", is_usd_base=True, cpi_ticker="QACPIYOY Index", policy_ticker="QACBODR Index"),
    "RUB": _build_meta("RUB", "Russian Ruble", "CEEMEA", is_usd_base=True, cpi_ticker="RUCPIYOY Index", policy_ticker="CBRONBR Index"),
    "UAH": _build_meta("UAH", "Ukrainian Hryvnia", "CEEMEA", is_usd_base=True, cpi_ticker="UKCPIYOY Index", policy_ticker="NBUKDISC Index"),

    # 3) LatAM: Latin America (6)
    "MXN": _build_meta("MXN", "Mexican Peso", "LatAm", is_usd_base=True, cpi_ticker="MXPCYOY Index", policy_ticker="MXONBR Index"),
    "BRL": _build_meta("BRL", "Brazilian Real", "LatAm", is_usd_base=True, cpi_ticker="BZIPTL Index", policy_ticker="BZSTSETA Index"),
    "CLP": _build_meta("CLP", "Chilean Peso", "LatAm", is_usd_base=True, cpi_ticker="CHCPIYOY Index", policy_ticker="CHPMINDX Index"),
    "COP": _build_meta("COP", "Colombian Peso", "LatAm", is_usd_base=True, cpi_ticker="COCPIYOY Index", policy_ticker="COPREBR Index"),
    "PEN": _build_meta("PEN", "Peruvian Sol", "LatAm", is_usd_base=True, cpi_ticker="PECPIYOY Index", policy_ticker="PRRPREF Index"),
    "ARS": _build_meta("ARS", "Argentine Peso", "LatAm", is_usd_base=True, cpi_ticker="ARCPIYOY Index", policy_ticker="ARLNDR Index"),

    # 4) SSA: Sub-Saharan Africa (8)
    "NGN": _build_meta("NGN", "Nigerian Naira", "SSA", is_usd_base=True, cpi_ticker="NGCPIYOY Index", policy_ticker="NGMPRATE Index"),
    "KES": _build_meta("KES", "Kenyan Shilling", "SSA", is_usd_base=True, cpi_ticker="KECPIYOY Index", policy_ticker="KECBRATE Index"),
    "GHS": _build_meta("GHS", "Ghanaian Cedi", "SSA", is_usd_base=True, cpi_ticker="GHCPIYOY Index", policy_ticker="GHPRATE Index"),
    "UGX": _build_meta("UGX", "Ugandan Shilling", "SSA", is_usd_base=True, cpi_ticker="UGCPIYOY Index", policy_ticker="UGCBRATE Index"),
    "ZMW": _build_meta("ZMW", "Zambian Kwacha", "SSA", is_usd_base=True, cpi_ticker="ZMCPIYOY Index", policy_ticker="ZMPRATE Index"),
    "TZS": _build_meta("TZS", "Tanzanian Shilling", "SSA", is_usd_base=True, cpi_ticker="TZCPIYOY Index", policy_ticker="TZCBRATE Index"),
    "AOA": _build_meta("AOA", "Angolan Kwanza", "SSA", is_usd_base=True, cpi_ticker="AOCPIYOY Index", policy_ticker="AOBNRATE Index"),
    "XOF": _build_meta("XOF", "West African CFA Franc", "SSA", is_usd_base=True, cpi_ticker="WACPIYOY Index", policy_ticker="BCEAOMPR Index"),

    # 5) Asia: Asia Pacific & South Asia (13)
    "CNY": _build_meta("CNY", "Chinese Yuan (Onshore)", "Asia", is_usd_base=True, cpi_ticker="CNCPIY Index", policy_ticker="PBC1YNDR Index"),
    "CNH": _build_meta("CNH", "Chinese Yuan (Offshore)", "Asia", is_usd_base=True, cpi_ticker="CNCPIY Index", policy_ticker="CNHHIB1M Index"),
    "HKD": _build_meta("HKD", "Hong Kong Dollar", "Asia", is_usd_base=True, cpi_ticker="HKCPIY Index", policy_ticker="HKBASE Index"),
    "SGD": _build_meta("SGD", "Singapore Dollar", "Asia", is_usd_base=True, cpi_ticker="SGCPIY Index", policy_ticker="MASOVERN Index"),
    "TWD": _build_meta("TWD", "Taiwan Dollar", "Asia", is_usd_base=True, cpi_ticker="TWCPIY Index", policy_ticker="CBCDR10D Index"),
    "KRW": _build_meta("KRW", "Korean Won", "Asia", is_usd_base=True, cpi_ticker="KOCPIYOY Index", policy_ticker="KORP7D Index"),
    "INR": _build_meta("INR", "Indian Rupee", "Asia", is_usd_base=True, cpi_ticker="INCPIYOY Index", policy_ticker="INRPTRR Index"),
    "IDR": _build_meta("IDR", "Indonesian Rupiah", "Asia", is_usd_base=True, cpi_ticker="IDCPIYOY Index", policy_ticker="IDBR7D Index"),
    "PHP": _build_meta("PHP", "Philippine Peso", "Asia", is_usd_base=True, cpi_ticker="PHCPIYOY Index", policy_ticker="PHRPON Index"),
    "THB": _build_meta("THB", "Thai Baht", "Asia", is_usd_base=True, cpi_ticker="THCPIYOY Index", policy_ticker="THRP1D Index"),
    "MYR": _build_meta("MYR", "Malaysian Ringgit", "Asia", is_usd_base=True, cpi_ticker="MACPIYOY Index", policy_ticker="MYOPR Index"),
    "VND": _build_meta("VND", "Vietnamese Dong", "Asia", is_usd_base=True, cpi_ticker="VNCPIYOY Index", policy_ticker="VNREFI Index"),
    "PKR": _build_meta("PKR", "Pakistani Rupee", "Asia", is_usd_base=True, cpi_ticker="PKCPIYOY Index", policy_ticker="PKPRATE Index"),

    # 6) Edge: Frontier / Central Asia & Caucasus (8)
    "KZT": _build_meta("KZT", "Kazakhstani Tenge", "Edge", is_usd_base=True, cpi_ticker="KZCPIYOY Index", policy_ticker="KZBRTONR Index"),
    "UZS": _build_meta("UZS", "Uzbekistani Som", "Edge", is_usd_base=True, cpi_ticker="UZCPIYOY Index", policy_ticker="UZCBRATE Index"),
    "TJS": _build_meta("TJS", "Tajikistani Somoni", "Edge", is_usd_base=True, cpi_ticker="TJCPIYOY Index", policy_ticker="TJCBRATE Index"),
    "KGS": _build_meta("KGS", "Kyrgyzstani Som", "Edge", is_usd_base=True, cpi_ticker="KGCPIYOY Index", policy_ticker="KGCBRATE Index"),
    "MNT": _build_meta("MNT", "Mongolian Tugrik", "Edge", is_usd_base=True, cpi_ticker="MNCPIYOY Index", policy_ticker="MNBPRATE Index"),
    "GEL": _build_meta("GEL", "Georgian Lari", "Edge", is_usd_base=True, cpi_ticker="GECPIYOY Index", policy_ticker="GEPOLRAT Index"),
    "AZN": _build_meta("AZN", "Azerbaijani Manat", "Edge", is_usd_base=True, cpi_ticker="AZCPIYOY Index", policy_ticker="AZCBREFI Index"),
    "AMD": _build_meta("AMD", "Armenian Dram", "Edge", is_usd_base=True, cpi_ticker="AMCPIYOY Index", policy_ticker="AMCBRATE Index"),
}

# -----------------------------------------------------------------------------
# Pre-defined Universes exactly matching User Categories
# -----------------------------------------------------------------------------
DEFAULT_UNIVERSES: Dict[str, List[str]] = {
    # 1) DM
    "DM": ["EUR", "GBP", "CHF", "AUD", "NZD", "CAD", "SEK", "NOK", "DKK"],

    # 2) CEEMEA
    "CEEMEA": ["CZK", "PLN", "HUF", "RON", "TRY", "ILS", "EGP", "ZAR", "SAR", "AED", "QAR", "RUB", "UAH"],

    # 3) LatAM
    "LATAM": ["MXN", "BRL", "CLP", "COP", "PEN", "ARS"],

    # 4) SSA
    "SSA": ["NGN", "KES", "GHS", "UGX", "ZMW", "TZS", "AOA", "XOF"],

    # 5) Asia
    "ASIA": ["CNY", "CNH", "HKD", "SGD", "TWD", "KRW", "INR", "IDR", "PHP", "THB", "MYR", "VND", "PKR"],

    # 6) Edge
    "EDGE": ["KZT", "UZS", "TJS", "KGS", "MNT", "GEL", "AZN", "AMD"],

    # Curated EM & Broad Universes
    "EM_CORE": ["MXN", "BRL", "CLP", "COP", "ZAR", "PLN", "HUF", "CZK", "TRY", "KRW", "INR", "IDR", "CNH", "SGD", "TWD"],
    "EM_ALL": [
        # CEEMEA
        "CZK", "PLN", "HUF", "RON", "TRY", "ILS", "EGP", "ZAR", "SAR", "AED", "QAR", "RUB", "UAH",
        # LatAM
        "MXN", "BRL", "CLP", "COP", "PEN", "ARS",
        # SSA
        "NGN", "KES", "GHS", "UGX", "ZMW", "TZS", "AOA", "XOF",
        # Asia
        "CNY", "CNH", "HKD", "SGD", "TWD", "KRW", "INR", "IDR", "PHP", "THB", "MYR", "VND", "PKR",
        # Edge
        "KZT", "UZS", "TJS", "KGS", "MNT", "GEL", "AZN", "AMD"
    ],
    "ALL": list(CURRENCIES.keys())
}

# Global Risk Benchmarks
GLOBAL_BENCHMARKS = {
    "SPX": "SPX Index",
    "VIX": "VIX Index",
    "US_FED_FUNDS": "FEDL01 Index",
    "US_CPI_YOY": "CPI YOY Index",
    "US_10Y_YIELD": "USGG10YR Index"
}
