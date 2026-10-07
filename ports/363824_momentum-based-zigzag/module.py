"""Momentum-based ZigZag (QQE mode): a QQE trend flip up goes long unless RSI(5) was oversold
since the last down flip; a flip down goes short unless RSI(5) was overbought since the last up
flip (always in).
Port of FMZ strategy #363824 "Momentum-based ZigZag".

Source
    https://www.fmz.com/strategy/363824 (PineScript v5, FMZ last modified 2022-05-17 16:29:07).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 116-225), momentum "QQE": RSI 14, factor 4.238,
smoothing 5; RSI(5) 80 / 20
    RsiMa = ema(rsi, 5); dar = ema(ema(|RsiMa - RsiMa[1]|, 27), 27) * 4.238
    longband / shortband ratchet around RsiMa; last_qqe_high / last_qqe_low track the swing
    trend := crossover(RsiMa, shortband[1]) or crossover(high, last_qqe_high) ? 1
           : crossunder(RsiMa, longband[1]) or crossunder(low, last_qqe_low) ? -1 : trend[1]
    qqeUP = trend flips -1 -> 1 (and TL[1] - 50 != 0); qqeDOWN mirrors
    GoLong  = qqeUP and not (barssince(qqeDOWN) >= barssince(rsi5 < 20))[1]
    GoShort = qqeDOWN and not (barssince(qqeUP) >= barssince(rsi5 > 80))[1]
    GoLong -> entry long; else GoShort -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * qqe_goingup/down are evaluated before the bar's flip counters are updated, so they use the
      flips up to the previous bar, as coded. barssince of a never-true condition is na and its
      comparisons are false.
    * The zigzag line, stop-loss levels and alert texts do not reach the orders; not ported.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363824_qqe_momentum_zigzag"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [9, 14, 21],
    "qqe_factor": [3.0, 4.238],
}
DEFAULT_PARAMS = {"rsi_len": 14, "qqe_factor": 4.238, "smoothing": 5}


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


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i, v in enumerate(cond):
        if v:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _qqe_flips(bars, rsi_len, factor, sf):
    h, l = bars["high"].to_numpy(dtype=float), bars["low"].to_numpy(dtype=float)
    rsi = _rsi(bars["close"], rsi_len)
    wp = rsi_len * 2 - 1
    rma = rsi.ewm(span=sf, adjust=False).mean()
    dar = ((rma.shift(1) - rma).abs().ewm(span=wp, adjust=False).mean()
           .ewm(span=wp, adjust=False).mean() * factor).to_numpy()
    r = rma.to_numpy()
    m = len(r)
    lb, sb, trend, tl = (np.full(m, np.nan) for _ in range(4))
    up, dn = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    xl = xs = 0
    last_up = last_dn = -1
    # var init is high/low, but bar 0 reassigns nz(last[1]) = 0 unless a swing condition holds
    lqh = lqh_prev = 0.0
    lql = lql_prev = 0.0
    going_up_prev = going_dn_prev = False
    for i in range(m):
        lb1 = lb[i - 1] if i else np.nan
        sb1 = sb[i - 1] if i else np.nan
        r1 = r[i - 1] if i else np.nan
        nl, ns = r[i] - dar[i], r[i] + dar[i]
        lb[i] = max(lb1, nl) if (r1 > lb1 and r[i] > lb1) else nl
        sb[i] = min(sb1, ns) if (r1 < sb1 and r[i] < sb1) else ns
        # barssince(QQExlong == 1) with QQExlong still holding the previous bar's value
        if xl == 1:
            last_up = i - 1
        if xs == 1:
            last_dn = i - 1
        bs_up = i - last_up if last_up >= 0 else np.nan
        bs_dn = i - last_dn if last_dn >= 0 else np.nan
        going_up, going_dn = bs_up < bs_dn, bs_up > bs_dn
        lqh = h[i] if ((h[i] > lqh_prev and going_up) or (going_dn_prev and going_up)) else lqh_prev
        lql = l[i] if ((l[i] < lql_prev and going_dn) or (going_up_prev and going_dn)) else lql_prev
        sb2 = sb[i - 2] if i >= 2 else np.nan
        lb2 = lb[i - 2] if i >= 2 else np.nan
        h1 = h[i - 1] if i else np.nan
        l1 = l[i - 1] if i else np.nan
        t1 = trend[i - 1] if i else np.nan
        x_up = (r[i] > sb1 and r1 <= sb2) or (h[i] > lqh and h1 <= lqh_prev)
        x_dn = (r[i] < lb1 and r1 >= lb2) or (l[i] < lql and l1 >= lql_prev)
        trend[i] = 1.0 if x_up else (-1.0 if x_dn else (1.0 if np.isnan(t1) else t1))
        tl[i] = lb[i] if trend[i] == 1 else sb[i]
        xl = 1 if (trend[i] == 1 and t1 == -1) else 0
        xs = 1 if (trend[i] == -1 and t1 == 1) else 0
        tl1 = tl[i - 1] if i else np.nan
        flag = not np.isnan(tl1) and tl1 - 50 != 0
        up[i], dn[i] = xl == 1 and flag, xs == 1 and flag
        lqh_prev, lql_prev = lqh, lql
        going_up_prev, going_dn_prev = going_up, going_dn
    return up, dn


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _qqe_flips(bars_df, int(p["rsi_len"]), float(p["qqe_factor"]), int(p["smoothing"]))
    rsi5 = _rsi(bars_df["close"], 5).to_numpy()
    bs_up, bs_dn = _barssince(up), _barssince(dn)
    bs_ob, bs_os = _barssince(rsi5 > 80), _barssince(rsi5 < 20)
    lag = lambda a: np.concatenate([[False], a[:-1]])
    force_down = lag(bs_dn >= bs_os)
    force_up = lag(bs_up >= bs_ob)
    go_long = up & ~(up & force_down)
    go_short = dn & ~(dn & force_up)
    return _always_in(go_long, go_short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
