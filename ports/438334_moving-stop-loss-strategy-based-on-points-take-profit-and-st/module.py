"""EMA 10 / WMA 20 crossings with a fixed pip bracket, 45-minute bars: from flat, the EMA crossing over the WMA goes long, crossing under goes short; each trade has a stop and a target 20 "pips" (200 ticks)
from the signal close, re-expressed as ATR multiples.
Port of FMZ strategy #438334 "Moving Stop Loss Strategy Based on Points Take Profit and Stop Loss" (PIP SL & TP).

FMZ source id: 438334

Source
    https://www.fmz.com/strategy/438334 (PineScript v5, FMZ last modified 2024-01-11 11:04:57).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 128-203), EMA 10, WMA 20; TP 20 pips, SL 20 pips (pip = 10 ticks); capital 1000
    long = crossover(ema, wma) and position_size == 0;  short = crossunder and position_size == 0;  EP := close, SL1 := EP -/+ 200 ticks, TP1 := EP +/- 200 ticks
    long and not SS -> entry buy;  short and not LS -> entry sell;  exit(stop = SL1, limit = TP1) for each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the pip bracket is re-expressed as sl_stop = k_atr x ATR(14) / close of the signal
      bar, shifted one bar inside stops() and re-based on the fill, with an equal target; 0.1 is the
      reading (200 ticks of 0.1 = 20 on BTC against a 45-minute ATR near 200), 1.0 a wider stop. The
      trailing values TVL / TSL are computed but feed no order. "Flat" follows the house bracket (the
      loop marks the trade closed when a bar's low or high reaches a level from the fill price). Entries
      only from flat: Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). The
      capital is sizing. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, pip bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the pip inputs and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438334_ema_wma_cross_pip_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.1, 1.0],
    "ema_period": [10, 5],
}
DEFAULT_PARAMS = {"k_atr": 0.1, "ema_period": 10, "wma_period": 20, "atr_len": 14, "tp_ratio": 1.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _frac(bars_df, p):
    return float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    w = _wma(c, int(p["wma_period"]))
    up = ((e > w) & (e.shift(1) <= w.shift(1))).to_numpy()
    dn = ((e < w) & (e.shift(1) >= w.shift(1))).to_numpy()
    f = _frac(bars_df, p).to_numpy()
    tpr = float(p["tp_ratio"])
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, sl = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - sl) or hv[i] >= x * (1 + tpr * sl)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + sl) or lv[i] <= x * (1 - tpr * sl)):
                pos = 0
        if pos == 0 and i + 1 < m and not np.isnan(f[i]):
            if up[i]:
                le[i], pos, entry_i, sl = True, 1, i + 1, f[i]
            elif dn[i]:
                se[i], pos, entry_i, sl = True, -1, i + 1, f[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = _frac(bars_df, p)
    return {"sl_stop": f.shift(1), "tp_stop": (float(p["tp_ratio"]) * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
