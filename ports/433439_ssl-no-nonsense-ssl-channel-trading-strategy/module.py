"""SSL channel crosses with an ATR bracket, broker days: the SSL up line crossing above the down line goes long, the
reverse cross goes short (each cross also closes the other side); every trade has a stop 1.5 ATR and a target 1 ATR from
the close, re-issued on every bar.
Port of FMZ strategy #433439 "基于SSL通道指标的趋势跟踪策略No-Nonsense-SSL-Channel-Trading-Strategy" (NNFX Strategy Indicator | jh).

FMZ source id: 433439

Source
    https://www.fmz.com/strategy/433439 (PineScript v3, FMZ last modified 2023-11-27 16:42:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 172-256), SSL 10; ATR 14 (SMA smoothing); SL 1.5 ATR, TP 1 ATR; year > 2009
    Hlv = close > sma(high, 10) ? 1 : close < sma(low, 10) ? -1 : Hlv[1];  sslUp / sslDown from Hlv
    crossover(up, down) -> order L1 long, close S1;  crossover(down, up) -> order S1 short, close L1
    exit(stop = close -/+ 1.5 atr, limit = close +/- 1 atr), recomputed from each bar's close

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.order on these crosses never accumulates: the crosses alternate and each one closes the
      other side, so the net position is long or short, as with strategy.entry.
    * The exits are re-placed every bar around the latest close, so the levels move after entry:
      stops() cannot express that (mark trailing_stop_pending). The port fixes the bracket at the
      signal bar (ATR / close of that bar, ATR = SMA 14 of the true range, shifted one bar, re-based
      on the fill).
    * REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; stops on daily bars: mark
      coarse_bar_stop. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar (approximation stated).
    2 generic: PASS, channel crosses and ATR exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
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

NAME = "fmz_433439_nnfx_ssl_atr_bracket"
FAMILY = "ssl_channel"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.5, 3.0],
    "tp_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"ssl_len": 10, "atr_len": 14, "sl_mult": 1.5, "tp_mult": 1.0}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["ssl_len"])
    sh, sl = h.rolling(n).mean(), lo.rolling(n).mean()
    shv, slv, cv = sh.to_numpy(), sl.to_numpy(), c.to_numpy(dtype=float)
    m = len(cv)
    hlv = np.full(m, np.nan)
    q = np.nan
    for i in range(m):
        if cv[i] > shv[i]:
            q = 1.0
        elif cv[i] < slv[i]:
            q = -1.0
        hlv[i] = q
    s_up = pd.Series(np.where(hlv < 0, slv, shv), index=c.index)
    s_dn = pd.Series(np.where(hlv < 0, shv, slv), index=c.index)
    le = ((s_up > s_dn) & (s_up.shift(1) <= s_dn.shift(1))).astype(bool)
    se = ((s_dn > s_up) & (s_dn.shift(1) <= s_up.shift(1))).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.rolling(int(p["atr_len"])).mean() / c
    return le, se, af


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_mult"])).shift(1), "tp_stop": (af * float(p["tp_mult"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
