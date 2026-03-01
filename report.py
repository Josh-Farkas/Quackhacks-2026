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


def generate_report(stress_over_time, avg_stress_per_game, output_path="stress_report.pdf"):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []

    # Title
    story.append(Paragraph("Gaming Stress Report", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "This report summarises your stress levels recorded during gaming sessions, "
        "broken down by game and over time.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.3 * inch))

    # Stress over time
    story.append(Paragraph("Stress Over Time", styles["Heading1"]))
    story.append(Paragraph(
        "The chart below shows your stress level throughout the session. "
        "Each colour represents a different game being played at that moment.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.15 * inch))

    fig1 = stress_over_time   # your existing plot function,
    story.append(fig_to_image(fig1))            # modified to return fig instead of plt.show()
    plt.close(fig1)

    story.append(PageBreak())

    # Average stress per game
    story.append(Paragraph("Average Stress by Game", styles["Heading1"]))
    story.append(Paragraph(
        "The bar chart below shows the mean stress level recorded during each game. "
        "Higher values indicate more stressful sessions.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.15 * inch))

    fig2 = avg_stress_per_game
    story.append(fig_to_image(fig2))
    plt.close(fig2)

    doc.build(story)
    print(f"Report saved to {output_path}")