"""RSI 14 pullbacks in the SMA 9 / 21 trend, 1-hour bars, entries only from flat: an RSI under 35 with the SMA 9 over the SMA 21 goes long, an RSI over 65 with the SMA 9 under goes short, each with a target 3 ATR from the signal close and no stop.
Port of FMZ strategy #471707 "双均线交叉RSI动量策略与风险收益优化系统-Dual-Moving-Average-Cross-RSI-Momentum-Strategy-with-Risk-Reward-Optimization-System" (JakeJohn).

FMZ source id: 471707

Source
    https://www.fmz.com/strategy/471707 (PineScript v5, FMZ last modified 2024-11-12 16:00:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-179), SMA 9 / 21; RSI 14, levels 35 / 65; ATR 14 x 1.5 x risk / reward 2 target; exits sent while a position is open (and after 180 bars, the same target)
    sma9 > sma21 and rsi < 35 and flat -> takeProfit = close + 1.5 atr x 2, entry Buy;  sma9 < sma21 and rsi > 65 and flat -> takeProfit = close - 3 atr, entry Sell
    while held: exit(limit = takeProfit)  (also after 180 bars: the same limit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is a price fixed on the signal bar (the ATR stop it names is only used to size the
      target; no stop is sent). It is sent as a fraction of the fill open (shifted into the fill bar; a
      target at or through the fill open is closed one bar late), and followed in the loop so the
      from-flat entries line up. The 180-bar rule repeats the same limit. Opposite entries cannot occur
      (entries only from flat). Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the signal-bar target as a fraction of the fill.
    2 generic: PASS, RSI pullbacks in the SMA trend with an ATR target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471707_rsi_pullback_sma9_21_trend_atr_target_from_flat"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [9, 5],
    "long_len": [21, 50],
    "rr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"short_len": 9, "long_len": 21, "rr": 2.0, "atr_mult": 1.5, "rsi_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    s, l = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    lc = ((s > l) & (r < 35)).to_numpy()
    sc = ((s < l) & (r > 65)).to_numpy()
    dist = (float(p["atr_mult"]) * float(p["rr"]) * _atr(bars_df, 14)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sent = np.full(m, np.nan)
    pos, pend, tgt, t_n = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, tgt = pend, 0, t_n
            if (pos == 1 and tgt <= ov[i]) or (pos == -1 and tgt >= ov[i]):
                if pos == 1:
                    lx[i] = True                 # target through the fill: closed at the next open
                else:
                    sx[i] = True
                pend, tgt = 2, np.nan
        elif pend == 2:
            pos, pend = 0, 0
        if (pos == 1 and hv[i] >= tgt) or (pos == -1 and lv[i] <= tgt):
            pos, tgt = 0, np.nan                 # the target fills inside this bar
        if pos == 0 and pend == 0:
            if lc[i]:
                t_n = cv[i] + dist[i]
                le[i], pend, sent[i] = True, 1, t_n
            if sc[i]:
                t_n = cv[i] - dist[i]
                se[i], pend, sent[i] = True, -1, t_n
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sent)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _, sent = _run(bars_df, p)
    o = bars_df["open"]
    t1 = sent.shift(1)                                        # the signal bar's target, read at the fill
    f = (t1 / o - 1).where(le.shift(1, fill_value=False), 1 - t1 / o)
    return {"tp_stop": f.where(f > 0)}


def portfolio_kwargs(**params):
    return {}
