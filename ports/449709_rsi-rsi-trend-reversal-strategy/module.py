"""An RSI- and ATR-scaled trailing threshold on Heikin-Ashi closes, daily bars, acting one bar late: the HA close crossing over the threshold goes long and crossing under goes short, each on the next bar;
reversing.
Port of FMZ strategy #449709 "RSI趋势反转策略-RSI-Trend-Reversal-Strategy" (RSI Trend Reversal).

FMZ source id: 449709

Source
    https://www.fmz.com/strategy/449709 (PineScript v5, FMZ last modified 2024-04-28 13:33:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-185), RSI / ATR length 8; multiplier 1.5; delay 1 bar; minimum difference 10 %; source close (Heikin-Ashi request)
    lower = highest(max(highest(highest(src, n) x (1 - (atr / src + mult / rsi)), n), src x 0.9), n);  upper = lowest(min(lowest(lowest(src, n) x (1 + (atr / src + mult / |rsi - 100|)), n), src x 1.1), n)
    n = bars since the last threshold cross (counting up from the start until the first);  thresh = lower while dir is up, upper while down;  dir flips on the previous bar's crossings
    buy = crossover(haclose, thresh);  sell = crossunder;  buy[1] -> entry long;  sell[1] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin-Ashi request on the chart period gives the HA close, (open + high + low + close) / 4
      of each bar. The custom highest / lowest loop over the current window length n inclusive (n + 1
      bars), each on the history of its own argument, and n is the bars since the last crossing (it
      counts up from the first bar until the first crossing), as written; the ATR is the chart's,
      divided by the HA close. A division by a zero RSI is na. The entries use the signals of the
      previous bar (the "delay to prevent idealization" input, 1). strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the signals are one bar old.
    2 generic: PASS, adaptive RSI / ATR threshold crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_449709_rsi_atr_adaptive_threshold_ha_cross_reversal"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [8, 14],
    "rsi_mult": [1.5, 3.0],
}
DEFAULT_PARAMS = {"rsi_length": 8, "rsi_mult": 1.5, "lookback": 1, "sltp": 10.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _hi(arr, t, n):
    """highest_custom: starts from the current value (na stays na), loops i = 0 .. n inclusive."""
    if np.isnan(arr[t]):
        return np.nan
    w = arr[max(0, t - n):t + 1]
    return np.nanmax(w)


def _lo(arr, t, n):
    if np.isnan(arr[t]):
        return np.nan
    w = arr[max(0, t - n):t + 1]
    return np.nanmin(w)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    hc = (o + h + lo + c) / 4                          # Heikin-Ashi close of each bar
    n = int(p["rsi_length"])
    mult = float(p["rsi_mult"])
    sl = (100 - float(p["sltp"])) / 100
    tp = (100 + float(p["sltp"])) / 100
    src = hc.to_numpy(dtype=float)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = (_rma(tr, n) / hc).to_numpy()
    r = _rsi(hc, n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        inv_lo = np.where(r == 0, np.nan, 1 / r)            # a division by zero is na
        inv_up = np.where(np.abs(r - 100) == 0, np.nan, 1 / np.abs(r - 100))
    m = len(src)
    a1, c1, a2, c2 = (np.full(m, np.nan) for _ in range(4))
    thresh = np.full(m, np.nan)
    cu_prev = cd_prev = False
    last_cross = -1
    bear = 0
    d = np.nan
    th = np.nan
    with np.errstate(invalid="ignore"):
        for t in range(m):
            if cu_prev or cd_prev:
                last_cross = t
            if last_cross < 0:
                bear += 1
            else:
                bear = t - last_cross
            k = int(bear)
            a1[t] = _hi(src, t, k) * (1 - (atr[t] + inv_lo[t] * mult))
            b1 = _hi(a1, t, k)
            c1[t] = np.nan if (np.isnan(b1) or np.isnan(src[t])) else max(b1, src[t] * sl)
            lower = _hi(c1, t, k)
            a2[t] = _lo(src, t, k) * (1 + (atr[t] + inv_up[t] * mult))
            b2 = _lo(a2, t, k)
            c2[t] = np.nan if (np.isnan(b2) or np.isnan(src[t])) else min(b2, src[t] * tp)
            upper = _lo(c2, t, k)
            if np.isnan(th):
                th = lower
            if np.isnan(d):
                d = 1.0
            if cd_prev:
                d = -1.0
            if cu_prev:
                d = 1.0
            if d == 1:
                th = lower
            if d == -1:
                th = upper
            thresh[t] = th
            p_src = src[t - 1] if t > 0 else np.nan
            p_th = thresh[t - 1] if t > 0 else np.nan
            cu_prev = bool(src[t] > th and p_src <= p_th)
            cd_prev = bool(src[t] < th and p_src >= p_th)
    s = pd.Series(src, index=c.index)
    th_s = pd.Series(thresh, index=c.index)
    buy = (s > th_s) & (s.shift(1) <= th_s.shift(1))
    sell = (s < th_s) & (s.shift(1) >= th_s.shift(1))
    lb = int(p["lookback"])
    le = buy.shift(lb, fill_value=False)
    se = sell.shift(lb, fill_value=False)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
