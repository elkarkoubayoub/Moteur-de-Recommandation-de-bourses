import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_cv(cv_data, output_path):
    """
    Generates a professional PDF CV based on Botpress user data.
    cv_data expects: user_name, email, education, experience, skills, languages
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title / Name
    pdf.set_font('Arial', 'B', 24)
    name = cv_data.get('user_name', 'Student Name')
    pdf.cell(0, 15, name, ln=True, align='C')
    
    # Email
    pdf.set_font('Arial', '', 12)
    email = cv_data.get('email', 'email@example.com')
    pdf.cell(0, 10, f'Email: {email}', ln=True, align='C')
    pdf.ln(10)
    
    # Sections
    sections = [
        ('Education', cv_data.get('education', 'No education listed.')),
        ('Experience', cv_data.get('experience', 'No experience listed.')),
        ('Skills', cv_data.get('skills', 'No specific skills listed.')),
        ('Languages', cv_data.get('languages', 'No languages listed.'))
    ]
    
    for title, content in sections:
        pdf.set_font('Arial', 'B', 14)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 8, title, ln=True, fill=True)
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 11)
        # Ensure we handle potential line breaks from the user text
        pdf.multi_cell(0, 6, str(content))
        pdf.ln(5)
    
    # Save the file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    return True
