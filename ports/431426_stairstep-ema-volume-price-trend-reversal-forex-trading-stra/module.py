"""Fractals in an EMA stack, faded as written (exlux99), 1-hour bars: a confirmed down fractal with the EMAs 10 < 20 < 100 of
hl2 goes long, a confirmed up fractal with the EMAs 10 > 20 > 100 goes short; the source's 250-tick target and stop become
ATR fractions.
Port of FMZ strategy #431426 "基于交易量平均价和Stairstep-EMA-的策略Volume-Price-Trend-Reversal-Forex-Trading-Strategy-Based-on-Stairstep-EMA" (Forex Fractal EMA Scalper).

FMZ source id: 431426

Source
    https://www.fmz.com/strategy/431426 (PineScript v5, FMZ last modified 2023-11-07 17:03:57).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 207-278), fractal n 2, EMA 10 / 20 / 100 of hl2, TP / SL 25 "pips" x 10 ticks
    upFractal = high[2] above the 2 later highs and above the earlier ones (Bill Williams, with up to 4 equal highs)
    long = ema10 > ema20 > ema100 and upFractal;  short = ema10 < ema20 < ema100 and downFractal
    strategy.entry("long", long, when = short);  strategy.entry("short", short, when = long)   (swapped as written)
    exit(profit = 250, loss = 250 ticks) per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are swapped in the source (the "short" setup enters long and the "long" setup
      short): ported as written. The fractal is confirmed n bars after its bar, using completed bars
      only; the flat-top variants (up to 4 equal highs to the left) as written.
    * Criterion 2: the target and stop are 250 ticks (25 USD on BTC_USDT at mintick 0.1, about 0.17 ATR
      on 1-hour BTC); they become tp_atr / sl_atr x the Wilder ATR 14 of the signal bar, as fractions
      of its close, fixed at entry.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick target / stop -> ATR fractions.
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

NAME = "fmz_431426_fractal_ema_stack_fade"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "n": [2, 3],
    "bracket_atr": [0.17, 1.0],
}
DEFAULT_PARAMS = {"n": 2, "len1": 10, "len2": 20, "len3": 100, "atr_len": 14, "bracket_atr": 0.17}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fractal(x, n, up):
    """The source's fractal at bar t - n, confirmed at bar t (x[k] means x k bars back)."""
    m = len(x)
    out = np.zeros(m, dtype=bool)

    def back(t, k):
        return x[t - k] if t - k >= 0 else np.nan

    def lt(a, b):        # a strictly beyond b on the fractal's side
        return a < b if up else a > b

    def le(a, b):
        return a <= b if up else a >= b
    for t in range(m):
        piv = back(t, n)
        if np.isnan(piv):
            continue
        right = all(lt(back(t, n - i), piv) for i in range(1, n + 1))
        if not right:
            continue
        ok = False
        for k in range(5):
            if all(le(back(t, n + j), piv) for j in range(1, k + 1)) and \
                    all(lt(back(t, n + i + k), piv) for i in range(1, n + 1)):
                ok = True
                break
        out[t] = ok
    return out


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    src = (h + lo) / 2
    e1, e2, e3 = (src.ewm(span=int(p[k]), adjust=False).mean() for k in ("len1", "len2", "len3"))
    n = int(p["n"])
    upf = _fractal(h.to_numpy(dtype=float), n, True)
    dnf = _fractal(lo.to_numpy(dtype=float), n, False)
    long_set = ((e1 > e2) & (e2 > e3)).to_numpy() & upf
    short_set = ((e1 < e2) & (e2 < e3)).to_numpy() & dnf
    idx = bars_df.index
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    se_ = pd.Series(long_set, index=idx)       # entries swapped, as written
    le_ = pd.Series(short_set & ~long_set, index=idx)
    return le_, se_, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    d = (af * float(p["bracket_atr"])).shift(1)
    return {"sl_stop": d, "tp_stop": d.copy()}


def portfolio_kwargs(**params):
    return {}
