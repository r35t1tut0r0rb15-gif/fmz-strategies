"""Stochastic and RSI extremes held while they last, broker days: from flat, a stochastic 5 under 50 with the RSI 14 under 30
goes long and a stochastic over 80 with the RSI over 70 goes short; each position is closed on the first bar its
condition no longer holds.
Port of FMZ strategy #433960 "双均线与RSI组合的MT5马丁格尔scalping策略RSI-and-Moving-Average-Combination-MT5-Martingale-Scalping-Strategy" (F2.2 Martingale Scalping Strategy).

FMZ source id: 433960

Source
    https://www.fmz.com/strategy/433960 (PineScript v5, FMZ last modified 2023-12-01 17:56:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-198), RSI 70 / 30; stochastic 5; K1 0.2 (zone high 80), K2 0.5 (zone low 50); trend activity 1.0
    long = stoch(5) < 50 and rsi < 30;  short = stoch(5) > 80 and rsi > 70  (trendActivity > 0 always)
    long and flat -> entry long;  short and flat -> entry short;  not long and long position -> close;  not short and short position -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The martingale lot variables are computed but never passed to an order: the entries use the
      default quantity, so the lot logic is sizing only and dropped.
    * Long only from flat and short only from flat; the close comes on the first bar the entry
      condition is false. Opposite entries cannot occur. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the martingale lot formula stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433960_stoch_rsi_extreme_hold"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "osc_len": [5, 14],
    "rsi_band": [30, 40],
}
DEFAULT_PARAMS = {"osc_len": 5, "rsi_band": 30, "zone_high": 80.0, "zone_low": 50.0}


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
    n = int(p["osc_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    st = 100 * (c - ll) / (hh - ll)
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    band = float(p["rsi_band"])
    lc = ((st < p["zone_low"]) & (r < band)).to_numpy()
    sc = ((st > p["zone_high"]) & (r > 100 - band)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 0:
            if lc[i]:
                pos = 1
            elif sc[i]:
                pos = -1
        elif start == 1 and not lc[i]:
            pos = 0
        elif start == -1 and not sc[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev == 0), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
