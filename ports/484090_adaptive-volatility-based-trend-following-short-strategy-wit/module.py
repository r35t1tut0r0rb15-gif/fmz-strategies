"""Close crossings under the SMA 50 below the SMA 200 in high ATR and outside a narrow range, 2-minute bars, short only: the cross goes short; a bar whose high reaches 0.5 % over the signal close closes it, and after 10 minutes a close back over the SMA 200 or the SMA 50 / 200 up-cross closes it; the exits are only checked while the entry filters hold.
Port of FMZ strategy #484090 "Adaptive Volatility Based Trend Following Short Strategy with Time Delay and Stop Loss Protection" (Profit Guard Short Strategy with Time Delay & Stop Loss).

FMZ source id: 484090

Source
    https://www.fmz.com/strategy/484090 (PineScript v5, FMZ last modified 2025-02-28 09:42:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 209-281), SMA 50 / 200; ATR 14 vs SMA 28 x 1.0; range 20 bars under 0.03 %; delay 10 minutes; stop 0.5 % (on the bar's high)
    filters = sma50 < sma200 and atr > sma(atr, 28) and range% >= 0.03
    filters and crossunder(close, sma50) and not open -> entry Short, open := true, entry := close, t0 := time
    filters and open: high >= entry x 1.005 -> close Short, open := false;  else time >= t0 + 10 min and (crossover(close, sma200) or crossover(sma50, sma200)) -> close Short, open := false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flag, entry close and entry time are followed in a loop, as written; the exits sit inside the
      filter block, so they are only tested on bars where the filters hold. The stop test reads the bar's
      high and closes at the next open (an exit signal, no stop module). A close called on the entry's own
      bar (before it fills) closes nothing but clears the flag, as written. Short only: Opposite entries
      cannot occur. The alerts are messages only. No sizing code. FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; high-based percent stop as an exit signal.
    2 generic: PASS, SMA crossings with volatility and range filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484090_close_under_sma50_below_sma200_atr_range_filter_delayed_exit_short"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_ma_length": [50, 20],
    "stop_loss_percent": [0.5, 1.0],
}
DEFAULT_PARAMS = {"fast_ma_length": 50, "stop_loss_percent": 0.5, "slow_ma_length": 200, "atr_length": 14,
                  "atr_sensitivity": 1.0, "range_percent": 0.03, "range_lookback": 20, "delay_minutes": 10}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["fast_ma_length"])).mean()
    s = c.rolling(int(p["slow_ma_length"])).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    al = int(p["atr_length"])
    atr = _rma(tr, al)
    vol_ok = atr > atr.rolling(al * 2).mean() * float(p["atr_sensitivity"])
    rl = int(p["range_lookback"])
    rng = (h.rolling(rl).max() - lo.rolling(rl).min()) / c.rolling(rl).mean() * 100
    in_range = rng < float(p["range_percent"])
    filt = ((f < s) & vol_ok & ~in_range).to_numpy()
    xd = ((c < f) & (c.shift(1) >= f.shift(1))).to_numpy()
    cu = (((c > s) & (c.shift(1) <= s.shift(1))) | ((f > s) & (f.shift(1) <= s.shift(1)))).to_numpy()
    hv, cv = h.to_numpy(dtype=float), c.to_numpy(dtype=float)
    t = np.asarray(bars_df.index.asi8) // 10 ** 6            # bar open time in ms, as Pine's time
    delay = int(p["delay_minutes"]) * 60 * 1000
    q = float(p["stop_loss_percent"]) / 100
    m = len(cv)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    flag = False
    ep = np.nan
    et = 0
    for i in range(m):
        if not filt[i]:
            continue
        if xd[i] and not flag:
            se[i], flag, ep, et = True, True, cv[i], t[i]
        if flag:
            if hv[i] >= ep * (1 + q):
                flag = False
                if not se[i]:
                    sx[i] = True              # a close on the entry's own bar closes nothing
            elif t[i] >= et + delay and cu[i]:
                sx[i], flag = True, False
    false = pd.Series(False, index=c.index)
    return false, false.copy(), pd.Series(se, index=c.index), pd.Series(sx, index=c.index)


def portfolio_kwargs(**params):
    return {}
