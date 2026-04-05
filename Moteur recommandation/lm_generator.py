import os

def generate_motivation_letter_text(lm_data):
    """
    Generates a personalized motivation letter using a structured template.
    If you choose to integrate OpenAI, this template serves as an excellent prompt or fallback.
    lm_data expects: user_name, target_country, level, field, scholarship, motivation, project
    """
    name = lm_data.get('user_name', '[Your Name]')
    country = lm_data.get('target_country', '[Target Country]')
    level = lm_data.get('level', '[Degree Level]')
    field = lm_data.get('field', '[Field of Study]')
    scholarship = lm_data.get('scholarship', '[Scholarship Name]')
    motivation = lm_data.get('motivation', '[State your core motivation here]')
    project = lm_data.get('project', '[Describe your future professional project]')
    
    letter = f"""
Dear Selection Committee,

I am writing to express my profound interest in the {scholarship} program. As an ambitious student pursuing higher education at the {level} level in {field}, I am highly motivated by the academic excellence and cultural opportunities offered by institutions in {country}.

{motivation}

Throughout my academic journey, I have developed a strong foundation in my discipline. Receiving the {scholarship} would be an invaluable step towards achieving my goals.

My long-term academic and professional objective is to:
{project}

I firmly believe that your program aligns perfectly with my aspirations, and I am confident that I can contribute positively to your academic community. 

Thank you for considering my application. I look forward to the possibility of discussing how my background, skills, and enthusiasms match your requirements.

Sincerely,

{name}
"""
    return letter.strip()

def save_motivation_letter(lm_data, output_path):
    text = generate_motivation_letter_text(lm_data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    return True
