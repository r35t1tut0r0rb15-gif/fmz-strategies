"""Turtle-style spot breakout: long above the prior channel high, out below a half-length channel
low or 2 ATR under the last buy price (long only).
Port of FMZ strategy #186598 "海龟策略btc现货版" (turtle strategy, BTC spot version).

Source
    https://www.fmz.com/strategy/186598 (Python, author "groot", FMZ last modified
    2020-03-06 12:04:41). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 55-115), fresh_rete 24, DC_range 30, atrlength 24
    records = GetRecords(fresh_rete*3600)  (one-day bars); current_price = records[-1].Close
    atr = TA.ATR(records, atrlength)[-1]
    max_price = max(High of records[-DC_range:-2]);  min_price = min(Low of records[-DC_range/2:-2])
    open:  no orders yet and current_price > max_price             -> buy
    add:   current_price > last_price + 0.5*atr                    -> buy  (last_price := close)
    stop:  current_price < min_price;  close: current_price < last_price - 2*atr -> sell all

Interpretation choices
    * Bars: the code asks for fresh_rete*3600-second records with fresh_rete = 24 (argument
      default), i.e. daily bars; daily bars are broker days (17:00 New York). It polls once a day
      on the forming bar; the port evaluates the same rule on completed bar t ([-1] -> t), so
      max_price covers bars t-DC_range+1..t-2 and min_price bars t-DC_range/2+1..t-2 (the
      source skips the last completed bar too).
    * Adds are sizing (not ported) but move last_price, which the 2-ATR exit uses, so the add
      rule is kept as state (no unit cap in the source). The exit signs are computed before the
      orders, with the old last_price, and an exit wins over an add on the same bar.
    * Long only (spot); shorts are never emitted, so opposite entries cannot occur.
    * ATR multiples are already volatility-normalised. The +10/+100 price offsets in the order
      code are execution details (original_sizing.txt).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_186598_spot_turtle_breakout"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # code requests fresh_rete*3600 s = 86400 s records (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dc_range": [20, 30, 40],
    "atr_length": [14, 24],
    "stop_atr": [1.5, 2.0, 3.0],
}
DEFAULT_PARAMS = {"dc_range": 30, "atr_length": 24, "stop_atr": 2.0, "add_atr": 0.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
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


def _atr(bars, n):
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dc = int(p["dc_range"])
    max_price = bars_df["high"].rolling(dc - 2).max().shift(2).to_numpy()
    min_price = bars_df["low"].rolling(int(dc / 2) - 2).min().shift(2).to_numpy()
    atr = _atr(bars_df, int(p["atr_length"])).to_numpy()
    c = bars_df["close"].to_numpy(dtype=float)

    m = len(c)
    entries, exits = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_pos, ref = False, np.nan
    for i in range(m):
        if not in_pos:
            if c[i] > max_price[i] and not np.isnan(atr[i]):
                entries[i], in_pos, ref = True, True, c[i]
            continue
        if c[i] < min_price[i] or c[i] < ref - p["stop_atr"] * atr[i]:
            exits[i], in_pos = True, False
        elif c[i] > ref + p["add_atr"] * atr[i]:
            ref = c[i]                 # add: moves the exit reference only

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(entries, index=idx), pd.Series(exits, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
