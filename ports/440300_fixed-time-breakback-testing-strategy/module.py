"""Previous-candle colour fades, 1-hour bars: after a red candle go long, after a green candle go short, each with a fixed target from the entry (tick distances, re-expressed as ATR multiples); no stop;
reversing.
Port of FMZ strategy #440300 "Fixed Time Breakback Testing Strategy" (Buy Sell at 08:35 GMT+5 with Profit Targets).

FMZ source id: 440300

Source
    https://www.fmz.com/strategy/440300 (PineScript v5, FMZ last modified 2024-01-29 10:22:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 162-193), desired time 08:35 (only shaded); long target 1000, short target 500 ("USD", passed as ticks)
    isBullish = close[1] < open[1] -> entry Buy;  isBearish = close[1] > open[1] -> entry Sell;  strategy.exit(profit = 1000) for Buy, strategy.exit(profit = 500) for Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The desired-time test only colours the background and does not gate the entries, so a signal comes
      on nearly every bar. The flags are named the other way round: a red previous candle buys, as
      written. The targets are ticks from the entry; the port reads them as ATR(14) multiples of the
      signal bar, long 0.67 and short 0.33 (100 / 50 on BTC with 0.1 ticks against a 1-hour ATR near
      150), shifted one bar inside stops() and re-based on the fill. No stop is placed. strategy.entry
      reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry.
    2 generic: ADAPT, tick targets -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the 08:35 test only shades the chart).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440300_prev_candle_fade_tick_target"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_long": [0.67, 2.0],
    "k_short": [0.33, 1.0],
}
DEFAULT_PARAMS = {"k_long": 0.67, "k_short": 0.33, "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _setup(bars_df, p):
    o, c = bars_df["open"], bars_df["close"]
    lsig = c.shift(1) < o.shift(1)
    ssig = c.shift(1) > o.shift(1)
    a = _atr(bars_df, p["atr_len"]) / c
    tp = (float(p["k_long"]) * a).where(lsig, (float(p["k_short"]) * a).where(ssig))
    return lsig.to_numpy(), ssig.to_numpy(), tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lsig, ssig, tp_s = _setup(bars_df, p)
    tp = tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, t_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and hv[i] >= x * (1 + t_):
                pos = 0
            elif pos == -1 and lv[i] <= x * (1 - t_):
                pos = 0
        if i + 1 < m and not np.isnan(tp[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, t_ = True, 1, i + 1, tp[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, t_ = True, -1, i + 1, tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tp = _setup(bars_df, p)[2]
    return {"tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
