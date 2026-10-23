"""Broker days: a 7-bar rise of 8 % or more on a bar with volume above its SMA 20 (the CVD rising) and the close above a VWAP anchored at the latest 20-bar volume high goes long; the mirror fall below it goes short; each trade gets a stop at the 200-bar low / high and a target twice that distance from the script's previous trade's entry price; reversing.
Port of FMZ strategy #437011 "基于锚定滚动CVDVWAP的信号策略Anchored-Rolling-CVDVWAP-Signal-Strategy" (Anchored Rolling CVDVWAP Signal Strategy).

FMZ source id: 437011

Source
    https://www.fmz.com/strategy/437011 (PineScript v5, FMZ last modified 2023-12-29 14:56:03).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 118-240), anchor period 20; envelope 2 sd (plots only); analysis period 7, -8 % / +8 %; VWAP filter on, CVD filter on (20); TP 200 % of the SL distance; SL lookback 200; toggle off
    dip = roc(close, 7) <= -8 and cvd > cvd[1] and close < anchoredVwap;  rip mirror;  tradeSL := dip ? highest(high, 200) : rip ? lowest(low, 200) : tradeSL
    tradeTP := dip ? tradeEntryPrice - (tradeSL - tradeEntryPrice) x 2 : rip ? tradeEntryPrice + (tradeEntryPrice - tradeSL) x 2 : tradeTP (tradeEntryPrice not yet updated)
    rip -> entry Long, close Short;  dip -> close Long, entry Short;  exit(limit = tradeTP, stop = tradeSL) for both sides every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * cvd = cum(volume - sma(volume, 20)), so "cvd rising" is the bar's volume above its SMA 20. The
      anchored VWAP restarts at each bar whose volume is the 20-bar highest. The target is computed before
      tradeEntryPrice is updated, so it uses the script's PREVIOUS trade entry (its own inTrade state,
      which only takes a new entry price when it is not in a trade): a target on the wrong side of the
      fill would fill at once in the script; the port then keeps no target (weird case, approximation).
      The stop / target are fixed at the signal bar as fractions of the fill; the script re-sends them
      every bar and a same-side signal while in a trade moves them (mark trailing_stop_pending). The
      envelope only feeds plots. REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing stop and distance target as fractions of the fill.
    2 generic: PASS, momentum bursts with volume and anchored-VWAP filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the CVD filter, the volume-high anchor and the anchored VWAP; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_437011_roc7_burst_cvd_anchored_vwap_swing_bracket_reversal"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "move_pct": [8.0, 5.0],
    "sl_periods": [200, 50],
}
DEFAULT_PARAMS = {"anchor_period": 20, "analysis": 7, "move_pct": 8.0, "cvd_len": 20, "tp_pct": 200.0,
                  "sl_periods": 200}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _levels(bars_df, p):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    hv, lv, cv, vv = (x.to_numpy(dtype=float) for x in (h, lo, c, v))
    hvol = v.rolling(int(p["anchor_period"])).max().to_numpy()
    m = len(cv)
    avwap = np.full(m, np.nan)
    num = den = np.nan
    anchored = False
    for i in range(m):
        if vv[i] == hvol[i]:
            num, den, anchored = (hv[i] + lv[i] + cv[i]) * vv[i], 3 * vv[i], True
        elif anchored:
            num, den = num + (hv[i] + lv[i] + cv[i]) * vv[i], den + 3 * vv[i]
        if anchored:
            avwap[i] = num / den if den else np.nan
    cvd_up = (v > v.rolling(int(p["cvd_len"])).mean()).to_numpy()
    k = int(p["analysis"])
    roc = (100 * (c - c.shift(k)) / c.shift(k)).to_numpy()
    mv = float(p["move_pct"])
    with np.errstate(invalid="ignore"):
        dip = (roc <= -mv) & cvd_up & (cv < avwap)
        rip = (roc >= mv) & cvd_up & (cv > avwap)
    n = int(p["sl_periods"])
    hh, ll = h.rolling(n).max().to_numpy(), lo.rolling(n).min().to_numpy()
    tpk = float(p["tp_pct"]) / 100
    sl, tp = np.full(m, np.nan), np.full(m, np.nan)
    s_p = t_p = ep = np.nan
    in_trade, t_long, t_short = False, False, False
    for i in range(m):
        if dip[i]:
            s_p = hh[i]
            t_p = ep - (s_p - ep) * tpk
        elif rip[i]:
            s_p = ll[i]
            t_p = ep + (ep - s_p) * tpk
        if (dip[i] or rip[i]) and not in_trade:
            ep, in_trade, t_long, t_short = cv[i], True, bool(rip[i]), bool(dip[i])
        if in_trade and ((t_long and (lv[i] < s_p or hv[i] > t_p)) or (t_short and (hv[i] > s_p or lv[i] < t_p))):
            in_trade = False
        sl[i], tp[i] = s_p, t_p
    return dip, rip, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dip, rip, sl, tp = _levels(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(rip & ~dip, index=ix), false, pd.Series(dip & ~rip, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dip, rip, sl, tp = _levels(bars_df, p)
    ix = bars_df.index
    o = bars_df["open"].to_numpy(dtype=float)
    sl1 = pd.Series(sl, index=ix).shift(1).to_numpy()  # the levels set on the signal bar
    tp1 = pd.Series(tp, index=ix).shift(1).to_numpy()
    short_fill = pd.Series(dip, index=ix).shift(1, fill_value=False).to_numpy()
    with np.errstate(invalid="ignore"):
        sl_f = np.where(short_fill, (sl1 - o) / o, (o - sl1) / o)
        tp_f = np.where(short_fill, (o - tp1) / o, (tp1 - o) / o)
    ix = bars_df.index
    sl_s, tp_s = pd.Series(sl_f, index=ix), pd.Series(tp_f, index=ix)
    return {"sl_stop": sl_s.where(sl_s > 0), "tp_stop": tp_s.where(tp_s > 0)}


def portfolio_kwargs(**params):
    return {}
