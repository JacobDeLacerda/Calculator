import streamlit as st
import math
import plotly.graph_objects as go # For chart

# --- Calculation Function (Slightly enhanced from before) ---
# (Keep the robust compound_interest function from the previous version)
def compound_interest(principal, rate, time, compound_type="annually", num_times=1):
    """
    Calculates compound interest. Returns (final_amount, total_interest).
    (Keep the full docstring and validation from the previous robust version)
    """
    # --- PASTE THE FULL compound_interest FUNCTION HERE ---
    # Input Type Validation
    if not all(isinstance(arg, (int, float)) for arg in [principal, rate, time]):
        raise TypeError("Principal, rate, and time must be numbers.")
    # Value Validation
    if principal < 0:
        raise ValueError("Principal cannot be negative.")
    if rate < 0:
        raise ValueError("Interest rate cannot be negative.")
    if time < 0:
        raise ValueError("Time cannot be negative.")

    # Determine actual num_times for calculation based on compound_type
    is_continuous = False
    if compound_type == "continuously":
        is_continuous = True
        actual_num_times = None # Not used in formula
    elif isinstance(compound_type, int):
        if compound_type <= 0:
            raise ValueError("Number of times compounded must be positive.")
        actual_num_times = compound_type
    elif compound_type == "annually":
        actual_num_times = 1
    else: # It's one of the text options mapped to an int
        if not isinstance(num_times, int) or num_times <= 0:
             raise ValueError("Number of times compounded must be a positive integer.")
        actual_num_times = num_times

    # --- Calculation ---
    try:
        if is_continuous:
            if rate == 0:
                 final_amount = principal
            else:
                 # Handle potential overflow for extremely large rt
                 rt = rate * time
                 if rt > 700: # exp(709) is near max float limit
                    return float('inf'), float('inf')
                 final_amount = principal * math.exp(rt)
        else: # Compounded n times
            base = 1 + rate / actual_num_times
            exponent = actual_num_times * time
             # Handle potential overflow for large exponents
            if exponent * math.log(base if base > 0 else 1) > 700: # Check approx log(result)
                return float('inf'), float('inf')
            final_amount = principal * (base ** exponent)

        # Handle potential precision issues resulting in tiny negative interest
        total_interest = max(0, final_amount - principal)
        return final_amount, total_interest

    except OverflowError:
        return float('inf'), float('inf')
    except ValueError as e: # Catch specific calculation errors like domain errors
        raise ValueError(f"Calculation error: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during calculation: {e}")
# --- END OF compound_interest FUNCTION ---


# --- Streamlit User Interface ---
st.set_page_config(page_title="Compound Interest Calculator", layout="wide") # Good practice per page

st.title("💰 Compound Interest Calculator")
st.write("Project how your savings or investments can grow over time.")

# --- Input Widgets ---
with st.form("interest_form"):
    col1, col2 = st.columns(2)

    with col1:
        principal = st.number_input(
            "Principal Amount ($)",
            min_value=0.0,
            value=1000.0, # Add a default value
            step=100.0,
            format="%.2f",
            help="The initial amount of money you are starting with."
        )
        rate_percent = st.number_input(
            "Annual Interest Rate (%)",
            min_value=0.0,
            value=5.0, # Default
            step=0.1,
            format="%.2f",
            help="The nominal annual interest rate (e.g., enter 5 for 5%)."
        )
        time = st.number_input(
            "Time Period (Years)",
            min_value=0.0,
            value=10.0, # Default
            step=0.5,
            format="%.1f",
            help="The number of years the money will be invested or saved."
        )

    with col2:
        compound_options = {
            "Annually (1/year)": 1,
            "Semi-Annually (2/year)": 2,
            "Quarterly (4/year)": 4,
            "Monthly (12/year)": 12,
            "Bi-Weekly (26/year)": 26, # Added
            "Weekly (52/year)": 52,   # Added
            "Daily (365/year)": 365,
            "Continuously": "continuously"
        }
        selected_compound_option = st.selectbox(
            "Compounding Frequency",
            options=list(compound_options.keys()),
            index=3, # Default to Monthly
            help="How often the interest is calculated and added to the principal."
        )

    # Submit button for the form
    submitted = st.form_submit_button("Calculate Interest")

# --- Calculation and Display Logic (runs when form is submitted) ---
if submitted:
    compound_input = compound_options[selected_compound_option]
    rate_decimal = rate_percent / 100.0

    try:
        if isinstance(compound_input, int):
            num_times = compound_input
            final_amount, total_interest = compound_interest(principal, rate_decimal, time, compound_type=num_times, num_times=num_times)
        else: # Continuously
            final_amount, total_interest = compound_interest(principal, rate_decimal, time, compound_type="continuously")

        st.subheader("Results")

        if final_amount == float('inf'):
             st.warning("The resulting amount is too large to calculate accurately (overflow).")
        else:
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.metric(label="Final Amount", value=f"${final_amount:,.2f}")
            with col_res2:
                st.metric(label="Total Interest Earned", value=f"${total_interest:,.2f}")

            st.write("---")

            # --- Enhancement: Pie Chart ---
            if principal > 0 or total_interest > 0: # Avoid chart error if both are zero
                labels = ['Principal', 'Interest Earned']
                values = [principal, total_interest]

                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3,
                                            marker_colors=['#1f77b4', '#ff7f0e'], # Example colors
                                            hoverinfo='label+percent+value', textinfo='value')])
                fig.update_layout(
                    title_text='Principal vs. Interest Breakdown',
                    # Add annotation inside the hole
                    annotations=[dict(text=f'Total<br>${final_amount:,.2f}', x=0.5, y=0.5, font_size=16, showarrow=False)]
                )
                st.plotly_chart(fig, use_container_width=True)

            # Optional: Display the formula used (from previous version)
            st.write("---")
            # ... (add st.latex and st.caption as before if desired) ...


    except (ValueError, TypeError) as e:
        st.error(f"Input Error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

st.caption("Note: This calculation assumes no additional contributions or withdrawals.")
