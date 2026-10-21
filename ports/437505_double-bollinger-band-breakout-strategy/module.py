"""Double Bollinger breakouts, broker days: with the RSI 14 above 50 and the close above the fast (31) upper band, a close crossing over the slow (45) upper band goes long, the mirror short (reversing); a long closes
when the close falls back under the fast upper band, a short when it rises over the fast lower band; each trade's stop is 1 % beyond the signal bar's low / high.
Port of FMZ strategy #437505 "Double Bollinger Band Breakout Strategy" (Double Bollinger Strategy).

FMZ source id: 437505

Source
    https://www.fmz.com/strategy/437505 (PineScript v4, FMZ last modified 2024-01-03 12:06:31).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 151-285), RSI 14, slow BB 45, fast BB 31 (1 sigma); stop type Strategy Stop with 1 % increment; TP none (StratTP = na); trailing off; strategy close on; direct reverse on; reverse off
    BUY = bar_index > 40 and RSI > 50 and close > upperF and crossover(close, upperS);  SELL mirror;  close long when close < upperF, close short when close > lowerF
    LongStop = valuewhen(bought, low[1], 0) x (1 - 0.01);  ShortStop = valuewhen(bought, high[1], 0) x 1.01;  exit(limit = na, stop = LongStop / ShortStop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the defaults the stop is the "Strategy Stop": 1 % under the low (above the high) of the bar
      before the position changed, i.e. the signal bar, as a distance from the signal close (sl_stop
      fractions), shifted one bar inside stops() and re-based on the fill; the script sets it from the
      fill bar's close, one bar later than the engine applies it (stated). Its take profit is na (no
      target). The other stop types, the trailing switch and the direction filter (all) are off or
      neutral by default and not ported. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: mark coarse_bar_stop. The 100 % of equity size and commission are sizing. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, Bollinger bands; stop beyond the signal bar's extreme.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, commission and the stop inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND434998 (4 members, best partner #438026, Jaccard 0.676); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_437505_double_bollinger_breakout"
FAMILY = "bollinger_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length_slow": [45, 50],
    "length_fast": [31, 20],
}
DEFAULT_PARAMS = {"length_slow": 45, "length_fast": 31, "rsi_len": 14, "perc_increment": 0.01, "warmup": 40}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    ns, nf = int(p["length_slow"]), int(p["length_fast"])
    ms, ds = c.rolling(ns).mean(), c.rolling(ns).std(ddof=0)
    mf, dfv = c.rolling(nf).mean(), c.rolling(nf).std(ddof=0)
    up_s, lo_s, up_f, lo_f = ms + ds, ms - ds, mf + dfv, mf - dfv
    warm = pd.Series(np.arange(len(c)) > int(p["warmup"]), index=c.index)
    buy = warm & (r > 50) & (c > up_f) & (c > up_s) & (c.shift(1) <= up_s.shift(1))
    sell = warm & (r < 50) & (c < lo_f) & (c < lo_s) & (c.shift(1) >= lo_s.shift(1))
    inc = float(p["perc_increment"])
    sl = pd.Series(np.where(buy, (c - lo * (1 - inc)) / c, np.where(sell, (h * (1 + inc) - c) / c, np.nan)),
                   index=c.index)
    return buy, sell, c < up_f, c > lo_f, sl.where(sl > 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, lxc, sxc, _ = _setup(bars_df, p)
    return buy, lxc, sell, sxc


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = _setup(bars_df, p)[4]
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
