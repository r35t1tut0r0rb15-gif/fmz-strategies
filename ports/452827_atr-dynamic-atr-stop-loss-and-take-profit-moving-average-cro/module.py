"""SMA 10 / 50 crossings in the 07-14 UTC window, 2-hour bars, long only in effect: the cross up goes long with a stop 1.5 ATR 14 under and a target 3 ATR over the signal close; the cross down closes the long (its short is closed at its own fill by the wrong-side levels).
Port of FMZ strategy #452827 "动态ATR止盈止损移动均线交叉策略-Dynamic-ATR-Stop-Loss-and-Take-Profit-Moving-Average-Crossover-Strategy" (Enhanced Moving Average Crossover Strategy).

FMZ source id: 452827

Source
    https://www.fmz.com/strategy/452827 (PineScript v5, FMZ last modified 2024-05-29 17:19:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 78-122), SMA 10 / 50; ATR 14; stop close - 1.5 ATR, target close + 3 ATR (for both ids); 'European session' hour 7-14; risk 1 % (unused)
    crossover(sma10, sma50) and 7 <= hour <= 14 -> entry Buy, exit(limit = close + 3 atr, stop = close - 1.5 atr)
    crossunder(sma10, sma50) and 7 <= hour <= 14 -> entry Sell, exit(the same long-side levels)

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour is the bar's UTC open hour (as #435514): on 2-hour bars the window holds the 08, 10, 12 and
      14 bars. The long levels are fixed on the signal bar: ported as fractions of the signal close
      (1.5 x ATR / close, 3 x ATR / close) applied to the fill, read at the fill bar from the signal
      bar. The short's exit is attached on its signal bar with the long-side levels: a buy limit over
      and a buy stop under the price, both already marketable when the short fills, so the short is
      closed at the very open it was filled at; the sell signal therefore only closes a held long and
      leaves the position flat (the port sends it as the long's exit, with no short). A repeat cross-up
      inside a long re-issues the levels from that bar, which stops() cannot express: the opening
      levels are kept and the module is marked trailing_stop_pending (as #434428). Long only. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. No sizing
      code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the long bracket as ATR fractions of the signal close; the zero-length short read as a close.
    2 generic: PASS, SMA crossings in a UTC hour window.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (the risk input is unused).
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: hour 7-14 on the UTC bar open.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452827_sma10_50_cross_hour_window_atr_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 20],
    "slow": [50, 100],
    "sl_atr": [1.5, 1.0],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 50, "sl_atr": 1.5, "tp_atr": 3.0, "atr_len": 14,
                  "hour_from": 7, "hour_to": 14}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    hr = bars_df.index.hour
    win = pd.Series((hr >= int(p["hour_from"])) & (hr <= int(p["hour_to"])), index=bars_df.index)
    buy = (f > s) & (f.shift(1) <= s.shift(1)) & win
    sell = (f < s) & (f.shift(1) >= s.shift(1)) & win
    return buy, sell


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return buy, sell, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
