"""Short-only SMA 50 breakdowns below SMA 200 in expanding, non-ranging volatility, with a 0.5 % bar-range stop and a
delayed bullish-cross exit, 2-minute bars: with SMA 50 under SMA 200, ATR above its 28-bar average and the 20-bar range
over 0.03 % of price, the close crossing under SMA 50 goes short; while those conditions hold, a high 0.5 % over the
entry close or, after 10 minutes, a bullish SMA 200 cross closes the trade.
Port of FMZ strategy #484090 "时间延迟与止损保护的自适应波动率趋势跟踪空头策略-Adaptive-Volatility-Based-Trend-Following-Short-Strategy-with-Time-Delay-and-Stop-Loss-Protection" (Profit Guard Short Strategy with Time Delay & Stop Loss).

FMZ source id: 484090

Source
    https://www.fmz.com/strategy/484090 (PineScript v5, FMZ last modified 2025-02-28 09:42:59).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 213-267), SMA 50 / 200, ATR 14 vs sma(ATR, 28) x 1.0, range 20 bars < 0.03 %
(inverted), delay 10 minutes, stop 0.5 %
    if sma50 < sma200 and atr > atrMA and not rangeCondition:
        crossunder(close, sma50) and not shortPositionOpen -> entry short, entry price = close, entry time = time
        shortPositionOpen: high >= entry x 1.005 -> close; else time >= entry time + 10 min and (crossover(close,
        sma200) or crossover(sma50, sma200)) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the exit tests run only inside the outer condition block (while SMA 50 < SMA 200 and the volatility
      tests hold); outside it the trade is held.
    * The 0.5 % stop is bar-range-checked with strategy.close: an exit signal at the next open (rule 3; #489638). The
      script's flag gates the entries; the Pine position follows the orders, with closes acting on the position held
      at the bar's start (#430850): a close on the entry's own bar does not undo the entry.
    * Session open: not used; the delay counts bar open times. Short only: opposite entries cannot occur.
      FREQ = "2min" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders and bar-range-checked exits.
    2 generic: PASS, moving averages, ATR and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_484090_short_sma_breakdown_delayed_exit"
FAMILY = "ma_trend_filter"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_pct": [0.5, 1.0],
    "delay_min": [10, 30],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "atr_len": 14, "atr_sens": 1.0, "range_pct": 0.03, "range_len": 20,
                  "delay_min": 10, "stop_pct": 0.5}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    n = int(p["atr_len"])
    atr = _atr(bars_df, n)
    vol = atr > atr.rolling(n * 2).mean() * p["atr_sens"]
    rl = int(p["range_len"])
    rsize = (h.rolling(rl).max() - lo.rolling(rl).min()) / c.rolling(rl).mean() * 100
    outer = ((f < s) & vol & ~(rsize < p["range_pct"])).to_numpy()
    x_dn = ((c < f) & (c.shift(1) >= f.shift(1))).to_numpy()
    up_s = ((c > s) & (c.shift(1) <= s.shift(1))).to_numpy()
    up_fs = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    hv, cv = h.to_numpy(dtype=float), c.to_numpy(dtype=float)
    t_ns = bars_df.index.asi8
    delay_ns = int(p["delay_min"]) * 60 * 10 ** 9
    stop = 1 + p["stop_pct"] / 100
    m = len(cv)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    flag, e_px, e_t, pos = False, np.nan, 0, 0
    for i in range(m):
        start = pos
        if outer[i]:
            if x_dn[i] and not flag:
                pos, flag, e_px, e_t = -1, True, cv[i], t_ns[i]
            if flag:
                close_now = hv[i] >= e_px * stop or (t_ns[i] >= e_t + delay_ns and (up_s[i] or up_fs[i]))
                if close_now:
                    flag = False
                    if start == -1 and pos == -1:
                        pos = 0
        se[i] = start == 0 and pos == -1
        sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return false, false.copy(), pd.Series(se, index=idx), pd.Series(sx, index=idx)


def portfolio_kwargs(**params):
    return {}
