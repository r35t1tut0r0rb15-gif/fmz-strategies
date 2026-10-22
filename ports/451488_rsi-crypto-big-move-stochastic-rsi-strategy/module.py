"""Stochastic RSI extremes after a big move, 1-hour bars: a move of at least 2.5 % against the close 23 bars back with the Stoch RSI %K or %D under 3 goes long, over 97 goes short; reversing.
Port of FMZ strategy #451488 "加密货币大幅波动随机RSI策略-Crypto-Big-Move-Stochastic-RSI-Strategy" (Crypto Big Move Stoch RSI Strategy).

FMZ source id: 451488

Source
    https://www.fmz.com/strategy/451488 (PineScript v5, FMZ last modified 2024-05-15 10:27:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-176), lookback 24 (close[23]); move 2.5 %; RSI 14, stochastic 14, %K 3, %D 3; 10 % of equity
    |close - close[23]| / close[23] >= 0.025 and (k < 3 or d < 3) -> entry Buy Signal;  same move and (k > 97 or d > 97) -> entry Sell Signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * The move is measured in either direction. The two conditions cannot meet on one bar (a %D over
      97 needs every %K over 91). There is no exit: positions end at the opposite entry. REVERSAL
      INTENDED. The 10 % of equity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Stoch RSI extremes after big moves.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing stored.
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

NAME = "fmz_451488_big_move_stoch_rsi_extreme_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [24, 12],
    "move_pct": [2.5, 4.0],
}
DEFAULT_PARAMS = {"lookback": 24, "move_pct": 2.5, "rsi_len": 14, "stoch_len": 14, "k": 3, "d": 3,
                  "lo": 3.0, "hi": 97.0}


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
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    lo_, hi_ = r.rolling(n).min(), r.rolling(n).max()
    rng = hi_ - lo_
    st = 100 * (r - lo_) / rng.where(rng > 0)
    k = st.rolling(int(p["k"])).mean()
    d = k.rolling(int(p["d"])).mean()
    past = c.shift(int(p["lookback"]) - 1)
    big = (c - past).abs() / past >= float(p["move_pct"]) / 100
    le = big & ((k < float(p["lo"])) | (d < float(p["lo"])))
    se = big & ((k > float(p["hi"])) | (d > float(p["hi"])))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
