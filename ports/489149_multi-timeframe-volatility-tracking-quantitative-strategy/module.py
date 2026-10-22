"""EMA 3 / 8 up-crossings above the EMA 55, 1-minute bars, long only, from flat and at least 72 bars after the last entry, with a 1.2 ATR 14 stop and a 2 ATR target from the signal close.
Port of FMZ strategy #489149 "Multi Timeframe Volatility Tracking Quantitative Strategy" (DOGE/USDT 5X Scalping Strategy).

FMZ source id: 489149

Source
    https://www.fmz.com/strategy/489149 (PineScript v6, FMZ last modified 2025-04-02 10:50:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 165-235), EMA 3 / 8 / 55; ATR 14; interval 72 bars; SL 1.2 ATR, TP 2 ATR; risk 1 % x 5 sizing
    crossover(ema3, ema8) and close > ema55 and bar - last entry bar >= 72 and flat -> entry Long + exit(stop = close - 1.2 atr, limit = close + 2 atr), last entry bar := bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The interval counts bars from bar 0 of the data. Entries need a flat position at the bar's close, so
      a loop follows the bracket on each bar's high / low (as #449508); the bracket is set on the signal bar
      and sent as fractions of the fill open (a level at or through it is marketable and closed one bar
      late, as #458256). Long only. Stop module: portfolio_kwargs {} (driver D4). The risk-sized leveraged
      quantity is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with a trend filter, cooldown and ATR bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: risk-sized leveraged quantity and margins stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489149_ema3_8_cross_ema55_cooldown72_atr_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tradeInterval": [72, 10],
    "slMultiplier": [1.2, 2.0],
}
DEFAULT_PARAMS = {"tradeInterval": 72, "slMultiplier": 1.2, "tpMultiplier": 2.0, "fastEMA": 3, "slowEMA": 8,
                  "trendEMA": 55, "atrPeriod": 14}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    f, s, t = ema(p["fastEMA"]), ema(p["slowEMA"]), ema(p["trendEMA"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    av = _rma(tr, int(p["atrPeriod"])).to_numpy()
    lc = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > t)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    ks, kt = float(p["slMultiplier"]), float(p["tpMultiplier"])
    gap = int(p["tradeInterval"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent = np.full(m, np.nan), np.full(m, np.nan)
    pos, pend, sl, tp, sl_n, tp_n, last = 0, 0, np.nan, np.nan, np.nan, np.nan, 0
    for i in range(m):
        if pend == 1:
            pos, pend, sl, tp = 1, 0, sl_n, tp_n
            if sl >= ov[i] or tp <= ov[i]:      # a level through the fill: closed at the next open
                lx[i], pend = True, 2
        elif pend == 2:
            pos, pend = 0, 0
        if pos == 1 and pend == 0 and (lv[i] <= sl or hv[i] >= tp):
            pos = 0                              # the bracket fills inside this bar
        if pos != 0 or pend != 0 or i - last < gap:
            continue
        if lc[i]:
            sl_n, tp_n = cv[i] - av[i] * ks, cv[i] + av[i] * kt
            le[i], pend, sl_sent[i], tp_sent[i], last = True, 1, sl_n, tp_n, i
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, sl_sent, tp_sent)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx = _run(bars_df, p)[:2]
    false = pd.Series(False, index=le.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, tp_l = _run(bars_df, p)[2:]
    o = bars_df["open"]
    sl_f = 1 - sl_l.shift(1) / o                  # the signal bar's levels, read at the fill
    tp_f = tp_l.shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
