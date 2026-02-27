# EdTrack3

## AI Face Recognition Attendance (New)

This project now supports AI-based face verification for attendance.

### Install dependencies

```bash
pip install opencv-python
pip install face_recognition
pip install git+https://github.com/ageitgey/face_recognition_models
```

> On Windows, you may need Visual Studio Build Tools if `dlib` fails to install.

### How to use

1. Log in as a student.
2. On the Student Dashboard, open the Attendance camera modal.
3. Click **Enroll Face (AI)** once to register your face.
4. Then click **Mark Attendance**. The system verifies your face before marking attendance.

### Notes
- Attendance will be rejected if **no face** or **multiple faces** are detected.
- Attendance will be rejected if the captured face does not match the enrolled face.
