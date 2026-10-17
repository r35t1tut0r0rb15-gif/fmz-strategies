"""Three red days bought when ATR 12 is above its 30-day mean, closed after three green days or 22 days, daily
(broker-day) bars, long only: from flat, three consecutive closes below their opens with ATR(12) above SMA(ATR, 30)
go long; three consecutive green bars or 22 bars since the entry signal close the trade.
Port of FMZ strategy #483676 "逆势突破交易系统基于多日价格模式与波动率过滤的量化策略-Counter-Trend-Breakout-Trading-System-A-Quantitative-Strategy-Based-on-Multi-Day-Price-Patterns-and-Volatility-Filtering" (3 Red / 3 Green Strategy with Volatility Check).

FMZ source id: 483676

Source
    https://www.fmz.com/strategy/483676 (PineScript v6, FMZ last modified 2025-02-25 10:49:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 208-249), max duration 22, green exit on, ATR 12, ATR mean 30
    entry: position_size == 0 and threeRed and atr_entry
    exit: position_size > 0 and ((useGreenExit and threeGreen) or bar_index - entryBarIndex >= 22)

Interpretation choices (Pine rules in SURVEY_README.md)
    * atr_entry is true when ATR or its 30-day mean is na or not positive (the warm-up), as written.
    * The duration counts bars from the entry-signal bar; the close acts at the next open. Entries only from flat:
      plain state machine (no stops); an entry can come on the bar after an exit signal (flat at that close).
    * Daily bars are broker days (17:00 America/New_York), each stamped with its first minute (as #430984).
    * Long only; the source has no shorts. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colours and ATR relative to its own mean.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults; initial capital quoted in original_sizing.txt).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483676_three_red_days_atr_filter_long"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "max_duration": [22, 11],
    "use_green_exit": [True, False],
}
DEFAULT_PARAMS = {"max_duration": 22, "use_green_exit": True, "atr_len": 12, "atr_mean_len": 30}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    red, green = c < o, c > o
    three_red = (red & red.shift(1, fill_value=False) & red.shift(2, fill_value=False)).to_numpy()
    three_green = (green & green.shift(1, fill_value=False) & green.shift(2, fill_value=False)).to_numpy()
    atr = _atr(bars_df, int(p["atr_len"]))
    avg = atr.rolling(int(p["atr_mean_len"])).mean()
    known = (atr > 0) & (avg > 0)
    atr_ok = np.where(known, atr > avg, True)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, sig_i, closing = 0, -1, False
    dur = int(p["max_duration"])
    for i in range(m):
        if closing:                                      # the close filled at this bar's open
            pos, closing = 0, False
        if pos == 1 and i > sig_i:
            if (p["use_green_exit"] and three_green[i]) or (i - sig_i >= dur):
                lx[i], closing = True, True
        elif pos == 0 and three_red[i] and atr_ok[i] and i + 1 < m:
            le[i], pos, sig_i = True, 1, i
    false = pd.Series(False, index=bars_df.index)
    idx = bars_df.index
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
