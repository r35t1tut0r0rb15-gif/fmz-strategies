"""A day-open +/- 3 ATR 12 channel with EMA 12 / 120 of the previous close and a 12-bar high / low test, hourly bars: the previous close at or over the upper band, the fast EMA over the slow one and the previous close at or over the high 12 bars back goes long (the short mirror goes short); a long closes when the previous close is at or over its entry close and at or under the low 120 bars back (the short mirror); reversing.
Port of FMZ strategy #425799 "Trade04-双均线ATR通道高低点" (Trade04-双均线ATR通道高低点).

FMZ source id: 425799

Source
    https://www.fmz.com/strategy/425799 (MyLanguage, FMZ last modified 2023-09-04 22:33:38).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 45-75), MyLanguage, no AUTOFILTER; LENGTH1 12, LENGTH2 120, X 3; ATR = MA(TR, 12); OPD = the day's first open; LOTS from MONEY (percent 5)
    BKVOL <= 0 and REF(C,1) >= REF(OPD + 3 ATR, 1) and VOL > 0 and EMA(REF(C,1), 12) > EMA(REF(C,1), 120) and REF(C,1) >= REF(H, 12) -> BPK;  SPK mirror
    REF(C,1) >= BKPRICE and REF(C,1) <= REF(L, 120) and BKVOL > 0 -> SP;  REF(C,1) <= SKPRICE and REF(C,1) >= REF(H, 120) and SKVOL > 0 -> BP

Interpretation choices (rules in SURVEY_README.md)
    * MyLanguage close-price model without AUTOFILTER (SURVEY_README MyLanguage rules): the statements
      apply in source order within a bar and the bar's net change is the order; BPK / SPK reverse.
      BKPRICE / SKPRICE are the signal bars' closes. The day (DATE <> REF(DATE, 1)) is read as the broker
      day (17:00 America/New_York), its open the first bar's open (as the VWAP anchor of #363564). The exit
      tests compare the previous close with the entry close and with the low / high 120 bars back, as
      written. BARPOS > 0 is always true. REVERSAL INTENDED. The LOTS formula (MONEY, MARGIN, UNIT) is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, day-open ATR channel breakout with an EMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: LOTS = max(1, intpart(percent / 100 x MONEY x C / (MARGIN x UNIT))) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in VOL > 0 on the entry bars; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the day open; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_425799_day_open_atr_channel_ema12_120_high_low_break_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length1": [12, 20],
    "x": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length1": 12, "x": 3.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    l1 = int(p["length1"])
    l2 = 10 * l1
    l1, l2 = min(l1, l2), max(l1, l2)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (pc - h).abs(), (pc - lo).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = tr.rolling(l1).mean()
    day = pd.Series(broker_day(bars_df.index), index=c.index)
    opd = o.groupby(day).transform("first")                      # VALUEWHEN(OO = 1, O)
    ub, lb = opd + float(p["x"]) * atr, opd - float(p["x"]) * atr
    ma1, ma2 = pc.ewm(span=l1, adjust=False).mean(), pc.ewm(span=l2, adjust=False).mean()
    vol_ok = v > 0
    lcond = ((pc >= ub.shift(1)) & vol_ok & (ma1 > ma2) & (pc >= h.shift(l1))).to_numpy()
    scond = ((pc <= lb.shift(1)) & vol_ok & (ma1 < ma2) & (pc <= lo.shift(l1))).to_numpy()
    pcv, cv = pc.to_numpy(dtype=float), c.to_numpy(dtype=float)
    exl, exs = lo.shift(l2).to_numpy(dtype=float), h.shift(l2).to_numpy(dtype=float)
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, px = 0, np.nan
    for i in range(m):
        old = pos
        if pos != 1 and lcond[i]:                                 # BPK
            pos, px = 1, cv[i]
        if pos != -1 and scond[i]:                                # SPK
            pos, px = -1, cv[i]
        if pos == 1 and pcv[i] >= px and pcv[i] <= exl[i]:        # SP
            pos = 0
        if pos == -1 and pcv[i] <= px and pcv[i] >= exs[i]:       # BP
            pos = 0
        if pos == 1 and old != 1:
            le[i] = True
        elif pos == -1 and old != -1:
            se[i] = True
        elif pos == 0 and old == 1:
            lx[i] = True
        elif pos == 0 and old == -1:
            sx[i] = True
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
