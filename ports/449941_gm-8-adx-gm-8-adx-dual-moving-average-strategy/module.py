"""Close crossings of the SMA 15 on the side of the EMA 59 with the script's directional index over 34, daily bars: a cross up above the EMA goes long, a cross down below it goes short; the opposite
crossing closes; reversing.
Port of FMZ strategy #449941 "GM-8-ADX-双均线策略-GM-8-ADX-Dual-Moving-Average-Strategy" (GM-8 and ADX Strategy with Second EMA).

FMZ source id: 449941

Source
    https://www.fmz.com/strategy/449941 (PineScript v5, FMZ last modified 2024-04-30 15:50:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 110-167), SMA 15 ("GM-8"); EMA 59; hand-written ADX 8, threshold 34; lot 0.4
    adx = 100 (plusDI - minusDI) / (plusDI + minusDI) from 8-bar sums (the script's own loop);  crossover(close, sma15) and close > ema59 and adx > 34 -> entry Buy;  crossunder ... -> entry Sell
    crossunder(close, sma15) -> close Buy;  crossover(close, sma15) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "ADX" is the script's loop: sums over bars 1..8 of a true range that uses the next bar's
      close and directional moves measured from bar i to bar i-1, then 100 (DI+ - DI-) / (DI+ + DI-), a
      signed value, as written; so the short entry also needs it over 34. The closes come after the
      entries: a close after a reversing entry leaves the reversal. REVERSAL INTENDED. The lot size is
      sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with an EMA side and a directional filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 0.4 lot stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449941_sma15_cross_ema59_side_signed_dx_reversal"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_threshold": [34.0, 20.0],
    "adx_period": [8, 14],
}
DEFAULT_PARAMS = {"adx_threshold": 34.0, "adx_period": 8, "gm_period": 15, "ema_period": 59}


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


def _script_dx(h, lo, c, n):
    """The script's adx(): sums over i = 1 .. n, with bar i - 1 as the 'next' bar, as written."""
    s_tr = s_p = s_m = 0.0
    for i in range(1, n + 1):
        hi, li = h.shift(i), lo.shift(i)
        hn, ln, cn = h.shift(i - 1), lo.shift(i - 1), c.shift(i - 1)
        trv = np.maximum(np.maximum(hi - li, hi - cn), li - cn)
        up, dn = hi - hn, ln - li
        pdm = up.where((up > dn) & (up > 0), 0.0)
        mdm = dn.where((dn > up) & (dn > 0), 0.0)
        s_tr = s_tr + trv
        s_p = s_p + pdm
        s_m = s_m + mdm
    pdi = s_p / s_tr * 100
    mdi = s_m / s_tr * 100
    tot = pdi + mdi
    return 100 * (pdi - mdi) / tot.where(tot != 0, 1.0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    gm = c.rolling(int(p["gm_period"])).mean()
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    dx = _script_dx(h, lo, c, int(p["adx_period"]))
    xo = (c > gm) & (c.shift(1) <= gm.shift(1))
    xu = (c < gm) & (c.shift(1) >= gm.shift(1))
    strong = dx > float(p["adx_threshold"])
    le = xo & (c > e) & strong
    se = xu & (c < e) & strong
    return le, xu & ~se, se, xo & ~le


def portfolio_kwargs(**params):
    return {}
