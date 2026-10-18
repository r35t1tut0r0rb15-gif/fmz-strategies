"""Three Supertrend lines and an EMA 100, 1-hour bars: a close over the EMA and over all three Supertrend lines goes long; under all four goes short (reversing). The script passes
its "period" and "multiplier" inputs in swapped positions, as written.
Port of FMZ strategy #436143 "Super Trend Triple Strategy" (Triple Supertrend Strategy).

FMZ source id: 436143

Source
    https://www.fmz.com/strategy/436143 (PineScript v5, FMZ last modified 2023-12-21 16:02:57).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 151-179), inputs period 3 / 2 / 1 and multiplier 12 / 11 / 10; EMA 100
    [st_i, _] = ta.supertrend(supertrend_i_period, supertrend_i_multiplier)   (Pine's signature is supertrend(factor, atrPeriod))
    longCondition = close > ema100 and close > st1 and close > st2 and close > st3;  shortCondition = the mirror;  entry long / short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend takes (factor, atrPeriod); the script passes the period input first and the
      multiplier second, so the factors are 3, 2, 1 and the ATR lengths are 12, 11, 10: ported as written.
      The conditions are states re-sent every bar; vbt ignores a same-side signal. pyramiding 1.
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Supertrend lines and an EMA.
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

NAME = "fmz_436143_triple_supertrend_swapped_args"
FAMILY = "supertrend"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [100, 200],
    "factor_scale": [1.0, 2.0],
}
DEFAULT_PARAMS = {"ema_length": 100, "factor_scale": 1.0}
SETTINGS = ((3.0, 12), (2.0, 11), (1.0, 10))      # (factor, ATR length) = (period input, multiplier input)


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


def _supertrend_line(h, lo, c, factor, n):
    """Line of Pine's built-in supertrend(factor, atrPeriod)."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            up_dir = False
        elif st[i - 1] == ub[i - 1]:
            up_dir = cv[i] > ub[i]
        else:
            up_dir = not (cv[i] < lb[i])
        st[i] = lb[i] if up_dir else ub[i]
    return pd.Series(st, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    lines = [_supertrend_line(h, lo, c, f * float(p["factor_scale"]), n) for f, n in SETTINGS]
    le = ((c > ema) & (c > lines[0]) & (c > lines[1]) & (c > lines[2])).fillna(False).astype(bool)
    se = ((c < ema) & (c < lines[0]) & (c < lines[1]) & (c < lines[2])).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
