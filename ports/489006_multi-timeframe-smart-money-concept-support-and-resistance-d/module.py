"""EMA 9 / 21 crossings on 2-day bars with the close beyond the 50-bar swing extreme and the last 5- and 15-minute SMA 50s, no close crossing of the SMA 50 and no wide-range bar: the up-cross goes long, the down-cross goes short, each with a 100-pip (3.33 %) target and stop from the signal close; reversing.
Port of FMZ strategy #489006 "Multi Timeframe Smart Money Concept Support and Resistance Dynamic Trading Strategy" (Optimized Trading Strategy v6).

FMZ source id: 489006

Source
    https://www.fmz.com/strategy/489006 (PineScript v6, FMZ last modified 2025-04-01 09:58:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 120-173), EMA 9 / 21; swing 50; security("5" / "15", sma(close, 50)); TR > 1.5 x SMA 20 filter; TP / SL 100 pips (mintick x 100); 10 % of equity
    crossover(ema9, ema21) and close > lowest(low, 50) and not breaker and close > m5 sma50 and close > m15 sma50 and not wide -> entry BUY NOW + exit(limit = close + 100 pip, stop = close - 100 pip);  mirror -> entry SELL NOW

Interpretation choices (Pine rules in SURVEY_README.md)
    * "5" and "15" are lower time frames requested without lookahead: each 2-day bar gets its last
      5- and 15-minute bar's SMA 50 of closes (as #436765), built from minutes in precompute. 100 pips of
      mintick x 100 are 10000 ticks, read as a percent at the header coin's price (ETH about 3000 with tick
      0.01: 100 USD = 3.33 %; C2 ADAPT, as #458242). The bracket is set on the signal bar from its close and
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar late,
      as #458256). A later same-side crossing while held re-sends the bracket; the port keeps the opening
      levels, mark trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark
      coarse_bar_stop. MPL 2.0 source (the notice is kept: Mozilla Public License 2.0, © maechelang). Bars
      are blocks of two broker days (17:00 America/New_York) counted from 1970-01-01, stamped with their
      first minute. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: ADAPT, the pip bracket read as a percent at the header price.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489006_ema9_21_cross_swing_ltf_sma50_filters_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bracket_pct": [3.333, 6.667],
    "swing": [50, 20],
}
DEFAULT_PARAMS = {"bracket_pct": 3.333, "swing": 50, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    days = int(p["days"])
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    for col, f in (("m5", "5min"), ("m15", "15min")):
        q = df["close"].resample(f, label="left", closed="left").last().dropna()
        qk = np.asarray((broker_day(q.index) - pd.Timestamp("1970-01-01")).days // days)
        t = pd.DataFrame({"k": qk, "v": q.rolling(50).mean().to_numpy()})
        last = t.groupby("k").tail(1).set_index("k")["v"]            # each block's last lower-frame bar
        bars[col] = last.reindex(bars.index).to_numpy()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=9, adjust=False).mean()
    s = c.ewm(span=21, adjust=False).mean()
    k = int(p["swing"])
    sma = c.rolling(50).mean()
    breaker = ((c > sma) & (c.shift(1) <= sma.shift(1))) | ((c < sma) & (c.shift(1) >= sma.shift(1)))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    wide = tr > tr.rolling(20).mean() * 1.5
    m5, m15 = bars_df["m5"], bars_df["m15"]
    le = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > lo.rolling(k).min()) & ~breaker
          & (c > m5) & (c > m15) & ~wide)
    se = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < h.rolling(k).max()) & ~breaker
          & (c < m5) & (c < m15) & ~wide)
    q = float(p["bracket_pct"]) / 100
    lvl = {"l_sl": c * (1 - q), "l_tp": c * (1 + q), "s_sl": c * (1 + q), "s_tp": c * (1 - q)}
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
