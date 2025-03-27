import streamlit as st
import pandas as pd
import numpy_financial as npf # Need to install: pip install numpy-financial
import math

# --- Calculation Functions ---

def calculate_loan_payment(principal, annual_rate, years, payments_per_year):
    """Calculates the fixed periodic loan payment."""
    if principal <= 0: return 0
    if annual_rate < 0: raise ValueError("Annual rate cannot be negative.")
    if years <= 0: raise ValueError("Loan term must be positive.")
    if payments_per_year <= 0: raise ValueError("Payments per year must be positive.")

    if annual_rate == 0: # Handle zero interest rate
        return principal / (years * payments_per_year)

    periodic_rate = annual_rate / payments_per_year
    num_payments = years * payments_per_year
    try:
        # Using numpy_financial.pmt which handles formula correctly
        # Note: npf.pmt returns a negative value for payment (cash outflow)
        payment = -npf.pmt(periodic_rate, num_payments, principal)
        return payment
    except Exception as e:
        raise ValueError(f"Could not calculate payment: {e}")


def calculate_amortization(principal, annual_rate, years, payments_per_year, extra_payment=0):
    """Calculates the amortization schedule and summary stats."""
    if principal <= 0: return pd.DataFrame(), 0, 0, 0, 0, 0 # Empty df and zeros

    try:
        regular_payment = calculate_loan_payment(principal, annual_rate, years, payments_per_year)
    except ValueError as e:
        raise e # Re-raise error from payment calculation

    if regular_payment == 0 and principal > 0: # e.g., zero interest loan
         regular_payment = principal / (years * payments_per_year)

    periodic_rate = annual_rate / payments_per_year
    total_payment = regular_payment + extra_payment

    schedule = []
    current_balance = principal
    total_interest_paid = 0
    payment_num = 0

    while current_balance > 0.01 and payment_num < (years * payments_per_year * 2): # Safety break
        payment_num += 1
        interest_paid = current_balance * periodic_rate
        principal_paid = total_payment - interest_paid

        # Adjust last payment
        if principal_paid > current_balance:
            principal_paid = current_balance
            total_payment = principal_paid + interest_paid # Actual payment made

        current_balance -= principal_paid
        total_interest_paid += interest_paid

        # Ensure balance doesn't go significantly negative due to float precision
        if current_balance < 0:
             principal_paid += current_balance # Adjust principal back
             current_balance = 0

        schedule.append({
            "Payment #": payment_num,
            "Starting Balance": current_balance + principal_paid, # Bal before this payment
            "Payment": total_payment,
            "Principal Paid": principal_paid,
            "Interest Paid": interest_paid,
            "Ending Balance": current_balance
        })

        if current_balance <= 0.01: # Consider paid off
            break

        # Reset total_payment for next iteration if last payment was adjusted
        total_payment = regular_payment + extra_payment


    amortization_df = pd.DataFrame(schedule)
    total_paid = amortization_df["Payment"].sum()

    return amortization_df, regular_payment, total_paid, total_interest_paid, payment_num


# --- Streamlit User Interface ---
st.set_page_config(page_title="Loan Calculator", layout="wide")

st.title("🏦 Loan Payment & Amortization Calculator")
st.write("Analyze loan payments, total interest, and the impact of making extra payments.")

# --- Input Widgets ---
# Using st.form to group inputs and calculate only on submit
with st.form("loan_form"):
    col1, col2 = st.columns(2)

    with col1:
        loan_principal = st.number_input(
            "Loan Amount ($)",
            min_value=0.0,
            value=25000.0,
            step=1000.0,
            format="%.2f",
            help="The total amount of the loan.",
        )
        loan_rate_percent = st.number_input(
            "Annual Interest Rate (%)",
            min_value=0.0,
            value=6.5,
            step=0.1,
            format="%.2f",
            help="The annual interest rate for the loan (e.g., enter 6.5 for 6.5%).",
        )

    with col2:
        loan_years = st.number_input(
            "Loan Term (Years)",
            min_value=0.0,
            value=5.0,
            step=0.5,
            format="%.1f",
            help="The duration of the loan in years.",
        )
        # Define payment frequency options
        payment_freq_options = {
            "Monthly": 12,
            "Bi-Weekly": 26,
            "Weekly": 52,
            "Quarterly": 4,
            "Semi-Annually": 2,
            "Annually": 1,
        }
        selected_freq_text = st.selectbox(
            "Payment Frequency",
            options=list(payment_freq_options.keys()),
            index=0, # Default to Monthly
            help="How often payments are made."
        )
        payments_per_year = payment_freq_options[selected_freq_text]

    # Extra Payment Input (Outside columns, but inside form)
    extra_payment = st.number_input(
        "Extra Payment Per Period ($)",
        min_value=0.0,
        value=0.0,
        step=10.0,
        format="%.2f",
        help="Additional amount paid with each regular payment to pay off the loan faster.",
    )

    # Form submission button
    loan_submitted = st.form_submit_button("Calculate Loan Details")


# --- Calculation and Display Logic ---
if loan_submitted:
    loan_rate_decimal = loan_rate_percent / 100.0

    try:
        # --- Calculate Base Scenario (No Extra Payments) ---
        base_schedule_df, base_payment, base_total_paid, base_total_interest, base_num_payments = \
            calculate_amortization(loan_principal, loan_rate_decimal, loan_years, payments_per_year, 0)

        st.subheader("Loan Summary (Standard Payments)")
        if base_payment is not None and not base_schedule_df.empty:
            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.metric(label=f"{selected_freq_text} Payment", value=f"${base_payment:,.2f}")
            with col_res2:
                st.metric(label="Total Interest Paid", value=f"${base_total_interest:,.2f}")
            with col_res3:
                st.metric(label="Total Paid", value=f"${base_total_paid:,.2f}")
            st.caption(f"Loan paid off in {base_num_payments} payments over approx. {base_num_payments/payments_per_year:.1f} years.")
        else:
             st.warning("Could not calculate standard payment details. Check inputs.")

        # --- Calculate Scenario With Extra Payments ---
        if extra_payment > 0:
            st.write("---")
            st.subheader(f"Loan Summary (With ${extra_payment:,.2f} Extra Payment)")

            extra_schedule_df, _, extra_total_paid, extra_total_interest, extra_num_payments = \
                calculate_amortization(loan_principal, loan_rate_decimal, loan_years, payments_per_year, extra_payment)

            if not extra_schedule_df.empty:
                payments_saved = base_num_payments - extra_num_payments
                years_saved = payments_saved / payments_per_year
                interest_saved = base_total_interest - extra_total_interest

                col_ex1, col_ex2, col_ex3 = st.columns(3)
                with col_ex1:
                    st.metric(label="New Payoff Time", value=f"{extra_num_payments} payments (~{extra_num_payments/payments_per_year:.1f} yrs)")
                    st.caption(f"({payments_saved} payments / ~{years_saved:.1f} years sooner)")
                with col_ex2:
                    st.metric(label="Total Interest Paid", value=f"${extra_total_interest:,.2f}")
                with col_ex3:
                    st.metric(label="Interest Saved", value=f"${interest_saved:,.2f}", delta=f"${interest_saved:,.2f}", delta_color="inverse") # Show savings

                # Assign schedules for potential display later
                schedule_to_display = extra_schedule_df
                schedule_title = "Amortization Schedule (With Extra Payments)"

            else:
                st.warning("Could not calculate details with extra payments.")
                schedule_to_display = base_schedule_df # Fallback to base
                schedule_title = "Amortization Schedule (Standard Payments)"
        else:
            # If no extra payment, set schedule for display
            schedule_to_display = base_schedule_df
            schedule_title = "Amortization Schedule (Standard Payments)"


        # --- Display Amortization Table (Optional) ---
        st.write("---")
        if not schedule_to_display.empty:
             with st.expander(f"View {schedule_title}"):
                # Format dataframe for display
                display_df = schedule_to_display.copy()
                for col in ["Starting Balance", "Payment", "Principal Paid", "Interest Paid", "Ending Balance"]:
                    display_df[col] = display_df[col].map('${:,.2f}'.format)
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
             st.info("Amortization schedule could not be generated.")


    except (ValueError, TypeError) as e:
        st.error(f"Input Error or Calculation Problem: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.exception(e) # Show traceback for debugging if needed
