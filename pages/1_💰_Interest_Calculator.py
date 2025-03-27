import streamlit as st
import math
import plotly.graph_objects as go # For chart

# --- Calculation Function (MODIFIED) ---
def future_value_with_contributions(
    principal,
    rate,
    time,
    compound_type="annually", # Can be 'continuously' or an integer n
    contribution_amount=0,
    contribution_frequency=0 # Times per year contributions are made
    ):
    """
    Calculates the future value of an investment with an initial principal
    and regular contributions.

    Args:
        principal (float): Initial principal amount.
        rate (float): Annual interest rate (as a decimal).
        time (float): Time period in years.
        compound_type (str|int): 'continuously' or integer n for compounding times per year.
        contribution_amount (float): Amount contributed each period. Defaults to 0.
        contribution_frequency (int): How many times per year contributions are made. Defaults to 0.

    Returns:
        tuple: (final_amount, total_interest, total_contributions) or (inf, inf, inf) on overflow.

    Raises:
        ValueError: For invalid inputs.
        TypeError: For incorrect input types.
    """

    # --- Input Validation ---
    if not all(isinstance(arg, (int, float)) for arg in [principal, rate, time, contribution_amount]):
        raise TypeError("Principal, rate, time, and contribution amount must be numbers.")
    if not isinstance(contribution_frequency, int):
         raise TypeError("Contribution frequency must be an integer.")
    # Value Validation
    if principal < 0: raise ValueError("Principal cannot be negative.")
    if rate < 0: raise ValueError("Interest rate cannot be negative.")
    if time < 0: raise ValueError("Time cannot be negative.")
    if contribution_amount < 0: raise ValueError("Contribution amount cannot be negative.")
    if contribution_frequency < 0: raise ValueError("Contribution frequency cannot be negative.")

    # Determine compounding frequency n or if continuous
    is_continuous = False
    n_compound = 1 # Default for annual
    if compound_type == "continuously":
        is_continuous = True
    elif isinstance(compound_type, int):
        if compound_type <= 0:
            raise ValueError("Compounding times per year must be positive.")
        n_compound = compound_type
    # Add other string types if needed, e.g., mapping "monthly" to 12 internally

    # --- Calculations ---
    try:
        # 1. Future Value of the Initial Principal
        principal_fv = 0
        if principal > 0:
            if is_continuous:
                if rate == 0:
                    principal_fv = principal
                else:
                    rt = rate * time
                    if rt > 700: return float('inf'), float('inf'), float('inf') # Overflow check
                    principal_fv = principal * math.exp(rt)
            else: # Compounded n times
                 # Ensure n_compound is positive if principal > 0
                if n_compound <= 0: raise ValueError("Compounding frequency (n) must be positive.")
                if rate == 0:
                     principal_fv = principal
                else:
                    base = 1 + rate / n_compound
                    exponent = n_compound * time
                    # Overflow check for discrete compounding
                    # log(principal) + exponent * log(base) > log(max_float) ~ 709
                    # Simpler check: if exponent is very large and base > 1
                    if exponent > 10000 and base > 1.00001: # Heuristic check
                         try:
                              # Try precise check if possible
                              if math.log(principal if principal > 0 else 1) + exponent * math.log(base if base > 1 else 1) > 700:
                                   return float('inf'), float('inf'), float('inf')
                         except ValueError: # Handle log(0) or potential issues
                               pass # Proceed with calculation, might overflow later
                    principal_fv = principal * (base ** exponent)


        # 2. Future Value of the Contributions (Annuity)
        annuity_fv = 0
        total_contributions = 0
        if contribution_amount > 0 and contribution_frequency > 0 and time > 0:
            total_contributions = contribution_amount * contribution_frequency * time

            if is_continuous:
                 # Formula for FV of continuous contributions
                 annual_contribution = contribution_amount * contribution_frequency
                 if rate == 0:
                      annuity_fv = annual_contribution * time
                 else:
                     rt = rate * time
                     if rt > 700: return float('inf'), float('inf'), float('inf') # Approx overflow check
                     annuity_fv = annual_contribution * (math.exp(rt) - 1) / rate
            else:
                # **ASSUMPTION:** Contribution frequency matches compounding frequency (n_compound)
                # We use n_compound for the annuity calculation periods.
                num_total_periods = n_compound * time
                periodic_rate = rate / n_compound

                if periodic_rate == 0: # Zero interest
                    annuity_fv = contribution_amount * num_total_periods
                else:
                    # Standard Future Value of Ordinary Annuity formula
                    fv_factor = ((1 + periodic_rate) ** num_total_periods - 1) / periodic_rate
                    annuity_fv = contribution_amount * fv_factor
                    # Check for potential overflow in annuity part
                    if annuity_fv == float('inf') or fv_factor == float('inf'):
                         return float('inf'), float('inf'), float('inf')

        # 3. Total Future Value
        final_amount = principal_fv + annuity_fv

        # 4. Total Interest Earned
        # Ensure interest isn't negative due to float precision issues
        total_interest = max(0, final_amount - principal - total_contributions)

        # Handle potential direct overflow from addition
        if final_amount == float('inf'):
             return float('inf'), float('inf'), float('inf')

        return final_amount, total_interest, total_contributions

    except OverflowError:
        return float('inf'), float('inf'), float('inf')
    except (ValueError, TypeError) as e: # Catch calculation domain errors etc.
        raise e # Re-raise specific calculation errors
    except Exception as e:
        # Catch any other unexpected calculation error
        raise Exception(f"An unexpected error occurred during calculation: {e}")

# --- Streamlit User Interface (MODIFIED) ---
st.set_page_config(page_title="Compound Interest Calculator", layout="wide")

st.title("💰 Compound Interest & Savings Calculator")
st.write("Project investment growth with initial principal and regular contributions.")

# --- Input Widgets ---
with st.form("interest_contribution_form"):
    st.subheader("Initial Investment")
    col1, col2 = st.columns(2)

    with col1:
        principal = st.number_input(
            "Principal Amount ($)",
            min_value=0.0, value=1000.0, step=100.0, format="%.2f",
            help="The initial amount of money you are starting with."
        )
        rate_percent = st.number_input(
            "Annual Interest Rate (%)",
            min_value=0.0, value=5.0, step=0.1, format="%.2f",
            help="The nominal annual interest rate (e.g., enter 5 for 5%)."
        )

    with col2:
        time = st.number_input(
            "Time Period (Years)",
            min_value=0.0, value=10.0, step=0.5, format="%.1f",
            help="The number of years the money will be invested or saved."
        )
        compound_options = {
            "Annually (1/year)": 1, "Semi-Annually (2/year)": 2, "Quarterly (4/year)": 4,
            "Monthly (12/year)": 12, "Bi-Weekly (26/year)": 26, "Weekly (52/year)": 52,
            "Daily (365/year)": 365, "Continuously": "continuously"
        }
        selected_compound_option = st.selectbox(
            "Interest Compounding Frequency",
            options=list(compound_options.keys()), index=3, # Default Monthly
            help="How often the interest is calculated and added to the principal."
        )

    st.divider()
    st.subheader("Regular Contributions (Optional)")
    col3, col4 = st.columns(2)
    with col3:
        contribution_amount = st.number_input(
            "Contribution Amount per Period ($)",
            min_value=0.0, value=100.0, step=10.0, format="%.2f",
            help="The amount added regularly to the investment."
        )
    with col4:
        # Define contribution frequency options - CAN differ from compounding
        contrib_freq_options = {
             "Matches Compounding": "match", # Special value
             "Monthly": 12, "Quarterly": 4, "Semi-Annually": 2, "Annually": 1,
             "Bi-Weekly": 26, "Weekly": 52,
        }
        selected_contrib_freq_text = st.selectbox(
            "Contribution Frequency",
            options=list(contrib_freq_options.keys()), index=0, # Default Match
            help="How often contributions are made."
        )


    # Submit button for the form
    submitted = st.form_submit_button("Calculate Future Value")

# --- Calculation and Display Logic (runs when form is submitted) ---
if submitted:
    compound_input = compound_options[selected_compound_option] # int or 'continuously'
    rate_decimal = rate_percent / 100.0

    # Determine the actual contribution frequency value
    if selected_contrib_freq_text == "Matches Compounding":
         if compound_input == "continuously":
              # Continuous contributions need a finite frequency for the formula PMT*freq*(e^rt-1)/r
              # Default to monthly if compounding is continuous and 'match' is selected.
              contribution_frequency = 12
              st.info("Contributions assumed to be spread evenly based on a Monthly frequency for continuous compounding calculation.")
         else: # It's an integer n
              contribution_frequency = compound_input
              # We need contribution_amount per compounding period for the standard discrete formula
              # If user selected 'match', contribution_amount is already correct.
    else:
        contribution_frequency = contrib_freq_options[selected_contrib_freq_text] # Get the integer value

    # ****** IMPORTANT ADJUSTMENT FOR DISCRETE COMPOUNDING ******
    # The standard FV annuity formula used requires the PMT *per compounding period*.
    # If contribution freq doesn't match compounding freq, we need to adjust.
    # Simple approach: Calculate total annual contribution and divide by compounding periods.
    # This assumes contributions are effectively spread evenly across compounding periods.
    contribution_per_compound_period = 0
    if compound_input != "continuously" and contribution_amount > 0:
        annual_contribution_total = contribution_amount * contribution_frequency
        n_compound = compound_input # Compounding freq
        if n_compound > 0:
             contribution_per_compound_period = annual_contribution_total / n_compound
             if selected_contrib_freq_text != "Matches Compounding":
                  st.info(f"Contribution frequency differs from compounding frequency. Calculation assumes the total annual contribution (${annual_contribution_total:,.2f}) is effectively added in portions (${contribution_per_compound_period:,.2f}) aligned with each compounding period.")
        else:
             st.error("Compounding frequency must be positive for discrete calculation.")
             contribution_per_compound_period = 0 # Avoid calculation error
    elif compound_input == "continuously":
         contribution_per_compound_period = contribution_amount # Use original for continuous formula logic

    # Use contribution_per_compound_period only for the discrete annuity calc
    # Pass original contribution_amount and contribution_frequency to function for total calc and continuous case.


    try:
        # Use the adjusted contribution amount for the discrete annuity part within the function
        # The function needs modification to handle this adjusted PMT internally OR adjust here
        # Let's adjust the arguments passed for the discrete case:
        if compound_input != "continuously":
             # Pass the adjusted PMT, and make contribution_frequency match n_compound
             final_amount, total_interest, total_contributions = future_value_with_contributions(
                 principal, rate_decimal, time,
                 compound_type=compound_input, # Pass n
                 contribution_amount=contribution_per_compound_period, # Adjusted PMT
                 contribution_frequency=compound_input # Match n
             )
             # Recalculate actual total contributions based on user input
             actual_total_contributions = contribution_amount * contribution_frequency * time
             total_interest = max(0, final_amount - principal - actual_total_contributions) # Recalculate interest

        else: # Continuous
             final_amount, total_interest, total_contributions = future_value_with_contributions(
                 principal, rate_decimal, time,
                 compound_type="continuously",
                 contribution_amount=contribution_amount, # Original PMT
                 contribution_frequency=contribution_frequency # Original freq
             )


        st.subheader("Results")

        if final_amount == float('inf'):
             st.warning("📈 The resulting amount is extremely large (overflow). Check inputs, especially time and rate.")
        else:
            total_principal_and_contributions = principal + total_contributions

            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.metric(label="Future Value", value=f"${final_amount:,.2f}")
            with col_res2:
                st.metric(label="Total Principal & Contributions", value=f"${total_principal_and_contributions:,.2f}")
            with col_res3:
                 st.metric(label="Total Interest Earned", value=f"${total_interest:,.2f}")

            st.write("---")

            # --- Enhancement: Updated Pie Chart ---
            if final_amount > 0 and final_amount != float('inf'):
                labels = ['Initial Principal', 'Total Contributions', 'Interest Earned']
                values = [principal, total_contributions, total_interest]

                # Filter out zero values for a cleaner chart if needed
                non_zero_labels = [l for l, v in zip(labels, values) if v > 0.005] # Threshold for display
                non_zero_values = [v for v in values if v > 0.005]

                if non_zero_values: # Only plot if there's something to show
                    fig = go.Figure(data=[go.Pie(labels=non_zero_labels,
                                                 values=non_zero_values,
                                                 hole=.3,
                                                 hoverinfo='label+percent+value', textinfo='value',
                                                 marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c'] # Colors for P, C, I
                                                 )])
                    fig.update_layout(
                        title_text='Breakdown of Future Value',
                        annotations=[dict(text=f'Total<br>${final_amount:,.2f}', x=0.5, y=0.5, font_size=16, showarrow=False)],
                        legend_title_text='Components'
                    )
                    st.plotly_chart(fig, use_container_width=True)

    except (ValueError, TypeError) as e:
        st.error(f"Input Error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.exception(e) # Provides traceback for debugging complex errors
