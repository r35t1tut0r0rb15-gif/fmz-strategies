"""Bollinger 20 extremes beyond a retested swing level, from flat, with a stop beyond the signal bar, 4-hour bars: a
close below the lower band and a set distance below the last retested 5-bar swing low goes long with a stop a little
below the signal bar's low; the mirror goes short (the source's target is never set, as written).
Port of FMZ strategy #489056 "多层布林通道支撑阻力价格突破交易策略-Multi-Layer-Bollinger-Bands-Support-Resistance-Price-Breakout-Trading-Strategy" (Gold BB Support/Resistance Strategy).

FMZ source id: 489056

Source
    https://www.fmz.com/strategy/489056 (PineScript v6, FMZ last modified 2025-04-01 16:55:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 166-209), BB 20 x 2, S/R distance 25 pips, SL 15 pips, TP 2 x SL (pip = 10 ticks)
    support = valuewhen(lowest(low, 5)[1] == low[1], low[1], 0);  validSupport = valuewhen(low within +-0.05 % of support, support, 0)
    long = close < lower and close <= validSupport - 25 pips and flat -> entry + exit(stop = low - 15 pips,
    limit = avg price + 2 x 15 pips);  short mirrored with resistance / upper

Interpretation choices (Pine rules in SURVEY_README.md)
    * The limit uses strategy.position_avg_price on the (flat) signal bar, which is na: no target is set, as written;
      only the stop exists.
    * Criterion 2: the pip distances become ATR(14) multiples on the title's market (gold; on the backtest's ETH the
      pips would be negligible): 15 pips (1.5 USD) ~ 0.1 and 25 pips ~ 0.17 of a 4-hour gold ATR (judgement before any
      backtest). The stop is the signal bar's low - 0.1 ATR: sl_stop = (close - low + 0.1 ATR) / close (shorts mirrored),
      shifted one bar inside stops(), re-based on the fill.
    * Entries only from flat: simulate() follows the house stop on bars (from the fill bar), as the desktop's flat-only
      bracket ports. A long and a short cannot fall on one bar. Opposite entries cannot occur.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "4h" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at the signal bar.
    2 generic: ADAPT, pip distances -> ATR multiples; percentage retest band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the stop ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489056_bb_beyond_retested_swing_stop"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sr_atr": [0.17, 0.5],
    "sl_atr": [0.1, 0.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "sr_atr": 0.17, "sl_atr": 0.1, "atr_len": 14}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _valuewhen(cond, val):
    out = np.full(len(cond), np.nan)
    cur = np.nan
    for i in range(len(cond)):
        if cond[i]:
            cur = val[i]
        out[i] = cur
    return out


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = p["mult"] * c.rolling(n).std(ddof=0)
    upper, lower = (basis + dev).to_numpy(), (basis - dev).to_numpy()
    atr = _atr(bars_df, int(p["atr_len"])).to_numpy(dtype=float)
    lo1, hi1 = lo.shift(1), h.shift(1)
    sup = _valuewhen((lo.rolling(5).min().shift(1) == lo1).to_numpy(), lo1.to_numpy())
    res = _valuewhen((h.rolling(5).max().shift(1) == hi1).to_numpy(), hi1.to_numpy())
    lv, hv, cv, ov = lo.to_numpy(dtype=float), h.to_numpy(dtype=float), c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    vsup = _valuewhen((lv <= sup * 1.0005) & (lv >= sup * 0.9995), sup)
    vres = _valuewhen((hv >= res * 0.9995) & (hv <= res * 1.0005), res)
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    dist = np.full(m, np.nan)
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:               # the house stop from the fill price
            e = ov[entry_i]
            if (pos == 1 and lv[i] <= e * (1 - s_)) or (pos == -1 and hv[i] >= e * (1 + s_)):
                pos = 0
        if pos != 0 or i + 1 >= m or np.isnan(atr[i]):
            continue
        sr, sl = p["sr_atr"] * atr[i], p["sl_atr"] * atr[i]
        if cv[i] < lower[i] and cv[i] <= vsup[i] - sr:
            d = (cv[i] - (lv[i] - sl)) / cv[i]
            le[i], dist[i], pos, entry_i, s_ = True, d, 1, i + 1, d
        elif cv[i] > upper[i] and cv[i] >= vres[i] + sr:
            d = ((hv[i] + sl) - cv[i]) / cv[i]
            se[i], dist[i], pos, entry_i, s_ = True, d, -1, i + 1, d
    return le, se, dist


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, dist = _run(bars_df, p)
    return {"sl_stop": pd.Series(dist, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
