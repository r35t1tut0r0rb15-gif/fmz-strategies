"""Close crossings of SMA 10 of highs plus 1.2 ATR 14 (or SMA 10 of lows minus it) in an EMA 50 / 200 trend, between 02:00 and 14:00 UTC with a 15-bar cooldown, hourly bars: the up-cross goes long, the down-cross goes short, each with a tick bracket read as percents; the break-even step closes the trade at the next open once the bar's extreme is 50 ticks past the close (as written); reversing.
Port of FMZ strategy #483790 "Multi Dimensional Adaptive Trend Following and Risk Management Strategy" (Optimized Target Trend Strategy v2).

FMZ source id: 483790

Source
    https://www.fmz.com/strategy/483790 (PineScript v5, FMZ last modified 2025-02-26 09:54:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-222), trend length 10; ATR 14 x 1.2; EMA 50 / 200 filter on; hours 2-14; cooldown 15 bars; SL 50 ticks (+ ATR buffer); TP 100 ticks; break-even after 50 ticks; 100 % of equity
    crossover(close, sma(high, 10) + 1.2 atr) and close > ema50 > ema200 and 2 <= hour < 14 and cooldown -> entry Long + exit(limit = close + 100 ticks, stop = close - 50 ticks - 1.2 atr)
    crossunder(close, sma(low, 10) - 1.2 atr) and close < ema50 < ema200 and hours and cooldown -> entry Short + mirror
    long and high >= close + 50 ticks -> exit(stop = close + 2 ticks);  short and low <= close - 50 ticks -> exit(stop = close - 2 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour reads the chart exchange's time zone, UTC for the header's Binance pair (the comment's New York
      is not applied): bars opening 02:00-13:59 UTC. The cooldown counts bars since the last signal.
    * Criterion 2: the tick amounts are read on the header's ETH_USDT (tick 0.01, about 3000 USDT) as
      50 ticks = 1.667e-04, 100 ticks = 3.333e-04 and 2 ticks = 6.667e-06 of the price (as #458242 at the
      header's prices). The opening bracket is fixed at the signal close and sent as fractions of the
      fill open (a level at or through it is marketable and closed one bar late, as #458256).
    * As written (intended version owed): the break-even test compares the bar's high with the CURRENT
      close plus 50 ticks and places a sell stop 2 ticks ABOVE that close, which is marketable, so the
      long closes at the next open whenever the bar's high is 50 ticks over its close (mirror for shorts);
      ported as that exit signal.
    * An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver
      D4). The 100 % of equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; tick bracket as fractions of the fill, break-even step as an exit signal.
    2 generic: ADAPT, tick amounts read as fractions at ETH 3000.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: clock window 02:00-14:00 UTC on the bar's open hour (fixed UTC, no DST; the header exchange's time zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483790_sma_high_low_atr_band_cross_trend_utc02_14_cooldown_tick_bracket_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
SESSION_TZ = "UTC"  # hour reads the chart exchange's zone: UTC for the header's Binance pair

GRID = {
    "length": [10, 20],
    "cooldown_bars": [15, 30],
}
DEFAULT_PARAMS = {"length": 10, "cooldown_bars": 15, "atr_mult": 1.2, "sl_frac": 1.667e-04, "tp_frac": 3.333e-04,
                  "be_frac": 1.667e-04, "be_buffer": 6.667e-06, "start_hour": 2, "end_hour": 14}


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
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    av = _rma(tr, 14) * float(p["atr_mult"])
    n = int(p["length"])
    up_l, dn_l = h.rolling(n).mean() + av, lo.rolling(n).mean() - av
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    hr = np.asarray(bars_df.index.tz_convert(SESSION_TZ).hour)
    t_ok = (hr >= int(p["start_hour"])) & (hr < int(p["end_hour"]))
    raw_l = ((c > up_l) & (c.shift(1) <= up_l.shift(1)) & (c > e50) & (e50 > e200)).to_numpy() & t_ok
    raw_s = ((c < dn_l) & (c.shift(1) >= dn_l.shift(1)) & (c < e50) & (e50 < e200)).to_numpy() & t_ok
    m = len(raw_l)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last = None
    cd = int(p["cooldown_bars"])
    for i in range(m):
        can = last is None or (i - last) > cd
        if raw_l[i] and can:
            le[i], last = True, i
        if raw_s[i] and can:
            se[i], last = True, i
    idx = c.index
    le, se = pd.Series(le, index=idx), pd.Series(se, index=idx)
    a, b = float(p["sl_frac"]), float(p["tp_frac"])
    lvl = {"l_sl": c * (1 - a) - av, "l_tp": c * (1 + b), "s_sl": c * (1 + a) + av, "s_tp": c * (1 - b)}
    be = float(p["be_frac"])
    lbe = h >= c * (1 + be)
    sbe = lo <= c * (1 - be)
    return le & ~se, se, lbe, sbe, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lbe, sbe, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    lx = (lf & l_thr) | lbe                    # the marketable break-even stop: next open
    sx = (sf & s_thr) | sbe
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
