"""CCI of highs and lows, 3-hour bars: the CCI(11) of the lows crossing up through -150 goes long, the CCI(11)
of the highs crossing down through +150 goes short; each trade has the source's (near-zero) bracket.
Port of FMZ strategy #429145 "4小时CCI反转策略4-Hour-CCI-Reversal-Strategy" (4H CCI Strategy).

FMZ source id: 429145

Source
    https://www.fmz.com/strategy/429145 (PineScript v4, FMZ last modified 2023-10-13 15:29:05).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 153-182), CCI 11, -150 / +150, exit profit 0.01 / loss 0.005 ticks
    dcci = cci(low, 11); ucci = cci(high, 11); only when cci(ohlc4, 11) exists
    crossover(dcci, -150) -> entry long + exit(profit = 0.01, loss = 0.005); crossunder(ucci, 150) -> entry short + exit(same)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 15-minute security, the KAMA and its slope are computed but never reach an order: not
      ported (so the lower-timeframe read does not matter).
    * Criterion 2: profit 0.01 / loss 0.005 ticks (0.001 / 0.0005 USD at a 0.1 tick) become tp_atr /
      sl_atr x Wilder ATR(14) of the signal bar (shifted one bar inside stops(), re-based on the fill):
      about 0.000003 / 0.0000015 ATR on 3-hourly BTC, i.e. an exit at the first price move, as written.
      The grid adds a wider declared pair (1 / 0.5 ATR) beside it.
    * strategy.entry reverses. Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
      Stops on 3-hour bars: mark coarse_bar_stop. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the bracket is ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_429145_cci_high_low_reversal"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.000003, 1.0],
    "sl_atr": [0.0000015, 0.5],
}
DEFAULT_PARAMS = {"length": 11, "oversold": -150, "overbought": 150, "tp_atr": 0.000003, "sl_atr": 0.0000015,
                  "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _cci(x, n):
    ma = x.rolling(n).mean()
    md = x.rolling(n).apply(lambda w: np.mean(np.abs(w - w.mean())), raw=True)
    return (x - ma) / (0.015 * md.replace(0.0, np.nan))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    ucci, dcci = _cci(h, n), _cci(lo, n)
    ok = _cci((o + h + lo + c) / 4, n).notna()
    os_, ob = float(p["oversold"]), float(p["overbought"])
    long_e = (ok & (dcci > os_) & (dcci.shift(1) <= os_)).astype(bool)
    short_e = (ok & (ucci < ob) & (ucci.shift(1) >= ob) & ~long_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    frac = _rma(tr, int(p["atr_length"])) / c
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
