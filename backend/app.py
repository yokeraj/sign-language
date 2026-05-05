from flask import Flask, request, jsonify
from database import init_db, insert_student, fetch_all_students, fetch_student, insert_marks, fetch_marks

app = Flask(__name__)
init_db()

@app.route("/students", methods=["POST"])
def add_student():
    d = request.json
    try:
        new_id = insert_student(d["name"], d["roll_no"], d["class"], d["section"])
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/students", methods=["GET"])
def get_students():
    rows = fetch_all_students()
    students = [
        {"id": r[0], "name": r[1], "roll_no": r[2], "class": r[3], "section": r[4]}
        for r in rows
    ]
    return jsonify(students)

@app.route("/marks", methods=["POST"])
def add_marks():
    d = request.json
    try:
        insert_marks(d["student_id"], d["subjects"])
        return jsonify({"success": True}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/report/<int:student_id>", methods=["GET"])
def get_report(student_id):
    student = fetch_student(student_id)
    if not student:
        return jsonify({"success": False, "error": "Student not found"}), 404
    marks = fetch_marks(student_id)
    return jsonify({
        "success"  : True,
        "student"  : {"id": student[0], "name": student[1], "roll_no": student[2],
                      "class": student[3], "section": student[4]},
        "marks"    : [{"subject": m[0], "marks": m[1], "max_marks": m[2]} for m in marks]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)