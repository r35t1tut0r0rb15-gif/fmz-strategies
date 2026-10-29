"""Tests for fmz_catalog/extra_tv.py.

Each indicator is checked against a literal bar-by-bar Python port of the
TradingView Pine source it reproduces (pine-facade ids in extra_tv's
docstring). Pine primitives already tested in tv_indicators (ta.sma,
ta.ema, ta.rsi) are reused as building blocks.
"""

import math

import numpy as np
import pandas as pd
import pytest

import fmz_catalog.extra_tv as xt
import tv_indicators as ti
from tv_indicators.tests.test_indicators import D, H, L, C, O, N, c, h, l, o, same

NA = float("nan")


def isna(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def at(series, i, back=0):
    """``series[back]`` evaluated on bar ``i``: na before bar 0."""
    j = i - back
    return series[j] if j >= 0 else NA


def bat(series, i, back=0):
    """History of a Pine v6 bool: false before bar 0."""
    j = i - back
    return bool(series[j]) if j >= 0 else False


def _gappy(seed=11, n=3000):
    """Candles with gaps, dojis and marubozus, so rare patterns fire."""
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.012, n)))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.008, n))
    doji = rng.random(n) < 0.15
    close[doji] = open_[doji] * (1 + rng.normal(0, 0.0002, doji.sum()))
    wick = np.abs(rng.normal(0, 0.004, (2, n)))
    high = np.maximum(open_, close) * (1 + wick[0])
    low = np.minimum(open_, close) * (1 - wick[1])
    maru = rng.random(n) < 0.1
    high[maru] = np.maximum(open_, close)[maru]
    low[maru] = np.minimum(open_, close)[maru]
    idx = pd.date_range("2023-01-01", periods=n, freq="h")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close}, index=idx)


G = _gappy()


# ---------------------------------------------------------------------------
# ta.pivothigh / ta.pivotlow
# ---------------------------------------------------------------------------

def port_pivot(src, left, right, is_high, strict=False):
    """ta.pivothigh/pivotlow with the TradingView/ZigZag/9 tie rule."""
    out = []
    for i in range(len(src)):
        res = NA
        if i >= left + right:
            p = src[i - right]
            window = [src[i - right - j] for j in range(1, left + 1)] + \
                     [src[i - right + j] for j in range(1, right + 1)]
            if not isna(p) and not any(isna(v) for v in window):
                if is_high:
                    ok = all(src[i - right - j] < p for j in range(1, left + 1)) and \
                        all((src[i - right + j] < p) if strict else (src[i - right + j] <= p)
                            for j in range(1, right + 1))
                else:
                    ok = all(src[i - right - j] > p for j in range(1, left + 1)) and \
                        all((src[i - right + j] > p) if strict else (src[i - right + j] >= p)
                            for j in range(1, right + 1))
                if ok:
                    res = p
        out.append(res)
    return np.array(out)


@pytest.mark.parametrize("left,right", [(10, 10), (5, 5), (4, 2), (2, 1), (1, 3)])
def test_pivots_match_port(left, right):
    ph = xt.pivothigh(H, left, right)
    pl = xt.pivotlow(L, left, right)
    exp_h = port_pivot(h, left, right, True)
    exp_l = port_pivot(l, left, right, False)
    same(ph.pivot, exp_h)
    same(pl.pivot, exp_l)
    np.testing.assert_array_equal(ph.found.to_numpy(), ~np.isnan(exp_h))
    np.testing.assert_array_equal(pl.found.to_numpy(), ~np.isnan(exp_l))
    assert ph.found.sum() > 10 and pl.found.sum() > 10


def test_pivot_ties_rounded_prices():
    # Round to create many ties, then compare with the port (both strict modes).
    src = np.round(c, 0)
    for strict in (False, True):
        same(xt.pivothigh(src, 3, 3, strict=strict).pivot, port_pivot(src, 3, 3, True, strict))
        same(xt.pivotlow(src, 3, 3, strict=strict).pivot, port_pivot(src, 3, 3, False, strict))


def test_pivot_tie_rule_explicit():
    x = np.array([1, 2, 3, 3, 2, 1, 1, 0, 1, 2], float)
    r = xt.pivothigh(x, 2, 2)
    # flat top at bars 2 and 3: the earliest one (bar 2) is the pivot,
    # confirmed on bar 4; bar 3 fails because bar 2 (left) is equal.
    assert list(np.flatnonzero(r.found)) == [4]
    assert r.pivot[4] == 3
    assert not xt.pivothigh(x, 2, 2, strict=True).found.any()
    # pivot low with equal bars to the right: bar 7 (0) is a pivot, bar 5/6 tie
    lo = xt.pivotlow(x, 2, 2)
    assert list(np.flatnonzero(lo.found)) == [9]
    x2 = np.array([3, 2, 1, 1, 2, 3], float)
    assert list(np.flatnonzero(xt.pivotlow(x2, 2, 2).found)) == [4]   # bar 2, not bar 3
    # NaN in the window -> no pivot
    x3 = np.array([1, np.nan, 3, 2, 1], float)
    assert not xt.pivothigh(x3, 2, 2).found.any()


def test_pivot_dataframe_columns():
    df = pd.DataFrame({"a": h, "b": l[::-1].copy()})
    r = xt.pivothigh(df, 5, 5)
    same(r.pivot["b"], port_pivot(df["b"].to_numpy(), 5, 5, True))


# ---------------------------------------------------------------------------
# RSI divergence indicator (STD;Divergence%1Indicator)
# ---------------------------------------------------------------------------

def pine_barssince(cond):
    out, last = [], None
    for i, x in enumerate(cond):
        if x:
            last = i
        out.append(NA if last is None else i - last)
    return out


def pine_valuewhen(cond, src, occ):
    out, hist = [], []
    for i, x in enumerate(cond):
        if x:
            hist.insert(0, src[i])
        out.append(hist[occ] if len(hist) > occ else NA)
    return out


def port_divergence(osc, high, low, lbL=5, lbR=5, rangeUpper=60, rangeLower=5):
    n = len(osc)
    plFound = [not isna(v) for v in port_pivot(osc, lbL, lbR, False)]
    phFound = [not isna(v) for v in port_pivot(osc, lbL, lbR, True)]

    def _inRange(cond):
        bars = pine_barssince([x is True for x in cond])
        return [(not isna(b)) and rangeLower <= b and b <= rangeUpper for b in bars]

    osc_lbR = [at(osc, i, lbR) for i in range(n)]
    low_lbR = [at(low, i, lbR) for i in range(n)]
    high_lbR = [at(high, i, lbR) for i in range(n)]
    inRangePl = _inRange([bat(plFound, i, 1) for i in range(n)])
    inRangePh = _inRange([bat(phFound, i, 1) for i in range(n)])
    vw_pl_osc = pine_valuewhen(plFound, osc_lbR, 1)
    vw_pl_low = pine_valuewhen(plFound, low_lbR, 1)
    vw_ph_osc = pine_valuewhen(phFound, osc_lbR, 1)
    vw_ph_high = pine_valuewhen(phFound, high_lbR, 1)
    bull, hbull, bear, hbear = [], [], [], []
    for i in range(n):
        oscHL = osc_lbR[i] > vw_pl_osc[i] and inRangePl[i]
        priceLL = low_lbR[i] < vw_pl_low[i]
        bull.append(priceLL and oscHL and plFound[i])
        oscLL = osc_lbR[i] < vw_pl_osc[i] and inRangePl[i]
        priceHL = low_lbR[i] > vw_pl_low[i]
        hbull.append(priceHL and oscLL and plFound[i])
        oscLH = osc_lbR[i] < vw_ph_osc[i] and inRangePh[i]
        priceHH = high_lbR[i] > vw_ph_high[i]
        bear.append(priceHH and oscLH and phFound[i])
        oscHH = osc_lbR[i] > vw_ph_osc[i] and inRangePh[i]
        priceLH = high_lbR[i] < vw_ph_high[i]
        hbear.append(priceLH and oscHH and phFound[i])
    return [np.array(x, bool) for x in (bull, hbull, bear, hbear, plFound, phFound)]


@pytest.mark.parametrize("params", [dict(), dict(lbL=3, lbR=2, rangeUpper=30, rangeLower=2)])
def test_rsi_divergence_matches_port(params):
    osc = ti.rsi(C, 14).to_numpy()
    exp = port_divergence(osc, h, l, **params)
    kw = {}
    if params:
        kw = dict(lookback_left=params["lbL"], lookback_right=params["lbR"],
                  range_upper=params["rangeUpper"], range_lower=params["rangeLower"])
    got = xt.rsi_divergence(C, H, L, **kw)
    got2 = xt.divergence(ti.rsi(C, 14), H, L, **kw)
    for g, g2, e in zip(got, got2, exp):
        np.testing.assert_array_equal(g.to_numpy(), e)
        np.testing.assert_array_equal(g2.to_numpy(), e)
    assert all(x.sum() > 0 for x in exp[:4])


def test_divergence_with_macd():
    m = ti.macd(C).macd.to_numpy()
    exp = port_divergence(m, h, l)
    got = xt.divergence(m, h, l)
    for g, e in zip(got, exp):
        np.testing.assert_array_equal(g, e)


# ---------------------------------------------------------------------------
# Candlestick patterns (STD;Candlestick%1Pattern%1All%1Candlestick%1Patterns)
# ---------------------------------------------------------------------------

def port_candles(o, h, l, c, trendRule="SMA50"):
    n = len(c)
    close_s = pd.Series(c)
    if trendRule == "SMA50":
        priceAvg = ti.sma(close_s, 50).to_numpy()
        DT = [c[i] < priceAvg[i] for i in range(n)]
        UT = [c[i] > priceAvg[i] for i in range(n)]
    elif trendRule == "SMA50, SMA200":
        sma200 = ti.sma(close_s, 200).to_numpy()
        sma50 = ti.sma(close_s, 50).to_numpy()
        DT = [c[i] < sma50[i] and sma50[i] < sma200[i] for i in range(n)]
        UT = [c[i] > sma50[i] and sma50[i] > sma200[i] for i in range(n)]
    else:
        DT = [True] * n
        UT = [True] * n
    C_Len, C_ShadowPercent, C_ShadowEqualsPercent, C_DojiBodyPercent, C_Factor = 14, 5.0, 100.0, 5.0, 2.0
    BodyHi = [max(c[i], o[i]) for i in range(n)]
    BodyLo = [min(c[i], o[i]) for i in range(n)]
    Body = [BodyHi[i] - BodyLo[i] for i in range(n)]
    BodyAvg = ti.ema(pd.Series(Body), C_Len).to_numpy()
    SmallBody = [Body[i] < BodyAvg[i] for i in range(n)]
    LongBody = [Body[i] > BodyAvg[i] for i in range(n)]
    UpShadow = [h[i] - BodyHi[i] for i in range(n)]
    DnShadow = [BodyLo[i] - l[i] for i in range(n)]
    HasUpShadow = [UpShadow[i] > C_ShadowPercent / 100 * Body[i] for i in range(n)]
    HasDnShadow = [DnShadow[i] > C_ShadowPercent / 100 * Body[i] for i in range(n)]
    White = [o[i] < c[i] for i in range(n)]
    Black = [o[i] > c[i] for i in range(n)]
    Range = [h[i] - l[i] for i in range(n)]
    BodyMiddle = [Body[i] / 2 + BodyLo[i] for i in range(n)]

    def pdiv(a, b):
        return NA if b == 0 else a / b

    ShadowEquals = [UpShadow[i] == DnShadow[i] or
                    (pdiv(abs(UpShadow[i] - DnShadow[i]), DnShadow[i]) * 100 < C_ShadowEqualsPercent and
                     pdiv(abs(DnShadow[i] - UpShadow[i]), UpShadow[i]) * 100 < C_ShadowEqualsPercent)
                    for i in range(n)]
    IsDojiBody = [Range[i] > 0 and Body[i] <= Range[i] * C_DojiBodyPercent / 100 for i in range(n)]
    Doji = [IsDojiBody[i] and ShadowEquals[i] for i in range(n)]
    hl2 = [(h[i] + l[i]) / 2 for i in range(n)]
    Marubozu = [LongBody[i] and UpShadow[i] <= 5.0 / 100 * Body[i] and DnShadow[i] <= 5.0 / 100 * Body[i]
                for i in range(n)]
    HaveNotUp = [Range[i] * 5.0 / 100 > UpShadow[i] for i in range(n)]
    HaveNotDn = [Range[i] * 5.0 / 100 > DnShadow[i] for i in range(n)]
    GapUp = [at(BodyHi, i, 1) < BodyLo[i] for i in range(n)]
    GapDn = [at(BodyLo, i, 1) > BodyHi[i] for i in range(n)]

    res = {k: [] for k in xt._CANDLE_OUTPUTS}
    for i in range(n):
        def F(s, b=0):
            return at(s, i, b)

        def B(s, b=0):
            return bat(s, i, b)

        open_, high, low, close = o[i], h[i], l[i], c[i]
        r = {}
        r["on_neck_bear"] = (B(DT) and B(Black, 1) and B(LongBody, 1) and B(White) and open_ < F(c, 1)
                             and B(SmallBody) and Range[i] != 0 and abs(close - F(l, 1)) <= BodyAvg[i] * 0.05)
        r["rising_window_bull"] = B(UT, 1) and (Range[i] != 0 and F(Range, 1) != 0) and low > F(h, 1)
        r["falling_window_bear"] = B(DT, 1) and (Range[i] != 0 and F(Range, 1) != 0) and high < F(l, 1)
        r["falling_three_methods_bear"] = (
            B(DT, 4) and (B(LongBody, 4) and B(Black, 4))
            and (B(SmallBody, 3) and B(White, 3) and F(o, 3) > F(l, 4) and F(c, 3) < F(h, 4))
            and (B(SmallBody, 2) and B(White, 2) and F(o, 2) > F(l, 4) and F(c, 2) < F(h, 4))
            and (B(SmallBody, 1) and B(White, 1) and F(o, 1) > F(l, 4) and F(c, 1) < F(h, 4))
            and (B(LongBody) and B(Black) and close < F(c, 4)))
        r["rising_three_methods_bull"] = (
            B(UT, 4) and (B(LongBody, 4) and B(White, 4))
            and (B(SmallBody, 3) and B(Black, 3) and F(o, 3) < F(h, 4) and F(c, 3) > F(l, 4))
            and (B(SmallBody, 2) and B(Black, 2) and F(o, 2) < F(h, 4) and F(c, 2) > F(l, 4))
            and (B(SmallBody, 1) and B(Black, 1) and F(o, 1) < F(h, 4) and F(c, 1) > F(l, 4))
            and (B(LongBody) and B(White) and close > F(c, 4)))
        r["tweezer_top_bear"] = (B(UT, 1) and (not B(IsDojiBody) or (B(HasUpShadow) and B(HasDnShadow)))
                                 and abs(high - F(h, 1)) <= BodyAvg[i] * 0.05 and B(White, 1) and B(Black)
                                 and B(LongBody, 1))
        r["tweezer_bottom_bull"] = (B(DT, 1) and (not B(IsDojiBody) or (B(HasUpShadow) and B(HasDnShadow)))
                                    and abs(low - F(l, 1)) <= BodyAvg[i] * 0.05 and B(Black, 1) and B(White)
                                    and B(LongBody, 1))
        r["dark_cloud_cover_bear"] = ((B(UT, 1) and B(White, 1) and B(LongBody, 1))
                                      and (B(Black) and open_ >= F(h, 1) and close < F(BodyMiddle, 1)
                                           and close > F(o, 1)))
        r["downside_tasuki_gap_bear"] = (B(LongBody, 2) and B(SmallBody, 1) and B(DT) and B(Black, 2)
                                         and F(BodyHi, 1) < F(BodyLo, 2) and B(Black, 1) and B(White)
                                         and BodyHi[i] <= F(BodyLo, 2) and BodyHi[i] >= F(BodyHi, 1))
        r["upside_tasuki_gap_bull"] = (B(LongBody, 2) and B(SmallBody, 1) and B(UT) and B(White, 2)
                                       and F(BodyLo, 1) > F(BodyHi, 2) and B(White, 1) and B(Black)
                                       and BodyLo[i] >= F(BodyHi, 2) and BodyLo[i] <= F(BodyLo, 1))
        r["evening_doji_star_bear"] = (B(LongBody, 2) and B(IsDojiBody, 1) and B(LongBody) and B(UT)
                                       and B(White, 2) and F(BodyLo, 1) > F(BodyHi, 2) and B(Black)
                                       and BodyLo[i] <= F(BodyMiddle, 2) and BodyLo[i] > F(BodyLo, 2)
                                       and F(BodyLo, 1) > BodyHi[i])
        r["doji_star_bear"] = (B(UT) and B(White, 1) and B(LongBody, 1) and B(IsDojiBody)
                               and BodyLo[i] > F(BodyHi, 1))
        r["doji_star_bull"] = (B(DT) and B(Black, 1) and B(LongBody, 1) and B(IsDojiBody)
                               and BodyHi[i] < F(BodyLo, 1))
        r["morning_doji_star_bull"] = (B(LongBody, 2) and B(IsDojiBody, 1) and B(LongBody) and B(DT)
                                       and B(Black, 2) and F(BodyHi, 1) < F(BodyLo, 2) and B(White)
                                       and BodyHi[i] >= F(BodyMiddle, 2) and BodyHi[i] < F(BodyHi, 2)
                                       and F(BodyHi, 1) < BodyLo[i])
        r["piercing_bull"] = ((B(DT, 1) and B(Black, 1) and B(LongBody, 1))
                              and (B(White) and open_ <= F(l, 1) and close > F(BodyMiddle, 1) and close < F(o, 1)))
        hammer_shape = (B(SmallBody) and Body[i] > 0 and BodyLo[i] > hl2[i]
                        and DnShadow[i] >= C_Factor * Body[i] and not B(HasUpShadow))
        star_shape = (B(SmallBody) and Body[i] > 0 and BodyHi[i] < hl2[i]
                      and UpShadow[i] >= C_Factor * Body[i] and not B(HasDnShadow))
        r["hammer_bull"] = hammer_shape and B(DT)
        r["hanging_man_bear"] = hammer_shape and B(UT)
        r["shooting_star_bear"] = star_shape and B(UT)
        r["inverted_hammer_bull"] = star_shape and B(DT)
        star3 = B(LongBody, 2) and B(SmallBody, 1) and B(LongBody)
        r["morning_star_bull"] = star3 and (B(DT) and B(Black, 2) and F(BodyHi, 1) < F(BodyLo, 2) and B(White)
                                            and BodyHi[i] >= F(BodyMiddle, 2) and BodyHi[i] < F(BodyHi, 2)
                                            and F(BodyHi, 1) < BodyLo[i])
        r["evening_star_bear"] = star3 and (B(UT) and B(White, 2) and F(BodyLo, 1) > F(BodyHi, 2) and B(Black)
                                            and BodyLo[i] <= F(BodyMiddle, 2) and BodyLo[i] > F(BodyLo, 2)
                                            and F(BodyLo, 1) > BodyHi[i])
        r["marubozu_white_bull"] = (B(White) and B(LongBody) and UpShadow[i] <= 5.0 / 100 * Body[i]
                                    and DnShadow[i] <= 5.0 / 100 * Body[i] and B(White))
        r["marubozu_black_bear"] = (B(Black) and B(LongBody) and UpShadow[i] <= 5.0 / 100 * Body[i]
                                    and DnShadow[i] <= 5.0 / 100 * Body[i] and B(Black))
        dragonfly = B(IsDojiBody) and UpShadow[i] <= Body[i]
        gravestone = B(IsDojiBody) and DnShadow[i] <= Body[i]
        r["doji"] = B(Doji) and not dragonfly and not gravestone
        r["gravestone_doji_bear"] = gravestone
        r["dragonfly_doji_bull"] = dragonfly
        r["harami_cross_bull"] = (B(LongBody, 1) and B(Black, 1) and B(DT, 1) and B(IsDojiBody)
                                  and high <= F(BodyHi, 1) and low >= F(BodyLo, 1))
        r["harami_cross_bear"] = (B(LongBody, 1) and B(White, 1) and B(UT, 1) and B(IsDojiBody)
                                  and high <= F(BodyHi, 1) and low >= F(BodyLo, 1))
        r["harami_bull"] = (B(LongBody, 1) and B(Black, 1) and B(DT, 1) and B(White) and B(SmallBody)
                            and high <= F(BodyHi, 1) and low >= F(BodyLo, 1))
        r["harami_bear"] = (B(LongBody, 1) and B(White, 1) and B(UT, 1) and B(Black) and B(SmallBody)
                            and high <= F(BodyHi, 1) and low >= F(BodyLo, 1))
        r["long_lower_shadow_bull"] = DnShadow[i] > Range[i] / 100 * 75.0
        r["long_upper_shadow_bear"] = UpShadow[i] > Range[i] / 100 * 75.0
        spin = (DnShadow[i] >= Range[i] / 100 * 34.0 and UpShadow[i] >= Range[i] / 100 * 34.0
                and not B(IsDojiBody))
        r["spinning_top_white"] = spin and B(White)
        r["spinning_top_black"] = spin and B(Black)
        tws = False
        if B(LongBody) and B(LongBody, 1) and B(LongBody, 2):
            if B(White) and B(White, 1) and B(White, 2):
                tws = (close > F(c, 1) and F(c, 1) > F(c, 2) and open_ < F(c, 1) and open_ > F(o, 1)
                       and F(o, 1) < F(c, 2) and F(o, 1) > F(o, 2) and B(HaveNotUp) and B(HaveNotUp, 1)
                       and B(HaveNotUp, 2))
        r["three_white_soldiers_bull"] = tws
        tbc = False
        if B(LongBody) and B(LongBody, 1) and B(LongBody, 2):
            if B(Black) and B(Black, 1) and B(Black, 2):
                tbc = (close < F(c, 1) and F(c, 1) < F(c, 2) and open_ > F(c, 1) and open_ < F(o, 1)
                       and F(o, 1) > F(c, 2) and F(o, 1) < F(o, 2) and B(HaveNotDn) and B(HaveNotDn, 1)
                       and B(HaveNotDn, 2))
        r["three_black_crows_bear"] = tbc
        r["engulfing_bull"] = (B(DT) and B(White) and B(LongBody) and B(Black, 1) and B(SmallBody, 1)
                               and close >= F(o, 1) and open_ <= F(c, 1) and (close > F(o, 1) or open_ < F(c, 1)))
        r["engulfing_bear"] = (B(UT) and B(Black) and B(LongBody) and B(White, 1) and B(SmallBody, 1)
                               and close <= F(o, 1) and open_ >= F(c, 1) and (close < F(o, 1) or open_ > F(c, 1)))
        r["abandoned_baby_bull"] = (B(DT, 2) and B(Black, 2) and B(IsDojiBody, 1) and F(l, 2) > F(h, 1)
                                    and B(White) and F(h, 1) < low)
        r["abandoned_baby_bear"] = (B(UT, 2) and B(White, 2) and B(IsDojiBody, 1) and F(h, 2) < F(l, 1)
                                    and B(Black) and F(l, 1) > high)
        three = B(Doji, 2) and B(Doji, 1) and B(Doji)
        r["tri_star_bull"] = three and B(DT, 2) and B(GapDn, 1) and B(GapUp)
        r["tri_star_bear"] = three and B(UT, 2) and B(GapUp, 1) and B(GapDn)
        r["kicking_bull"] = (B(Marubozu, 1) and B(Black, 1)) and (B(Marubozu) and B(White)) and F(h, 1) < low
        r["kicking_bear"] = (B(Marubozu, 1) and B(White, 1)) and (B(Marubozu) and B(Black)) and F(l, 1) > high
        r["inside_bar"] = high < F(h, 1) and low > F(l, 1)          # STD;InSide%1Bar%1Strategy
        r["pin_bar_bull"] = Range[i] > 0 and DnShadow[i] >= 2 / 3 * Range[i]   # non-TV
        r["pin_bar_bear"] = Range[i] > 0 and UpShadow[i] >= 2 / 3 * Range[i]
        for kname in res:
            res[kname].append(bool(r[kname]))
    return {kname: np.array(v) for kname, v in res.items()}


_HITS = {}


@pytest.mark.parametrize("data", ["D", "G"])
@pytest.mark.parametrize("rule", ["SMA50", "SMA50, SMA200", "No detection"])
def test_candlestick_patterns_match_port(data, rule):
    df = D if data == "D" else G
    a = [df[x].to_numpy() for x in ("open", "high", "low", "close")]
    exp = port_candles(*a, trendRule=rule)
    got = xt.candlestick_patterns(df.open, df.high, df.low, df.close, trend_rule=rule)
    assert list(got._fields) == xt._CANDLE_OUTPUTS
    for name in xt._CANDLE_OUTPUTS:
        np.testing.assert_array_equal(getattr(got, name).to_numpy(), exp[name], err_msg=name)
        _HITS[name] = _HITS.get(name, 0) + int(exp[name].sum())


def _crafted():
    """Small candles with textbook rare patterns spliced in; returns (df, {pattern: bar})."""
    rows, where = [], {}

    def base(n=20):
        for j in range(n):
            p = 100 + (0.3 if j % 2 else -0.3)
            rows.append((p, p + 0.8, p - 0.8, p + (0.5 if j % 2 else -0.5)))

    def put(name, bars):
        rows.extend(bars)
        where[name] = len(rows) - 1

    base(30)
    put("kicking_bull", [(100, 100, 95, 95), (101, 106, 101, 106)])
    base()
    put("kicking_bear", [(95, 100, 95, 100), (94, 94, 89, 89)])
    base()
    put("three_white_soldiers_bull", [(100, 104, 99.5, 104), (102, 106, 101.8, 106), (104, 108, 103.8, 108)])
    base()
    put("tri_star_bull", [(100, 101, 99, 100), (98, 99, 97, 98), (100, 101, 99, 100)])
    base()
    put("tri_star_bear", [(100, 101, 99, 100), (102, 103, 101, 102), (100, 101, 99, 100)])
    base()
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"],
                      index=pd.date_range("2024-01-01", periods=len(rows), freq="h"))
    return df, where


def test_candlestick_rare_patterns_crafted():
    df, where = _crafted()
    a = [df[x].to_numpy() for x in ("open", "high", "low", "close")]
    exp = port_candles(*a, trendRule="No detection")
    got = xt.candlestick_patterns(df.open, df.high, df.low, df.close, trend_rule="No detection")
    for name in xt._CANDLE_OUTPUTS:
        np.testing.assert_array_equal(getattr(got, name).to_numpy(), exp[name], err_msg=name)
        _HITS[name] = _HITS.get(name, 0) + int(exp[name].sum())
    for name, bar in where.items():
        assert getattr(got, name).iloc[bar], name


def test_candlestick_patterns_coverage():
    # every pattern fires at least once over the data sets and three trend rules
    df, _ = _crafted()
    for data in (D, G, df):
        for rule in ("SMA50", "SMA50, SMA200", "No detection"):
            got = xt.candlestick_patterns(data.open, data.high, data.low, data.close, trend_rule=rule)
            for name in xt._CANDLE_OUTPUTS:
                _HITS[name] = _HITS.get(name, 0) + int(getattr(got, name).sum())
    missing = [n for n in xt._CANDLE_OUTPUTS if _HITS.get(n, 0) == 0]
    assert missing == [], missing


def test_candlestick_bad_rule():
    with pytest.raises(ValueError):
        xt.candlestick_patterns(O, H, L, C, trend_rule="EMA")


# ---------------------------------------------------------------------------
# Zigzag (STD;Zig_Zag + TradingView/ZigZag/9 library), projections off
# ---------------------------------------------------------------------------

class _Pivot:
    def __init__(self, is_high, start, end):
        self.isHigh, self.start, self.end = is_high, start, end   # points are (bar, price)


def port_zigzag(high, low, devThreshold=5.0, depthSetting=10, allowZigZagOnOneBar=True):
    """Literal port of ZigZag.update() (projectionPivots false, no drawings)."""
    n = len(high)
    pivots = []
    rows = []

    def findPivotPoint(src, depth, isHigh, bar_index):
        pivotPrice = at(src, bar_index, depth)
        pivotPrice = 0.0 if isna(pivotPrice) else pivotPrice
        if depth * 2 <= bar_index:
            isFound = True
            for i in range(0, depth):
                v = at(src, bar_index, i)
                if (isHigh and v > pivotPrice) or (not isHigh and v < pivotPrice):
                    isFound = False
                    break
            if isFound:
                for i in range(depth + 1, 2 * depth + 1):
                    v = at(src, bar_index, i)
                    if (isHigh and v >= pivotPrice) or (not isHigh and v <= pivotPrice):
                        isFound = False
                        break
            if isFound:
                return (bar_index - depth, pivotPrice)
        return None

    def calcDev(start, end):
        return NA if start == 0 else 100 * (end - start) / abs(start)

    for bar in range(n):
        ev = {"new": False, "upd": False, "sh": NA, "shb": NA, "sl": NA, "slb": NA}
        depth = max(2, int(math.floor(depthSetting / 2)))

        def newPivotPointFound(isHigh, point):
            last = pivots[-1] if pivots else None
            if last is not None:
                if last.isHigh == isHigh:
                    m = 1 if last.isHigh else -1
                    if point[1] * m > last.end[1] * m:
                        if len(pivots) == 1:
                            last.start = point
                        last.end = point
                        ev["upd"] = True
                        return True
                else:
                    dev = calcDev(last.end[1], point[1])
                    if (not last.isHigh and dev >= devThreshold) or (last.isHigh and dev <= -1 * devThreshold):
                        if last.isHigh:
                            ev["sh"], ev["shb"] = last.end[1], last.end[0]
                        else:
                            ev["sl"], ev["slb"] = last.end[1], last.end[0]
                        pivots.append(_Pivot(isHigh, last.end, point))
                        ev["new"] = True
                        return True
                return False
            pivots.append(_Pivot(isHigh, point, point))
            ev["new"] = True
            return True

        def tryFindPivot(src, isHigh, registerPivot=True):
            point = findPivotPoint(src, depth, isHigh, bar)
            return newPivotPointFound(isHigh, point) if point is not None and registerPivot else False

        newHigh = tryFindPivot(high, True)
        tryFindPivot(low, False, allowZigZagOnOneBar or not newHigh)
        last = pivots[-1] if pivots else None
        rows.append([
            NA if last is None else (1.0 if last.isHigh else -1.0),
            NA if last is None else last.end[1],
            NA if last is None else last.end[0],
            NA if len(pivots) < 2 else last.start[1],
            NA if len(pivots) < 2 else last.start[0],
            ev["new"], ev["upd"], ev["sh"], ev["shb"], ev["sl"], ev["slb"],
        ])
    return pivots, list(zip(*rows))


@pytest.mark.parametrize("dev,depth", [(5.0, 10), (1.0, 10), (0.5, 4), (2.0, 7), (0.3, 30)])
def test_zigzag_matches_library_port(dev, depth):
    pivots, exp = port_zigzag(h, l, dev, depth)
    got = xt.zigzag(H, L, dev, depth)
    for name, e in zip(got._fields, exp):
        g = getattr(got, name).to_numpy()
        if g.dtype == bool:
            np.testing.assert_array_equal(g, np.array(e, bool), err_msg=name)
        else:
            same(g, np.array(e, float))
    # every finished pivot is emitted exactly once as a confirmed swing, and swings alternate
    sw = pd.concat([got.swing_high.dropna().rename("p").to_frame().assign(hi=True),
                    got.swing_low.dropna().rename("p").to_frame().assign(hi=False)])
    assert len(sw) == len(pivots) - 1
    hb = got.swing_high_bar.dropna().to_numpy()
    assert np.all(np.flatnonzero(got.swing_high.notna()) - hb >= max(2, depth // 2))


def test_zigzag_no_lookahead():
    full = xt.zigzag(H, L, 1.0, 10)
    cut = 1700
    part = xt.zigzag(H.iloc[:cut], L.iloc[:cut], 1.0, 10)
    for name in full._fields:
        a = getattr(full, name).iloc[:cut].to_numpy().astype(float)
        b = getattr(part, name).to_numpy().astype(float)
        same(a, b)


# ---------------------------------------------------------------------------
# Linear regression channel (STD;Linear_Regression)
# ---------------------------------------------------------------------------

def port_linreg_channel(src, high, low, length, useUpperDev=True, upperMult=2.0, useLowerDev=True, lowerMult=2.0):
    n = len(src)
    out = {k_: np.full(n, NA) for k_ in ("upper", "mid", "lower", "pearson_r", "slope", "stdev")}
    for b in range(n):
        if length <= 1 or b < length - 1:     # source[i] beyond history is na
            continue

        def source(i):
            return src[b - i]
        sumX = sumY = sumXSqr = sumXY = 0.0
        for i in range(0, length):
            val = source(i)
            per = i + 1.0
            sumX += per
            sumY += val
            sumXSqr += per * per
            sumXY += val * per
        slope = (length * sumXY - sumX * sumY) / (length * sumXSqr - sumX * sumX)
        average = sumY / length
        intercept = average - slope * sumX / length + slope
        upDev = dnDev = stdDevAcc = dsxx = dsyy = dsxy = 0.0
        periods = length - 1
        daY = intercept + slope * periods / 2
        val = intercept
        for j in range(0, periods + 1):
            price = high[b - j] - val
            if price > upDev:
                upDev = price
            price = val - low[b - j]
            if price > dnDev:
                dnDev = price
            price = source(j)
            dxt = price - average
            dyt = val - daY
            price -= val
            stdDevAcc += price * price
            dsxx += dxt * dxt
            dsyy += dyt * dyt
            dsxy += dxt * dyt
            val += slope
        stdDev = math.sqrt(stdDevAcc / (1 if periods == 0 else periods))
        pearsonR = 0 if (dsxx == 0 or dsyy == 0) else dsxy / math.sqrt(dsxx * dsyy)
        endPrice = intercept
        out["mid"][b] = endPrice
        out["upper"][b] = endPrice + (upperMult * stdDev if useUpperDev else upDev)
        out["lower"][b] = endPrice + (-lowerMult * stdDev if useLowerDev else -dnDev)
        out["pearson_r"][b] = pearsonR
        out["slope"][b] = -slope
        out["stdev"][b] = stdDev
    return out


@pytest.mark.parametrize("length,use_up,use_dn", [(100, True, True), (20, False, True), (7, True, False), (2, False, False)])
def test_linreg_channel_matches_port(length, use_up, use_dn):
    exp = port_linreg_channel(c, h, l, length, use_up, 2.0, use_dn, 1.5)
    got = xt.linreg_channel(H, L, C, length, 2.0, 1.5, use_up, use_dn)
    for name in got._fields:
        same(getattr(got, name), exp[name], rtol=1e-10, atol=1e-10)


def test_linreg_channel_mid_is_ta_linreg():
    got = xt.linreg_channel(H, L, C, 50)
    same(got.mid, ti.lsma(C, 50), rtol=1e-8)
    assert (got.pearson_r.dropna() >= 0).all()
    assert xt.linreg_channel(H, L, C, 1).mid.isna().all()


# ---------------------------------------------------------------------------
# request.security alignment
# ---------------------------------------------------------------------------

def port_security(chart, rule_len, expr="close", sma_len=3):
    """Bar-by-bar emulation of request.security on historical bars.

    HTF bars are built as the chart bars arrive (HTF period = floor of the bar
    time to ``rule_len``). ``lookahead_off``: the HTF value is confirmed on the
    chart bar whose close time reaches the HTF close (or, if that bar is
    missing, the first bar after it). ``offset1``: ``expr[1]`` with lookahead
    on, i.e. from the first chart bar of HTF bar k, the value of HTF bar k-1.
    """
    times = chart.index
    step = pd.Series(times).diff().dropna().min()
    closes = []          # completed HTF closes in order
    vals = []            # completed HTF expression values
    off, on1 = [], []
    cur_period = None
    cur_close = None
    cur_done = False
    for t, px in zip(times, chart["close"].to_numpy()):
        period = t.floor(rule_len)
        if period != cur_period:
            if cur_period is not None and not cur_done:
                closes.append(cur_close)
                vals.append(_expr(closes, expr, sma_len))
            cur_period, cur_done = period, False
        cur_close = px
        if not cur_done and t + step >= period + pd.Timedelta(rule_len):
            closes.append(cur_close)
            vals.append(_expr(closes, expr, sma_len))
            cur_done = True
        off.append(vals[-1] if vals else NA)
        # offset1: previous HTF bar's value = last value completed before this period
        n_before = len(vals) - (1 if cur_done else 0)
        on1.append(vals[n_before - 1] if n_before >= 1 else NA)
    return np.array(off), np.array(on1)


def _expr(closes, expr, n):
    if expr == "close":
        return closes[-1]
    return NA if len(closes) < n else sum(closes[-n:]) / n


@pytest.mark.parametrize("rule", ["4h", "1D"])
@pytest.mark.parametrize("drop", [False, True])
def test_htf_matches_security_port(rule, drop):
    chart = D
    if drop:   # remove some chart bars, including last bars of HTF periods
        rng = np.random.default_rng(3)
        keep = np.ones(len(D), bool)
        keep[rng.choice(len(D), 300, replace=False)] = False
        chart = D[keep]
    bars = xt.resample_ohlcv(chart, rule)
    for expr in ("close", "sma"):
        series = bars["close"] if expr == "close" else ti.sma(bars["close"], 3)
        e_off, e_on1 = port_security(chart, rule, expr)
        same(xt.htf(series, chart.index, "lookahead_off", rule=rule, chart_freq="1h"), e_off)
        same(xt.htf(series, chart.index, "lookahead_on_offset1", rule=rule, chart_freq="1h"), e_on1)


def test_htf_timing_daily_on_hourly():
    bars = xt.resample_ohlcv(D, "D")
    off = xt.htf(bars, D.index)                      # uses the close_time column
    on1 = xt.htf(bars, D.index, "lookahead_on_offset1")
    day1_close = D.close.iloc[23]
    assert off.close.iloc[:23].isna().all() and off.close.iloc[23] == day1_close
    assert on1.close.iloc[:24].isna().all() and on1.close.iloc[24] == day1_close
    assert (on1.close.iloc[24:48] == day1_close).all()
    gap = xt.htf(bars.close, D.index, gaps=True)
    assert gap.notna().sum() == len(bars) - (0 if len(D) % 24 == 0 else 1)
    with pytest.raises(ValueError):
        xt.htf(bars.close, D.index, "lookahead_on")


def test_resample_ohlcv():
    for rule, key in (("4h", D.index.floor("4h")), ("D", D.index.floor("D"))):
        bars = xt.resample_ohlcv(D, rule)
        g = D.groupby(key)
        same(bars.open, g.open.first())
        same(bars.high, g.high.max())
        same(bars.low, g.low.min())
        same(bars.close, g.close.last())
        same(bars.volume, g.volume.sum())
    w = xt.resample_ohlcv(D, "W")
    assert (w.index.day_of_week == 0).all()        # TradingView weeks open on Monday
    assert ((w.close_time - w.index) == pd.Timedelta("7D")).all()
    m = xt.resample_ohlcv(D, "M")
    assert (m.index.day == 1).all()
    first_month = D[D.index < m.close_time.iloc[0]]
    assert m.close.iloc[0] == first_month.close.iloc[-1]


def test_registry_kept_separate():
    from tv_indicators._core import REGISTRY
    for name in xt.EXTRA_TV:
        assert name not in REGISTRY
    assert {"PIVOT_HIGH", "PIVOT_LOW", "DIVERGENCE", "RSI_DIVERGENCE", "CANDLESTICK_PATTERNS",
            "ZIGZAG", "LINREG_CHANNEL"} <= set(xt.EXTRA_TV)
