"""EMA 8 / 14 / 16 "traffic lights" above a daily EMA 100, 1-hour bars: from flat, with the EMAs stacked up and the fast
EMA above the last completed day's EMA 100, a fresh cross among them goes long (the mirror short); a fast / medium cross
back closes the trade. Each trade has a 40 % (long) or 30 % (short) target and a ratcheting stop at the bar low minus 2
ATR (high plus 2 ATR for shorts), which the house trail cannot express.
Port of FMZ strategy #433122 "基于EMA均线的交易策略Traffic-Light-Trading-Strategy-Based-on-EMA" (Trafic Lights Strategy (TLS)).

FMZ source id: 433122

Source
    https://www.fmz.com/strategy/433122 (PineScript v4, FMZ last modified 2023-11-24 15:46:48).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 198-334), EMA 8 / 14 / 16, filter EMA 100 on "D"; TP on (40 % / 30 %), SL off, trailing stop on (ATR 14 x 2)
    goLong = fema > mema > sema and fema > filter and (crossover(fema, mema) or crossover(mema, sema) or crossover(sema, filter)); goShort mirrors
    goLong and flat -> entry long;  long and crossunder(fema, mema) -> close;  exit(limit = avg (1 + 40 %), stop = long_T_stop)
    long_T_stop = max(long_T_stop[1], low - 2 atr(14)) while long (0 when flat); short: min(short_T_stop[1], high + 2 atr) (9999999 when flat)

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(..., 'D', ema(close, 100)) without lookahead is read as the last completed daily bar
      (SURVEY_README), built from the port's own bars on broker days (17:00 America/New_York).
    * The trailing stop ratchets on each bar's low minus 2 ATR (not on the best price), which the
      house trail spec cannot express: mark trailing_stop_pending. The port fixes the stop at its first
      level, 2 ATR / close of the signal bar, shifted one bar and re-based on the fill. The target is
      side-dependent: tp_stop is 0.40 after a long signal and 0.30 after a short one (read on the fill
      bar). The 1 % stop is off by default.
    * Entries only from flat (notInTrade); the entries are emitted on every qualifying bar except
      against the position the signals hold, so a stop or target exit is followed by a new entry on
      the next signal. Opposite entries cannot occur (the cross that would allow one closes the trade
      on the same bar). Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily filter from completed broker days; bracket fixed at entry.
    2 generic: PASS, EMA order and percent / ATR exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 20 % of equity and the commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily filter on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_433122_traffic_light_emas"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [2.0, 3.0],
    "filter_len": [100, 50],
}
DEFAULT_PARAMS = {"f_len": 8, "m_len": 14, "s_len": 16, "filter_len": 100, "atr_len": 14, "atr_mult": 2.0,
                  "tp_long": 0.40, "tp_short": 0.30}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["f_len"]), adjust=False).mean()
    md = c.ewm(span=int(p["m_len"]), adjust=False).mean()
    s = c.ewm(span=int(p["s_len"]), adjust=False).mean()
    day = broker_day(bars_df.index)
    dc = pd.Series(c.to_numpy(), index=day).groupby(level=0).last()
    dema = dc.ewm(span=int(p["filter_len"]), adjust=False).mean()
    flt = pd.Series(dema.shift(1).reindex(day).to_numpy(), index=c.index)
    go_l = ((f > md) & (md > s) & (f > flt) & (_xo(f, md) | _xo(md, s) | _xo(s, flt))).to_numpy()
    go_s = ((f < md) & (md < s) & (f < flt) & (_xo(md, f) | _xo(s, md) | _xo(flt, s))).to_numpy()
    cl_l = _xo(md, f).to_numpy()
    cl_s = _xo(f, md).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lx, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        start = pos
        if start == 1 and cl_l[i]:
            pos, lx[i] = 0, True
        elif start == -1 and cl_s[i]:
            pos, sx[i] = 0, True
        if go_l[i] and start != -1 and not lx[i]:
            pos, le[i] = 1, True
        elif go_s[i] and start != 1 and not sx[i]:
            pos, se[i] = -1, True
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return le, lx, se, sx, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _ = _signals(bars_df, p)
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _, af = _signals(bars_df, p)
    tp = pd.Series(np.where(le, float(p["tp_long"]), float(p["tp_short"])), index=bars_df.index)
    return {"sl_stop": (af * float(p["atr_mult"])).shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
