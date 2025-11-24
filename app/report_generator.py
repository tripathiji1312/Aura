# file: report_generator.py

import os
from fpdf import FPDF
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# We need to talk to the database to get all the user's data
import database as db

# --- Helper to create a temporary folder for our generated files ---
TEMP_FOLDER = 'temp_reports'
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)


def create_glucose_chart_image(glucose_readings: list, user_id: int) -> str:
    """
    Generates a PNG image of the user's glucose chart and saves it temporarily.
    Returns the path to the saved image.
    """
    if not glucose_readings:
        return None

    # Extract data for plotting
    times = [r['timestamp'] for r in glucose_readings]
    values = [r['glucose_value'] for r in glucose_readings]

    # Create the plot using Matplotlib
    fig, ax = plt.subplots(figsize=(10, 4)) # 10 inches wide, 4 inches tall
    ax.plot(times, values, marker='o', linestyle='-', color='#7C3AED', markersize=2, label='Glucose (mg/dL)')
    
    # Add horizontal lines for target range
    ax.axhspan(70, 180, color='green', alpha=0.1, label='Target Range (70-180)')
    
    # Formatting the plot to look professional
    ax.set_title("Glucose Readings (Last 24 Hours)", fontsize=16)
    ax.set_ylabel("Glucose (mg/dL)")
    ax.set_xlabel("Time")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()
    
    # Format the x-axis to show time nicely
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate() # Rotate date labels
    
    plt.tight_layout()
    
    # Save the plot to a temporary file
    chart_path = os.path.join(TEMP_FOLDER, f"temp_chart_user_{user_id}.png")
    plt.savefig(chart_path)
    plt.close(fig) # Close the figure to free up memory
    
    return chart_path


def create_user_report(user_id: int) -> str:
    """
    Generates a comprehensive PDF report for a user.
    Returns the path to the generated PDF file.
    """
    print(f"--- [Report Gen] Creating report for user {user_id} ---")
    
    # 1. Fetch all necessary data from the database
    dashboard_data = db.get_dashboard_data_for_user(user_id)
    user_profile = dashboard_data.get('user_profile', {})
    health_score = dashboard_data.get('health_score', {})
    
    # 2. Generate the glucose chart image
    chart_path = create_glucose_chart_image(dashboard_data.get('glucose_readings', []), user_id)

    # 3. Create the PDF document
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- PDF Header ---
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, "Aura Health Report", 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Patient: {user_profile.get('name', 'N/A')}", 0, 1, 'C')
    pdf.cell(0, 8, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
    pdf.ln(10)

    # --- Summary Section ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "24-Hour Health Summary", 0, 1)
    
    pdf.set_font("Arial", '', 12)
    score_msg = f"Daily Health Score: {health_score.get('score', 'N/A')} / 100"
    tir_msg = f"Time in Range (70-180 mg/dL): {health_score.get('time_in_range_percent', 'N/A')}%"
    hypo_msg = f"Low Glucose Events (< 70 mg/dL): {health_score.get('hypo_events_count', 'N/A')}"
    
    pdf.multi_cell(0, 8, f"{score_msg}\n{tir_msg}\n{hypo_msg}")
    pdf.ln(10)

    # --- Glucose Chart Section ---
    if chart_path:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Glucose Chart (Last 24 Hours)", 0, 1)
        pdf.image(chart_path, x=10, y=None, w=190) # w=190mm fits a standard A4 page
        os.remove(chart_path) # Clean up the temporary image file
        pdf.ln(5)

    # --- Recent Meal Logs Section ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Recent Meal Logs", 0, 1)
    
    pdf.set_font("Arial", 'B', 10)
    # Create table header
    pdf.cell(40, 8, 'Time', 1)
    pdf.cell(110, 8, 'Description', 1)
    pdf.cell(40, 8, 'Carbs (g)', 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 10)
    for meal in dashboard_data.get('recent_meals', []):
        time = meal['timestamp'].strftime('%b %d, %H:%M')
        desc = meal['meal_description'][:60] # Truncate long descriptions
        carbs = str(meal['carb_count'])
        pdf.cell(40, 6, time, 1)
        pdf.cell(110, 6, desc, 1)
        pdf.cell(40, 6, carbs, 1)
        pdf.ln()

    # 4. Save the PDF to a file
    pdf_filename = f"aura_report_user_{user_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    pdf_path = os.path.join(TEMP_FOLDER, pdf_filename)
    pdf.output(pdf_path)
    
    print(f"--- [Report Gen] SUCCESS: Saved PDF to {pdf_path} ---")
    return pdf_path, pdf_filename