"""EMA 21 / 55 crossings, 3-hour bars, long only: the EMA 21 crossing over the EMA 55 goes long with a target 3 ATR(14) above and a stop 2 ATR below the signal close; the EMA 9 crossing under the EMA 21
closes.
Port of FMZ strategy #440957 "Triple Exponential Moving Average Profit Taking and Stop Loss Strategy" (3EMA with TP & SL (ATR)).

FMZ source id: 440957

Source
    https://www.fmz.com/strategy/440957 (PineScript v4, FMZ last modified 2024-02-04 10:38:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-185), EMA 55 / 21 / 9; SMA 200 and RSI 14 plotted only; ATR 14, target 3, stop 2; dates 2017-2022 (inDateRange is true)
    goLong = crossover(ema21, ema55) -> entry Long, strategy.exit(stop = close - 2 atr, limit = close + 3 atr);  closeLong = crossunder(ema9, ema21) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close: sl_stop = 2 ATR / close, tp_stop = 3 ATR /
      close of the signal bar, shifted one bar inside stops() and re-based on the fill; a later crossing
      while long only moves the script's levels, which the port does not follow. inDateRange is fixed
      true. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on 3-hour bars: mark
      coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest header (bars on UTC multiples of 3
      hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, EMA crossings and ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440957_ema21_55_cross_atr_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_mult": [3, 2],
    "sl_mult": [2, 1],
}
DEFAULT_PARAMS = {"tp_mult": 3, "sl_mult": 2, "slow": 55, "mid": 21, "fast": 9, "atr_len": 14}


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


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    es, em, ef = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("slow", "mid", "fast"))
    go = ((em > es) & (em.shift(1) <= es.shift(1))).to_numpy()
    xl = ((ef < em) & (ef.shift(1) >= em.shift(1))).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = _rma(tr, int(p["atr_len"])) / c
    return go, xl, float(p["sl_mult"]) * a, float(p["tp_mult"]) * a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    go, xl, sl_s, tp_s = _setup(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 1 and i >= entry_i and xl[i]:
            lx[i], pos = True, 0
        elif pos == 0 and go[i] and i + 1 < m and not np.isnan(sl[i]):
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
