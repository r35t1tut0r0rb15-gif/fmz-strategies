"""MA5X long, broker days: the WMA 3 crossing above the WMA 195, or the first bar of the alignment WMA 3
> WMA 78 > WMA 195, goes long; the WMA 3 crossing under the WMA 195 closes it, and so does the close
crossing under an ATR(40) x 6 ratchet line once the trade is more than 20 % in profit.
Port of FMZ strategy #427461 "5-day Moving Average Golden Cross Momentum Strategy".

FMZ source id: 427461

Source
    https://www.fmz.com/strategy/427461 (PineScript v4, FMZ last modified 2023-09-21 12:16:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 165-205), WMA 3 / 78 / 195, ATR 40 x 6, pyramiding 2
    crossover(s, l) -> entry "X Up" (qty 30000 / close); s > m > l starting -> entry "UTA" (qty 20000 / close)
    crossunder(s, l) -> close_all
    sl = hl2 - 6 atr(40); sl := s[1] > sl[1] ? max(sl, sl[1]) : sl
    crossunder(close, sl) and openprofit > 30000 x 0.2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two entries are two units (pyramiding 2, cash quantities): sizing. The port holds one
      position, opened by whichever signal comes first.
    * The stop's profit filter is in cash (openprofit > 6000 on a 30000 first unit): re-expressed
      as the close more than 20 % above the entry fill (criterion 2 / 4: the filter is a return on the
      first unit, the second unit's share is sizing). The line is tested on closes: an exit signal.
    * The 1 July 2020 start is the author's backtest window: dropped. The 78 / 195 / 390 lengths
      are named "2 / 5 / 10-day" averages in the comments (intraday bars), but the header runs daily
      bars: ported on the header's bar size.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * Long only. FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-based exits.
    2 generic: ADAPT, the cash profit filter -> a return threshold; ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 2 and cash quantities stored in original_sizing.txt.
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

NAME = "fmz_427461_ma5x_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "l_len": [195, 100],
    "multiplier": [6.0, 3.0],
    "profit_gate": [0.2, 0.1],
}
DEFAULT_PARAMS = {"s_len": 3, "m_len": 78, "l_len": 195, "atr_period": 40, "multiplier": 6.0, "profit_gate": 0.2}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    s, mm, ll = _wma(c, int(p["s_len"])), _wma(c, int(p["m_len"])), _wma(c, int(p["l_len"]))
    x_up = ((s > ll) & (s.shift(1) <= ll.shift(1))).to_numpy()
    x_dn = ((s < ll) & (s.shift(1) >= ll.shift(1))).to_numpy()
    al = (s > mm) & (mm > ll)
    uta = (al & ~al.shift(1, fill_value=False)).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    base = (((h + lo) / 2) - p["multiplier"] * _rma(tr, int(p["atr_period"]))).to_numpy()
    sv = s.to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    m = len(cv)
    line = np.full(m, np.nan)
    for i in range(m):
        prev = line[i - 1] if i and not np.isnan(line[i - 1]) else base[i]      # nz(sl[1], sl)
        line[i] = max(base[i], prev) if i and sv[i - 1] > prev else base[i]
    c1 = np.concatenate(([np.nan], cv[:-1]))
    l1 = np.concatenate(([np.nan], line[:-1]))
    x_line = (cv < line) & (c1 >= l1)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, entry_px = 0, False, np.nan
    for i in range(m):
        if pending:
            pos, pending, entry_px = 1, False, ov[i]
        if pos == 1:
            if x_dn[i] or (x_line[i] and cv[i] / entry_px - 1 > p["profit_gate"]):
                lx[i], pos = True, 0
        elif not pending and (x_up[i] or uta[i]):
            le[i], pending = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
