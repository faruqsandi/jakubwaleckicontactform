from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Sample data (will be replaced with database calls later)
sample_missions = [
    {'id': 1, 'name': 'Marketing Campaign 2025', 'created_date': '2025-08-01', 'status': 'Active'},
    {'id': 2, 'name': 'Customer Survey', 'created_date': '2025-07-15', 'status': 'Draft'},
    {'id': 3, 'name': 'Product Feedback', 'created_date': '2025-07-20', 'status': 'Active'},
]

sample_domains = [
    'example.com',
    'testsite.org',
    'demo.net',
    'sample.io'
]

sample_missing_forms = [
    'missingform1.com',
    'noform.org'
]

sample_fields = [
    {'name': 'name', 'type': 'text', 'required': True},
    {'name': 'email', 'type': 'email', 'required': True},
    {'name': 'phone', 'type': 'tel', 'required': False},
    {'name': 'message', 'type': 'textarea', 'required': True},
    {'name': 'company', 'type': 'text', 'required': False},
]


@app.route('/')
def mission_list():
    """First page: Show list of missions"""
    return render_template('mission_list.html', missions=sample_missions)


@app.route('/create_mission', methods=['GET', 'POST'])
def create_mission():
    """Create new mission"""
    if request.method == 'POST':
        mission_name = request.form.get('mission_name')
        # TODO: Save to database
        flash(f'Mission "{mission_name}" created successfully!', 'success')
        return redirect(url_for('mission_list'))
    return render_template('create_mission.html')


@app.route('/mission/<int:mission_id>')
def select_mission(mission_id):
    """Select a mission and store in session"""
    session['current_mission_id'] = mission_id
    mission = next((m for m in sample_missions if m['id'] == mission_id), None)
    if mission:
        session['current_mission_name'] = mission['name']
        flash(f'Mission "{mission["name"]}" selected!', 'info')
    return redirect(url_for('config_page'))


@app.route('/config')
def config_page():
    """Second page: Config page with CSV upload"""
    if 'current_mission_id' not in session:
        flash('Please select a mission first.', 'warning')
        return redirect(url_for('mission_list'))
    return render_template('config.html', mission_name=session.get('current_mission_name'))


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    """Handle CSV upload"""
    if 'csv_file' not in request.files:
        flash('No file selected!', 'error')
        return redirect(url_for('config_page'))

    file = request.files['csv_file']
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('config_page'))

    # TODO: Process CSV file and extract URLs
    # For now, simulate processing with sample domains
    uploaded_domains = [
        'example.com',
        'testsite.org',
        'demo.net',
        'sample.io',
        'contact-form.com',
        'business-site.net'
    ]

    session['uploaded_domains'] = uploaded_domains
    session['csv_filename'] = file.filename
    flash(f'CSV uploaded successfully! Found {len(uploaded_domains)} domains.', 'success')
    session['csv_uploaded'] = True
    return redirect(url_for('config_page'))


@app.route('/missing_forms')
def missing_forms():
    """Third page: Missing forms page"""
    if 'current_mission_id' not in session:
        flash('Please select a mission first.', 'warning')
        return redirect(url_for('mission_list'))

    if not session.get('csv_uploaded'):
        flash('Please upload CSV file first.', 'warning')
        return redirect(url_for('config_page'))

    return render_template('missing_forms.html',
                           missing_forms=sample_missing_forms,
                           mission_name=session.get('current_mission_name'))


@app.route('/get_forms', methods=['POST'])
def get_forms():
    """Get form information for missing domains"""
    # TODO: Implement form detection logic
    flash('Form information retrieved successfully!', 'success')
    session['forms_retrieved'] = True
    return redirect(url_for('missing_forms'))


@app.route('/submission_config')
def submission_config():
    """Fourth page: Submission config page"""
    if 'current_mission_id' not in session:
        flash('Please select a mission first.', 'warning')
        return redirect(url_for('mission_list'))

    return render_template('submission_config.html',
                           fields=sample_fields,
                           mission_name=session.get('current_mission_name'))


@app.route('/save_submission_config', methods=['POST'])
def save_submission_config():
    """Save submission configuration"""
    # TODO: Save field values to session or database
    for field in sample_fields:
        field_value = request.form.get(field['name'])
        session[f'field_{field["name"]}'] = field_value

    flash('Submission configuration saved!', 'success')
    return redirect(url_for('submission_process'))


@app.route('/submission_process')
def submission_process():
    """Fifth page: Submission process page"""
    if 'current_mission_id' not in session:
        flash('Please select a mission first.', 'warning')
        return redirect(url_for('mission_list'))

    # Use uploaded domains if available, otherwise use sample data
    domains = session.get('uploaded_domains', sample_domains)

    return render_template('submission_process.html',
                           domains=domains,
                           mission_name=session.get('current_mission_name'))


@app.route('/submit_forms', methods=['POST'])
def submit_forms():
    """Submit forms to all domains"""
    # TODO: Implement form submission logic
    flash('Forms submitted successfully to all domains!', 'success')
    return redirect(url_for('submission_process'))


@app.route('/reset_session')
def reset_session():
    """Reset session and go back to mission list"""
    session.clear()
    flash('Session reset. Please start over.', 'info')
    return redirect(url_for('mission_list'))


@app.route('/clear_csv')
def clear_csv():
    """Clear uploaded CSV data"""
    session.pop('uploaded_domains', None)
    session.pop('csv_filename', None)
    session.pop('csv_uploaded', None)
    flash('CSV data cleared.', 'info')
    return redirect(url_for('config_page'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
