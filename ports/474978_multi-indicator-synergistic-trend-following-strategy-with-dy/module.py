"""2-hour bars: a Chandelier Exit flip to up (22 bars, 3 ATR 22) above the EMA 200 with a PVT crossing over its EMA 21 or a fast EMA-gap oscillator crossing over its signal goes long, the mirror goes short; each trade gets a stop 3 ATR beyond the signal bar's low / high; reversing.
Port of FMZ strategy #474978 "Multi Indicator Synergistic Trend Following Strategy with Dynamic Stop Loss System" (Triple Indicator Strategy (TIS)).

FMZ source id: 474978

Source
    https://www.fmz.com/strategy/474978 (PineScript v5, FMZ last modified 2024-12-13 11:45:19).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 104-165), Chandelier 22 x 3 ATR; EMA 200; PVT / EMA 21; "Ninja" (EMA 3 - EMA 13) / EMA 13 vs its EMA 24
    dir := close > lowest(low, 22) + atr ? 1 : close < highest(high, 22) - atr ? -1 : dir;  buySignal = dir == 1 and dir[1] == -1
    longCondition = buySignal and close > ema200 and (crossover(pvt, ema(pvt, 21)) or crossover(ninjaOsc, ema(ninjaOsc, 24))) -> entry Buy, exit("Exit Long", "Buy", stop = low - atr)  (short mirrored, stop = high + atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * atr is already 3 x ATR 22. The stop is sent on the signal bar only, at that bar's low minus the
      ATR distance: ported as a fraction of the fill, exact (1e-6 floor); there is no target. The
      direction flag starts at 1. PVT = cumulative (close change / previous close) x volume. Entries
      only; an opposite entry reverses. REVERSAL INTENDED. No sizing code. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-hour bars: coarse_bar_stop. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop from the signal bar as a fraction of the fill.
    2 generic: PASS, Chandelier flips confirmed by PVT or a fast oscillator in the EMA 200 trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the PVT; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474978_chandelier_flip_pvt_ninja_ema200_atr_stop_2h_reversal"
FAMILY = "chandelier"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_len": [22, 14],
    "atr_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_len": 22, "atr_mult": 3.0, "ema_len": 200}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _atr_dist(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return float(p["atr_mult"]) * _rma(tr, int(p["atr_len"]))


def _cross(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["atr_len"])
    atr = _atr_dist(bars_df, p)
    long_stop = (h.rolling(n).max() - atr).to_numpy(dtype=float)
    short_stop = (lo.rolling(n).min() + atr).to_numpy(dtype=float)
    cn = c.to_numpy(dtype=float)
    d = np.ones(len(cn))
    for i in range(len(cn)):
        prev = d[i - 1] if i > 0 else 1.0
        d[i] = 1.0 if cn[i] > short_stop[i] else (-1.0 if cn[i] < long_stop[i] else prev)
    d = pd.Series(d, index=c.index)
    d1 = d.shift(1)
    flip_up, flip_dn = (d == 1) & (d1 == -1), (d == -1) & (d1 == 1)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    pvt = (c.diff() / c.shift(1) * v).fillna(0.0).cumsum()
    pvt_s = pvt.ewm(span=21, adjust=False).mean()
    e13 = c.ewm(span=13, adjust=False).mean()
    osc = (c.ewm(span=3, adjust=False).mean() - e13) / e13 * 100
    osc_s = osc.ewm(span=24, adjust=False).mean()
    buy = flip_up & (c > ema) & (_cross(pvt, pvt_s) | _cross(osc, osc_s))
    sell = flip_dn & (c < ema) & (_cross(pvt_s, pvt) | _cross(osc_s, osc))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, h, lo = bars_df["open"], bars_df["high"], bars_df["low"]
    atr = _atr_dist(bars_df, p)
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (lo - atr).shift(1) / o)
            .mask(sf, (h + atr).shift(1) / o - 1))
    return {"sl_stop": sl_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
