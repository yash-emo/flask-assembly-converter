from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS  # Allows requests from different origins

app = Flask(__name__, template_folder="templates")  # Ensure "templates" folder exists
CORS(app)  # Enable CORS for frontend requests

# Route to serve the frontend
@app.route("/")
def home():
    return render_template("index.html")  # Ensure "index.html" is inside "templates/" folder

# Sample assembly-to-machine code mapping
assembly_to_machine = {
    "MOV A, B": "0001 1010",
    "MOV A, 5": "0001 0101",
    "MOV B, 10": "0001 1010",
    "ADD A, B": "0001 1100",
    "STORE A, 20": "0011 1010"
}

@app.route("/execute", methods=["POST"])
def execute_code():
    data = request.json
    assembly_code = data.get("assembly_code", "").split("\n")

    # Local (per-request) state
    registers = {"A": 0, "B": 0}
    memory = {}  # Simulated memory
    flags = {"ZF": 0, "CF": 0}  # Zero Flag, Carry Flag
    
    machine_code = []
    execution_steps = []

    for step, line in enumerate(assembly_code):
        line = line.strip()

        if line in assembly_to_machine:
            machine_code.append(assembly_to_machine[line])

            # Handle Register Updates
            if line == "MOV A, 5":
                registers["A"] = 5
            elif line == "MOV B, 10":
                registers["B"] = 10
            elif line == "ADD A, B":
                registers["A"] += registers["B"]
                flags["ZF"] = 1 if registers["A"] == 0 else 0  # Zero Flag
                if registers["A"] > 255:
                    flags["CF"] = 1  # Carry Flag
                    registers["A"] %= 256  # Simulate 8-bit overflow
            elif line == "STORE A, 20":
                memory[20] = registers["A"]

        else:
            machine_code.append("ERROR: Invalid instruction")

        # Log execution step
        execution_steps.append({
            "step": step + 1,
            "instruction": line,
            "registers": registers.copy(),
            "flags": flags.copy(),
            "memory": memory.copy()
        })

    return jsonify({
        "assembly_code": assembly_code,
        "machine_code": machine_code,
        "execution_steps": execution_steps
    })


@app.route("/download_report")
def download_report():
    """Generates a downloadable execution report"""
    assembly_code = request.args.get("assembly_code", "").strip()
    machine_code = request.args.get("machine_code", "").strip()

    if not assembly_code or not machine_code:
        return "Error: Missing assembly or machine code", 400

    report = f"""
    Assembly Code Execution Report

    Assembly Code:
    {assembly_code.replace(",", "\n")}

    Machine Code:
    {machine_code.replace(",", "\n")}
    """

    response = Response(report, mimetype="text/plain")
    response.headers["Content-Disposition"] = "attachment; filename=assembly_report.txt"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Ensure Flask runs on all interfaces
