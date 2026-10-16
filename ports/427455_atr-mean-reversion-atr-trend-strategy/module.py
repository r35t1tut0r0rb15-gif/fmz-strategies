"""Mean reversion (ATR) [KL], long only, broker days: with ATR(20) outside its own band (SMA 20 +-
1 stdev) and an upward drift of log returns, go long; a ratchet line max(low - 2 x ATR 14) is kept
while long, and a bar whose low touches it closes the long.
Port of FMZ strategy #427455 "Mean Reversion ATR Trend Strategy".

FMZ source id: 427455

Source
    https://www.fmz.com/strategy/427455 (PineScript v4, FMZ last modified 2023-09-21 11:42:06).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 141-202), TSL ATR 14 x 2 on lows, volatility ATR 20, drift 20
    diverted = atr20 > sma(atr20, 20) + stdev(atr20, 20) or atr20 < sma - stdev
    drift = sma(log(close / close[1]), 20) - 0.5 stdev(...)^2; uptrend = (drift > drift[1] and drift > drift[2]) or drift > 0
    stop = flat ? low - 2 atr14 : max(stop, low - 2 atr14) while long (reset to 0 when flat at the bar's end)
    long and low <= stop -> close; else diverted and uptrend and flat -> entry long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing line is TESTED on each completed bar's low and the exit is a strategy.close
      (next open): a close-based exit signal from simulate() (rule 2 second half), not a stop order;
      no mark. The line ratchets on lows (not on the best high), which the house trail could not
      express anyway.
    * The add while long (pyramiding 1) never fires; entries only from flat. Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. The
      backtest time inputs are the author's window (within_timeframe is the constant true).
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bar-close exit test.
    2 generic: PASS, ATR multiples and log returns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427455_kl_atr_mean_reversion_long"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tsl_mult": [2.0, 3.0],
    "len_volat": [20, 40],
    "len_drift": [20, 40],
}
DEFAULT_PARAMS = {"tsl_atr": 14, "tsl_mult": 2.0, "len_volat": 20, "len_drift": 20}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    line = (lo - _rma(tr, int(p["tsl_atr"])) * p["tsl_mult"]).to_numpy()
    nv = int(p["len_volat"])
    av = _rma(tr, nv)
    diverted = ((av > av.rolling(nv).mean() + av.rolling(nv).std(ddof=0))
                | (av < av.rolling(nv).mean() - av.rolling(nv).std(ddof=0))).to_numpy()
    nd = int(p["len_drift"])
    lr = np.log(c / c.shift(1))
    drift = lr.rolling(nd).mean() - lr.rolling(nd).std(ddof=0) ** 2 * 0.5
    up = (((drift > drift.shift(1)) & (drift > drift.shift(2))) | (drift > 0)).to_numpy()
    lv = lo.to_numpy(dtype=float)
    m = len(lv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, stop = 0, False, 0.0
    for i in range(m):
        if pending:
            pos, pending = 1, False
        if pos == 0:
            stop = line[i]
        else:
            stop = max(stop, line[i])
        if pos == 1 and lv[i] <= stop:
            lx[i], pos = True, 0
        elif pos == 0 and not pending and diverted[i] and up[i]:
            le[i], pending = True, True
        if pos == 0:
            stop = 0.0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
