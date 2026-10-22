"""Close crossings of the EMA 50 on the side of the EMA 200 with the DMI 14 side, 5-minute bars, 16:30-20:00 UTC: the up-cross goes long and the down-cross goes short, each with a 0.2 % target and a 0.1 % stop from the signal close; reversing.
Port of FMZ strategy #488165 "Multi Timeframe Exponential Moving Average Crossover Strategy with Trend Confirmation System" (15 MIN Strategy).

FMZ source id: 488165

Source
    https://www.fmz.com/strategy/488165 (PineScript v6, FMZ last modified 2025-03-25 16:58:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-226), EMA 50 / 200; DMI 14 / 14; hours 16:30-20:00; TP 600 ticks, SL 300 ticks
    crossover(close, ema50) and ema50 > ema200 and in hours and di+ > di- -> entry Buy + exit(limit = close + 600 ticks, stop = close - 300 ticks);  mirror -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The tick distances are read as percents at the header coin's price (ETH about 3000 with tick 0.01:
      600 ticks = 0.2 %, 300 ticks = 0.1 %; C2 ADAPT, as #458242). hour() / minute() on the Binance header
      read UTC, from each bar's opening time; 20:00 itself is inside. The bracket is set on the signal bar
      from its close and sent as fractions of the fill open (a level at or through it is marketable and
      closed one bar late, as #458256). A later same-side signal while held re-sends the bracket; the port
      keeps the opening levels, mark trailing_stop_pending (as #434428). An entry on the other side reverses
      (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "5min" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: ADAPT, tick bracket read as percents at the header price.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 16:30-20:00 UTC (bar opening times, the Binance header's time zone).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488165_close_ema50_cross_ema200_dmi_utc_window_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.2, 0.4],
    "sl_pct": [0.1, 0.2],
}
DEFAULT_PARAMS = {"tp_pct": 0.2, "sl_pct": 0.1, "adx_length": 14, "start_minute": 990, "end_minute": 1200}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e50 = c.ewm(span=50, adjust=False).mean()
    e200 = c.ewm(span=200, adjust=False).mean()
    up, dn = h.diff(), -lo.diff()
    n = int(p["adx_length"])
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index)
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index)
    pdm, mdm = pdm.where(up.notna()), mdm.where(up.notna())    # na on the first bar, as ta.dmi
    dip, dim = _rma(pdm, n), _rma(mdm, n)      # the shared true-range divisor cancels in the comparison
    idx = c.index.tz_convert("UTC")
    mins = pd.Series(idx.hour * 60 + idx.minute, index=c.index)
    inside = (mins >= int(p["start_minute"])) & (mins <= int(p["end_minute"]))
    le = (c > e50) & (c.shift(1) <= e50.shift(1)) & (e50 > e200) & inside & (dip > dim)
    se = (c < e50) & (c.shift(1) >= e50.shift(1)) & (e50 < e200) & inside & (dim > dip)
    tp, sl = float(p["tp_pct"]) / 100, float(p["sl_pct"]) / 100
    lvl = {"l_sl": c * (1 - sl), "l_tp": c * (1 + tp), "s_sl": c * (1 + sl), "s_tp": c * (1 - tp)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
