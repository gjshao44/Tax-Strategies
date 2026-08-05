"""State (+ federal context) retiree tax estimator for CA, WA, OR, IL, NJ, MA, NC, TX, FL, PA.

Loads data/states/<abbr>.json (one sourced fact file per state, following the same
value/unit/as_of/source pattern used elsewhere in this project's sibling app) and computes
a planning-grade estimate of state income tax + property tax for a retiree, given the same
income picture already driving the federal calculation in engine.py.

This is a simplified estimate, not tax advice: income-tested senior relief programs (circuit
breakers, freezes, deferrals, rebates) are described in each state's `relief_programs_note`/
`senior_tax_credits` but are NOT auto-applied, since eligibility depends on income limits this
app doesn't fully model. Only the two universal (non-income-tested) property-tax homestead
reductions -- TX's general + over-65 exemption, FL's general exemption -- are applied directly.
"""

import glob
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "states")

STATE_ORDER = ["CA", "WA", "OR", "IL", "NJ", "MA", "NC", "TX", "FL", "PA"]


def load_all_states() -> dict:
    """Returns {abbr: parsed_json_dict} for every file in data/states/."""
    states = {}
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
        abbr = os.path.splitext(os.path.basename(path))[0].upper()
        with open(path) as f:
            states[abbr] = json.load(f)
    return states


def fact_value(section, key, default=None):
    """Extract a fact's `value`; passes through non-fact/missing values as default."""
    if not isinstance(section, dict):
        return default
    fact = section.get(key)
    if isinstance(fact, dict):
        return fact.get("value", default)
    return default


def get_alt_property_rate_key(pt_section):
    """Find the state's alternate (non-statewide-average) property rate fact, if any --
    e.g. new_buyer_effective_rate_pct, recent_construction_effective_rate_pct,
    reassessed_effective_rate_pct. Each state has at most one."""
    if not isinstance(pt_section, dict):
        return None
    for key in pt_section:
        if key != "effective_rate_pct" and key.endswith("effective_rate_pct"):
            return key
    return None


def apply_brackets(taxable, brackets):
    """brackets: ascending list of [lower_threshold, marginal_rate_pct]. Marginal tax calc."""
    if taxable <= 0 or not brackets:
        return 0.0
    tax = 0.0
    for i, (lower, rate) in enumerate(brackets):
        upper = brackets[i + 1][0] if i + 1 < len(brackets) else float("inf")
        if taxable <= lower:
            break
        band = min(taxable, upper) - lower
        tax += band * (rate / 100.0)
    return tax


def _num_qualifying(h_age, w_age, tax_status, threshold):
    """How many filers in the household meet an age threshold (for per-person deduction amounts)."""
    if tax_status == "MFJ":
        return (1 if h_age >= threshold else 0) + (1 if w_age >= threshold else 0)
    return 1 if h_age >= threshold else 0


def _any_qualifying(h_age, w_age, tax_status, threshold):
    """Whether the household has at least one filer meeting an age threshold (eligibility gates)."""
    if tax_status == "MFJ":
        return h_age >= threshold or w_age >= threshold
    return h_age >= threshold


def compute_state_tax(state_data: dict, tax_status: str, h_age: float, w_age: float,
                       income: dict, home_value: float = 0.0,
                       property_rate_basis: str = "avg") -> dict:
    """income keys (all annual $, current-year/Year-1 picture): salary, ordinary_other
    (taxable bond interest + non-qualified dividend portion), qualified_dividends, capital_gains,
    ira_income (RMDs + discretionary IRA/401k withdrawals + Roth conversion -- all ordinary,
    tax-deferred-account-sourced income), total_ss (gross annual Social Security).

    property_rate_basis: "avg" uses each state's statewide-average effective_rate_pct.
    "new_buyer" uses the state's alternate rate fact (see get_alt_property_rate_key) when
    that state has one -- CA/FL/TX price in a fresh purchase-year assessment, OR/PA price
    in a newly-built/recently-reassessed property -- falling back to "avg" otherwise.

    Returns a dict with income_tax, property_tax, total_tax, and a breakdown for display.
    """
    tc = state_data.get("income_tax", {}) or {}
    tax_type = tc.get("type")

    breakdown = {}
    income_tax = 0.0
    excluded_retirement_income = 0.0

    ira_income = income.get("ira_income", 0.0)
    salary = income.get("salary", 0.0)
    ordinary_other = income.get("ordinary_other", 0.0)
    qualified_dividends = income.get("qualified_dividends", 0.0)
    capital_gains = income.get("capital_gains", 0.0)
    total_ss = income.get("total_ss", 0.0)

    if tax_type == "none":
        cge = state_data.get("capital_gains_excise")
        if cge:
            val = cge.get("value", {})
            std_ded = val.get("standard_deduction", 0) or 0
            cg_brackets = val.get("brackets", [[0, 0]])
            taxable_gain = max(0.0, capital_gains - std_ded)
            wa_tax = apply_brackets(taxable_gain, cg_brackets)
            income_tax = wa_tax
            breakdown["capital_gains_excise_tax"] = wa_tax
        else:
            breakdown["income_tax"] = 0.0
    else:
        ss_taxable = fact_value(state_data.get("social_security", {}), "taxable", False)
        ri = state_data.get("retirement_income", {}) or {}
        treatment = fact_value(ri, "treatment", "ordinary")

        if treatment == "exempt":
            taxed_ira = 0.0
            excluded_retirement_income = ira_income
        elif treatment == "partial":
            eligibility_age = ri.get("eligibility_age", 62)
            eligible = _any_qualifying(h_age, w_age, tax_status, eligibility_age)
            cap = fact_value(ri, "exclusion_cap_mfj" if tax_status == "MFJ" else "exclusion_cap_single", 0) or 0
            income_limit = fact_value(ri, "exclusion_income_limit", 0) or 0
            total_income_test = ira_income + ordinary_other + qualified_dividends + capital_gains + salary
            # Mirrors NJ-1040 2025 instructions, Line 28a worksheet exactly: Line A = actual
            # pension/IRA/annuity income (ira_income); Line B = per the chart below; the
            # exclusion is the LESSER of Line A or Line B. In the 100% tier, Line B is the flat
            # statutory cap; in the 50%/25% tiers, Line B is that percentage of Line A itself
            # (not of the cap) -- so in those tiers the exclusion is just pct * ira_income.
            if not eligible or (income_limit and total_income_test > income_limit):
                line_b = 0.0
            elif total_income_test <= 100000:
                line_b = cap
            elif total_income_test <= 125000:
                line_b = ira_income * 0.5
            else:
                line_b = ira_income * 0.25
            excluded_retirement_income = min(ira_income, line_b)
            taxed_ira = max(0.0, ira_income - excluded_retirement_income)
        else:  # ordinary
            taxed_ira = ira_income
            excluded_retirement_income = 0.0

        ss_included = total_ss if ss_taxable else 0.0
        base = salary + ordinary_other + qualified_dividends + capital_gains + taxed_ira + ss_included

        # Oregon-only: OR-40 Line 10 lets filers subtract federal tax liability (capped,
        # phased out by federal AGI) from OR taxable income before the standard deduction.
        fts = tc.get("federal_tax_subtraction")
        federal_tax_subtraction = 0.0
        if isinstance(fts, dict):
            fv = fts.get("value", {})
            fts_cap = fv.get("cap_mfj" if tax_status == "MFJ" else "cap_single", 0)
            fts_start = fv.get("phaseout_start_mfj" if tax_status == "MFJ" else "phaseout_start_single", float("inf"))
            fts_end = fv.get("phaseout_end_mfj" if tax_status == "MFJ" else "phaseout_end_single", float("inf"))
            federal_agi = income.get("federal_agi", 0.0)
            federal_tax_liability = income.get("federal_tax_liability", 0.0)
            if federal_agi <= fts_start:
                fts_max_allowed = fts_cap
            elif federal_agi >= fts_end:
                fts_max_allowed = 0.0
            else:
                fts_max_allowed = fts_cap * (fts_end - federal_agi) / (fts_end - fts_start)
            federal_tax_subtraction = min(federal_tax_liability, fts_max_allowed)
            base -= federal_tax_subtraction
        breakdown["federal_tax_subtraction"] = federal_tax_subtraction

        std = fact_value(tc, "standard_deduction_mfj" if tax_status == "MFJ" else "standard_deduction_single", 0) or 0
        pe = fact_value(tc, "personal_exemption_mfj" if tax_status == "MFJ" else "personal_exemption_single", 0) or 0
        senior_ded_per = fact_value(tc, "senior_addl_deduction_mfj" if tax_status == "MFJ" else "senior_addl_deduction_single", 0) or 0
        senior_exempt_per = fact_value(tc, "senior_addl_exemption_mfj" if tax_status == "MFJ" else "senior_addl_exemption_single", 0) or 0
        num_65 = _num_qualifying(h_age, w_age, tax_status, 65)

        senior_addl_total = (senior_ded_per + senior_exempt_per) * num_65
        deduction = std + pe + senior_addl_total
        taxable = max(0.0, base - deduction)

        breakdown["base_deduction"] = std + pe
        breakdown["senior_addl_deduction"] = senior_addl_total
        breakdown["total_deduction"] = deduction
        breakdown["num_65_plus"] = num_65

        if tax_type == "flat":
            rate = fact_value(tc, "flat_rate_pct", 0) or 0
            income_tax = taxable * (rate / 100.0)
        elif tax_type == "progressive":
            brackets = fact_value(tc, "brackets_mfj" if tax_status == "MFJ" else "brackets_single", [[0, 0]])
            income_tax = apply_brackets(taxable, brackets)

        surtax = tc.get("surtax")
        if isinstance(surtax, dict):
            sv = surtax.get("value", {})
            threshold = sv.get("threshold", float("inf"))
            srate = sv.get("rate_pct", 0)
            surtax_amt = max(0.0, taxable - threshold) * (srate / 100.0)
            income_tax += surtax_amt
            breakdown["surtax"] = surtax_amt

        breakdown["state_ordinary_taxable"] = taxable
        breakdown["excluded_retirement_income"] = excluded_retirement_income

    breakdown["income_tax"] = income_tax

    pt = state_data.get("property_tax", {}) or {}
    rate_key = "effective_rate_pct"
    if property_rate_basis == "new_buyer":
        rate_key = get_alt_property_rate_key(pt) or "effective_rate_pct"
    rate_pct = fact_value(pt, rate_key, 0) or 0
    general_reduction = fact_value(pt, "general_homestead_reduction_usd", 0) or 0
    senior_reduction = fact_value(pt, "senior_homestead_reduction_usd", 0) or 0
    num_65_any = 1 if _any_qualifying(h_age, w_age, tax_status, 65) else 0
    taxable_home_value = max(0.0, home_value - general_reduction - senior_reduction * num_65_any)
    property_tax = taxable_home_value * (rate_pct / 100.0)

    breakdown["property_tax"] = property_tax
    breakdown["property_tax_rate_key"] = rate_key
    breakdown["property_tax_rate_pct"] = rate_pct

    return {
        "income_tax": income_tax,
        "property_tax": property_tax,
        "total_tax": income_tax + property_tax,
        "breakdown": breakdown,
    }
