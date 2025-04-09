from flask import Flask, render_template, request, flash
import os
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'  # Change this to a secure key

# Options for filters
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

def convert_height(height_str):
    """Convert height string to decimal feet (5.10 -> 5.833, 5.11 -> 5.916)"""
    try:
        if '.' in height_str:
            feet, inches = height_str.split('.')
            if len(inches) > 1:  # Format like 5.10 or 5.11
                return float(feet) + float(inches)/12
            return float(height_str)  # Regular decimal like 5.8
        return float(height_str)
    except:
        return 0.0

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

                # Extract Height (with improved handling)
                elif line.startswith(("👔Height:", "👗Height:")):
                    try:
                        height_str = line.split(":", 1)[1].strip()
                        profile_dict["Height"] = convert_height(height_str)
                    except:
                        profile_dict["Height"] = 0.0

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
    min_height, max_height = 4.5, 6.5
    selected_marital_status = "All"
    selected_cast = "All"
    selected_gender = "All"

    if request.method == "POST":
        try:
            min_age = int(request.form.get("min_age", 18))
            max_age = int(request.form.get("max_age", 40))
            min_height = float(request.form.get("min_height", 4.5))
            max_height = float(request.form.get("max_height", 6.5))
            selected_marital_status = request.form.get("marital_status", "All").strip()
            selected_cast = request.form.get("cast", "All").strip()
            selected_gender = request.form.get("gender", "All").strip()

            # Validate ranges
            if min_age > max_age:
                error = "❌ Maximum age cannot be less than minimum age"
            elif min_height > max_height:
                error = "❌ Maximum height cannot be less than minimum height"
            
            if not error:
                filtered_profiles = []
                for p in profiles:
                    age = p.get("Age", 0)
                    height = p.get("Height", 0.0)
                    marital_status = p.get("Marital_Status", "")
                    cast = p.get("Cast", "")
                    gender = p.get("Gender", "")

                    if (min_age <= age <= max_age and
                        min_height <= height <= max_height and
                        (selected_marital_status == "All" or marital_status == selected_marital_status) and
                        (selected_cast == "All" or cast == selected_cast) and
                        (selected_gender == "All" or gender == selected_gender)):
                        filtered_profiles.append(p)

        except ValueError:
            error = "❌ Please enter valid numbers for age and height"

    return render_template(
        "index.html", 
        profiles=filtered_profiles,
        min_age=min_age,
        max_age=max_age,
        min_height=min_height,
        max_height=max_height,
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
