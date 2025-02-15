from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import  sqlite3
import json

app = Flask(__name__)
CORS(app, resources={r"/audit": {"origins": "https://192.168.1.15:8080"}})

def json_utf8(data):
    """ Funkcija za vraćanje JSON-a s UTF-8 podrškom """
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype='application/json; charset=utf-8')

@app.route('/audit', methods=['POST'])
def audit_equipment():
    data = request.json
    equipment_id = data.get('equipment_id')

    print("Primljen zahtjev za audit opreme:", equipment_id)  # Dodano

    if not equipment_id:
        return jsonify(json.loads(json.dumps({"status": "error", "message": "Equipment ID je obavezan"}, ensure_ascii=False))), 400
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM equipment WHERE id = ?", (equipment_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify(json.loads(json.dumps({"status": "error", "message": "Oprema nije pronađena"}, ensure_ascii=False))), 404
    
    # Ažurirajte last_audit
    cursor.execute("UPDATE equipment SET last_audit = datetime('now') WHERE id = ?", (equipment_id,))
    conn.commit()
    conn.close()

    print("Oprema ažurirana:", equipment_id)  # Dodano
    return jsonify(json.loads(json.dumps({"status": "success", "message": "Oprema ažurirana"}, ensure_ascii=False)))
    

@app.route('/equipment', methods=['GET'])
def get_equipment():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, assigned_to, last_audit FROM equipment")
    rows = cursor.fetchall()
    conn.close()

    equipment_list = []
    for row in rows:
        equipment_list.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "assigned_to": row[3],
            "last_audit": row[4]
        })

    return json_utf8(equipment_list)

@app.route('/employees', methods=['GET'])
def get_employees():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name, company FROM employees")
    rows = cursor.fetchall()
    conn.close()

    employees_list = []
    for row in rows:
        employees_list.append({
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "company": row[3]
        })
    
    print(employees_list)
    return json_utf8(employees_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('localhost.pem', 'localhost-key.pem'),)