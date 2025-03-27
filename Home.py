import streamlit as st

st.set_page_config(
    page_title="FinCalc Pro",
    page_icon="✨", # Optional: add an emoji icon
    layout="wide"
)

# --- Title with Gradient Attempt (using Markdown and HTML/CSS) ---
# Note: Streamlit's native theming might override complex CSS sometimes.
# This is a basic example, more complex gradients might require more robust CSS.
gradient_text_html = """
<style>
.gradient-text {
    background: -webkit-linear-gradient(left, #FF8C00, #FF0080); /* Example gradient */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: bold; /* Make it bolder */
    font-size: 3em; /* Make it larger */
    display: inline; /* Ensure it behaves like text */
}
</style>
<div style="text-align: center;">
    <span class="gradient-text">The World's Most Advanced* Money Calculator</span>
    <p><small>*Maybe not, but it's pretty useful!</small></p>
</div>
"""
st.markdown(gradient_text_html, unsafe_allow_html=True)


st.write("") # Add some space
st.write("") # Add some space

st.markdown(
    """
    Welcome to **FinCalc Pro**!

    Your one-stop application for exploring compound interest and analyzing loan scenarios.

    ---

    **Navigate using the sidebar on the left** to access the calculators:

    *   **💰 Interest Calculator:** Project investment growth with various compounding options.
    *   **🏦 Loan Calculator:** Analyze loan payments, total interest, and the impact of extra payments.

    ---
    """
)

# --- Placeholder for Buttons (Less standard for multi-page navigation) ---
# While requested, Streamlit's primary navigation is the sidebar.
# Adding buttons here that *don't* navigate can be confusing.
# Instead, we clearly instruct the user to use the sidebar above.
# If you absolutely wanted buttons, they would typically trigger actions
# *on this page* or potentially use session state hacks to switch pages,
# which is usually less clean than the built-in sidebar.

# Example of how you *might* add non-functional buttons for visual cue:
# st.write("---")
# st.write("Quick Access (Use Sidebar for Navigation):")
# col1, col2 = st.columns(2)
# with col1:
#     st.button("Go to Interest Calculator", disabled=True, help="Use sidebar navigation")
# with col2:
#     st.button("Go to Loan Calculator", disabled=True, help="Use sidebar navigation")


st.info("👈 Use the navigation menu on the left to select a calculator!")

st.caption("Built with Streamlit.")
