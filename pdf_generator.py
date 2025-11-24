# backend/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io
import textwrap

def generate_pdf(report, transcript, source_filename="lesson.mp4", teacher_info=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 72
    y = height - margin

    def new_page_if_needed(required_space=50):
        nonlocal y
        if y < margin + required_space:
            c.showPage()
            y = height - margin

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, y, "Teacher Lesson Evaluation Report")
    y -= 28

    if teacher_info:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"Teacher: {teacher_info.get('first_name', '')} {teacher_info.get('last_name', '')}")
        y -= 14
        c.setFont("Helvetica", 10)
        c.drawString(margin, y, f"Email: {teacher_info.get('email', '')}")
        y -= 14
        c.drawString(margin, y, "Educational Details:")
        y -= 12
        for line in split_text(teacher_info.get('education_details', ''), 90):
            new_page_if_needed()
            c.drawString(margin, y, line)
            y -= 12
        y -= 10

    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Source file: {source_filename}")
    y -= 18
    c.drawString(margin, y, f"Clarity Score: {report.get('clarity_score', 'N/A')}/10")
    y -= 14
    c.drawString(margin, y, f"Engagement Score: {report.get('engagement_score', 'N/A')}/10")
    y -= 20

    # Summary
    new_page_if_needed()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Summary")
    y -= 16
    c.setFont("Helvetica", 10)
    for line in split_text(report.get("summary", ""), 90):
        new_page_if_needed()
        c.drawString(margin, y, line)
        y -= 12
    y -= 10

    # Strengths
    new_page_if_needed()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Strengths")
    y -= 14
    c.setFont("Helvetica", 10)
    for s in report.get("strengths", []):
        for line in split_text("• " + s, 90):
            new_page_if_needed()
            c.drawString(margin, y, line)
            y -= 12
    y -= 6

    # Weaknesses
    new_page_if_needed()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Weaknesses")
    y -= 14
    c.setFont("Helvetica", 10)
    for s in report.get("weaknesses", []):
        for line in split_text("• " + s, 90):
            new_page_if_needed()
            c.drawString(margin, y, line)
            y -= 12
    y -= 6

    # Suggestions
    new_page_if_needed()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Suggestions")
    y -= 14
    c.setFont("Helvetica", 10)
    for s in report.get("suggestions", []):
        for line in split_text("• " + s, 90):
            new_page_if_needed()
            c.drawString(margin, y, line)
            y -= 12
    y -= 10

    # Transcript excerpt
    new_page_if_needed(100)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Transcript (excerpt)")
    y -= 16
    c.setFont("Helvetica", 9)
    excerpt = transcript.strip()[:8000]  # limit size
    for line in split_text(excerpt, 90):
        new_page_if_needed()
        c.drawString(margin, y, line)
        y -= 11

    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def split_text(text, n):
    """Wrap text into lines of maximum n characters."""
    wrapped_lines = []
    for paragraph in text.split("\n"):
        lines = textwrap.wrap(paragraph, width=n)
        if not lines:
            wrapped_lines.append("")
        else:
            wrapped_lines.extend(lines)
    return wrapped_lines
