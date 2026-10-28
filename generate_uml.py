import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.platypus import SimpleDocTemplate, PageBreak, Image as RLImage, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

def draw_actor_pil(draw, font, name, cx, cy):
    # Head
    draw.ellipse([cx - 10, cy - 35, cx + 10, cy - 15], outline="black", width=2)
    # Body
    draw.line([cx, cy - 15, cx, cy + 20], fill="black", width=2)
    # Arms
    draw.line([cx - 20, cy - 5, cx + 20, cy - 5], fill="black", width=2)
    # Legs
    draw.line([cx, cy + 20, cx - 12, cy + 45], fill="black", width=2)
    draw.line([cx, cy + 20, cx + 12, cy + 45], fill="black", width=2)
    # Label
    draw.text((cx, cy + 55), name, fill="black", font=font, anchor="mm")

def draw_usecase_pil(draw, font, name, x, y, w, h):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill="#f8f9fa", outline="#0d6efd", width=2)
    draw.text((x + w/2, y + h/2), name, fill="black", font=font, anchor="mm")

def create_usecase_diagram():
    print("Generating Use Case Diagram using PIL...")
    # Create image
    img = Image.new("RGB", (650, 650), "white")
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 12)
        actor_font = ImageFont.truetype("arial.ttf", 10)
        uc_font = ImageFont.truetype("arial.ttf", 9)
    except IOError:
        # Fallback to default
        title_font = actor_font = uc_font = ImageFont.load_default()
        
    # System boundary box
    draw.rectangle([150, 40, 500, 620], outline="#0d6efd", width=2)
    draw.text((325, 55), "System Boundary: Hospital Prep & Readiness", fill="#0b5ed7", font=title_font, anchor="mm")
    
    # Actors
    draw_actor_pil(draw, actor_font, "Patient", 60, 300)
    draw_actor_pil(draw, actor_font, "Attending Doctor", 580, 240)
    draw_actor_pil(draw, actor_font, "Administrator", 580, 460)
    
    # 11 Use Cases
    ucs = [
        ("UC1: User Authentication & Login", 80),
        ("UC2: Manage User Profiles", 130),
        ("UC3: Configure Master Procedures", 180),
        ("UC4: View Pre-operative Checklist", 230),
        ("UC5: Upload Clinical Reports", 280),
        ("UC6: Log Patient Vitals Data", 330),
        ("UC7: Schedule Procedure Slots", 380),
        ("UC8: Verify & Signoff Checklist", 430),
        ("UC9: Override Readiness Status", 480),
        ("UC10: View Reports & Suggestions", 530),
        ("UC11: Trigger Risk Alerts", 580)
    ]
    
    for label, y in ucs:
        draw_usecase_pil(draw, uc_font, label, 190, y - 16, 270, 32)
        
    # Association Lines
    # Patient connects to: UC1, UC2, UC4, UC5, UC6, UC10
    draw.line([60, 300, 190, 96], fill="#6c757d", width=1)
    draw.line([60, 300, 190, 146], fill="#6c757d", width=1)
    draw.line([60, 300, 190, 246], fill="#6c757d", width=1)
    draw.line([60, 300, 190, 296], fill="#6c757d", width=1)
    draw.line([60, 300, 190, 346], fill="#6c757d", width=1)
    draw.line([60, 300, 190, 546], fill="#6c757d", width=1)

    # Doctor connects to: UC1, UC2, UC7, UC8, UC9, UC10, UC11
    draw.line([580, 240, 460, 96], fill="#6c757d", width=1)
    draw.line([580, 240, 460, 146], fill="#6c757d", width=1)
    draw.line([580, 240, 460, 396], fill="#6c757d", width=1)
    draw.line([580, 240, 460, 446], fill="#6c757d", width=1)
    draw.line([580, 240, 460, 496], fill="#6c757d", width=1)
    draw.line([580, 240, 460, 546], fill="#6c757d", width=1)
    draw.line([580, 240, 460, 596], fill="#6c757d", width=1)

    # Admin connects to: UC1, UC2, UC3, UC7, UC10
    draw.line([580, 460, 460, 96], fill="#6c757d", width=1)
    draw.line([580, 460, 460, 146], fill="#6c757d", width=1)
    draw.line([580, 460, 460, 196], fill="#6c757d", width=1)
    draw.line([580, 460, 460, 396], fill="#6c757d", width=1)
    draw.line([580, 460, 460, 546], fill="#6c757d", width=1)
    
    # Save Image
    img.save("usecase_diagram.png", "PNG")
    print("Use Case Diagram saved to usecase_diagram.png")

def draw_class_pil(draw, title_font, content_font, title, attributes, methods, x, y, w, h):
    # Main Box
    draw.rectangle([x, y, x + w, y + h], fill="#f8f9fa", outline="black", width=2)
    # Header Area
    header_h = 24
    draw.rectangle([x, y, x + w, y + header_h], fill="#cfe2ff", outline="black", width=2)
    # Title
    draw.text((x + w/2, y + header_h/2), title, fill="black", font=title_font, anchor="mm")
    
    # Separator
    sep_y = y + header_h + len(attributes)*13 + 6
    draw.line([x, sep_y, x + w, sep_y], fill="black", width=1)
    
    # Attributes text
    curr_y = y + header_h + 4
    for attr in attributes:
        draw.text((x + 6, curr_y), attr, fill="black", font=content_font)
        curr_y += 13
        
    # Methods text
    curr_y = sep_y + 4
    for meth in methods:
        draw.text((x + 6, curr_y), meth, fill="black", font=content_font)
        curr_y += 13

def create_class_diagram():
    print("Generating Class Diagram using PIL...")
    # Clean simple layout of 7 classes
    img = Image.new("RGB", (850, 520), "white")
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 10)
        class_title_font = ImageFont.truetype("arial.ttf", 10)
        content_font = ImageFont.truetype("arial.ttf", 9)
    except IOError:
        title_font = class_title_font = content_font = ImageFont.load_default()
        
    draw.text((425, 20), "Hospital Procedure Preparation and Readiness System – UML Class Diagram", fill="#0b5ed7", font=title_font, anchor="mm")
    
    # Draw simple rectangular class boxes
    # User (Left Col Top)
    draw_class_pil(draw, class_title_font, content_font, "User", [
        "+ id: int",
        "+ role_id: int",
        "+ username: str",
        "+ email: str",
        "+ first_name: str",
        "+ last_name: str",
        "+ phone: str",
        "+ is_active: bool"
    ], [], 30, 50, 160, 140)
    
    # Patient (Left Col Bottom)
    draw_class_pil(draw, class_title_font, content_font, "Patient", [
        "+ patient_id: int",
        "+ date_of_birth: date",
        "+ gender: enum"
    ], [], 30, 270, 160, 80)
    
    # Doctor (Middle Col Top)
    draw_class_pil(draw, class_title_font, content_font, "Doctor", [
        "+ doctor_id: int",
        "+ specialization: str"
    ], [], 240, 50, 160, 70)
    
    # ScheduledProcedure (Middle Col Bottom)
    draw_class_pil(draw, class_title_font, content_font, "ScheduledProcedure", [
        "+ id: int",
        "+ patient_id: int",
        "+ doctor_id: int",
        "+ procedure_id: int",
        "+ scheduled_at: datetime",
        "+ location: str",
        "+ status: enum"
    ], [], 240, 170, 170, 130)
    
    # Procedure (Right Col Top)
    draw_class_pil(draw, class_title_font, content_font, "Procedure", [
        "+ id: int",
        "+ code: str",
        "+ name: str",
        "+ category: str"
    ], [], 450, 50, 160, 95)
    
    # ChecklistItem (Right Col Middle)
    draw_class_pil(draw, class_title_font, content_font, "ChecklistItem", [
        "+ id: int",
        "+ scheduled_procedure_id: int",
        "+ task_name: str",
        "+ task_type: enum",
        "+ description: text",
        "+ due_by_datetime: datetime",
        "+ is_critical: bool",
        "+ status: enum"
    ], [], 450, 170, 170, 140)
    
    # UploadedReport (Far Right Col Bottom)
    draw_class_pil(draw, class_title_font, content_font, "UploadedReport", [
        "+ id: int",
        "+ checklist_item_id: int",
        "+ patient_id: int",
        "+ file_name: str",
        "+ uploaded_at: timestamp"
    ], [], 650, 290, 160, 105)

    # Drawing Class Relationship Lines
    # User ➔ Doctor
    draw.line([190, 85, 240, 85], fill="black", width=1)
    draw.text((215, 72), "1", fill="black", font=content_font)
    draw.text((215, 87), "0..1", fill="black", font=content_font)
    
    # User ➔ Patient
    draw.line([110, 190, 110, 270], fill="black", width=1)
    draw.text((95, 205), "1", fill="black", font=content_font)
    draw.text((95, 250), "0..1", fill="black", font=content_font)

    # Patient ➔ ScheduledProcedure
    draw.line([190, 310, 220, 310], fill="black", width=1)
    draw.line([220, 310, 220, 235], fill="black", width=1)
    draw.line([220, 235, 240, 235], fill="black", width=1)
    draw.text((195, 295), "1", fill="black", font=content_font)
    draw.text((225, 220), "0..*", fill="black", font=content_font)

    # Doctor ➔ ScheduledProcedure
    draw.line([320, 120, 320, 170], fill="black", width=1)
    draw.text((325, 125), "1", fill="black", font=content_font)
    draw.text((325, 150), "0..*", fill="black", font=content_font)

    # Procedure ➔ ScheduledProcedure
    draw.line([450, 95, 425, 95], fill="black", width=1)
    draw.line([425, 95, 425, 200], fill="black", width=1)
    draw.line([425, 200, 410, 200], fill="black", width=1)
    draw.text((435, 80), "1", fill="black", font=content_font)
    draw.text((415, 185), "0..*", fill="black", font=content_font)

    # ScheduledProcedure ➔ ChecklistItem
    draw.line([410, 235, 450, 235], fill="black", width=1)
    draw.text((415, 220), "1", fill="black", font=content_font)
    draw.text((435, 220), "0..*", fill="black", font=content_font)

    # ChecklistItem ➔ UploadedReport
    draw.line([620, 240, 640, 240], fill="black", width=1)
    draw.line([640, 240, 640, 340], fill="black", width=1)
    draw.line([640, 340, 650, 340], fill="black", width=1)
    draw.text((625, 225), "1", fill="black", font=content_font)
    draw.text((642, 322), "0..1", fill="black", font=content_font)

    # Patient ➔ UploadedReport
    draw.line([110, 350, 110, 430], fill="black", width=1)
    draw.line([110, 430, 730, 430], fill="black", width=1)
    draw.line([730, 430, 730, 395], fill="black", width=1)
    draw.text((115, 360), "1", fill="black", font=content_font)
    draw.text((735, 405), "0..*", fill="black", font=content_font)
    
    # Save Image
    img.save("class_diagram.png", "PNG")
    print("Class Diagram saved to class_diagram.png")

def generate_pdf_report():
    print("Compiling combined PDF report using Pillow generated images...")
    pdf_filename = "MediPrep_UML_Diagrams.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0b5ed7'),
        alignment=1, # Center
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.gray,
        alignment=1,
        spaceAfter=30
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0b5ed7'),
        spaceAfter=10
    )
    
    # Cover / Header
    story.append(Paragraph("Hospital Procedure Preparation and Readiness System", title_style))
    story.append(Paragraph("System Architecture UML Documentation - MCA Project Submission", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Page 1: Use Case Diagram
    story.append(Paragraph("1. System Use Case Diagram", h2_style))
    story.append(RLImage("usecase_diagram.png", width=520, height=520))
    story.append(PageBreak())
    
    # Page 2: Class Diagram
    story.append(Paragraph("2. System UML Class Diagram", h2_style))
    story.append(RLImage("class_diagram.png", width=530, height=450))
    
    doc.build(story)
    print(f"UML Diagrams compiled into PDF: {pdf_filename}")

if __name__ == "__main__":
    create_usecase_diagram()
    create_class_diagram()
    generate_pdf_report()
