"""Creates a PDF report based on data"""
import io
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors


def fig_to_image(fig, width=6*inch):
    """Convert a matplotlib figure to a reportlab Image object."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    # Scale height proportionally
    w_px, h_px = fig.get_size_inches() * fig.dpi
    aspect = h_px / w_px
    return Image(buf, width=width, height=width * aspect)


def make_cards(cards):
    """
    Build a row of info cards from a list of (label, value) tuples.
    e.g. [("Highest Stress Game", "CS2"), ("Peak Stress", "87 @ 14:32")]
    """
    headers = [Paragraph(f"<b>{label}</b>", getSampleStyleSheet()["Normal"]) for label, _ in cards]
    values  = [Paragraph(str(value),         getSampleStyleSheet()["Normal"]) for _, value  in cards]

    table = Table(
        [headers, values],
        colWidths=[6.5 * inch / len(cards)] * len(cards),
    )
    table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  colors.HexColor("#2c2c2c")),
        ("BACKGROUND",   (0, 1), (-1, 1),  colors.HexColor("#f5f5f5")),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("TEXTCOLOR",    (0, 1), (-1, 1),  colors.HexColor("#222222")),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE",     (0, 0), (-1, 0),  8),
        ("FONTSIZE",     (0, 1), (-1, 1),  10),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return table


def generate_report(stress_over_time, avg_stress_per_game, body_battery_over_time, peak_stress_value, peak_stress_time, output_path="report.pdf",):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    content = []

    def add_fig_report(fig, title, paragraph):
        content.append(Paragraph(title, styles["Heading1"]))
        content.append(Paragraph(paragraph, styles["Normal"]))
        content.append(Spacer(1, 0.15 * inch))
        content.append(fig_to_image(fig))
        plt.close(fig)

    # Adds Title
    content.append(Paragraph("Recent Impacts of Gaming on Your Sleep and Mental Health", styles["Title"]))
    content.append(Spacer(1, 0.2 * inch))
    content.append(Paragraph("This report visualizes correlations between your gaming sessions and their respective impacts on your body, like on your stress over time broken down by game, average stress by game, and body battery.", styles["Normal"]))
    content.append(Spacer(1, 0.3 * inch))

    # Adds Stress Over Time Report
    add_fig_report(stress_over_time, "Stress Over Time", "The chart below shows your stress level throughout the time period. Each color indicates when different games were played.")
    content.append(Paragraph(f"Peak Stress: {peak_stress_value:.0f} at {peak_stress_time}"))
    content.append(PageBreak())
    

    # Adds Average Stress Per Game Report
    add_fig_report(avg_stress_per_game, "Average Stress by Game", "The bar chart below shows the mean stress level recorded during each game. Higher values indicate more stressful sessions.")
    content.append(PageBreak())

    # Adds Body Battery by Game Over Time Report
    add_fig_report(body_battery_over_time, "Body Battery by Game Over Time", "The chart below shows your body battery levels throughout the time period. Each color indicates when different games were played.")

    doc.build(content)
    print(f"Report saved to {output_path}")
