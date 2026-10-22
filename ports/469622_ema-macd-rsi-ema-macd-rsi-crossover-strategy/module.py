"""Fast EMA 3 / 4 or MACD 1 / 2 / 3 crossings with an RSI 42 filter, 3-hour bars: either crossing up with the RSI over 30 goes long (unless already long) with a 1 ATR stop from the signal close, either crossing down with the RSI under 70 goes short with the mirror stop; reversing.
Port of FMZ strategy #469622 "EMA-MACD-RSI-交叉策略-EMA-MACD-RSI-Crossover-Strategy" (Mister Buy / sell signals).

FMZ source id: 469622

Source
    https://www.fmz.com/strategy/469622 (PineScript v5, FMZ last modified 2024-10-14 12:22:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 120-199), EMA 3 / 4 (EMA 5 plotted only); MACD 1 / 2 / 3; RSI 42, levels 30 / 70; ATR 12 x 1 stop
    (crossover(ema3, ema4) or crossover(macd, signal)) and rsi > 30 and not long -> entry Buy + exit(stop = close - atr)
    (crossunder(ema3, ema4) or crossunder(macd, signal)) and rsi < 70 and not short -> entry Sell + exit(stop = close + atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is sent once on the signal bar: ported as ATR 12 / close of the signal bar shifted into the
      fill. An entry while already on that side is skipped, as written; entries on the other side
      reverse. MACD 1 / 2 / 3 uses an EMA 1 (the close itself). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 3-hour bars: mark coarse_bar_stop. No sizing code. FREQ =
      "3h" from the backtest header (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop at entry.
    2 generic: PASS, fast EMA / MACD crossings with an RSI filter and an ATR stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_469622_ema3_4_or_macd123_cross_rsi42_atr_stop_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [42, 14],
    "atr_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"rsi_len": 42, "atr_mult": 1.0, "atr_len": 12}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _x(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e3, e4 = c.ewm(span=3, adjust=False).mean(), c.ewm(span=4, adjust=False).mean()
    macd = c - c.ewm(span=2, adjust=False).mean()
    sig = macd.ewm(span=3, adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (_x(e3, e4) | _x(macd, sig)) & (r > 30)
    se = (_x(e4, e3) | _x(sig, macd)) & (r < 70)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["atr_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1)}


def portfolio_kwargs(**params):
    return {}
