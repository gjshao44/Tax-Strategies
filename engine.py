import streamlit as st
import pandas as pd
import numpy as np
import json
from config import LANG_MAP

def get_survival_prob(age):
    # Simplified lookup based on actuarial trends (prob of survival for one individual)
    # Returns 1.0 until age 65, then declines
    if age < 65: return 1.0
    if age >= 100: return 0.05
    # Approximate mortality curve (roughly 1% drop per year starting at 65)
    return max(0.05, 1.0 - (age - 65) * 0.02)

def get_rmd_divisor(age, rmd_start_age=73):
    if age < rmd_start_age: return 0.0
    table = {
        73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1,
        80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2,
        87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1,
        94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4
    }
    return table.get(age, max(1.0, 6.4 - (age - 100) * 0.4))

def get_irmaa_surcharge(magi, inf_factor, num_spouses_medicare):
    base_irmaa = 218000 * inf_factor
    t1, t2, t3, t4, t5 = base_irmaa, base_irmaa * (272/218), base_irmaa * (340/218), base_irmaa * (408/218), base_irmaa * (750/218)
    if magi > t5: return 5, 480 * 12 * num_spouses_medicare * inf_factor
    if magi > t4: return 4, 440 * 12 * num_spouses_medicare * inf_factor
    if magi > t3: return 3, 320 * 12 * num_spouses_medicare * inf_factor
    if magi > t2: return 2, 200 * 12 * num_spouses_medicare * inf_factor
    if magi > t1: return 1, 80 * 12 * num_spouses_medicare * inf_factor
    return 0, 0

# --- 3. CORE CALCULATORS ---
def calculate_comprehensive_tax(ordinary_taxable, qd_ltcg_total, magi, inf_factor, taxable_ss, status, year_idx):
    ord_tax = 0
    if status == "MFJ":
        brackets = [(23200, 0.10), (94300, 0.12), (201050, 0.22), (383900, 0.24)]
        top_rate = 0.32
    else: 
        brackets = [(11600, 0.10), (47150, 0.12), (100525, 0.22), (191950, 0.24)]
        top_rate = 0.32

    prev_limit = 0
    for limit, rate in brackets:
        adj_limit = limit * inf_factor
        taxable_in_bracket = min(ordinary_taxable, adj_limit) - prev_limit
        if taxable_in_bracket > 0:
            ord_tax += taxable_in_bracket * rate
        prev_limit = adj_limit
    if ordinary_taxable > prev_limit:
        ord_tax += (ordinary_taxable - prev_limit) * top_rate

    if status == "MFJ":
        zero_limit = 94050 * inf_factor
        fifteen_limit = 583750 * inf_factor
    else: 
        zero_limit = 47025 * inf_factor
        fifteen_limit = 291850 * inf_factor
    
    ltcg_in_zero = max(0, min(qd_ltcg_total, zero_limit - ordinary_taxable))
    ltcg_in_fifteen = max(0, min(qd_ltcg_total - ltcg_in_zero, fifteen_limit - max(ordinary_taxable, zero_limit)))
    ltcg_in_twenty = max(0, qd_ltcg_total - ltcg_in_zero - ltcg_in_fifteen)
    
    ltcg_tax = (ltcg_in_fifteen * 0.15) + (ltcg_in_twenty * 0.20)

    niit_threshold = (250000 if status == "MFJ" else 200000 if status == "Single" else 125000) * inf_factor
    tax_niit = 0
    if magi > niit_threshold:
        investment_income = qd_ltcg_total + max(0, (ordinary_taxable - taxable_ss))
        tax_niit = min(investment_income, magi - niit_threshold) * 0.038
        
    return ord_tax + ltcg_tax + tax_niit

@st.cache_data
def calculate_roadmap(
    ira_h_init, ira_w_init, roth_init, brokerage_init,
    retire_year, sim_years, h_age_at_retire, w_age_at_retire,
    tax_status, roth_conv, annual_ltcg, annual_expense, qd_perc,
    taxable_div_in, muni_int_in, last_salary,
    ss_h_monthly, ss_h_start, ss_w_monthly, ss_w_start,
    ira_growth, roth_growth, broker_growth, inflation_rate,
    lang, withdrawal_strategy="tax_efficient",
    conv_override=None, ltcg_override=None, horizon_override=None,
    ss_start_h=None, ss_start_w=None, conv_stop_age_override=None,
    growth_sequence=None
    ):
    t_internal = LANG_MAP[lang]
    rows = []
    cur_ira_h, cur_ira_w = ira_h_init, ira_w_init
    cur_roth, cur_brokerage = roth_init, brokerage_init
    oom_triggered = False    
    conversion_already_stopped = False

    sim_roth_conv = conv_override if conv_override is not None else roth_conv
    sim_annual_ltcg = ltcg_override if ltcg_override is not None else annual_ltcg
    sim_horizon = horizon_override if horizon_override is not None else sim_years
    actual_ss_h_start = ss_start_h if ss_start_h is not None else ss_h_start
    actual_ss_w_start = ss_start_w if ss_start_w is not None else ss_w_start

    birth_year_h = 2026 - h_age_at_retire
    birth_year_w = 2026 - w_age_at_retire
    rmd_age_h = 75 if birth_year_h >= 1960 else 73
    rmd_age_w = 75 if birth_year_w >= 1960 else 73

    sim_conv_stop_age = conv_stop_age_override if conv_stop_age_override is not None else min(rmd_age_h, rmd_age_w)

    for i in range(sim_horizon):
        year = retire_year + i
        age_h, age_w = h_age_at_retire + i, w_age_at_retire + i
        inf_factor = (1 + inflation_rate) ** i
        ev = []
        
        # Survival Probabilities
        prob_h = get_survival_prob(age_h)
        prob_w = get_survival_prob(age_w)
        joint_survival = 1 - ((1 - prob_h) * (1 - prob_w))

        if year == retire_year: ev.append(t_internal["event_retire"])
        if age_h == 65: ev.append(t_internal["event_hmed"])
        if age_w == 65: ev.append(t_internal["event_wmed"])
        if age_h == rmd_age_h: ev.append(t_internal["event_hrmd"])
        if age_w == rmd_age_w: ev.append(t_internal["event_wrmd"])

        active_conversion = min(sim_roth_conv, cur_ira_h + cur_ira_w)
        stop_reason = ""
        
        if age_h >= sim_conv_stop_age or age_w >= sim_conv_stop_age:
            active_conversion = 0
            stop_reason = "Target Age Reached" if conv_stop_age_override else "RMD Start"
        elif (cur_ira_h + cur_ira_w) <= 1000 and sim_roth_conv > 0:
            active_conversion = 0
            stop_reason = "IRA Depleted"

        if active_conversion == 0 and not conversion_already_stopped and sim_roth_conv > 0:
            ev.append(f"{t_internal['event_roth_stop']} ({stop_reason})")
            conversion_already_stopped = True

        divisor_h = get_rmd_divisor(age_h, rmd_age_h)
        divisor_w = get_rmd_divisor(age_w, rmd_age_w)
        rmd_h = (cur_ira_h / divisor_h) if divisor_h > 0 else 0
        rmd_w = (cur_ira_w / divisor_w) if divisor_w > 0 else 0
        total_rmd = rmd_h + rmd_w
        salary = last_salary if year == retire_year else 0
        h_ss = (ss_h_monthly * 12 * inf_factor) if year >= actual_ss_h_start else 0
        w_ss = (ss_w_monthly * 12 * inf_factor) if year >= actual_ss_w_start else 0
        total_ss = h_ss + w_ss
        
        qual_div = taxable_div_in * qd_perc
        ord_div = taxable_div_in * (1 - qd_perc)
        
        combined_income = salary + ord_div + qual_div + sim_annual_ltcg + active_conversion + total_rmd + muni_int_in + (total_ss * 0.5)
        taxable_ss = 0
        if tax_status == "MFJ":
            if combined_income > 44000:
                taxable_ss = min(0.85 * total_ss, 6000 + 0.85 * (combined_income - 44000))
            elif combined_income > 32000:
                taxable_ss = min(0.5 * total_ss, 0.5 * (combined_income - 32000))
        else:
            if combined_income > 34000:
                taxable_ss = min(0.85 * total_ss, 4500 + 0.85 * (combined_income - 34000))
            elif combined_income > 25000:
                taxable_ss = min(0.5 * total_ss, 0.5 * (combined_income - 25000))
                
        ordinary_gross = salary + ord_div + taxable_ss + active_conversion + total_rmd
        qd_ltcg_total = qual_div + sim_annual_ltcg
        magi = ordinary_gross + qd_ltcg_total + muni_int_in
        
        num_spouses_medicare = (1 if age_h >= 65 else 0) + (1 if age_w >= 65 else 0)
        irmaa_tier, irmaa_surcharge = get_irmaa_surcharge(magi, inf_factor, num_spouses_medicare)

        base_deduct = 32200 if tax_status == "MFJ" else 16100
        extra_deduct = 0
        if tax_status == "MFJ":
            if age_h >= 65: extra_deduct += 1650
            if age_w >= 65: extra_deduct += 1650
        else:
            if age_h >= 65: extra_deduct += 1950 
        
        deduct = (base_deduct + extra_deduct) * inf_factor
        ord_taxable = max(0, ordinary_gross - deduct)
        
        fed_tax = calculate_comprehensive_tax(ord_taxable, qd_ltcg_total, magi, inf_factor, taxable_ss, tax_status, i)
        
        target_expense = (annual_expense * inf_factor) + fed_tax + irmaa_surcharge       
        available_cash = total_ss + salary + taxable_div_in + sim_annual_ltcg + muni_int_in + total_rmd
        shortfall = max(0, target_expense - available_cash)
        
        if shortfall > (cur_brokerage + (cur_ira_h + cur_ira_w) + cur_roth) and not oom_triggered:
            ev.append(t_internal["event_oom"])
            oom_triggered = True

        from_broker = 0
        ira_withdrawn = 0
        from_roth = 0

        def _withdraw_ira(need):
            nonlocal ord_taxable, magi, fed_tax, irmaa_tier, irmaa_surcharge, target_expense
            if need <= 0 or (cur_ira_h + cur_ira_w) <= 0:
                return 0
            gross_needed = need
            for _ in range(5):
                test_ord = ord_taxable + gross_needed
                test_magi = magi + gross_needed
                test_fed_tax = calculate_comprehensive_tax(test_ord, qd_ltcg_total, test_magi, inf_factor, taxable_ss, tax_status, i)
                _, test_irmaa_sur = get_irmaa_surcharge(test_magi, inf_factor, num_spouses_medicare)
                extra_tax = test_fed_tax - fed_tax
                extra_irmaa = test_irmaa_sur - irmaa_surcharge
                gross_needed = need + extra_tax + extra_irmaa
                if gross_needed >= (cur_ira_h + cur_ira_w):
                    gross_needed = cur_ira_h + cur_ira_w
                    break
            ord_taxable += gross_needed
            magi += gross_needed
            fed_tax = calculate_comprehensive_tax(ord_taxable, qd_ltcg_total, magi, inf_factor, taxable_ss, tax_status, i)
            irmaa_tier, irmaa_surcharge = get_irmaa_surcharge(magi, inf_factor, num_spouses_medicare)
            target_expense = (annual_expense * inf_factor) + fed_tax + irmaa_surcharge
            return gross_needed

        if withdrawal_strategy == "tax_efficient":
            from_broker = min(cur_brokerage, shortfall)
            cur_brokerage -= from_broker
            shortfall -= from_broker
            if shortfall > 0:
                ira_withdrawn = _withdraw_ira(shortfall)
                shortfall = max(0, target_expense - available_cash - from_broker - ira_withdrawn)
            from_roth = min(cur_roth, shortfall)
            cur_roth -= from_roth

        elif withdrawal_strategy == "ira_first":
            ira_withdrawn = _withdraw_ira(shortfall)
            shortfall = max(0, target_expense - available_cash - ira_withdrawn)
            from_broker = min(cur_brokerage, shortfall)
            cur_brokerage -= from_broker
            shortfall -= from_broker
            from_roth = min(cur_roth, shortfall)
            cur_roth -= from_roth

        elif withdrawal_strategy == "roth_first":
            from_roth = min(cur_roth, shortfall)
            cur_roth -= from_roth
            shortfall -= from_roth
            from_broker = min(cur_brokerage, shortfall)
            cur_brokerage -= from_broker
            shortfall -= from_broker
            if shortfall > 0:
                ira_withdrawn = _withdraw_ira(shortfall)

        elif withdrawal_strategy == "proportional":
            total_avail = cur_brokerage + (cur_ira_h + cur_ira_w) + cur_roth
            if total_avail > 0 and shortfall > 0:
                broker_frac = cur_brokerage / total_avail
                ira_frac = (cur_ira_h + cur_ira_w) / total_avail
                roth_frac = cur_roth / total_avail
                from_broker = min(cur_brokerage, shortfall * broker_frac)
                cur_brokerage -= from_broker
                from_roth = min(cur_roth, shortfall * roth_frac)
                cur_roth -= from_roth
                ira_need = shortfall * ira_frac
                if ira_need > 0:
                    ira_withdrawn = _withdraw_ira(ira_need)
                # Mop up any remaining shortfall from tax increase on IRA portion
                remaining = max(0, target_expense - available_cash - from_broker - ira_withdrawn - from_roth)
                if remaining > 0:
                    extra_b = min(cur_brokerage, remaining)
                    cur_brokerage -= extra_b
                    from_broker += extra_b
                    remaining -= extra_b
                    extra_r = min(cur_roth, remaining)
                    cur_roth -= extra_r
                    from_roth += extra_r

        # Save surplus cash to the Brokerage account
        surplus = max(0, available_cash - target_expense)
        cur_brokerage += surplus

        # Deduct RMDs and other withdrawals from the Traditional IRA
        ira_total = cur_ira_h + cur_ira_w
        amt_to_deduct = total_rmd + ira_withdrawn + active_conversion
        if amt_to_deduct > ira_total:
            amt_to_deduct = ira_total
            
        if ira_total > 0:
            h_ratio = cur_ira_h / ira_total
            w_ratio = cur_ira_w / ira_total
            cur_ira_h -= h_ratio * amt_to_deduct
            cur_ira_w -= w_ratio * amt_to_deduct
        
        if growth_sequence is not None:
            yr_ira_g, yr_roth_g, yr_broker_g = growth_sequence[0][i], growth_sequence[1][i], growth_sequence[2][i]
        else:
            yr_ira_g, yr_roth_g, yr_broker_g = ira_growth, roth_growth, broker_growth
        cur_ira_h = max(0, cur_ira_h) * (1 + yr_ira_g)
        cur_ira_w = max(0, cur_ira_w) * (1 + yr_ira_g)
        yearly_roth_growth = cur_roth * yr_roth_g
        cur_roth = (cur_roth + active_conversion + yearly_roth_growth)
        cur_brokerage *= (1 + yr_broker_g)
        
        total_nw = cur_ira_h + cur_ira_w + cur_roth + cur_brokerage
        
        rows.append({
            "Year": year, "Ages": f"{age_h}/{age_w}", "INPUT: SS": total_ss, 
            "raw_div": taxable_div_in, "raw_muni": muni_int_in, "raw_cg": sim_annual_ltcg,
            "LEVER: Roth": active_conversion, "INPUT: RMDs": total_rmd, "OUT: MAGI": magi, "OUT: Fed Tax": fed_tax,
            "raw_outflow": target_expense, "Roth Bal": cur_roth, "IRA Bal": cur_ira_h + cur_ira_w, 
            "Brokerage": cur_brokerage, "Total Net Worth": total_nw,
            "Expected Net Worth": total_nw * joint_survival,
            "IRMAA": "✅ Safe" if irmaa_tier == 0 else f"🚩 Tier {irmaa_tier}",
            "irmaa_tier": irmaa_tier,
            "🚨 Important Events": ", ".join(ev), "raw_roth_yield": yearly_roth_growth, "raw_rmd": total_rmd
        })
    return pd.DataFrame(rows)
