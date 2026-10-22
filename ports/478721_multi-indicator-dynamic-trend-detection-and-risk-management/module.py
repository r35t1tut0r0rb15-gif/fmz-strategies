"""RSI 14 extremes with a turning stochastic 14, 4-hour bars: RSI under 30 with the stochastic turning up goes long, RSI over 70 with it turning down goes short, each with a 5 % stop and 1 % target from the entry price; a side's entries wait while that side's levels are set.
Port of FMZ strategy #478721 "Multi Indicator Dynamic Trend Detection and Risk Management Trading Strategy" (RSI + CHOP + Stochastic Strategy).

FMZ source id: 478721

Source
    https://www.fmz.com/strategy/478721 (PineScript v5, FMZ last modified 2025-01-17 15:55:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-203), RSI 14, 30 / 70; "chop" = 100 log10(range14 / sma14) / log10(2) under 50; stochastic 14 with d = k[1]; TP 1 %, SL 5 % of strategy.position_avg_price
    buy = rsi < 30 and chop < 50 and crossover(k, k[1]) and na(longStop) -> entry Long;  sell = rsi > 70 and chop < 50 and crossunder(k, k[1]) and na(shortStop) -> entry Short
    long and na(longTP) -> set long levels from avg;  short -> set short levels;  flat -> reset all levels;  in a position: exit(limit, stop) from the levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "choppiness" is the log of the 14-bar range over the SMA 14 of the close, which is almost always
      under 50, as written; d is the previous stochastic value. The bracket is set from the position's
      average price on its first bar: scalar fractions of the entry fill, active from the fill (as
      #440797). The level flags gate the entries: they are set while a side is held and cleared only when
      flat, so a short that reversed a long cannot be reversed back to long until it exits. A loop
      follows the flags and the bracket on each bar's high / low (as #449508) to know when the position is
      flat. On a bar with both signals the later short call wins (#437773). REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No
      sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price bracket as fractions of the fill.
    2 generic: PASS, RSI extremes with a turning stochastic and a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
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

NAME = "fmz_478721_rsi14_extreme_stoch_turn_pct_bracket_level_gate_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.01, 0.03],
    "sl_pct": [0.05, 0.02],
}
DEFAULT_PARAMS = {"tp_pct": 0.01, "sl_pct": 0.05, "rsi_period": 14, "chop_period": 14, "stoch_k": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    r = _rsi(c, int(p["rsi_period"]))
    n = int(p["chop_period"])
    rng = h.rolling(n).max() - lo.rolling(n).min()
    ratio = (rng / c.rolling(n).mean()).where(rng > 0)
    chop = 100 * np.log10(ratio) / np.log10(2)
    ks = int(p["stoch_k"])
    ll, hh = lo.rolling(ks).min(), h.rolling(ks).max()
    k = 100 * (c - ll) / (hh - ll).where(hh > ll)
    d = k.shift(1)
    buy = ((r < 30) & (chop < 50) & (k > d) & (k.shift(1) <= d.shift(1))).to_numpy()
    sell = ((r > 70) & (chop < 50) & (k < d) & (k.shift(1) >= d.shift(1))).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    tp, sl = float(p["tp_pct"]), float(p["sl_pct"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, avg = 0, 0, np.nan
    l_set = s_set = False
    for i in range(m):
        if pend != 0:
            pos, pend, avg = pend, 0, ov[i]
        if pos == 1 and (lv[i] <= avg * (1 - sl) or hv[i] >= avg * (1 + tp)):
            pos = 0                              # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= avg * (1 + sl) or lv[i] <= avg * (1 - tp)):
            pos = 0
        want = 0
        if buy[i] and not l_set:
            want = 1
        if sell[i] and not s_set:
            want = -1
        if pos == 1:
            l_set = True
        elif pos == -1:
            s_set = True
        else:
            l_set = s_set = False
        if want == 1 and pos != 1:
            le[i], pend = True, 1
        elif want == -1 and pos != -1:
            se[i], pend = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
