"""Broker days: a weighted "sentiment" of where the close sits in ten Fibonacci-length expected ranges (1 .. 89 bars) builds running long / short deltas; once the sentiment has crossed zero after 89 bars, the short delta beating 0.7 x the 89-bar peak of the long delta goes long and the mirror (0.68) goes short; a 53 % run-up from the entry closes, a 7 % stop; after a target the same side waits for an opposite signal; reversing.
Port of FMZ strategy #436248 "基于情绪的XBT期货交易策略Sentiment-Based-XBT-Futures-Trading-Strategy" (expected range STRATEGY (Jomy)).

FMZ source id: 436248

Source
    https://www.fmz.com/strategy/436248 (PineScript v4, FMZ last modified 2023-12-22 14:48:44).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 171-389), leverage 1; TP 53 %; SL 7 %; levels 0.70 / 0.68; weights 1.158 .. 2.832 for ranges 1, 2, 3, 5, 8, 13, 21, 34, 55, 89
    place_k = ((close - l_k) / (h_k - l_k) - 0.5) x -100 with h_k / l_k = sma(ohlc4, k)[1] +- range_k[1] / 2;  sentiment = sum(place_k / k' x range_k x w_k) / sum(w) (k' the reversed length)
    deltalong := sentiment > 0 ? deltalong[1] + change(sentiment) : 0;  long = deltashort > highest(deltalong, 89) x 0.7 and o == 1 -> entry Long1 (stoptrade == 0)
    closelong = (highest high since entry / close at the fill bar - 1) > 53 % -> close;  exit("Long1", stop = fill-bar close x 0.93);  stoptrade blocks the side after a target until an opposite signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * The sentiment is in price units (ranges times positions) but every test compares it with its own
      running peaks, so the units cancel. "n" counts bars (volume > -1 is always true): volume is not used.
      The stop is the script's "longstart x 0.93", anchored on the fill bar's close and sent from the next
      bar; the port uses 7 % (shorts 1 / 0.93 - 1 = 7.53 %) of the fill price (mark trailing_stop_pending).
      The 53 % target is a bar-close test on the highest high since the entry (the bar before the fill
      included), exiting at the next open, in the signals. The script's own stop and target state is
      followed in the signals. The header says 1d; the comment names a 2h XBTUSD chart (the header is
      used). REVERSAL INTENDED. The leverage-based contracts are sizing. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent stop from the fill; run-up target in the signals.
    2 generic: PASS, expected-range sentiment delta peaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity / close x leverage (1), not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_436248_expected_range_sentiment_delta_peak_reversal"
FAMILY = "sentiment_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "level": [0.70, 0.50],
    "tp": [53.0, 20.0],
}
DEFAULT_PARAMS = {"level": 0.70, "level_short": 0.68, "tp": 53.0, "sl": 7.0}
_LENS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89)
_W = (1.158, 1.119, 1.153, 1.272, 1.295, 1.523, 1.588, 2.100, 1.816, 2.832)


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


def _signals(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    o4 = (o + h + lo + c) / 4
    tot = 0.0
    for k, w, kd in zip(_LENS, _W, reversed(_LENS)):
        r = h.rolling(k).max() - lo.rolling(k).min()
        a = o4.rolling(k).mean()
        hk, lk = a.shift(1) + r.shift(1) / 2, a.shift(1) - r.shift(1) / 2
        place = ((c - lk) / (hk - lk).where(hk != lk) - 0.5) * -100
        tot = tot + place / kd * r * w
    sent = (tot / sum(_W)).to_numpy()
    m = len(sent)
    dl, ds = np.zeros(m), np.zeros(m)
    pdl = pds = np.nan
    for i in range(m):
        s1 = sent[i - 1] if i else np.nan
        dl[i] = ((0.0 if np.isnan(pdl) else pdl) + sent[i] - s1) if sent[i] > 0 else 0.0
        ds[i] = ((0.0 if np.isnan(pds) else pds) + (sent[i] - s1) * -1) if sent[i] < 0 else 0.0
        pdl, pds = dl[i], ds[i]
    dls, dss = pd.Series(dl, index=c.index), pd.Series(ds, index=c.index)
    pk_l = dls.rolling(89).max() * float(p["level"])            # peakfindlong
    pk_s = dss.rolling(89).max() * float(p["level_short"])      # peakfindshort
    ss = pd.Series(sent, index=c.index)
    crossed = (((ss > 0) & (ss.shift(1) <= 0)) | ((ss < 0) & (ss.shift(1) >= 0))).to_numpy()
    om = np.zeros(m, dtype=bool)
    q = False
    for i in range(m):
        if crossed[i] and (i + 1) > 89:
            q = True
        om[i] = q
    long_c = (dss > pk_l).to_numpy() & om
    short_c = (dls > pk_s).to_numpy() & om
    return long_c, short_c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c = _signals(bars_df, p)
    ov, hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    tp, sl = float(p["tp"]), float(p["sl"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, avg, start_c, hsl, lss, st = 0, 0, np.nan, np.nan, 0.0, 1e7, 0
    for i in range(m):
        if pend != 0:
            pos, avg, start_c, pend = pend, ov[i], cv[i], 0       # filled at this open; longstart = this close
        if pos == 1 and lv[i] <= avg * (1 - sl):
            pos = 0                                                # the stop (house level from the fill)
        elif pos == -1 and hv[i] >= avg / (1 - sl):
            pos = 0
        hp = hv[i - 1] if i else np.nan
        lp = lv[i - 1] if i else np.nan
        hsl = max(hsl, hv[i], hp if not np.isnan(hp) else hv[i]) if pos == 1 else 0.0
        lss = min(lss, lv[i], lp if not np.isnan(lp) else lv[i]) if pos == -1 else 1e7
        c_long = pos == 1 and (hsl / start_c - 1) * 100 > tp
        c_short = pos == -1 and (start_c / lss - 1) * 100 > tp
        st_prev = st
        st = 1 if c_long else st_prev
        if short_c[i] and st_prev == 1:
            st = 0
        if c_short:
            st = -1
        if long_c[i] and st_prev == -1:
            st = 0
        entered = False
        if long_c[i] and st == 0 and pos != 1 and i + 1 < m:
            le[i], pend, entered = True, 1, True
        if c_long and not entered:
            lx[i], pos = True, 0
        if short_c[i] and st == 0 and pos != -1 and pend != -1 and i + 1 < m:
            se[i], le[i], lx[i], pend, entered = True, False, False, -1, True
        if c_short and not entered:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    sl = float(p["sl"]) / 100
    short_fill = se.shift(1, fill_value=False).to_numpy()
    sl_f = np.where(short_fill, 1 / (1 - sl) - 1, sl)
    return {"sl_stop": pd.Series(sl_f, index=bars_df.index)}


def portfolio_kwargs(**params):
    return {}
