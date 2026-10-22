"""SuperTrend (ATR 10 x 3 on hl2) flips, 1-hour bars, with an ATR bracket: a flip up goes long, a flip down goes short, each with a stop and target 1.5 ATR(14) from the signal close; reversing.
Port of FMZ strategy #446525 "超级趋势ATR策略Supertrend-ATR-Strategy" (Supertrend (tradez99)).

FMZ source id: 446525

Source
    https://www.fmz.com/strategy/446525 (PineScript v5, FMZ last modified 2024-03-29 11:29:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-196), SuperTrend ATR 10 x 3 on hl2 (Wilder ATR); bracket ATR 14 x 1.5, risk : reward 1; risk 1 % per trade
    buySignal (trend flips to 1) -> t_stop = close - 1.5 atr14, t_target = close + 1.5 atr14, entry Long (qty from risk);  sellSignal mirrored -> entry Short
    exit(Long, limit = t_target, stop = t_stop);  exit(Short, limit = t_target, stop = t_stop)  (every bar, from the saved levels)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are saved on the signal bar and re-sent unchanged until the next signal, which always
      reverses the position, so they are fixed per trade: sl_stop = tp_stop = 1.5 ATR(14) / close of
      the signal bar, shifted one bar inside stops() and re-based on the fill. The SuperTrend follows
      the script's nz() seeds. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The risk
      quantity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed on the signal bar.
    2 generic: PASS, SuperTrend flips with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1 % risk quantity stored.
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

NAME = "fmz_446525_supertrend10x3_flip_atr_bracket_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "multiplier": [3.0, 2.0],
    "sl_mult": [1.5, 3.0],
}
DEFAULT_PARAMS = {"multiplier": 3.0, "sl_mult": 1.5, "periods": 10, "atr_len": 14, "rr": 1.0}


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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)


def _nmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _nmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _rma(_tr(bars_df), int(p["periods"])).to_numpy()
    src = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    mult = float(p["multiplier"])
    m = len(cv)
    tr_ = np.zeros(m)
    up_p = dn_p = np.nan
    d = 1
    for i in range(m):
        u, dd = src[i] - mult * atr[i], src[i] + mult * atr[i]
        u1 = u if np.isnan(up_p) else up_p
        d1 = dd if np.isnan(dn_p) else dn_p
        if i > 0 and cv[i - 1] > u1:
            u = _nmax(u, u1) if not np.isnan(u) else u
        if i > 0 and cv[i - 1] < d1:
            dd = _nmin(dd, d1) if not np.isnan(dd) else dd
        if d == -1 and cv[i] > d1:
            d = 1
        elif d == 1 and cv[i] < u1:
            d = -1
        tr_[i] = d
        up_p, dn_p = u, dd
    t1 = np.concatenate(([1], tr_[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((tr_ == 1) & (t1 == -1), index=ix), false, pd.Series((tr_ == -1) & (t1 == 1), index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["sl_mult"]) * _rma(_tr(bars_df), int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": a.shift(1), "tp_stop": (a * float(p["rr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
