"""DI and MACD agreement state, broker days: +DI above -DI with the MACD line above its signal goes long, the mirror goes
short (reversing), otherwise the last side is kept; the "stop loss" exits close an id that was never opened, so they do
nothing (as written).
Port of FMZ strategy #435252 "基于ADX和MACD指标的交易策略ADX-and-MACD-Indicators-based-Trading-Strategy" (TUE ADX/MACD Confluence V1.0).

FMZ source id: 435252

Source
    https://www.fmz.com/strategy/435252 (PineScript v5, FMZ last modified 2023-12-13 15:45:24).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 165-221), DMI 14 / 10; MACD 12 / 26 / 9 on close; stop loss input 100
    longcheck = diplus > diminus and macdline > signalline;  shortcheck = diminus > diplus and signalline > macdline;  trade = 1 / -1 on a check, else trade[1]
    trade == 1 -> entry "Long";  trade == -1 -> entry "Short";  trade == 1 and close < close[1] - 100 -> close("LongExit");  trade == -1 and close > close[1] + 100 -> close("ShortExit")

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.close("LongExit") names an id that no entry uses ("Long", "Short"): it closes
      nothing, so the stop-loss rules never act. Ported as written: no exit; the intended
      version (exits on a 100-unit move) is owed. strategy.entry reverses: REVERSAL INTENDED.
    * The DI length is the ADX input 14 (the second argument, 10, only smooths the ADX, which is
      not used). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, exits on a missing id: as written, none.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the stop loss input 100 stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND368715 (2 members, best partner #368715, Jaccard 0.679); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435252_adx_macd_agreement"
FAMILY = "trend_confluence"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "di_len": [14, 21],
    "macd_fast": [12, 8],
}
DEFAULT_PARAMS = {"di_len": 14, "macd_fast": 12, "macd_slow": 26, "macd_sig": 9}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["di_len"])
    a = 1 / n
    up, dn = h.diff(), -lo.diff()
    plus = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    minus = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(up.notna())
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    trn = tr.ewm(alpha=a, adjust=False).mean()
    dip = 100 * plus.ewm(alpha=a, adjust=False).mean() / trn
    dim = 100 * minus.ewm(alpha=a, adjust=False).mean() / trn
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["macd_sig"]), adjust=False).mean()
    lc = ((dip > dim) & (macd > sig)).to_numpy()
    sc = ((dim > dip) & (sig > macd)).to_numpy()
    m = len(lc)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if lc[i]:
            q = 1
        elif sc[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
