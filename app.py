from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Dictionary for assembly-to-machine conversion
assembly_to_machine = {
    "MOV A, B": "0001 1010",
    "MOV A, 5": "0001 0101",
    "MOV B, 10": "0001 1010",
    "ADD A, B": "0001 1100",
    "SUB A, B": "0001 1101",
    "STORE A, 20": "0011 1010"
}

@app.route("/")
def home():
    return render_template("index.html")  # Serve the frontend

@app.route("/execute", methods=["POST"])
def execute_code():
    data = request.json
    assembly_code = data.get("assembly_code", "").split("\n")

    machine_code = []
    memory_allocation = {}
    registers = {"A": 0, "B": 0}

    for line in assembly_code:
        line = line.strip()

        if line.startswith("MOV A, "):
            value = int(line.split(", ")[1])
            registers["A"] = value
            machine_code.append(f"0001 {value:04b}")

        elif line.startswith("MOV B, "):
            value = int(line.split(", ")[1])
            registers["B"] = value
            machine_code.append(f"0001 {value:04b}")

        elif line == "ADD A, B":
            registers["A"] += registers["B"]
            machine_code.append("0001 1100")

        elif line == "SUB A, B":
            registers["A"] -= registers["B"]
            machine_code.append("0001 1101")

        elif line.startswith("STORE A, "):  # ✅ FIX: Properly handle store instruction
            address = int(line.split(", ")[1])
            memory_allocation[address] = registers["A"]
            machine_code.append(f"0011 {address:04b}")  # Convert address to 4-bit binary

        elif line in assembly_to_machine:
            machine_code.append(assembly_to_machine[line])

        else:
            machine_code.append(f"ERROR: Invalid instruction -> {line}")  # ✅ Show the exact error

    return jsonify({
        "assembly_code": assembly_code,
        "machine_code": machine_code,
        "memory_allocation": memory_allocation,
        "registers": registers
    })


if __name__ == "__main__":
    app.run(debug=True)
