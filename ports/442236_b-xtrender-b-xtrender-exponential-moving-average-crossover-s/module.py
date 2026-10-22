"""B-Xtrender short- and long-term agreement with an EMA 200 filter and a 20 % trailing stop on closes, broker days: both Xtrenders above zero with the close above the EMA 200 goes long, both below zero
under it short; either turning against the position closes it; reversing.
Port of FMZ strategy #442236 "指数均线交叉B-Xtrender策略B-Xtrender-Exponential-Moving-Average-Crossover-Strategy" (B-Xtrender [Backtest Edition] @QuantTherapy).

FMZ source id: 442236

Source
    https://www.fmz.com/strategy/442236 (PineScript v4, FMZ last modified 2024-02-20 14:45:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-183), short 5 / 20 / 15, long 20 / 15; MA filter on, EMA 200; trailing stop 20 %
    short = rsi(ema(close, 5) - ema(close, 20), 15) - 50;  long = rsi(ema(close, 20), 15) - 50;  long > 0 and short > 0 and close > ema200 -> entry Long;  either < 0 -> close Long;  short side mirrored
    longStopPrice = max(close - 20 % close, longStopPrice[1]) while long (shorts min(close + 20 %, ..));  strategy.exit(stop = ..) while open

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop ratchets on the bar close, 20 % from it: a percent trailing stop on closes, the house trail
      {"type": "percent", "pct": 0.2, "anchor": "close"} (its best close runs to the previous minute;
      stated approximation, mark trailing_stop). The conditions are levels: after a stop exit the entry
      fires again while it still holds. A close written after a reversing entry leaves the reversal
      standing (as #438020). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily
      bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: PASS, Xtrender agreement, EMA filter and percent trail.
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

NAME = "fmz_442236_b_xtrender_agreement_ema200_pct_trail"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_len": [200, 100],
    "trail_pct": [0.2, 0.1],
}
DEFAULT_PARAMS = {"ma_len": 200, "trail_pct": 0.2, "s1": 5, "s2": 20, "s3": 15, "l1": 20, "l2": 15}


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
    sx_ = _rsi(c.ewm(span=int(p["s1"]), adjust=False).mean() - c.ewm(span=int(p["s2"]), adjust=False).mean(),
               int(p["s3"])) - 50
    lx_ = _rsi(c.ewm(span=int(p["l1"]), adjust=False).mean(), int(p["l2"])) - 50
    ma = c.ewm(span=int(p["ma_len"]), adjust=False).mean()
    long_ = (sx_ > 0) & (lx_ > 0) & (c > ma)
    short_ = (sx_ < 0) & (lx_ < 0) & (c < ma)
    close_l = (sx_ < 0) | (lx_ < 0)
    close_s = (sx_ > 0) | (lx_ > 0)
    return long_, close_l & ~short_, short_, close_s & ~long_


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "close"}}


def portfolio_kwargs(**params):
    return {}
