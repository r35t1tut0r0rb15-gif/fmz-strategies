"""Narrow Bollinger breakouts with an EMA 80 filter, 15-minute bars: a close crossing above the upper band (20, 0.38 sd) with
the close above the EMA goes long with the stop at the 7-bar low and a target 1.6 times that distance; a close crossing
under the lower band below the EMA goes short with the stop at the 7-bar high (reversing).
Port of FMZ strategy #435248 "Dual Moving Average Line Capture Strategy" (Bollinger Bands Modified (Stormer)).

FMZ source id: 435248

Source
    https://www.fmz.com/strategy/435248 (PineScript v5, FMZ last modified 2023-12-13 15:28:50).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 128-227), BB 20 x 0.38; EMA 80 trend check on; stop look back 7 / 7; target factor 1.6; extra cross checks off
    crossover(close, upper) and close > ema80 and not isLongEntry -> entry long, exit(stop = lowest(low, 7), limit = close + |close - stop| x 1.6)
    crossunder(close, lower) and close < ema80 and not isShortEntry -> entry short, exit(stop = highest(high, 7), limit = close - |close - stop| x 1.6)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal bar (a new same-side signal is blocked while that side is
      open), ported as fractions of the signal close shifted one bar inside stops() (re-based on
      the fill). A signal whose stop is not beyond the close places no entry.
    * The entry flags reset when flat; an opposite signal reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar.
    2 generic: PASS, band breakouts, an average filter and swing exits.
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

NAME = "fmz_435248_stormer_narrow_bb_bracket"
FAMILY = "bollinger_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [0.38, 1.0],
    "target": [1.6, 3.0],
}
DEFAULT_PARAMS = {"bb_len": 20, "mult": 0.38, "ema_len": 80, "hh_len": 7, "ll_len": 7, "target": 1.6}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["bb_len"])
    mid, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up, lw = mid + float(p["mult"]) * sd, mid - float(p["mult"]) * sd
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    cv = c.to_numpy(dtype=float)
    ll = lo.rolling(int(p["ll_len"])).min().to_numpy()
    hh = h.rolling(int(p["hh_len"])).max().to_numpy()
    with np.errstate(invalid="ignore"):
        l_sl, s_sl = (cv - ll) / cv, (hh - cv) / cv
        le = ((c > up) & (c.shift(1) <= up.shift(1)) & (c > ema)).to_numpy() & (l_sl > 0)
        se = ((c < lw) & (c.shift(1) >= lw.shift(1)) & (c < ema)).to_numpy() & (s_sl > 0)
    sl = np.where(le, l_sl, np.where(se, s_sl, np.nan))
    return le, se, sl, sl * float(p["target"])


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _setup(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
