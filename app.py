from flask import Flask, render_template, request, session, redirect, url_for, send_file
import ibm_db
import json
from custom.db import db_connect
from custom.cos import cos_connect
from datetime import datetime, date
from docx import Document
import os
from html2docx import html2docx
from io import BytesIO
import pdfkit
from pdf2docx import Converter
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

output_pdf_path = 'output.pdf'
curr_dir = os.getcwd()
parent_dir = os.path.dirname(curr_dir)

today_date = datetime.now().strftime('%d-%m-%Y')

conn = db_connect()
cos = cos_connect()

project_list = []
doc_list = []
pnames = []
dnames = []
curr_pname = ''
curr_dname = ''

def authorizeUser(email,pword):
    sql = f"SELECT * FROM user_data where user_mail = '{email}'"
    stmt = ibm_db.exec_immediate(conn, sql)
    u_data = ibm_db.fetch_assoc(stmt)
    print(u_data)
    if u_data:
        if u_data['USER_PASS'] == pword:
            return True
        else:
            return False
    else:
        return False
    
def newUser(fname,email,pword):
    uname = email.split('@')[0]
    try:
        sql = f"insert into user_data (user_name,user_uname,user_mail,user_pass) values ('{fname}','{uname}','{email}','{pword}');"
        ibm_db.exec_immediate(conn, sql)
        print("User Created Successfully.")
    except:
        print("Error creating user...")

def createProject(pname,pdesc,uname):
    cm_date = date.today().strftime("%d-%m-%Y")
    try:
        sql = f"insert into project_data (project_name,project_desc,project_user,project_last_modified) values ('{pname}','{pdesc}','{uname}','{cm_date}');"
        ibm_db.exec_immediate(conn, sql)
        print("Project Created Successfully.")
    except:
        print("Error creating project...")

def isProject(pname,uname):
    sql = f"select * from project_data where project_name = '{pname}' and project_user = '{uname}';"
    stmt = ibm_db.exec_immediate(conn,sql)
    p_data = ibm_db.fetch_assoc(stmt)
    if p_data:
        return True
    else:
        return False
    
def getProjectFiles(pid):
    p_data = []
    sql = f"select * from documents_data where doc_pid = '{pid}';"
    stmt = ibm_db.exec_immediate(conn,sql)
    curr_data = ibm_db.fetch_assoc(stmt)
    while curr_data != False:
        p_data.append(curr_data)
        curr_data = ibm_db.fetch_assoc(stmt)
    return p_data

def getDocDetails(d_path):
    d_path = session['fname']+'_'+d_path
    c_time = os.path.getctime(d_path)
    m_time = os.path.getmtime(d_path)
    details = {
        'd_size' : os.path.getsize(d_path),
        'c_time' : datetime.fromtimestamp(c_time).strftime('%d-%m-%Y'),
        'm_time' : datetime.fromtimestamp(m_time).strftime('%d-%m-%Y'),
        'd_type' : os.path.splitext(d_path)[1][1:]
    }
    return details

def createDocument(d_name,d_uname,d_pid):
    details = getDocDetails(d_name)
    print(d_name)
    print(details)
    try:
        sql = f"insert into documents_data (doc_name,doc_uname,doc_pid,doc_type,doc_size,doc_created_date,doc_modified_date) values ('{d_name}','{d_uname}',{d_pid},'{details['d_type']}','{details['d_size']}','{details['c_time']}','{details['m_time']}');"
        print(sql)
        ibm_db.exec_immediate(conn, sql)
        print("Document uploaded Successfully.")
    except:
        print("Error uploading document...")

@app.route('/')
def home():
    if session.get('authorized', None) is None:
        session['authorized'] = False
    return render_template('index.html')

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/base2')
def base2():
    return render_template('base2.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/feature')
def feature():
    return render_template('feature.html')

@app.route('/dashboard')
def dashboard():
    global project_list
    global doc_list
    global pnames
    global dnames
    sql = f"SELECT * FROM project_data where project_user = '{session['uname']}'"
    stmt = ibm_db.exec_immediate(conn, sql)
    project_list = []
    curr_doc = ibm_db.fetch_assoc(stmt)
    while curr_doc != False:
        project_list.append(curr_doc)
        curr_doc = ibm_db.fetch_assoc(stmt)
    print(project_list)
    sql = f"SELECT * FROM documents_data where doc_uname = '{session['uname']}'"
    stmt = ibm_db.exec_immediate(conn, sql)
    doc_list = []
    curr_doc = ibm_db.fetch_assoc(stmt)
    while curr_doc != False:
        doc_list.append(curr_doc)
        curr_doc = ibm_db.fetch_assoc(stmt)
    print(doc_list)
    pnames = [curr_proj['PROJECT_NAME'] for curr_proj in project_list]
    print(pnames)
    dnames = [curr_doc['DOC_NAME'] for curr_doc in doc_list]
    print(dnames)
    return render_template('dashboard.html',project_count = len(project_list),doc_count = len(doc_list), proj_list = project_list, doc_list = doc_list)

@app.route('/project')
def project():
    return render_template('project.html')

@app.route('/doc/<int:project_id>')
def doc(project_id):
    sql = f"SELECT * FROM documents_data where doc_pid = '{project_id}'"
    stmt = ibm_db.exec_immediate(conn, sql)
    doc_list2 = []
    curr_doc = ibm_db.fetch_assoc(stmt)
    while curr_doc != False:
        doc_list2.append(curr_doc)
        curr_doc = ibm_db.fetch_assoc(stmt)
    print(doc_list2)
    return render_template('docs.html', proj_list = project_list, doc_list = doc_list2)

@app.route('/editor')
def editor():
    return render_template('editor.html')

@app.route('/file_info/<int:doc_id>')
def file_info(doc_id):
    sql = f"SELECT * FROM documents_data where doc_id = '{doc_id}'"
    print(sql)
    stmt = ibm_db.exec_immediate(conn, sql)
    curr_doc = ibm_db.fetch_assoc(stmt)
    proj_id = curr_doc['DOC_PID']
    sql = f"SELECT * FROM project_data where project_id = '{proj_id}'"
    print(sql)
    stmt = ibm_db.exec_immediate(conn, sql)
    curr_proj = ibm_db.fetch_assoc(stmt)
    return render_template('file_info.html',curr_doc = curr_doc, curr_proj = curr_proj)

@app.route('/myprojects')
def myprojects():
    return render_template('project.html', proj_list = project_list)

@app.route('/mydocs')
def mydocs():
    return render_template('docs.html', doc_list = doc_list, proj_list = project_list)

@app.route('/newproject', methods=['GET','POST'])
def newproject():
    global pnames
    if request.method == 'POST':
        pname = request.form['pname']
        pdesc = request.form['pdesc']
        if pname not in pnames:
            print(pname,pnames)
            pnames.append(pname)
            sql = f"insert into project_data (project_name,project_desc,project_user,project_last_modified) values ('{pname}','{pdesc}','{session['uname']}','{today_date}');"
            ibm_db.exec_immediate(conn, sql)
            return render_template('project.html')
        else:
            return render_template('project.html',project_message = 'Project already exists.', proj_list = project_list)
    return redirect(url_for('dashboard'))

@app.route('/newdoc', methods=['GET','POST'])
def newdoc():
    global curr_dname
    global curr_pname
    global pnames
    if request.method == 'POST':
        pname = request.form['pname']
        dname = request.form['dname']
        if pname not in pnames:
            return render_template('project.html', doc_message = 'Project not found.', proj_list = project_list)
        else:
            sql = f"select * from project_data where project_name = '{pname}' and project_user = '{session['uname']}';"
            stmt = ibm_db.exec_immediate(conn,sql)
            p_data = ibm_db.fetch_assoc(stmt)
            proj_files = getProjectFiles(p_data['PROJECT_ID'])
            dnames = [curr_doc['DOC_NAME'] for curr_doc in proj_files]
            if dname in dnames:
                return render_template('project.html',doc_message = 'Document already exists.', proj_list = project_list)
            else:
                curr_dname = dname
                curr_pname = pname
                return render_template('editor.html',project_name = curr_pname,doc_name = curr_dname,pid = p_data['PROJECT_ID'])
    else:
        return redirect(url_for('dashboard'))
    
@app.route('/save/<int:pid>', methods=['POST'])
def save(pid):
    global curr_dname
    print("curr_dname = ",curr_dname)
    data = json.loads(request.data)
    print(data)
    print("hello world")
    quill_content = data['content']
    print(quill_content)
    object_name = session['fname']+'_'+curr_dname
    print(object_name)

    pdfkit.from_string(quill_content, output_pdf_path, configuration=config)
    cv = Converter(output_pdf_path)
    cv.convert(object_name, start=0, end=None)
    cv.close()
    os.remove(output_pdf_path)

    bucket_name = 'cloudcollab-main'
    file_path = os.path.join(curr_dir,object_name)
    print(file_path)

    cos.upload_file(file_path, bucket_name, object_name)
    createDocument(curr_dname,session['uname'],pid)
    return render_template('uploadsuccess.html')

@app.route('/download')
def download():
    object_name = session['fname']+'_'+curr_dname
    file_path = os.path.join(curr_dir,object_name)
    return send_file(file_path, as_attachment=True)



@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pword = request.form['pword']
        sql = f"SELECT * FROM user_data where user_mail = '{email}'"
        print(sql)
        stmt = ibm_db.exec_immediate(conn, sql)
        curr_user = ibm_db.fetch_assoc(stmt)
        if curr_user:
            actual_pword = curr_user['USER_PASS']
            if pword == actual_pword:
                session['fname'] = curr_user['USER_NAME']
                session['uname'] = curr_user['USER_UNAME']
                session['authorized'] = True
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html',error_message = 'Password is incorrect.')
        else:
            return render_template('login.html', error_message = 'User is not registered.')
    else:
        return render_template('login.html')
    
@app.route('/logout')
def logout():
    session['authorized'] = False
    session.pop('fname')
    session.pop('uname')
    return render_template('login.html')
    
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        fname = request.form['fname']
        email = request.form['email']
        uname = email.split('@')[0]
        pword = request.form['pword']
        cpword = request.form['cpword']
        sql = f"SELECT * FROM user_data where user_mail = '{email}'"
        stmt = ibm_db.exec_immediate(conn, sql)
        curr_user = ibm_db.fetch_assoc(stmt)
        if curr_user:
            return render_template('register.html', error_message = 'Email already in use.')
        else:
            if pword != cpword:
                return render_template('register.html', error_message = 'Passwords not matched.')
            else:
                sql = f"insert into user_data (user_name,user_uname,user_mail,user_pass) values ('{fname}','{uname}','{email}','{pword}');"
                ibm_db.exec_immediate(conn, sql)
                print("Data Inserted...")
                return render_template('login.html', success_message = 'Registration Successful. Please login.')
    else:
        return render_template('signup.html')

    
if __name__ == '__main__':
    app.run(debug = True)