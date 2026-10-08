"""Gunbot Bbands: OHLC4 below the lower band pulled 25 % toward the mean goes long on the first
such bar after a short signal (shorts mirrored at the upper band); a long is closed on a bar
close once the bar's high reaches the signal close + tp, its low the signal close - sl, or its
high slips ts under the highest high since the signal.
Port of FMZ strategy #426298 "The Gunbot Bands Strategy".

Source
    https://www.fmz.com/strategy/426298 (PineScript v3, FMZ last modified 2023-09-10 21:31:29).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 96-261), length 15, mult 2, LOW_BB / HIGH_BB 25,
ts / tp / sl 99999e-8, tsi 0, pyramiding < 0 / = 1 / > 100, leverage 1
    basis = sma(close, length * (15 / timeframe.multiplier)); dev = mult * stdev(same)
    lower_low_bb = lower + (basis - lower) * 25 %; upper_high_bb = upper - (upper - basis) * 25 %
    long = ohlc4 < lower_low_bb; short = ohlc4 > upper_high_bb
    sectionLongs counts long bars since the last short bar (shorts mirrored)
    longCondition = long and (sectionLongs <= 0 or >= 100 or == 1)    -> entry Long
    last_open = close of the latest longCondition; in_long = latest condition was long
    last_high = highest high since in_long began (na when not in_long)
    long_ts = high <= last_high - ts and high >= last_open + tsi and not longCondition
    long_tp = high >= last_open + tp and not longCondition
    long_sl = low <= last_open - sl and not longCondition
    long_call = low <= last_open - (0.8 + 0.2 / lev) / lev * last_open (never at leverage 1)
    any of them -> close Long   (shorts mirrored; short call at last_open * (1 + 0.78 + 0.2))

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy() is commented out, so FMZ's defaults hold: one position (the pyramiding inputs
      only gate the signal as above). isAdding (martingale qty) is off by default: sizing only.
    * 15 / timeframe.multiplier is v3 integer division: 5 on the 3-minute header bars, so the
      band length is 5 x length.
    * Criterion 2: ts / tp / sl / tsi are price distances (99999e-8, i.e. Gunbot satoshis; under a
      tick on BTC_USDT). They become *_atr x ATR(14) at the latest signal bar; the source's
      defaults are 0 ATR.
    * The exits are strategy.close calls evaluated on the bar close (filled next open), so the
      trailing exit is a close-based exit signal (rule 2: a trail checked on closes needs no mark).
    * Same bar: the entry fills first, then a close of the other side finds nothing to close.
      strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "3min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426298_gunbot_bbands"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)
TF_MULT = 3  # timeframe.multiplier of FREQ

GRID = {
    "tp_atr": [0.0, 1.0, 2.0],
    "sl_atr": [0.0, 1.0, 2.0],
    "ts_atr": [0.0, 1.0],
}
DEFAULT_PARAMS = {"length": 15, "mult": 2.0, "low_bb": 25, "high_bb": 25, "pyr_lt": 0, "pyr_eq": 1,
                  "pyr_gt": 100, "leverage": 1.0, "tp_atr": 0.0, "sl_atr": 0.0, "ts_atr": 0.0,
                  "tsi_atr": 0.0}


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
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"]) * (15 // TF_MULT)
    basis = c.rolling(n).mean()
    dev = p["mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    lower_bb = lower + (basis - lower) * (p["low_bb"] / 100)
    upper_bb = upper - (upper - basis) * (p["high_bb"] / 100)
    ohlc4 = (o + h + l + c) / 4
    long_ = (ohlc4 < lower_bb).to_numpy()
    short = (ohlc4 > upper_bb).to_numpy()
    atr = _atr_pine(bars_df, ATR_LEN).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), l.to_numpy(dtype=float), c.to_numpy(dtype=float)
    lev = p["leverage"]
    m = len(cv)
    target = np.zeros(m, dtype=int)
    sec_l = sec_s = 0
    open_l = open_s = 0.0  # nz(last_open_*): 0 until the first condition
    atr_l = atr_s = np.nan
    t_l = t_s = -1  # bar of the latest condition (nz(time) = 0 before any)
    last_high = last_low = np.nan
    pos = 0
    for i in range(m):
        if long_[i]:
            sec_l, sec_s = sec_l + 1, 0
        if short[i]:
            sec_l, sec_s = 0, sec_s + 1
        lc = long_[i] and (sec_l <= p["pyr_lt"] or sec_l >= p["pyr_gt"] or sec_l == p["pyr_eq"])
        sc = short[i] and (sec_s <= p["pyr_lt"] or sec_s >= p["pyr_gt"] or sec_s == p["pyr_eq"])
        if lc:
            open_l, atr_l, t_l = cv[i], atr[i], i
        if sc:
            open_s, atr_s, t_s = cv[i], atr[i], i
        in_l, in_s = t_l > t_s, t_s > t_l
        last_high = np.nan if not in_l else (hv[i] if np.isnan(last_high) or hv[i] > last_high else last_high)
        last_low = np.nan if not in_s else (lv[i] if np.isnan(last_low) or lv[i] < last_low else last_low)
        ts_l, tp_l, sl_l, tsi_l = (p[k] * atr_l for k in ("ts_atr", "tp_atr", "sl_atr", "tsi_atr"))
        ts_s, tp_s, sl_s, tsi_s = (p[k] * atr_s for k in ("ts_atr", "tp_atr", "sl_atr", "tsi_atr"))
        l_exit = (lv[i] <= open_l - (0.8 + 0.2 * (1 / lev)) / lev * open_l) or (not lc and (
            (not np.isnan(last_high) and hv[i] <= last_high - ts_l and hv[i] >= open_l + tsi_l)
            or hv[i] >= open_l + tp_l or lv[i] <= open_l - sl_l))
        s_exit = (hv[i] >= open_s + (0.78 + 0.2 * (1 / lev)) / lev * open_s) or (not sc and (
            (not np.isnan(last_low) and lv[i] >= last_low + ts_s and lv[i] <= open_s - tsi_s)
            or lv[i] <= open_s - tp_s or hv[i] >= open_s + sl_s))
        before = pos
        if lc:
            pos = 1
        elif sc:
            pos = -1
        if pos == 1 and before == 1 and l_exit:
            pos = 0
        elif pos == -1 and before == -1 and s_exit:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
