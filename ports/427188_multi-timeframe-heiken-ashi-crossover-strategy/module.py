"""Heikin-Ashi on three timeframes, long by default: a long opens when the daily, weekly and monthly
Heikin-Ashi candles are all bullish (close above open) and closes when any of them turns bearish;
with shorts on, the mirror.
Port of FMZ strategy #427188 "Multi-Timeframe Heiken Ashi Crossover Strategy".

FMZ source id: 427188

Source
    https://www.fmz.com/strategy/427188 (PineScript v4, FMZ last modified 2023-09-18 21:50:05).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 148-188), TM 'D', 'W', 'M', longs on, shorts off
    ha_diff_X = HA open - HA close of security(heikinashi(ticker), X, ...): > 0 -> 1 (bearish), < 0 -> 2 (bullish)
    long = all three == 2; exitlong = any == 1; short = all three == 1; exitshort = any == 2

Interpretation choices (Pine rules in SURVEY_README.md, skill section 4)
    * Bars are broker days (session ends 17:00 America/New_York; `broker_day(index)` below, bound by
      the desktop to registry_schema.broker_day), each stamped with its session's first minute.
    * 'D' on the daily chart is the current bar's own Heikin-Ashi candle (complete at its close).
    * 'W' and 'M' (v4: lookahead_off, so on history only completed higher bars are seen): the
      Heikin-Ashi candle of the last COMPLETED broker week (ISO week of the broker-day date) and
      broker month. House rule: a higher bar counts as completed from the first daily bar of the
      next week / month (TradingView shows it one daily bar earlier, on the period's last bar,
      which needs the calendar to know the period is ending).
    * Heikin-Ashi: close = (o + h + l + c) / 4; open = (open[1] + close[1]) / 2, seeded with
      (o + c) / 2 on the first bar of each series (Pine).
    * Inputs: defaults are used (longs on, shorts off). The backtest header's args set
      v_input_5 (shorts) true; the grid tries both (`short_on`).
    * With shorts on, entries reverse (REVERSAL INTENDED); long only by default.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; higher timeframes only after they complete.
    2 generic: PASS, candle colours only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED (with shorts on); long only by default.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427188_heikin_ashi_d_w_m"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_on": [False, True],
}
DEFAULT_PARAMS = {"short_on": False}


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


def _ha(o, h, l, c):
    hc = (o + h + l + c) / 4
    ho = np.empty(len(hc))
    for i in range(len(hc)):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 else (ho[i - 1] + hc[i - 1]) / 2
    return ho, hc


def _ha_state(ho, hc):
    d = ho - hc
    return np.where(d > 0, 1, np.where(d < 0, 2, 3))


def _completed_higher(bars, key):
    """HA state of the last completed higher period (week / month) for each daily bar; 0 if none yet."""
    k = key.to_numpy()
    grp = pd.DataFrame({"k": k, "o": bars["open"].to_numpy(), "h": bars["high"].to_numpy(),
                        "l": bars["low"].to_numpy(), "c": bars["close"].to_numpy()})
    agg = grp.groupby("k", sort=True).agg(o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"))
    ho, hc = _ha(*(agg[x].to_numpy(dtype=float) for x in ("o", "h", "l", "c")))
    state = _ha_state(ho, hc)
    pos_of = {key_: j for j, key_ in enumerate(agg.index)}
    out = np.zeros(len(k), dtype=np.int64)
    for i, key_ in enumerate(k):
        j = pos_of[key_] - 1               # the previous (completed) period
        out[i] = state[j] if j >= 0 else 0
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, l, c = (bars_df[x].to_numpy(dtype=float) for x in ("open", "high", "low", "close"))
    d_state = _ha_state(*_ha(o, h, l, c))
    bday = broker_day(bars_df.index)
    iso = bday.isocalendar()
    week_key = pd.Series(iso["year"].to_numpy() * 100 + iso["week"].to_numpy(), index=bars_df.index)
    month_key = pd.Series(bday.year * 100 + bday.month, index=bars_df.index)
    w_state = _completed_higher(bars_df, week_key)
    m_state = _completed_higher(bars_df, month_key)
    long_c = (d_state == 2) & (w_state == 2) & (m_state == 2)
    long_x = (d_state == 1) | (w_state == 1) | (m_state == 1)
    short_c = (d_state == 1) & (w_state == 1) & (m_state == 1)
    short_x = (d_state == 2) | (w_state == 2) | (m_state == 2)
    shorts = bool(p["short_on"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif shorts and short_c[i] and pos != -1:
            pos = -1
        elif pos == 1 and long_x[i]:
            pos = 0
        elif pos == -1 and short_x[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
