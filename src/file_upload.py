import os

def upload_files(uploaded_files):
    mat_file = None
    hea_file = None

    for uploaded_file in uploaded_files:
        file_path = os.path.join("temp_data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if uploaded_file.name.endswith(".mat"):
            mat_file = file_path
        elif uploaded_file.name.endswith(".hea"):
            hea_file = file_path

    return mat_file, hea_file
