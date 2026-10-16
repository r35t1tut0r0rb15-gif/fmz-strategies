"""HMA and daily open, hourly bars: buy when the HMA(14) of the open is rising, the bar's open is above
the last completed day's open and the daily open just stepped up; sell on the mirror. A Sell while long
(or a Buy while short) only flattens. Positions close when the open profit passes a small target or a
small loss.
Port of FMZ strategy #427615 "HMA Daily Crossover Trading Strategy" (SeaSide420).

FMZ source id: 427615

Source
    https://www.fmz.com/strategy/427615 (PineScript v4, FMZ last modified 2023-09-22 17:07:15).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 175-197), SL -0.05 $, TP 0.05 $, price = open, period 14
    hma = wma(2 wma(open, 7) - wma(open, 14), 4); s1 = open; s2 = security("D", open, lookahead_off)
    closeall = openprofit < SL or openprofit > TP -> close_all
    hma > hma[1] and s1 > s2 and s2[1] > s2[2] and s1 > s2[1] -> order("Buy", long)
    hma < hma[1] and s1 < s2 and s2[1] < s2[2] and s1 < s2[1] -> order("Sell", short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out: Pine defaults (1 contract).
    * strategy.order nets against the position: Buy from flat goes long, Buy while short flattens;
      adds on the same side are sizing (one unit held), so a Sell while long flattens.
    * s2 is the broker-day open; historical lookahead_off values are the last completed day's (the
      new day's from the bar whose end reaches the day's 17:00 New York close). s2[1], s2[2] are
      one and two HOURLY bars back, as written.
    * Criterion 2: the open-profit thresholds of 0.05 $ on one contract are price distances; they
      become `tp_atr` / `sl_atr` x Wilder ATR(14) of the signal bar, measured from the fill price
      (next open) and checked on bar closes (exit signals). The source's 0.05 $ on hourly BTC is
      about 0.0003 ATR (closes on almost any move); the grid starts at 0.01 (judgement before any
      backtest). Close-all and a new order on the same bar: the close is applied first, then the
      order from flat (a same-side re-entry keeps the position; stated approximation).
    * Opposite entries cannot occur: an opposite order only flattens (strategy.order nets), so a
      new side always starts from flat.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; profit check on bar closes.
    2 generic: ADAPT, dollar thresholds -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() sizing stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily open.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427615_hma_daily_open_basket"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
BAR_HOURS = 1

GRID = {
    "period": [14, 28],
    "tp_atr": [0.01, 0.5],
    "sl_atr": [0.01, 0.5],
}
DEFAULT_PARAMS = {"period": 14, "tp_atr": 0.01, "sl_atr": 0.01, "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily_open(bars_df):
    day = broker_day(bars_df.index)
    dopen = bars_df["open"].groupby(day).first()
    end_ny = (bars_df.index + pd.Timedelta(hours=BAR_HOURS)).tz_convert("America/New_York")
    day_end_ny = (pd.DatetimeIndex(day) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    at_close = np.asarray(end_ny >= day_end_ny)
    return np.where(at_close, dopen.reindex(day).to_numpy(), dopen.shift(1).reindex(day).to_numpy())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o = bars_df["open"]
    n = int(p["period"])
    hma = _wma(2 * _wma(o, n // 2) - _wma(o, n), int(round(np.sqrt(n)))).to_numpy()
    s1 = o.to_numpy(dtype=float)
    s2 = _daily_open(bars_df)
    s2_1 = np.concatenate(([np.nan], s2[:-1]))
    s2_2 = np.concatenate(([np.nan, np.nan], s2[:-2]))
    hma1 = np.concatenate(([np.nan], hma[:-1]))
    with np.errstate(invalid="ignore"):
        buy = (hma > hma1) & (s1 > s2) & (s2_1 > s2_2) & (s1 > s2_1)
        sell = (hma < hma1) & (s1 < s2) & (s2_1 < s2_2) & (s1 < s2_1)
    pc = bars_df["close"].shift(1)
    tr = pd.concat([bars_df["high"] - bars_df["low"], (bars_df["high"] - pc).abs(),
                    (bars_df["low"] - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, int(p["atr_length"])).to_numpy()
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, entry_i, dist_tp, dist_sl = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and entry_i < i:                       # open profit on this bar's close
            prof = (c[i] - s1[entry_i]) * pos
            if prof < -dist_sl or prof > dist_tp:
                pos = 0
        new = pos
        if buy[i]:
            new = 0 if pos == -1 else 1
        elif sell[i]:
            new = 0 if pos == 1 else -1
        if new != pos and new != 0:
            entry_i = i + 1                                # fills at the next open
            dist_tp, dist_sl = p["tp_atr"] * atr[i], p["sl_atr"] * atr[i]
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
