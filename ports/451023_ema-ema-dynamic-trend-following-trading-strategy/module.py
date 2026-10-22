"""An ATR envelope around the EMA 14 of the previous channel midline, daily bars: the lower envelope crossing over the 30-bar low with the close under the envelope middle goes long; the upper envelope
crossing under the 60-bar high above the middle, or a high reaching the far sell line, goes short; reversing.
Port of FMZ strategy #451023 "EMA动态趋势追踪交易策略-EMA-Dynamic-Trend-Following-Trading-Strategy" (buy sell Trend (Maboi_q)).

FMZ source id: 451023

Source
    https://www.fmz.com/strategy/451023 (PineScript v5, FMZ last modified 2024-05-11 11:31:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-150), ATR 14; highest 60, lowest 30; envelope 2.382 ATR; sell line EMA 55 of the prior 60-bar high + 5.618 ATR
    ema_hl = ema((highest[1] + lowest[1]) / 2, 14);  envelope = ema_hl -+ 2.382 atr;  sell_line = ema(highest60[1] + 5.618 atr, 55)
    crossover(ema_lowest, lowest) and close < mid -> entry BUY;  (crossunder(ema_highest, highest) and close > mid) or high >= sell_line -> entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.highest / ta.lowest without a source use high / low. No exit: positions end at the opposite
      entry. When both fire, the later short wins (as #437773). strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the channel from the previous bar.
    2 generic: PASS, ATR envelope crossings of the channel edges.
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

NAME = "fmz_451023_atr_envelope_channel_edge_cross_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "f": [2.382, 1.5],
    "highest_len": [60, 30],
}
DEFAULT_PARAMS = {"f": 2.382, "highest_len": 60, "lowest_len": 30, "f2": 5.618, "atr_len": 14, "sell_len": 55}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"]))
    hn = int(p["highest_len"])
    hi = h.rolling(hn).max()
    low_ = lo.rolling(int(p["lowest_len"])).min()
    ema_hl = ((hi.shift(1) + low_.shift(1)) / 2).ewm(span=14, adjust=False).mean()
    e_hi = ema_hl + atr * float(p["f"])
    e_lo = ema_hl - atr * float(p["f"])
    mid = (e_hi + e_lo) / 2
    sell_line = (hi.shift(1) + atr * float(p["f2"])).ewm(span=int(p["sell_len"]), adjust=False).mean()
    le = (e_lo > low_) & (e_lo.shift(1) <= low_.shift(1)) & (c < mid)
    se = ((e_hi < hi) & (e_hi.shift(1) >= hi.shift(1)) & (c > mid)) | (h >= sell_line)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
