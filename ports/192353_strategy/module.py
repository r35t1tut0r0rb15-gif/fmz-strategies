"""Turtle 55-bar breakout with 2-ATR stop from the last unit and 20-bar channel exit
(the long exit uses the highest LOW, as written).
Port of FMZ strategy #192353 "海龟" (turtle).

Source
    https://www.fmz.com/strategy/192353 (Python, author "aawww", FMZ last modified
    2020-03-23 14:44:24). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 61-193)
    n = TA.ATR(records, Atr=20)[-1];  current_price = records[-1].Close
    channel_high = TA.Highest(records, 55, 'High'); channel_low = TA.Lowest(records, 55, 'Low')
        (hard-coded 55 overrides the Donchian_open argument on the next line)
    stop_high = TA.Highest(records, 20, 'High'); stop_low = TA.Highest(records, 20, 'Low') [sic]
    flat:  price > channel_high -> long 1 unit;  price < channel_low -> short 1 unit
    long:  price >= last_price + 0.5n and units < 4 -> add 1 unit (last_price := price)
           elif price <= last_price - 2n -> flat;   then if price <= stop_low -> flat
    short: mirror (price >= stop_high -> flat)

Interpretation choices
    * The bot polls the forming bar in a tight loop; the port evaluates the same rule on the
      completed bar t (records[-1] -> t). TA.Highest/Lowest exclude the current bar (SURVEY_README
      FMZ TA rule), so the channels cover bars t-N..t-1. ATR is Wilder's (TA.ATR) at t.
    * stop_low is the highest LOW of the prior 20 bars (the code says TA.Highest(..., 'Low')),
      which exits longs much sooner than the evident "lowest low". Ported exactly as written;
      the short side uses the highest HIGH, as the turtle rule does.
    * Adds are sizing (not ported) but move last_price, which the 2-ATR stop uses, so the add rule
      is kept as state (4-unit cap). An add skips the 2-ATR check on that bar (if/elif, as
      written) but not the channel exit.
    * After an exit the bot re-enters at once if the breakout still holds; the port evaluates
      re-entry from the next bar. Entries only from flat: opposite entries cannot occur;
      portfolio_kwargs also returns upon_opposite_entry="ignore" (rule 6).
    * No bar size in the source (GetRecords() default, no backtest header):
      FREQ = "bar_size_pending" (rule 1).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_192353_turtle_55_highest_low_exit"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_period": [40, 55, 70],
    "exit_period": [10, 20, 30],
    "stop_atr": [1.5, 2.0, 3.0],
}
DEFAULT_PARAMS = {"entry_period": 55, "exit_period": 20, "atr_length": 20, "stop_atr": 2.0,
                  "add_atr": 0.5, "max_units": 4}


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


def _atr(bars, n):
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ne, nx = int(p["entry_period"]), int(p["exit_period"])
    high, low = bars_df["high"], bars_df["low"]
    ch_hi = high.rolling(ne).max().shift(1).to_numpy()
    ch_lo = low.rolling(ne).min().shift(1).to_numpy()
    stop_high = high.rolling(nx).max().shift(1).to_numpy()
    stop_low = low.rolling(nx).max().shift(1).to_numpy()     # highest LOW, as written
    atr = _atr(bars_df, int(p["atr_length"])).to_numpy()
    c = bars_df["close"].to_numpy(dtype=float)

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, ref, units = 0, np.nan, 0
    for i in range(m):
        if pos == 0:
            if np.isnan(atr[i]):
                continue
            if c[i] > ch_hi[i]:
                le[i], pos, ref, units = True, 1, c[i], 1
            elif c[i] < ch_lo[i]:
                se[i], pos, ref, units = True, -1, c[i], 1
            continue
        add = units + 1 <= p["max_units"] and pos * (c[i] - ref) >= p["add_atr"] * atr[i]
        stop = (not add) and pos * (c[i] - ref) <= -p["stop_atr"] * atr[i]
        if add:
            ref, units = c[i], units + 1
        leave = c[i] <= stop_low[i] if pos == 1 else c[i] >= stop_high[i]
        if stop or leave:
            (lx if pos == 1 else sx)[i] = True
            pos = 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
