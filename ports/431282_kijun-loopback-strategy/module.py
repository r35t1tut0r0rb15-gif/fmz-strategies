"""Kijun-sen loopback, 1-hour bars, from flat: a bar opening below the 20-bar Kijun-sen and closing above it goes long
(mirror short); a close back across the Kijun closes the position; a 1.5 ATR stop and the source's 100-point target
(as an ATR fraction) bracket each trade.
Port of FMZ strategy #431282 "Kijun Loopback Strategy" (Master VP).

FMZ source id: 431282

Source
    https://www.fmz.com/strategy/431282 (PineScript v4, FMZ last modified 2023-11-06 16:46:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 192-251), ATR 14, Kijun 20, stop atr x 100000 x 1.5 ticks, target 100 points
    long = open < kijun and close > kijun (flat) -> entry long;  short = open > kijun and close < kijun (flat) -> entry short
    exit(loss = atr x 100000 x 1.5, profit = 100) per side;  close < kijun -> close long;  close > kijun -> close short
    floating loss > 30 % of the balance -> close_all (equity protector)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the stop of atr x 100000 x 1.5 ticks is 1.5 ATR on a 5-digit quote (tick 0.00001),
      the market the formula was written for; it is ported as 1.5 x the signal bar's Wilder ATR 14.
      The 100-point target (10 pips on such a quote) becomes tp_atr x the same ATR (about one ATR of
      1-hour EURUSD), both as fractions of the signal close, fixed at entry.
    * The equity protector depends on the position size (a loss in account currency against the
      balance): a sizing rule, stored with the lot formula, not ported. The Kijun exits are
      close-checked; entry and exit cannot meet on one bar. "Flat" follows the house bracket on bars.
      Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick stop / point target -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based lot formula and the equity protector stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431282_kijun_loopback"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ks_len": [20, 40],
    "tp_atr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "ks_len": 20, "sl_atr": 1.5, "tp_atr": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return out


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["ks_len"])
    ks = ((h.rolling(n).max() + lo.rolling(n).min()) / 2).to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    af = _rma(tr, int(p["atr_len"])) / cv
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if pos == 1 and cv[i] < ks[i]:
            lx[i], pos = True, 0
        elif pos == -1 and cv[i] > ks[i]:
            sx[i], pos = True, 0
        elif pos == 0 and not np.isnan(af[i]):
            if ov[i] < ks[i] and cv[i] > ks[i]:
                le[i], pos = True, 1
            elif ov[i] > ks[i] and cv[i] < ks[i]:
                se[i], pos = True, -1
            if pos != 0:
                entry_i, s_, t_ = i + 1, af[i] * float(p["sl_atr"]), af[i] * float(p["tp_atr"])
                sl_arr[i], tp_arr[i] = s_, t_
    return le, lx, se, sx, sl_arr, tp_arr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(a, index=idx) for a in _run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_arr, tp_arr = _run(bars_df, p)[4:]
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
