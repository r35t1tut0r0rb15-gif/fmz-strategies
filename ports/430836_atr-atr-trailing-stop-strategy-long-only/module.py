"""Two ATR trailing lines, 1-minute bars, long only: the fast line (0.5 x ATR 5) crossing above the slow line (3 x ATR 10)
goes long; the long is stopped by the slow line, ratcheted up, as a house volatility trail on closes.
Port of FMZ strategy #430836 "基于ATR的跟踪止损策略仅做多ATR-Trailing-Stop-Strategy-Long-Only" (ATR Trailing Stop Strategy (Long Position Only)).

FMZ source id: 430836

Source
    https://www.fmz.com/strategy/430836 (PineScript v4, FMZ last modified 2023-11-02 14:05:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 200-235), fast ATR 5 x 0.5, slow ATR 10 x 3
    Trail = src > Trail[1] and src[1] > Trail[1] ? max(Trail[1], src - k atr) : src < Trail[1] ? src + k atr : na
    Buy = crossover(Trail1, Trail2) -> entry long
    trailingStopPrice = Trail2 at the cross, then the running maximum of Trail2 -> exit(stop = trailingStopPrice)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the slow line's running maximum from the entry signal: ported natively (mark
      trailing_stop) as {"type": "volatility", "atr_n": 10, "k": 3.0, "anchor": "close"}. Stated
      approximation: the source ratchets close - 3 ATR(10) and never retreats; the house trails the best
      minute close minus 3 ATR(10) of the module's bars (it may retreat when the ATR grows).
    * The lines follow the source's nz / na pattern (a line that is na on a bar restarts from 0).
    * Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: PASS, ATR lines.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430836_atr_two_trails_long"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "af2": [3.0, 2.0],
    "ap2": [10, 20],
}
DEFAULT_PARAMS = {"ap1": 5, "af1": 0.5, "ap2": 10, "af2": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _trail(src, sl):
    m = len(src)
    out = np.full(m, np.nan)
    for i in range(m):
        t1 = out[i - 1] if i > 0 and not np.isnan(out[i - 1]) else 0.0
        s1 = src[i - 1] if i > 0 else np.nan
        if src[i] > t1 and s1 > t1:
            out[i] = max(t1, src[i] - sl[i])
        elif src[i] < t1:
            out[i] = src[i] + sl[i]
        else:
            out[i] = np.nan
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    src = bars_df["close"].to_numpy(dtype=float)
    t1 = pd.Series(_trail(src, (p["af1"] * _atr(bars_df, int(p["ap1"]))).to_numpy()), index=bars_df.index)
    t2 = pd.Series(_trail(src, (p["af2"] * _atr(bars_df, int(p["ap2"]))).to_numpy()), index=bars_df.index)
    buy = ((t1 > t2) & (t1.shift(1) <= t2.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "volatility", "atr_n": int(p["ap2"]), "k": float(p["af2"]), "anchor": "close"}}


def portfolio_kwargs(**params):
    return {}
