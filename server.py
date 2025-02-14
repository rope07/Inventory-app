from flask import Flask, request, jsonify
import  sqlite3

app = Flask(__name__)

@app.route('/audit', methods=['POST'])
def audit_equipment():
    data = request.json
    equipment_id = data.get('equipment_id')

    if not equipment_id:
        return jsonify({"status": "error", "message": "Equipment ID je obavezan"}), 400
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE equipment SET last_audit = datetime('now') WHERE id = ?", (equipment_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Oprema ažurirana"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)