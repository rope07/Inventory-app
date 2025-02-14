import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt

# Database Setup
def setup_databases():
    # Inventory Database
    conn_inv = sqlite3.connect("inventory.db")
    cursor_inv = conn_inv.cursor()
    cursor_inv.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            assigned_to TEXT DEFAULT 'Slobodno'
        )
    ''')
    conn_inv.commit()
    conn_inv.close()

    # Employees Database
    conn_emp = sqlite3.connect("employees.db")
    cursor_emp = conn_emp.cursor()
    cursor_emp.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            company TEXT NOT NULL
        )
    ''')
    conn_emp.commit()
    conn_emp.close()

# Employee Management Window
class EmployeeWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Upravljanje djelatnicima")
        self.setGeometry(300, 200, 500, 350)

        layout = QVBoxLayout()

        # Input fields
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Ime djelatnika")
        layout.addWidget(self.first_name_input)

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Prezime djelatnika")
        layout.addWidget(self.last_name_input)

        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("Ime tvrtke")
        layout.addWidget(self.company_input)

        # Add Employee Button
        add_employee_button = QPushButton("Dodaj djelatnika")
        add_employee_button.clicked.connect(self.add_employee)
        layout.addWidget(add_employee_button)

        # Employee Table
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(4)
        self.employee_table.setHorizontalHeaderLabels(["ID", "Ime", "Prezime", "Tvrtka"])
        self.load_employees()
        layout.addWidget(self.employee_table)

        # Delete Employee Button
        delete_employee_button = QPushButton("Obriši odabranog djelatnika")
        delete_employee_button.clicked.connect(self.delete_employee)
        layout.addWidget(delete_employee_button)

        show_equipment_button = QPushButton("Prikaži dodijeljenu opremu")
        show_equipment_button.clicked.connect(self.show_assigned_equipment)
        layout.addWidget(show_equipment_button)

        self.setLayout(layout)

    # Load Employees into Table
    def load_employees(self):
        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        conn.close()

        self.employee_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, data in enumerate(row):
                self.employee_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

    # Add New Employee
    def add_employee(self):
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        company = self.company_input.text().strip()

        if not first_name or not last_name or not company:
            QMessageBox.warning(self, "Greška", "Popunite sva polja!")
            return

        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO employees (first_name, last_name, company) VALUES (?, ?, ?)", 
                       (first_name, last_name, company))
        conn.commit()
        conn.close()

        self.load_employees()
        self.parent.load_employees()  # Refresh dropdown in main window
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.company_input.clear()

    # Delete Selected Employee
    def delete_employee(self):
        selected_row = self.employee_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Greška", "Odaberite djelatnika za brisanje!")
            return

        employee_id = self.employee_table.item(selected_row, 0).text()

        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        conn.commit()
        conn.close()

        self.load_employees()
        self.parent.load_employees()  # Refresh dropdown in main window

    def show_assigned_equipment(self):
        selected_row = self.employee_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Greška", "Odaberite djelatnika")
        
        employee_id = self.employee_table.item(selected_row, 0).text()
        first_name = self.employee_table.item(selected_row, 1).text()
        last_name = self.employee_table.item(selected_row, 2).text()
        company = self.employee_table.item(selected_row, 3).text()

        employee_name = f"{first_name} {last_name} ({company})"

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipment WHERE assigned_to = ?", (employee_name,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            QMessageBox.information(self, "Dodijeljena oprema", "Nema dodijeljene opreme za ovog djelatnika.")
            return
        
        self.equipment_window = QWidget()
        self.equipment_window.setWindowTitle(f"Dodijeljena oprema za {employee_name}")
        self.equipment_window.setGeometry(400, 200, 600, 400)

        layout = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID", "Naziv", "Kategorija", "Dodijeljeno"])
        table.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):
            for col_idx, data in enumerate(row):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

        layout.addWidget(table)
        self.equipment_window.setLayout(layout)
        self.equipment_window.show()

# Main IT Inventory App
class ITInventory(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IT Inventar")
        self.setGeometry(100, 100, 1000, 800)
        
        # Layouts
        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        filter_layout = QHBoxLayout()
        
        # Input Fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Naziv opreme")

        self.category_input = QComboBox()
        self.category_input.addItems(["Monitor", "Kučište", "Miš", "Tipkovnica", "Laptop"])
        
        self.employee_select = QComboBox()
        self.load_employees()

        # Search Field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pretraži opremu po nazivu")
        self.search_input.textChanged.connect(self.load_equipment)

        # Filter ComboBox
        self.filter_category = QComboBox()
        self.filter_category.addItems(["Sve kategorije", "Monitor", "Kučište", "Miš", "Tipkovnica", "Laptop"])
        self.filter_category.currentIndexChanged.connect(self.load_equipment)

        # Buttons
        add_button = QPushButton("Dodaj opremu")
        add_button.clicked.connect(self.add_equipment)
        
        show_employees_button = QPushButton("Upravljanje djelatnicima")
        show_employees_button.clicked.connect(self.show_employees_window)

        # Arrange Inputs
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.category_input)
        input_layout.addWidget(self.employee_select)
        input_layout.addWidget(add_button)
        input_layout.addWidget(show_employees_button)

        # Arrange Filter and Search
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.filter_category)

        # Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Naziv", "Kategorija", "Dodijeljeno", "Akcije", "Obriši"])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)

        # Add Layouts to Main
        main_layout.addLayout(input_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
        self.load_equipment()

    # Show Employees Window
    def show_employees_window(self):
        self.employee_window = EmployeeWindow(self)
        self.employee_window.show()

    # Load Employees into Dropdown
    def load_employees(self):
        self.employee_select.clear()
        self.employee_select.addItem("Slobodno")
        
        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()
        cursor.execute("SELECT first_name, last_name, company FROM employees")
        employees = cursor.fetchall()
        conn.close()
        
        for emp in employees:
            self.employee_select.addItem(f"{emp[0]} {emp[1]} ({emp[2]})")

    def add_equipment(self):
        name = self.name_input.text().strip()
        category = self.category_input.currentText()
        assigned_to = self.employee_select.currentText()

        if not name or not category:
            QMessageBox.warning(self, "Greška", "Naziv i kategorija su obavezni!")
            return

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO equipment (name, category, assigned_to) VALUES (?, ?, ?)", 
                    (name, category, assigned_to if assigned_to != "Slobodno" else "Slobodno"))
        conn.commit()
        conn.close()

        self.load_equipment()  # Refresh Table
        self.name_input.clear()


    # Load Equipment into Table
    def load_equipment(self):
        search_text = self.search_input.text().strip()
        filter_category = self.filter_category.currentText()

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()

        query = "SELECT * FROM equipment WHERE 1=1"
        params = []

        if search_text:
            query += " AND name LIKE ?"
            params.append(f"%{search_text}%")

        if filter_category != "Sve kategorije":
            query += " AND category = ?"
            params.append(filter_category)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setRowHeight(row_idx, 50)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))  # ID
            self.table.setItem(row_idx, 1, QTableWidgetItem(row[1]))  # Naziv
            self.table.setItem(row_idx, 2, QTableWidgetItem(row[2]))  # Kategorija
            self.table.setItem(row_idx, 3, QTableWidgetItem(row[3]))  # Dodijeljeno

            # Stupac "Akcije" (Dodijeli ili Odvojiti)
            action_layout = QHBoxLayout()
            action_widget = QWidget()

            if row[3] == "Slobodno":
                assign_button = QPushButton("Dodijeli")
                assign_button.setStyleSheet("min-height: 20px")
                assign_button.clicked.connect(lambda _, id=row[0]: self.open_assign_employee_window(id))
                action_layout.addWidget(assign_button)
            else:
                unassign_button = QPushButton("Odvojiti")
                unassign_button.setStyleSheet("background-color: orange; color: black; min-height: 20px;")
                unassign_button.clicked.connect(lambda _, id=row[0]: self.unassign_equipment(id))
                action_layout.addWidget(unassign_button)

            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 4, action_widget)  # Stupac "Akcije"

            # Stupac "Obriši"
            delete_button = QPushButton("🗑️ Obriši")
            delete_button.setStyleSheet("background-color: red; color: white; min-height: 20px;")
            delete_button.clicked.connect(lambda _, id=row[0]: self.delete_equipment(id))

            delete_widget = QWidget()
            delete_layout = QHBoxLayout()
            delete_layout.addWidget(delete_button)
            delete_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            delete_widget.setLayout(delete_layout)

            self.table.setCellWidget(row_idx, 5, delete_widget)  # Stupac "Obriši"


    def delete_equipment(self, equipment_id):
        reply = QMessageBox.question(self, "Potvrda", "Jeste li sigurni da želite obrisati ovu opremu?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                 QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
            conn.commit()
            conn.close()

            self.load_equipment()  # Osvježi prikaz


    def open_assign_employee_window(self, equipment_id):
        self.assign_window = AssignEmployeeWindow(self, equipment_id)
        self.assign_window.show()

    def unassign_equipment(self, equipment_id):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE equipment SET assigned_to = 'Slobodno' WHERE id = ?", (equipment_id,))
        conn.commit()
        conn.close()

        self.load_equipment()  # Osvježi tablicu

class AssignEmployeeWindow(QWidget):
    def __init__(self, parent, equipment_id):
        super().__init__()
        self.parent = parent
        self.equipment_id = equipment_id
        self.setWindowTitle("Dodijeli djelatnika")
        self.setGeometry(400, 200, 300, 150)

        layout = QVBoxLayout()

        # Dropdown za odabir djelatnika
        self.employee_select = QComboBox()
        self.load_employees()
        layout.addWidget(self.employee_select)

        # Gumb za potvrdu dodjele
        assign_button = QPushButton("Dodijeli")
        assign_button.clicked.connect(self.assign_employee)
        layout.addWidget(assign_button)

        self.setLayout(layout)

    def load_employees(self):
        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()
        cursor.execute("SELECT first_name, last_name, company FROM employees")
        employees = cursor.fetchall()
        conn.close()

        self.employee_select.clear()
        for emp in employees:
            self.employee_select.addItem(f"{emp[0]} {emp[1]} ({emp[2]})")

    def assign_employee(self):
        selected_employee = self.employee_select.currentText()
        if not selected_employee:
            QMessageBox.warning(self, "Greška", "Odaberite djelatnika!")
            return

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE equipment SET assigned_to = ? WHERE id = ?", (selected_employee, self.equipment_id))
        conn.commit()
        conn.close()

        self.parent.load_equipment()  # Ažuriraj tablicu
        self.close()


# Run App
if __name__ == "__main__":
    setup_databases()
    app = QApplication(sys.argv)
    window = ITInventory()
    window.show()
    sys.exit(app.exec())
