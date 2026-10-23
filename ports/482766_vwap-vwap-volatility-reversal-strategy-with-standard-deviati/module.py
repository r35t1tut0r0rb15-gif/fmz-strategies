"""Hourly bars: after a red bar closing under the session VWAP minus one 20-bar deviation and a green bar dipping under that band, a close above the red bar's high while still under the band goes long, with a target at the VWAP and a stop at the red bar's low; a red bar poking over the upper band that closes under the previous bar's low while still above the band goes short, with a target at the lower band and a stop at the previous bar's high; reversing.
Port of FMZ strategy #482766 "VWAP波动反转策略在标准差通道上的多空突破系统-VWAP-Volatility-Reversal-Strategy-with-Standard-Deviation-Channel-Breakout-System" (VRS Strategy).

FMZ source id: 482766

Source
    https://www.fmz.com/strategy/482766 (PineScript v6, FMZ last modified 2025-02-20 09:33:31).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 100-181), session VWAP; bands VWAP +- stdev(close, 20); stored reversal-bar levels; targets VWAP / upper band; stops at bar extremes
    candleReversalCondition = close[1] < lowerBand and close[1] < open[1] and close > open and low < lowerBand -> previousGreenCandleHigh := high[1], previousGreenCandleLow := low[1]
    close > previousGreenCandleHigh and close < lowerBand -> entry Buy, exit(limit = vwap), exit(limit = upperBand), exit(stop = previousGreenCandleLow)
    close < open and high > upperBand and close < low[1] and close > upperBand -> entry Sell, exit(limit = lowerBand), exit(stop = high[1])
    position_size > 0 -> the stored levels := na

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.vwap(close) restarts each session: the house session is the broker day (17:00
      America/New_York). The stored reversal levels survive until a long is open, then are cleared, so a
      long needs a fresh reversal after each trade; the loop follows the bracket hits (on the bars) only
      to know when the strategy is flat. The two long targets are both limits; the VWAP is always the
      nearer one. Every level is fixed on the signal bar: ported as fractions of the fill, exact (1e-6
      floor); a repeated signal while in the same side re-sends the levels (rare; not followed). Pine's
      stdev is the population deviation. The title names ETH; the rules are generic. REVERSAL INTENDED.
      No sizing code. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar levels as fractions of the fill.
    2 generic: PASS, VWAP-band reversal breakouts back toward the VWAP.
    3 crypto-exchange-only: no (exchange pair in the header only (ETH named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482766_vwap_band_reversal_breakout_vwap_target_1h_reversal"
FAMILY = "vwap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "dev_len": [20, 50],
    "dev_mult": [1.0, 1.5],
}
DEFAULT_PARAMS = {"dev_len": 20, "dev_mult": 1.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def _run(bars_df, p):
    o, h, lo, c, v = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close", "volume"))
    cs, vs = bars_df["close"], bars_df["volume"]
    day = broker_day(bars_df.index)
    vw = ((cs * vs).groupby(day).cumsum() / vs.groupby(day).cumsum()).to_numpy(dtype=float)
    sd = (cs.rolling(int(p["dev_len"])).std(ddof=0) * float(p["dev_mult"])).to_numpy(dtype=float)
    up, dn = vw + sd, vw - sd
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lv_sl, lv_tp = np.full(m, np.nan), np.full(m, np.nan)
    gh = gl = np.nan
    pine, st, tg = 0, np.nan, np.nan
    for i in range(1, m):
        held = pine
        if held == 1 and (lo[i] <= st or h[i] >= tg):
            held = 0                       # the bracket is hit: flat at this close
        elif held == -1 and (h[i] >= st or lo[i] <= tg):
            held = 0
        new = held
        if c[i - 1] < dn[i] and c[i - 1] < o[i - 1] and c[i] > o[i] and lo[i] < dn[i]:
            gh, gl = h[i - 1], lo[i - 1]
        if not np.isnan(gh) and c[i] > gh and c[i] < dn[i] and held != 1:
            new, st, tg = 1, gl, vw[i]
            le[i], lv_sl[i], lv_tp[i] = True, gl, vw[i]
        if c[i] < o[i] and h[i] > up[i] and c[i] < lo[i - 1] and c[i] > up[i] and held != -1:
            new, st, tg = -1, h[i - 1], dn[i]
            se[i], lv_sl[i], lv_tp[i] = True, h[i - 1], dn[i]
        if held == 1:                      # position_size > 0 at this close
            gh = gl = np.nan
        pine = new
    return le, se, lv_sl, lv_tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lv_sl, lv_tp = _run(bars_df, p)
    ix = bars_df.index
    o = bars_df["open"]
    lf = pd.Series(le, index=ix).shift(1, fill_value=False)
    sf = pd.Series(se, index=ix).shift(1, fill_value=False)
    sl_p, tp_p = pd.Series(lv_sl, index=ix).shift(1), pd.Series(lv_tp, index=ix).shift(1)
    sl_f = pd.Series(np.nan, index=ix).mask(lf, 1 - sl_p / o).mask(sf, sl_p / o - 1)
    tp_f = pd.Series(np.nan, index=ix).mask(lf, tp_p / o - 1).mask(sf, 1 - tp_p / o)
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
