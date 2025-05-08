from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
import uuid
from app.extensions import db
from app.models import Data, DataType
from app.forms import DataUploadForm, StudySessionForm
from datetime import datetime

data_bp = Blueprint('data', __name__, url_prefix='/data')

# Upload data page
@data_bp.route('/upload', methods=['GET'])
@login_required
def upload():
    data_upload_form = DataUploadForm()
    study_session_form = StudySessionForm()
    return render_template('upload_data.html', 
                          data_upload_form=data_upload_form,
                          study_session_form=study_session_form,
                          title="Upload Data")

# Process file upload
@data_bp.route('/upload-file', methods=['POST'])
@login_required
def upload_file():
    form = DataUploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        
        if file:
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Secure the filename and ensure uniqueness
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Create data record
            new_data = Data(
                user_id=current_user.id,
                title=form.title.data,
                data_type=DataType(form.data_type.data),
                description=form.description.data,
                file_path=os.path.join('uploads', str(current_user.id), unique_filename)
            )
            
            db.session.add(new_data)
            db.session.commit()
            
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('data.upload'))
        else:
            flash('No file selected!', 'error')
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{getattr(form, field).label.text}: {error}', 'error')
            
    return redirect(url_for('data.upload'))

# Process study session logging
@data_bp.route('/log-study-session', methods=['POST'])
@login_required
def log_study_session():
    form = StudySessionForm()
    
    if form.validate_on_submit():
        try:
            # Create metadata
            metadata = {
                'date': form.date.data,
                'duration': form.duration.data
            }
            
            # Create data record
            new_data = Data(
                user_id=current_user.id,
                title=form.title.data,
                data_type=DataType.STUDY_TIME,
                content=form.content.data,
                metadata=metadata
            )
            
            db.session.add(new_data)
            db.session.commit()
            
            flash('Study session logged successfully!', 'success')
        except Exception as e:
            flash(f'Error logging study session: {str(e)}', 'error')
            
    return redirect(url_for('data.upload'))

# View all user data
@data_bp.route('/my-data')
@login_required
def my_data():
    user_data = Data.query.filter_by(user_id=current_user.id).order_by(Data.created_at.desc()).all()
    return render_template('my_data.html', data=user_data, title='My Data')
