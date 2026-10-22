"""Close crossings of the Bollinger basis an ATR away, daily bars: the close crossing over the basis while more than one ATR(14) above it with the MACD over its signal goes long, the mirror short (the
band-crossing variants can never hold); reversing.
Port of FMZ strategy #444018 "基于多阶段布林带和MACD指标的量化交易策略Multi-Stage-Bollinger-Bands-MACD-Crossover-Signal-Quantitative-Trading-Strategy" (Multi-Stage Bollinger Bands Strategy with MACD).

FMZ source id: 444018

Source
    https://www.fmz.com/strategy/444018 (PineScript v5, FMZ last modified 2024-03-08 16:14:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-181), BB 20 / 2; MACD 12 / 26 / 9; ATR 14
    long1 = crossover(close, lower) and close > basis + atr and macd > signal -> entry Buy1;  long2 = crossover(close, basis) and close > basis + atr and macd > signal -> entry Buy2
    short1 / short2 mirrored on the upper band and the basis -> entry Sell1 / Sell2

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close just crossing over the lower band cannot also be an ATR above the basis, so Buy1 (and
      Sell1) never fire, as written. With one position at a time (default pyramiding) the ids only
      reverse each other. Pine's stdev is the population deviation. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, basis crossings an ATR away with a MACD filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444018_basis_cross_atr_away_macd_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "atr_length": [14, 7],
}
DEFAULT_PARAMS = {"length": 20, "atr_length": 14, "mult": 2.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_length"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()

    def xo(a):
        return (c > a) & (c.shift(1) <= a.shift(1))

    def xu(a):
        return (c < a) & (c.shift(1) >= a.shift(1))

    far_up, far_dn = c > basis + atr, c < basis - atr
    le = (xo(dn) | xo(basis)) & far_up & (macd > sig)
    se = (xu(up) | xu(basis)) & far_dn & (macd < sig)
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
