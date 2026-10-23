"""Broker days, from flat only: a breakout of the 65-bar price high together with a filtered OBV oscillator (OBV that skips low-volume bars, minus its EMA 40) above its own 65-bar high and above 0 goes long; the mirror goes short; a 3.75 % stop that becomes a 2.5 % trail once 2.5 % in profit, and any change of the script's position signal closes; reversing state, entries only when flat.
Port of FMZ strategy #435282 "Dual directional Trading Strategy Based on Quantitative Indicators Bullish and Bearish Signals" (Hancock - Filtered Volume OBV OSC [Strategy]).

FMZ source id: 435282

Source
    https://www.fmz.com/strategy/435282 (PineScript v4, FMZ last modified 2023-12-13 17:30:13).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 159-322), volume filter 20 x 1.2; oscillator 40; channels 65 / 45 (70 %); leverage 2; stop 7.5 %, trail threshold 5 %, trail 5 % (all divided by the leverage); direction Both
    obv := volume < abs(sma(v, 20) - 1.2 stdev(v, 20)) ? obv[1] : obv[1] + sign(change(close)) x volume;  osc = obv - ema(obv, 40)
    enter long = osc > highest(osc, 65)[1] and osc > 0 and high > highest(high, 65)[1];  position_signal = enter long ? 1 : enter short ? -1 : exits ? 0 : prev;  close_all when it changes
    opentrades == 0 -> entry LONG / SHORT;  exit(stop = high since entry > avg x 1.025 ? that high x 0.975 : avg x 0.9625)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The leverage input (2) halves every percentage, as written: stop 3.75 %, trail 2.5 % after 2.5 %. The
      trail is ported as the house percent trail {"pct": 0.025, "anchor": "high_low", "activate_after":
      0.025} with the fixed 3.75 % stop (the tighter level applies; mark trailing_stop); the script uses
      the highest bar high from the fill bar, sent from the next bar. The fast channel length is 65 x 70 /
      100 = 45 (integer division). Entries need no open trade; the close_all on a change of the position
      signal acts only on a position the bar's entries leave unchanged (call order). The script's own stop
      state is followed in the signals to know when the position is flat. The volume filter compares the
      volume with its own mean and deviation. REVERSAL INTENDED. Leverage and risk sizing are sizing. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent stop and house trail from the fill.
    2 generic: PASS, price and OBV-oscillator channel breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x leverage 2 / close x risk 100 %, commission 0.075 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the filtered OBV and its low-volume filter; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the 2019 start dropped).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435282_filtered_obv_osc_channel_breakout_trail_reversal"
FAMILY = "obv"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "channel_length": [65, 40],
    "osc_length": [40, 20],
}
DEFAULT_PARAMS = {"vol_len": 20, "vol_mult": 1.2, "osc_length": 40, "channel_length": 65, "channel_pct": 70,
                  "leverage": 2, "stop_pct": 7.5, "trail_threshold": 5.0, "trail_pct": 5.0}


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


def _fractions(p):
    lev = float(p["leverage"])
    return (float(p["stop_pct"]) / lev / 100, float(p["trail_threshold"]) / lev / 100,
            float(p["trail_pct"]) / lev / 100)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    nf = int(p["vol_len"])
    thr = (v.rolling(nf).mean() - v.rolling(nf).std(ddof=0) * float(p["vol_mult"])).abs().to_numpy()
    sgn = np.sign(c.diff().to_numpy())
    vv = v.to_numpy(dtype=float)
    m = len(vv)
    obv = np.full(m, np.nan)
    prev = np.nan
    for i in range(m):
        base = 0.0 if np.isnan(prev) else prev
        obv[i] = base if vv[i] < thr[i] else base + sgn[i] * vv[i]
        prev = obv[i]
    ob = pd.Series(obv, index=c.index)
    osc = ob - ob.ewm(span=int(p["osc_length"]), adjust=False).mean()
    ns = int(p["channel_length"])
    nfast = ns * int(p["channel_pct"]) // 100
    el_p = h > h.rolling(ns).max().shift(1)
    xl_p = lo < lo.rolling(nfast).min().shift(1)
    es_p = lo < lo.rolling(ns).min().shift(1)
    xs_p = h > h.rolling(nfast).max().shift(1)
    el_o = (osc > osc.rolling(ns).max().shift(1)) & (osc > 0)
    es_o = (osc < osc.rolling(nfast).min().shift(1)) & (osc < 0)
    xl_o = osc < osc.rolling(ns).min().shift(1)
    xs_o = osc > osc.rolling(nfast).max().shift(1)
    el, es = (el_o & el_p).to_numpy(), (es_o & es_p).to_numpy()
    xl, xs = (xl_o & xl_p).to_numpy(), (xs_o & xs_p).to_numpy()
    sig = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        q = 1 if el[i] else (-1 if es[i] else (0 if (xl[i] or xs[i]) else q))
        sig[i] = q
    chg = np.concatenate(([False], sig[1:] != sig[:-1]))
    sl, act, tr = _fractions(p)
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, avg, ext, need_fill = 0, np.nan, np.nan, False
    for i in range(m):
        if need_fill:
            avg, need_fill = ov[i], False
            ext = hv[i] if pos == 1 else lv[i]                 # the fill bar's own extreme; the stop starts next bar
        elif pos == 1:
            stop = ext * (1 - tr) if ext > avg * (1 + act) else avg * (1 - sl)
            if lv[i] <= stop:
                pos = 0
            else:
                ext = max(ext, hv[i])
        elif pos == -1:
            stop = ext * (1 + tr) if ext < avg * (1 - act) else avg * (1 + sl)
            if hv[i] >= stop:
                pos = 0
            else:
                ext = min(ext, lv[i])
        if pos == 0 and i + 1 < m and (el[i] or es[i]):
            if el[i]:
                le[i], pos = True, 1
            else:
                se[i], pos = True, -1
            need_fill = True
        elif pos != 0 and not need_fill and chg[i]:
            if pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, act, tr = _fractions(p)
    return {"sl_stop": sl, "trail": {"type": "percent", "pct": tr, "anchor": "high_low", "activate_after": act}}


def portfolio_kwargs(**params):
    return {}
