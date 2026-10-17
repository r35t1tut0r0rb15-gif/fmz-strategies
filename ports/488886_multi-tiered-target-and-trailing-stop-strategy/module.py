"""Heikin-Ashi momentum entries from flat with a range-checked stop that moves to break-even and then trails after a
first target, two-day bars: a rising green Heikin-Ashi candle goes long when flat (a falling red one short); the stop
starts 1.2 ATR from the entry close, moves to the entry once the high reaches 4 ATR of profit, then trails 0.6 ATR
behind the best high; a bar whose low reaches the stop closes the trade at the next open (shorts mirrored).
Port of FMZ strategy #488886 "多层级目标和尾随止损策略-Multi-Tiered-Target-and-Trailing-Stop-Strategy" (Algo Trading v1 | SUNNY GUHA By OIESU).

FMZ source id: 488886

Source
    https://www.fmz.com/strategy/488886 (PineScript v6, FMZ last modified 2025-03-31 16:20:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 174-355), first target 10000, stop 3000, trail 1500 ($ price units), HA candles
    bullish = haClose > haOpen and haClose > haClose[1];  bearish mirrored
    flat: bullish -> long (base = close, target = base + 10000, stop = base - 3000, highest = high); bearish -> short
    long held: highest = max(high, highest); before the target: stop = base - 3000; high >= base + 10000 -> first
    target hit, stop = base; after it: stop = max(base, highest - 1500) (the target only moves up: no order)
    low <= stop -> close_all and reset everything (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is checked on the completed bar's low (high) and closed with close_all: a range-checked exit at the
      next open (rule 3; as #489638), so all of it lives in simulate(); no stops().
    * Criterion 2: the dollar distances become multiples of the signal bar's Wilder ATR(14): on BTC (the dollar scale
      the inputs imply; on the backtest's ETH_USDT 10000 / 3000 would never be reached) a 2-day ATR is about 2500, so
      3000 / 10000 / 1500 are about 1.2 / 4 / 0.6 ATR (judgement before any backtest).
    * Every stop exit clears firstTargetHit, so the "second entry" branch can never run: dead code, as written. The
      target-zone increases move no order.
    * Entries only from flat: Opposite entries cannot occur. Pyramiding 100 does not matter (flat-only entries).
    * FREQ = "2D" from the backtest header (period 2d): two-day bars from broker days in fixed blocks counted from
      1970-01-01 (block phase: decision owed), as #426509.

Admission criteria
    1 fits the interface: PASS, bar-close orders and range-checked exits at the next open.
    2 generic: ADAPT, dollar distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (pyramiding quoted in original_sizing.txt).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488886_heikin_ashi_be_trail_stop_2d"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_atr": [1.2, 2.4],
    "target_atr": [4.0, 2.0],
}
DEFAULT_PARAMS = {"stop_atr": 1.2, "target_atr": 4.0, "trail_atr": 0.6, "atr_len": 14}


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


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


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


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    atr = _atr(bars_df, int(p["atr_len"])).to_numpy(dtype=float)
    m = len(c)
    hc = (o + h + lo + c) / 4
    ho = np.empty(m)
    for i in range(m):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 else (ho[i - 1] + hc[i - 1]) / 2
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    held = 0               # position during this bar (filled at its open)
    tgt = 0                # position after this bar's orders
    base = stop = best = unit = np.nan
    hit = False
    for i in range(1, m):
        held = tgt
        bull = hc[i] > ho[i] and hc[i] > hc[i - 1]
        bear = hc[i] < ho[i] and hc[i] < hc[i - 1]
        if held == 1:
            best = max(h[i], best)
            if not hit and h[i] >= base + p["target_atr"] * unit:
                hit, stop = True, base
            elif hit:
                stop = max(base, best - p["trail_atr"] * unit)
            else:
                stop = base - p["stop_atr"] * unit
            if lo[i] <= stop:
                lx[i], tgt, hit = True, 0, False
        elif held == -1:
            best = min(lo[i], best)
            if not hit and lo[i] <= base - p["target_atr"] * unit:
                hit, stop = True, base
            elif hit:
                stop = min(base, best + p["trail_atr"] * unit)
            else:
                stop = base + p["stop_atr"] * unit
            if h[i] >= stop:
                sx[i], tgt, hit = True, 0, False
        if held == 0 and not np.isnan(atr[i]) and i + 1 < m:
            if bull:
                le[i], tgt, base, best, unit, hit = True, 1, c[i], h[i], atr[i], False
                stop = base - p["stop_atr"] * unit
            elif bear:
                se[i], tgt, base, best, unit, hit = True, -1, c[i], lo[i], atr[i], False
                stop = base + p["stop_atr"] * unit
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
