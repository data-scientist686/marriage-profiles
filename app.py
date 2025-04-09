from flask import Flask, render_template, request, flash
import os
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'  # Change this for production

# Filter options
MARITAL_STATUS_OPTIONS = [
    "Single", "Divorced", "Widow", "Widower", "Nikkah Break (No Rukhsati)",
    "Khula", "Third Marriage", "Married (1st wife Alive) want second marriage"
]

CAST_OPTIONS = [
    "Jutt", "Arain", "Rajput", "Mughal", "Malik", "Ansari", 
    "Gujjar", "Shiekh", "Butt", "Syed", "Raja", "Qureshi", 
    "Pathan", "Rehmani", "Kamboh", "Khokhar"
]

GENDER_OPTIONS = ["Male", "Female"]

def parse_height_input(height_str):
    """
    Convert height input string to total inches.
    Handles both formats:
    - 5.10 → 5'10" → 70 inches
    - 5.1 → 5'1" → 61 inches
    - 5.8 → 5'8" → 68 inches
    """
    try:
        if '.' in height_str:
            feet_part, inches_part = height_str.split('.')
            feet = int(feet_part)
            
            # Determine if single digit (5.1) or double digit (5.10)
            if len(inches_part) == 1 and int(inches_part) < 10:
                return feet * 12 + int(inches_part)  # 5.1 → 61 inches
            else:
                return feet * 12 + int(inches_part)  # 5.10 → 70 inches
        return int(float(height_str) * 12)  # Handle whole numbers
    except:
        return 0

def parse_profile_height(height_str):
    """Convert profile height text to total inches"""
    try:
        # Remove non-numeric characters except decimal point
        clean_str = re.sub(r'[^0-9.]', '', height_str)
        
        if '.' in clean_str:
            feet_part, inches_part = clean_str.split('.')
            feet = int(feet_part)
            
            # Check if inches part is single digit (5.1) or double digit (5.10)
            if len(inches_part) == 1 and int(inches_part) < 10:
                return feet * 12 + int(inches_part)
            else:
                return feet * 12 + int(inches_part)
                
        return int(float(clean_str) * 12)
    except:
        return 0

def extract_value(line, key):
    """Helper function to extract values from profile lines"""
    if key in line:
        value = line.split(":", 1)[1].strip().replace("*", "")
        return value
    return None

def read_profiles():
    profiles = []
    file_path = os.path.join(os.path.dirname(__file__), "profiles.txt")

    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read().strip().split("------------------------------------------------------------------------------------")
        
        for profile in data:
            profile = profile.strip()
            if not profile:
                continue

            profile_lines = profile.split("\n")
            profile_dict = {"Details": profile}

            for line in profile_lines:
                line = line.strip()
                if not line:
                    continue

                # Extract Age
                if line.startswith(("👔Age:", "👗Age:")):
                    try:
                        age_str = line.split(":", 1)[1].strip()
                        profile_dict["Age"] = int(re.search(r'\d+', age_str).group())
                    except:
                        profile_dict["Age"] = 0

                # Extract Height
                elif line.startswith(("👔Height:", "👗Height:")):
                    height_str = line.split(":", 1)[1].strip()
                    profile_dict["Height"] = parse_profile_height(height_str)

                # Extract Marital Status
                elif line.startswith(("👔Marital Status:", "👗Marital Status:")):
                    marital_status = extract_value(line, "Marital Status")
                    if marital_status:
                        profile_dict["Marital_Status"] = marital_status

                # Extract Cast
                elif line.startswith(("👔Cast:", "👗Cast:")):
                    cast = extract_value(line, "Cast")
                    if cast:
                        profile_dict["Cast"] = cast

                # Extract Gender
                elif line.startswith(("👔Gender:", "👗Gender:")):
                    gender = extract_value(line, "Gender")
                    if gender:
                        profile_dict["Gender"] = gender

            if profile_dict:
                profiles.append(profile_dict)

    return profiles

@app.route("/", methods=["GET", "POST"])
def index():
    profiles = read_profiles()
    filtered_profiles = profiles
    error = None

    # Default values
    min_age, max_age = 18, 40
    min_height_input, max_height_input = "5.4", "6.0"
    min_height, max_height = parse_height_input(min_height_input), parse_height_input(max_height_input)
    selected_marital_status = "All"
    selected_cast = "All"
    selected_gender = "All"

    if request.method == "POST":
        try:
            min_age = int(request.form.get("min_age", 18))
            max_age = int(request.form.get("max_age", 40))
            
            # Get and validate height inputs
            min_height_input = request.form.get("min_height", "5.4")
            max_height_input = request.form.get("max_height", "6.0")
            
            if not re.match(r'^\d+\.\d{1,2}$', min_height_input) or not re.match(r'^\d+\.\d{1,2}$', max_height_input):
                raise ValueError("Invalid height format")
                
            min_height = parse_height_input(min_height_input)
            max_height = parse_height_input(max_height_input)

            selected_marital_status = request.form.get("marital_status", "All").strip()
            selected_cast = request.form.get("cast", "All").strip()
            selected_gender = request.form.get("gender", "All").strip()

            # Validate ranges
            if min_age > max_age:
                error = "❌ Maximum age cannot be less than minimum age"
            elif min_height > max_height:
                error = "❌ Maximum height cannot be less than minimum height"
            
            if not error:
                filtered_profiles = [
                    p for p in profiles
                    if (min_age <= p.get("Age", 0) <= max_age and
                        min_height <= p.get("Height", 0) <= max_height and
                        (selected_marital_status == "All" or p.get("Marital_Status", "") == selected_marital_status) and
                        (selected_cast == "All" or p.get("Cast", "") == selected_cast) and
                        (selected_gender == "All" or p.get("Gender", "") == selected_gender))
                ]

        except ValueError as e:
            error = f"❌ Invalid input: {str(e)}" if str(e) else "❌ Please enter valid numbers for age and height"

    return render_template(
        "index.html", 
        profiles=filtered_profiles,
        min_age=min_age,
        max_age=max_age,
        min_height=min_height_input,
        max_height=max_height_input,
        marital_status_options=MARITAL_STATUS_OPTIONS,
        selected_marital_status=selected_marital_status,
        cast_options=CAST_OPTIONS,
        selected_cast=selected_cast,
        gender_options=GENDER_OPTIONS,
        selected_gender=selected_gender,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)
