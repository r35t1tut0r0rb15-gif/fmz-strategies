"""EMA 9 / HMA 69 of the Heikin Ashi close, broker days, long only: the HMA under the EMA goes long; the HMA over the EMA
closes the long when it is in profit, and a close crossing under 6.5 % below the entry price closes it as a stop.
Port of FMZ strategy #431224 "Trend Following Strategy" (EMA / HMA trend).

FMZ source id: 431224

Source
    https://www.fmz.com/strategy/431224 (PineScript v5, FMZ last modified 2023-11-06 10:34:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 172-209), HA source on, EMA 9, HMA 69, stop -6.5 %
    src = heikin-ashi close (same timeframe); ema = ema(src, 9); hma = hma(src, 69)
    hma < ema -> entry long;  hma > ema and openprofit > 0 -> close
    stop = avg price x 0.935 crossing above the close (stoploss > close and stoploss[1] < close[1]) while long -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin Ashi close of the chart's own timeframe is ohlc4. HMA = wma(2 wma(src, 34) -
      wma(src, 69), floor(sqrt 69)). openprofit > 0 is a close above the entry price (the fill at the
      open after the signal). The stop is a close-checked exit from the bar after the fill bar
      (stoploss[1] needs a position on the previous bar).
    * The closes act on the position held at the bar's start (an entry signal while long is
      ignored). Long only; Opposite entries cannot occur. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, moving averages and a percentage stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 15 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431224_ha_ema_hma_long"
FAMILY = "hull_ma"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hma_len": [69, 34],
    "stop_pct": [6.5, 3.0],
}
DEFAULT_PARAMS = {"ema_len": 9, "hma_len": 69, "stop_pct": 6.5}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: (a * w).sum() / w.sum(), raw=True)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    ema = src.ewm(span=int(p["ema_len"]), adjust=False).mean()
    n = int(p["hma_len"])
    hma = _wma(2 * _wma(src, n // 2) - _wma(src, n), int(np.floor(np.sqrt(n))))
    buy, sell = (hma < ema).to_numpy(), (hma > ema).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    k = 1 - float(p["stop_pct"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, entry_i = 0, -1
    for i in range(m):
        start = pos
        if buy[i] and pos == 0:
            pos, nxt = 1, i + 1
        if start == 1:
            e = ov[entry_i]
            sl = e * k
            stop = sl > cv[i] and i - 1 >= entry_i and sl < cv[i - 1]
            if (sell[i] and cv[i] > e) or stop:
                pos = 0
        if pos == 1 and start == 0:
            entry_i = nxt
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
