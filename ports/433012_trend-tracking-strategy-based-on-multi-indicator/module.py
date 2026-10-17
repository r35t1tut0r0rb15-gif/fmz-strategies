"""Multi-indicator band crosses, broker days, as written: a "buy" opens when the close is under the SMAs 5 / 10 and EMAs
20 / 30 and crosses down through both the lower Bollinger band (5, 1.5 sd) and the basis while RSI 7 crosses under RSI
25; the mirror (above everything, crossing up through the upper band and the basis, RSI 7 over RSI 75) opens a "sell".
An open crossing above the upper band closes the buy, an open crossing under the lower band closes the sell.
Port of FMZ strategy #433012 "Trend Tracking Strategy Based on Multi indicator" (1 (lepstick-TC)).

FMZ source id: 433012

Source
    https://www.fmz.com/strategy/433012 (PineScript v4, FMZ last modified 2023-11-23 15:43:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 140-180), BB 5 / 1.5, RSI 7, RSI lengths 25 and 75 (the level inputs), SMA 10 / 5, EMA 30 / 20
    idunno = close < sma5, sma10, ema30, ema20 and crossunder(close, lower) and crossunder(rsi7, rsi(close, 25)) and crossunder(close, basis)
    idunno2 = the mirror with crossover(close, upper), crossover(rsi7, rsi(close, 75)), crossover(close, basis)
    entry long ("Al") when idunno;  entry short ("Sat") when idunno2;  close Al when crossover(open, upper);  close Sat when crossunder(open, lower)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written: the long entry fires on the bearish pattern and the short on the bullish one, and the
      RSI comparisons use the level inputs 25 / 75 as RSI lengths. "ema(close, 30) and ..." and
      "sma(close, 5) and ..." are truthy (non-zero prices), so the closes are the open crosses.
    * Each bar: the closes act on the position held at the start of the bar, then an entry wins (an
      entry against the position reverses it, as strategy.entry does). Pine's stdev is the population
      stdev; RSI is Wilder's.
    * REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band, average and RSI crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433012_inverted_band_rsi_cross"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 10],
    "mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 5, "mult": 1.5, "rsi_len": 7, "rsi_lo": 25, "rsi_hi": 75, "sma_hi": 10, "sma_lo": 5,
                  "ema_hi": 30, "ema_lo": 20}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = 100 - 100 / (1 + up / dn)
    return r.where(up != 0, 0.0).where(dn != 0, 100.0).where(~(c.isna()))


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    r = _rsi(c, int(p["rsi_len"]))
    r2, r3 = _rsi(c, int(p["rsi_lo"])), _rsi(c, int(p["rsi_hi"]))
    s_lo, s_hi = c.rolling(int(p["sma_lo"])).mean(), c.rolling(int(p["sma_hi"])).mean()
    e_hi = c.ewm(span=int(p["ema_hi"]), adjust=False).mean()
    e_lo = c.ewm(span=int(p["ema_lo"]), adjust=False).mean()
    le = ((c < s_lo) & (c < s_hi) & (c < e_hi) & (c < e_lo) & _xo(dn, c) & _xo(r2, r) & _xo(basis, c)).to_numpy()
    se = ((c > s_lo) & (c > s_hi) & (c > e_hi) & (c > e_lo) & _xo(c, up) & _xo(r, r3) & _xo(c, basis)).to_numpy()
    lx = _xo(o, up).to_numpy()
    sx = _xo(dn, o).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and lx[i]:
            pos = 0
        elif pos == -1 and sx[i]:
            pos = 0
        if le[i]:
            pos = 1
        elif se[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
