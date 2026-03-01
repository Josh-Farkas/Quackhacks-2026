"""Creates a PDF report based on data"""
import io
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak

def fig_to_image(fig, width=6*inch):
    """Convert a matplotlib figure to a reportlab Image object."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    # Scale height proportionally
    w_px, h_px = fig.get_size_inches() * fig.dpi
    aspect = h_px / w_px
    return Image(buf, width=width, height=width * aspect)


def generate_report(stress_over_time, avg_stress_per_game, output_path="report.pdf"):
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
    content.append(Paragraph("This report visualizes correlations between your gaming sessions and their respective impacts on your body, like on your stress over time broken down by game, average stress by game, and on your sleep scores.", styles["Normal"]))
    content.append(Spacer(1, 0.3 * inch))

    # Adds Stress Over Time Report
    add_fig_report(stress_over_time, "Stress Over Time", "The chart below shows your stress level throughout the session. Each color represents a different game being played at that moment.")
    content.append(PageBreak())

    # Adds Average Stress Per Game Report
    add_fig_report(avg_stress_per_game, "Average Stress by Game", "The bar chart below shows the mean stress level recorded during each game. Higher values indicate more stressful sessions.")

    doc.build(content)
    print(f"Report saved to {output_path}")
