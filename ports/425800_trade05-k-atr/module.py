"""A 250-bar resistance / support of the weighted price ((H + L + 2C) / 4 reflected through the low / high), hourly bars: the high reaching the previous bar's resistance goes long, the low reaching its support goes short; a long closes when the high reaches its entry close + 50 x the current ATR 250 (the short mirror); reversing.
Port of FMZ strategy #425800 "Trade05-K线支撑阻力ATR止盈" (Trade05-K线支撑阻力ATR止盈).

FMZ source id: 425800

Source
    https://www.fmz.com/strategy/425800 (MyLanguage, FMZ last modified 2023-09-04 22:33:45).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 45-95), MyLanguage, no AUTOFILTER; LENTH 250, ATRS 50; ATR = MA(TR, 250); LOTS from MONEY (percent 5)
    AVGP := (H + L + 2C) / 4;  RS := HHV(2 AVGP - L, 250);  ST := LLV(2 AVGP - H, 250)
    BKVOL <= 1 and H >= REF(RS, 1) and VOL > 0 -> BPK;  SKVOL <= 1 and L <= REF(ST, 1) and VOL > 0 -> SPK
    BKVOL > 0 and BARSBK > 0: MYEXITPRICE := BKPRICE + ATRVAL x 50;  H >= MYEXITPRICE and VOL > 0 -> SP;  short mirror -> BP

Interpretation choices (rules in SURVEY_README.md)
    * MyLanguage close-price model without AUTOFILTER: the IF blocks apply in source order within a bar
      and the bar's net change is the order; BPK / SPK reverse. BKPRICE / SKPRICE are the signal bars'
      closes. BKVOL <= 1 is read as "not long" (LOTS is at least 1; with LOTS = 1 the source would add a
      second lot, which the house engine does not do). The target is recomputed every bar from the CURRENT
      ATR 250 (the comment says the entry bar's ATR; the code does not keep it), and it is an exit signal
      at the bar's close (no stop). BARSBK > 0 keeps the exit off the entry bar. REVERSAL INTENDED. The
      LOTS formula is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, weighted-price support / resistance breakout with an ATR target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: LOTS = max(1, intpart(percent / 100 x MONEY x C / (MARGIN x UNIT))) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in VOL > 0 on the entry and exit bars; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_425800_weighted_price_support_resistance_break_atr50_target_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lenth": [250, 100],
    "atrs": [50, 20],
}
DEFAULT_PARAMS = {"lenth": 250, "atrs": 50}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["lenth"])
    avgp = (h + lo + 2 * c) / 4
    rs = (2 * avgp - lo).rolling(n).max()
    st = (2 * avgp - h).rolling(n).min()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (pc - h).abs(), (pc - lo).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = (tr.rolling(n).mean() * float(p["atrs"])).to_numpy(dtype=float)
    vol_ok = (v > 0).to_numpy()
    lcond = ((h >= rs.shift(1)).to_numpy()) & vol_ok
    scond = ((lo <= st.shift(1)).to_numpy()) & vol_ok
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, px, ent = 0, np.nan, -1
    for i in range(m):
        old = pos
        if pos != 1 and lcond[i]:                                   # BPK
            pos, px, ent = 1, cv[i], i
        if pos != -1 and scond[i]:                                  # SPK
            pos, px, ent = -1, cv[i], i
        if pos == 1 and i > ent and vol_ok[i] and hv[i] >= px + atr[i]:      # SP
            pos = 0
        if pos == -1 and i > ent and vol_ok[i] and lv[i] <= px - atr[i]:     # BP
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
