"""RSI exits with deep MACD readings, broker days: the RSI 14 crossing over 30 while the MACD is under its signal and under -100 (price units) goes long, crossing under 83 with the MACD above its signal
and above 250 goes short; a 2.5 % stop from the entry; reversing.
Port of FMZ strategy #440551 "基于RSI和MACD指标的交易策略Trading-Strategy-Based-on-RSI-and-MACD-Indicators" (BTC/USDT RSI and MACD Strategy).

FMZ source id: 440551

Source
    https://www.fmz.com/strategy/440551 (PineScript v5, FMZ last modified 2024-01-31 16:07:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-174), RSI 14; MACD 12 / 26 / 9; levels -100 / 250 (price units); stop factor 2.5 %
    enterLong = crossover(rsi, 30) and macd < signal and macd < -100;  enterShort = crossunder(rsi, 83) and macd > signal and macd > 250
    in a trade: strategy.exit(stop = avg price x (1 -/+ 2.5 %)) (named trailing, but fixed at the entry)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the MACD thresholds are price units; the port uses fractions of the close at the BTC
      reading near 42000 (-100 -> -0.00238, 250 -> 0.00595). The stop is a fixed fraction of the entry:
      sl_stop 0.025 (the script sends it from the fill bar on). strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop.
      No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: ADAPT, price-unit MACD levels -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440551_rsi_cross_deep_macd_stop"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.025, 0.05],
    "rsi_period": [14, 7],
}
DEFAULT_PARAMS = {"sl": 0.025, "rsi_period": 14, "lo_frac": -0.00238, "hi_frac": 0.00595}


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
    r = _rsi(c, int(p["rsi_period"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lsig = ((r > 30) & (r.shift(1) <= 30) & (macd < sig) & (macd < float(p["lo_frac"]) * c)).to_numpy()
    ssig = ((r < 83) & (r.shift(1) >= 83) & (macd > sig) & (macd > float(p["hi_frac"]) * c)).to_numpy()
    s_ = float(p["sl"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and lv[i] <= x * (1 - s_):
                pos = 0
            elif pos == -1 and hv[i] >= x * (1 + s_):
                pos = 0
        if i + 1 < m:
            if lsig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i = True, -1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
