import xml.etree.ElementTree as ET
import pymysql
from pymysql import MySQLError
from dotenv import load_dotenv
import time
import os

def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id VARCHAR(10) PRIMARY KEY,
        name VARCHAR(100)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id VARCHAR(10) PRIMARY KEY,
        department_fk VARCHAR(10),
        name VARCHAR(100),
        position VARCHAR(100),
        salary DECIMAL(10, 2),
        currency VARCHAR(10),
        hire_date DATE,
        email VARCHAR(100),
        phone_work VARCHAR(20),
        phone_mobile VARCHAR(20),
        FOREIGN KEY (department_fk) REFERENCES departments(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id VARCHAR(10) PRIMARY KEY,
        name VARCHAR(100),
        start_date DATE,
        end_date DATE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_team (
        id INT AUTO_INCREMENT PRIMARY KEY,
        project_fk VARCHAR(10),
        employee_fk VARCHAR(10),
        role VARCHAR(100),
        FOREIGN KEY (project_fk) REFERENCES projects(id),
        FOREIGN KEY (employee_fk) REFERENCES employees(id)
    )
    """)

def insert_data(cursor, root):
    # Insert data into departments and employees tables
    for dept in root.find('departments'):
        dept_id = dept.get('id')
        dept_name = dept.find('name').text
        
        cursor.execute("INSERT INTO departments (id, name) VALUES (%s, %s)", (dept_id, dept_name))
        
        for emp in dept.find('employees'):
            emp_id = emp.get('id')
            emp_name = emp.find('name').text
            emp_position = emp.find('position').text
            emp_salary = emp.find('salary').text
            emp_currency = emp.find('salary').get('currency')
            emp_hire_date = emp.find('hire_date').text
            emp_email = emp.find('contact').find('email').text
            emp_phone_work = None
            emp_phone_mobile = None

            for phone in emp.find('contact').findall('phone'):
                if phone.get('type') == 'work':
                    emp_phone_work = phone.text
                elif phone.get('type') == 'mobile':
                    emp_phone_mobile = phone.text
            
            cursor.execute("""
            INSERT INTO employees (id, department_fk, name, position, salary, currency, hire_date, email, phone_work, phone_mobile)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (emp_id, dept_id, emp_name, emp_position, emp_salary, emp_currency, emp_hire_date, emp_email, emp_phone_work, emp_phone_mobile))

    # Insert data into projects and project_team tables
    for proj in root.find('projects'):
        proj_id = proj.get('id')
        proj_name = proj.find('name').text
        proj_start_date = proj.find('start_date').text
        proj_end_date = proj.find('end_date').text
        
        cursor.execute("INSERT INTO projects (id, name, start_date, end_date) VALUES (%s, %s, %s, %s)", (proj_id, proj_name, proj_start_date, proj_end_date))
        
        for member in proj.find('team'):
            emp_id = member.get('employee_id')
            role = member.get('role')
            
            cursor.execute("INSERT INTO project_team (project_fk, employee_fk, role) VALUES (%s, %s, %s)", (proj_id, emp_id, role))

def main():
    # Load environment var
    load_dotenv()

    try:
        # Parse the XML
        tree = ET.parse('company.xml')
        root = tree.getroot()

        # Connect to the MySQL database with defaults if env variables are not set
        db = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'CompanyTree')
        )
        cursor = db.cursor()

        # Create tables
        create_tables(cursor)

        # Insert data
        insert_data(cursor, root)

        # Commit the transaction
        db.commit()
        print(f"Succes mapping xml to company db")
    except MySQLError as e:
        print(f"Error: {e}")
    
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'db' in locals() and db is not None:
            db.close()

if __name__ == "__main__":
    # Wait 10 seconds until mysql image fireup
    time.sleep(10)
    main()
