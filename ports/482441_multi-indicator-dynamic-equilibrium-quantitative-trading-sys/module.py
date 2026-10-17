"""Long when RSI 14 is below 30 with the close under the lower Bollinger band (20, 2), or when EMA 50 is above EMA 200
with MACD above its signal; closed when RSI is above 70 or the close is above the upper band, long only, daily bars.
Port of FMZ strategy #482441 "多指标动态平衡量化交易系统-Multi-Indicator-Dynamic-Equilibrium-Quantitative-Trading-System" (ETH/USDT Multi-Indicator Strategy).

FMZ source id: 482441

Source
    https://www.fmz.com/strategy/482441 (PineScript v5, FMZ last modified 2025-02-18 14:44:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 122-176), RSI 14 (70 / 30), BB 20 / 2, EMA 50 / 200, MACD 12 / 26 / 9
    buy = (rsi < 30 and close < lower) or (ema50 > ema200 and macd > signal) -> entry long
    sell = rsi > 70 or close > upper -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close is written after the entry: it acts on the position held at the bar's start and never undoes an
      entry on that bar (#430850). State machine; exits emitted only on going flat.
    * Long only. Signal module, no stops. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI, Bollinger bands, EMAs and MACD.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 250 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482441_rsi_bb_dip_or_ema_macd_trend_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [2.0, 1.5],
    "ob": [70.0, 80.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "os": 30.0, "ob": 70.0, "bb_len": 20, "bb_mult": 2.0, "ema_fast": 50,
                  "ema_slow": 200}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    buy = (((rsi < p["os"]) & (c < basis - dev)) | ((ef > es) & (macd > sig))).to_numpy()
    sell = ((rsi > p["ob"]) | (c > basis + dev)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i] and pos != 1:
            le[i], pos = True, 1
        if sell[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
