"""EMA 21 / 34 spread with RSI extremes and a 2 % trailing stop, broker days: the RSI 14 over 60 with the EMA 21 above the EMA 34 goes long, the RSI under 25 with the EMA 21 under the EMA 34 goes short;
reversing; each trade trails 2 % behind the best price once it is 2 % in profit.
Port of FMZ strategy #438064 "基于多时间框架移动平均线与RSI的趋势跟踪策略Trend-Following-Strategy-Based-on-Multi-Timeframe-Moving-Average-and-RSI" (ATA v4 Strategy).

FMZ source id: 438064

Source
    https://www.fmz.com/strategy/438064 (PineScript v4, FMZ last modified 2024-01-08 16:57:29).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 127-179), source close; fast 21, slow 34; time frames 240 / 60 / 5 (on a 1-day chart); RSI 14 at 60 / 25; trail points and offset 2 % of the close
    ln / md / sh = security(ticker, "240" / "60" / "5", close);  lnma = ema(ln, 21) - ema(ln, 34);  mdma = ema(sh, 21) - ema(md, 34);  shma = ema(sh, 21) - ema(sh, 34)
    "sell" = rsi > 60 and lnma, mdma, shma > 0 -> entry long;  "buy" = rsi < 25 and all < 0 -> entry short;  exit(trail_points = close x 0.02 / mintick, trail_offset = close x 0.02 / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 4-hour, 1-hour and 5-minute closes requested from a daily chart are the day's LAST bar of each
      size (a lower time frame returns its last bar inside the chart bar); counted from the broker day's
      start their close is the broker day's close, so the three spreads are the same EMA 21 - EMA 34 of
      the daily closes. The trail is 2 % of the close in price (the ticks are divided back by the tick
      size): read as the house percent trail, 2 % behind the best price, active after a 2 % gain (anchor
      high_low; the original re-sends it from each bar's close: stated approximation; mark trailing_stop).
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      1-day bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house percent trail.
    2 generic: PASS, EMA spread and RSI levels; percent trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_438064_ema_spread_rsi_pct_trail"
FAMILY = "trend_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [21, 13],
    "trail_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"fast": 21, "trail_pct": 0.02, "slow": 34, "rsi_len": 14, "rsiob": 60.0, "rsios": 25.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    spread = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (r > float(p["rsiob"])) & (spread > 0)
    se = (r < float(p["rsios"])) & (spread < 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t = float(p["trail_pct"])
    return {"trail": {"type": "percent", "pct": t, "anchor": "high_low", "activate_after": t}}


def portfolio_kwargs(**params):
    return {}
