"""The close against a monthly VWAP of the low, with a rising (falling) MACD 12 / 26 / 9 histogram and the SMI ergodic (TSI 6 / 22 against its EMA 5) above (below) zero, 4-hour bars: all bullish goes long, all bearish goes short; only shorts carry the 5 % / 2.5 % bracket (the two exits share one id); reversing.
Port of FMZ strategy #429773 "黄金VWAP-MACD-SMO交易策略Gold-VWAP-MACD-SMO-Trading-Strategy" (VWAP Gold strategy).

FMZ source id: 429773

Source
    https://www.fmz.com/strategy/429773 (PineScript v4, FMZ last modified 2023-10-20 16:23:33).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 165-216), monthly VWAP of low; MACD 12 / 26 / 9; TSI 6 / 22, signal 5; TP / SL long 8.5 % / 3 %, short 5 % / 2.5 % of the close (ticks); strategy() commented out
    longCondition = close > vwapMonthly and hist > hist[1] and osc > 0 -> entry long;  shortCondition mirror -> entry short
    exit("short_tp/sl", "long", profit = close x 0.085, loss = close x 0.03);  exit("short_tp/sl", "short", profit = close x 0.05, loss = close x 0.025)  (in ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits use the id "short_tp/sl", so the later one (for "short") replaces the first: only shorts
      have a bracket, longs end at a short entry (a weird case, as #363970). The short's distances are 5 %
      and 2.5 % of the latest close; the port fixes them at the signal close as fractions of the fill (mark
      trailing_stop_pending). The month is the UTC calendar month (time("M") of the header exchange), the
      VWAP restarting at its first bar. ta.tsi is the double-smoothed ratio (its scale does not matter for
      the sign). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 4-hour bars:
      mark coarse_bar_stop. strategy() is commented out. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; short-only bracket from the signal close.
    2 generic: PASS, monthly VWAP side with MACD and SMI momentum.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() (10000 % of equity) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the monthly VWAP of the low; exchange volume to be compared later (Austin, 2026-10-23).
Session open: month start 00:00 UTC (time("M") of the header exchange; fixed UTC, no DST) for the VWAP.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_429773_monthly_vwap_macd_hist_smi_short_bracket_reversal"
FAMILY = "vwap_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tpshort": [0.05, 0.03],
    "slshort": [0.025, 0.04],
}
DEFAULT_PARAMS = {"tpshort": 0.05, "slshort": 0.025, "longlen": 22, "shortlen": 6, "siglen": 5}


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


def _signals(bars_df, p):
    lo, c, v = bars_df["low"], bars_df["close"], bars_df["volume"]
    utc = bars_df.index.tz_convert("UTC")
    month = utc.year * 12 + utc.month
    vw = (lo * v).groupby(month).cumsum() / v.groupby(month).cumsum()
    vw = pd.Series(vw.to_numpy(), index=c.index)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    pcm = c.diff()
    ll, sl_ = int(p["longlen"]), int(p["shortlen"])
    ds = lambda x: x.ewm(span=ll, adjust=False).mean().ewm(span=sl_, adjust=False).mean()
    erg = ds(pcm) / ds(pcm.abs())
    osc = erg - erg.ewm(span=int(p["siglen"]), adjust=False).mean()
    le = (c > vw) & (hist > hist.shift(1)) & (osc > 0)
    se = (c < vw) & (hist < hist.shift(1)) & (osc < 0)
    return le, se & ~le


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    o, c = bars_df["open"], bars_df["close"]
    sf = se.shift(1, fill_value=False)               # only the short has the shared-id exit
    sl_f = (float(p["slshort"]) * c.shift(1) / o).where(sf)
    tp_f = (float(p["tpshort"]) * c.shift(1) / o).where(sf)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
