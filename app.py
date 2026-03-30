import os
import io
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from llm_transformer import generate_transformation_code
from reliability_engine import calculate_reliability
from semantic_engine import get_suggestions
from dataset_loader import load_dataset
import database
from schema_harmonizer import analyze_schemas, apply_mappings
from explainability_engine import generate_explanation

app = Flask(__name__)
# In production, use a more secure secret key.
app.secret_key = 'samanvãya_hackathon_super_secret'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure demo datasets exist
def create_demo_datasets():
    customer_path = os.path.join(UPLOAD_FOLDER, 'customer_data.csv')
    sales_path = os.path.join(UPLOAD_FOLDER, 'sales_data.csv')
    if not os.path.exists(customer_path):
        pd.DataFrame({
            'cust_id': [101, 102, 103], 
            'name': ['alice smith', 'Bob Johnson ', 'CHARLIE Brown'], 
            'height': [160.5, 175.0, 155.0], 
            'price': [12.55, 9.99, 150.0]
        }).to_csv(customer_path, index=False)
    if not os.path.exists(sales_path):
        pd.DataFrame({
            'invoice': ['A-1', 'B-2', 'A-3'], 
            'date': ['12/31/2023', '01/01/2024', '01/15/2024'], 
            'sales': [100.5, 200.1, 50.99]
        }).to_csv(sales_path, index=False)

create_demo_datasets()

@app.route('/')
def index():
    return render_template('intro.html')

@app.route('/landing')
def landing():
    return render_template('intro.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('signup.html')

        if database.get_user(username):
            flash('Username already exists. Please choose another.', 'error')
            return render_template('signup.html')

        password_hash = generate_password_hash(password)
        created = database.create_user(username, password_hash, email)
        if not created:
            flash('Unable to create user. Please try again.', 'error')
            return render_template('signup.html')

        flash('Registration successful. Please login with your credentials.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if database.verify_user(username, password):
            session['user'] = username
            return redirect(url_for('dashboard'))

        flash('Invalid credentials. Please check your username and password.', 'error')
        return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    db_status = database.is_connected()
    db_history = database.get_recent_history(5)
    
    # Format history for UI
    recent_history = []
    for h in db_history:
        recent_history.append({
            "dataset_name": h.get("dataset_name", "Unknown"),
            "columns_modified": ", ".join(h.get("columns_modified", [])),
            "date": h.get("transformation_date", "").strftime("%Y-%m-%d %H:%M") if hasattr(h.get("transformation_date"), "strftime") else "Unknown"
        })
        
    return render_template('dashboard.html', user=session.get('user'), db_status=db_status, recent_history=recent_history)

@app.route('/upload', methods=['POST'])
def upload():
    # Handle File Upload (Single or Multiple)
    files = request.files.getlist('file')
    allowed_exts = ('.csv', '.xlsx', '.xls', '.tsv', '.json', '.parquet', '.feather', '.xml')
    
    saved_filepaths = []
    
    if files and len(files) > 0 and files[0].filename:
        for file in files:
            if file.filename.lower().endswith(allowed_exts):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                saved_filepaths.append(filepath)
                
                # Record to Mongo if applicable
                username = session.get('user', 'guest')
                database.save_dataset_metadata(filename, filepath, username)

        if len(saved_filepaths) == 1:
            session['filepath'] = saved_filepaths[0]
            return redirect(url_for('column_select'))
        elif len(saved_filepaths) > 1:
            session['multi_filepaths'] = saved_filepaths
            return redirect(url_for('schema_align'))
        
    # Handle Demo Mode
    demo_file = request.form.get('demo_file')
    if demo_file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], demo_file)
        session['filepath'] = filepath
        username = session.get('user', 'guest')
        database.save_dataset_metadata(demo_file, filepath, username)
        return redirect(url_for('column_select'))
        
    return redirect(url_for('dashboard'))

@app.route('/schema_align', methods=['GET', 'POST'])
def schema_align():
    filepaths = session.get('multi_filepaths', [])
    if not filepaths:
        return redirect(url_for('dashboard'))
        
    if request.method == 'GET':
        dfs = []
        for fp in filepaths:
            df, err = load_dataset(fp)
            if not err:
                dfs.append(df)
        
        alignment_data = analyze_schemas(dfs)
        return render_template('schema_align.html', alignment=alignment_data)
        
    elif request.method == 'POST':
        mappings_to_apply = []
        # Parse posted mappings (simplified)
        for key, val in request.form.items():
            if key.startswith('map_'):
                parts = key.split('_')
                if len(parts) >= 3:
                    ds_idx = int(parts[1])
                    orig_col = parts[2]
                    # Simple workaround to handle cols with underscores
                    orig_col = key.replace(f"map_{ds_idx}_", "")
                    mappings_to_apply.append({
                        'dataset_index': ds_idx,
                        'original_col': orig_col,
                        'new_col': val
                    })
        
        dfs = []
        for fp in filepaths:
            df, err = load_dataset(fp)
            if not err:
                dfs.append(df)
                
        harmonized_df = apply_mappings(dfs, mappings_to_apply)
        
        # Save harmonized mapping record to db
        database.save_schema_mapping({"mappings": mappings_to_apply, "user": session.get('user', 'guest')})
        
        out_filename = "harmonized_" + os.path.basename(filepaths[0])
        out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
        harmonized_df.to_csv(out_path, index=False)
        
        session['filepath'] = out_path
        session.pop('multi_filepaths', None)
        return redirect(url_for('column_select'))

@app.route('/column_select')
def column_select():
    filepath = session.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return redirect(url_for('dashboard'))
    
    df, err = load_dataset(filepath)
    if err:
        return f"Error reading file: {err}"
        
    # Get head(10) instead of 5, and include datatypes
    preview_df = df.head(10).copy()
    
    # Store types info to display
    dtypes_dict = df.dtypes.astype(str).to_dict()
    
    # Convert empty/NaN for better visuals
    preview_df = preview_df.fillna("NaN")
    
    # Render table WITHOUT the 'classes' keyword to pandas, so we style it cleanly
    # Instead, we will add styling classes in the HTML using Tailwind
    preview_html = preview_df.to_html(index=False, border=0, classes='w-full text-left text-sm text-slate-600 data-table')
    
    # Prepare column list with types for the UI
    columns = [{'name': col, 'dtype': dtypes_dict.get(col, '')} for col in df.columns]
    
    return render_template('column_select.html', preview=preview_html, columns=columns)

@app.route('/setup_transform', methods=['POST'])
def setup_transform():
    selected_columns = request.form.getlist('columns')
    if not selected_columns:
        return redirect(url_for('column_select'))
        
    session['selected_columns'] = selected_columns
    
    # Get column metadata and suggested prompts
    filepath = session.get('filepath')
    df, err = load_dataset(filepath)
    if err:
        return f"Error loading dataset: {err}"
    
    col_data = []
    for col in selected_columns:
        suggestions = get_suggestions(df, col)
        col_data.append({
            'name': col,
            'suggestions': suggestions
        })
        
    return render_template('prompt_transform.html', col_data=col_data)

@app.route('/execute_transform', methods=['POST'])
def execute_transform():
    filepath = session.get('filepath')
    df, err = load_dataset(filepath)
    if err:
        return f"Error scaling dataset: {err}"
        
    old_df = df.copy()
    selected_columns = session.get('selected_columns', [])
    transformations = []
    
    # Process each column's specific request
    for col in selected_columns:
        mode = request.form.get(f'mode_{col}', 'rule')
        
        if mode == 'prompt':
            prompt = request.form.get(f'prompt_{col}')
            if not prompt: continue
            
            sample_values = df[col].dropna().head(3).tolist()
            code, reasoning = generate_transformation_code(col, sample_values, prompt)
            transformations.append({
                'col': col, 'mode': 'AI', 'prompt': prompt, 
                'code': code, 'reasoning': reasoning
            })
            
        elif mode == 'rule':
            rule = request.form.get(f'rule_{col}')
            if not rule: continue
            
            code = ""
            if rule == 'round':
                code = f"df['{col}'] = pd.to_numeric(df['{col}'], errors='coerce').round()"
            elif rule == 'upper':
                code = f"df['{col}'] = df['{col}'].astype(str).str.upper()"
            elif rule == 'lower':
                code = f"df['{col}'] = df['{col}'].astype(str).str.lower()"
            elif rule == 'fill_missing':
                code = f"df['{col}'] = df['{col}'].fillna('Unknown')"
            else:
                code = f"# Unknown rule for {col}"
                
            reasoning = generate_explanation(code, f"Applied rule: {rule}")
                
            transformations.append({
                'col': col, 'mode': 'Manual', 'rule': rule, 
                'code': code, 'reasoning': reasoning
            })

    # Execute generated code
    for t in transformations:
        try:
            local_vars = {'df': df, 'pd': pd, 'np': __import__('numpy')}
            exec(t['code'], globals(), local_vars)
            df = local_vars['df']
            t['status'] = 'Success'
        except Exception as e:
            t['status'] = 'Failed'
            t['error'] = str(e)
            
    # Save output
    out_filename = "transformed_" + os.path.basename(filepath)
    # Regardless of input format, output as CSV for simplicity of download 
    # unless original was xlsx, then keep xlsx.
    if filepath.endswith('.xlsx'):
        out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
        df.to_excel(out_path, index=False)
    else:
        out_filename = out_filename.rsplit('.', 1)[0] + '.csv'
        out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
        df.to_csv(out_path, index=False)
    
    # Calculate score
    reliability = calculate_reliability(transformations)
    
    before_preview = old_df.head(10).to_html(classes='w-full text-sm data-table text-slate-600', index=False)
    after_preview = df.head(10).to_html(classes='w-full text-sm data-table text-slate-600', index=False)
    
    if 'history' not in session:
        session['history'] = []
    
    # Append to history
    session['history'].append({
        'filename': out_filename,
        'transformations': transformations,
        'reliability': reliability
    })
    session.modified = True
    
    # After calculations, save transformation details
    database.save_transformation_history(out_filename, [t['col'] for t in transformations])
    return render_template('result.html', 
                          transformations=transformations, 
                          reliability=reliability,
                          before_preview=before_preview, 
                          after_preview=after_preview, 
                          out_file=out_filename)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/history')
def history():
    # In a real app we'd fetch from mongo: list(database.transformations_collection.find())
    hist = session.get('history', [])
    return render_template('history.html', history=hist)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
