from flask import Flask, render_template, request
import o

app = Flask(__name__)

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

def read_profiles():
    profiles = []
    file_path = os.path.join(os.path.dirname(__file__), "profiles.txt")

    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read().strip().split("-----")
        
        for profile in data:
            profile = profile.strip()  # Remove leading/trailing spaces
            if not profile:  # Skip empty entries
                continue  

            profile_lines = profile.split("\n")
            profile_dict = {}

            for line in profile_lines:
                if "Age:" in line:
                    try:
                        profile_dict["Age"] = int(line.split(":")[1].strip())
                    except ValueError:
                        profile_dict["Age"] = 0  

                if "Height:" in line:
                    try:
                        profile_dict["Height"] = float(line.split(":")[1].strip())
                    except ValueError:
                        profile_dict["Height"] = 0.0  

                if "Marital Status:" in line:
                    marital_status = line.split(":")[1].strip().replace("*", "")
                    profile_dict["Marital_Status"] = marital_status

                if "Cast:" in line:
                    cast = line.split(":")[1].strip().replace("*", "")
                    profile_dict["Cast"] = cast

                if "Gender:" in line:
                    gender = line.split(":")[1].strip().replace("*", "")
                    profile_dict["Gender"] = gender

                profile_dict["Details"] = profile  # Store full profile details
            
            if profile_dict:  # Only add non-empty profiles
                profiles.append(profile_dict)

    return profiles



@app.route("/", methods=["GET", "POST"])
def index():
    profiles = read_profiles()
    filtered_profiles = profiles  

    min_age, max_age = 0, 100  
    min_height, max_height = 4.0, 7.0  
    selected_marital_status = "All"  
    selected_cast = "All"
    selected_gender = "All"

    if request.method == "POST":
        try:
            min_age = int(request.form.get("min_age", 0))
            max_age = int(request.form.get("max_age", 100))
            min_height = float(request.form.get("min_height", 4.0))
            max_height = float(request.form.get("max_height", 7.0))
            selected_marital_status = request.form.get("marital_status", "All").replace("*", "").strip()
            selected_cast = request.form.get("cast", "All").replace("*", "").strip()
            selected_gender = request.form.get("gender", "All").replace("*", "").strip()
        except ValueError:
            min_age, max_age = 0, 100
            min_height, max_height = 4.0, 7.0
            selected_marital_status = "All"
            selected_cast = "All"
            selected_gender = "All"

        filtered_profiles = [
            p for p in profiles if 
            min_age <= p.get("Age", 0) <= max_age and 
            min_height <= p.get("Height", 0) <= max_height and
            (selected_marital_status == "All" or p.get("Marital_Status", "") == selected_marital_status) and
            (selected_cast == "All" or p.get("Cast", "") == selected_cast) and
            (selected_gender == "All" or p.get("Gender", "") == selected_gender)
        ]

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
        selected_gender=selected_gender
    )


if __name__ == "__main__":
    app.run(debug=True)
