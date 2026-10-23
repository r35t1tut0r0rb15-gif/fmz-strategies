"""Hourly bars: a "kNN" vote over the RSI 29 / RSI 8 feature history (as coded: the labels of the points that set a new largest distance, kept in a running buffer of 20) turning positive goes long above the SMA 40, turning negative goes short below it; a turn against a position closes it; a stop 2 ATR 7 from the entry; reversing.
Port of FMZ strategy #434677 "基于kNN的趋势跟随策略kNN-based-Trend-Following-Strategy" (kNN-based | Trend Following (sosacur01, from Capissimo)).

FMZ source id: 434677

Source
    https://www.fmz.com/strategy/434677 (PineScript v5, FMZ last modified 2023-12-08 11:33:31).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 160-478), indicator RSI; short 8, long 29; base K 400 (k = 20); volatility filter off; bar threshold 300; MA filter SMA 40; ATR 7, stop 2 x ATR; risk 2 % of equity
    for i = 0 to size - 1: d = dist(current, point i); if d > maxdist: maxdist := d, push directions[i] into predictions (shift when size >= k);  prediction = sum(predictions)
    signal = prediction > 0 ? BUY : < 0 ? SELL : CLEAR;  change(signal) and BUY and close > sma(40) -> entry Long;  change and SELL -> close Long;  stop = entry - 2 x atr(7) (mirror for shorts)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The neighbour search is ported as coded, not as its comments say: within each bar the loop pushes
      the direction of every point that sets a new LARGEST distance so far (the farthest-so-far records,
      starting with the oldest valid point), into a "var" buffer of k = floor(sqrt(400)) = 20 that is never
      cleared between bars; the vote is the buffer's sum. The training label is sign(close[1] - close), so
      "BUY" marks a falling bar, as written (weird case). The feature arrays include the current bar.
      Points whose RSI is na never set a record. The 300-bar counter is overwritten by the next signal
      line, and "clear" is always true, so signal = the sign of the vote. Indicator RSI: volume is not used
      (only the 'Volume' and 'All' options read it). The stop is set when the position changes, from the
      fill price and the ATR at that bar; the port takes the ATR up to the signal bar (known at the fill
      open) as a fraction of the fill. Entries are sent as the conditions fire (an entry while in the same
      side adds nothing); a turn without the MA filter closes. REVERSAL INTENDED. The risk-based size
      (2 % of equity per 2 ATR) is sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop from the fill.
    2 generic: PASS, nearest-neighbour style vote with an MA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 2 % / (2 x ATR 7), commission 0.2 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the date filters are always true).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434677_knn_rsi_feature_vote_sma40_atr_stop_reversal"
FAMILY = "machine_learning_vote"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "base_k": [400, 100],
    "ma_len": [40, 100],
}
DEFAULT_PARAMS = {"long_win": 29, "short_win": 8, "base_k": 400, "ma_len": 40, "atr_len": 7, "atr_mult": 2.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _vote(f1, f2, dirs, k):
    """The source's loop: per bar, push the labels of farthest-so-far points into a var buffer of k."""
    m = len(f1)
    pred = np.zeros(m)
    buf = []
    for t in range(m):
        if not (np.isnan(f1[t]) or np.isnan(f2[t])):
            d = np.sqrt((f1[t] - f1[:t + 1]) ** 2 + (f2[t] - f2[:t + 1]) ** 2)
            dd = np.where(np.isnan(d), -np.inf, d)
            prev = np.concatenate(([-999.0], np.maximum.accumulate(dd)[:-1]))
            rec = np.flatnonzero(dd > prev)
            if len(rec):
                buf = (buf + dirs[rec].tolist())[-k:]
        pred[t] = sum(buf)
    return pred


def _signals(bars_df, p):
    c = bars_df["close"]
    f1 = _rsi(c, int(p["long_win"])).to_numpy()
    f2 = _rsi(c, int(p["short_win"])).to_numpy()
    dirs = np.nan_to_num(np.sign((c.shift(1) - c).to_numpy())).astype(int)
    k = int(np.floor(np.sqrt(int(p["base_k"]))))
    pred = _vote(f1, f2, dirs, k)
    sig = np.sign(pred).astype(int)
    changed = np.concatenate(([False], sig[1:] != sig[:-1]))
    start_l, start_s = changed & (sig == 1), changed & (sig == -1)
    ma = c.rolling(int(p["ma_len"])).mean()
    le = start_l & (c > ma).to_numpy()
    se = start_s & (c < ma).to_numpy()
    return le, start_s & ~se, se, start_l & ~le


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = _signals(bars_df, p)
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, o = (bars_df[k] for k in ("high", "low", "close", "open"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, int(p["atr_len"]))
    sl_f = (float(p["atr_mult"]) * atr).shift(1) / o      # the ATR up to the signal bar, known at the fill open
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}
