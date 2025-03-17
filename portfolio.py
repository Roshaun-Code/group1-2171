from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SelectField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.exceptions import RequestEntityTooLarge
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'mp4'}
MAX_ITEMS = 6

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

portfolio_bp = Blueprint('portfolio', __name__, template_folder='templates', static_folder='static')

db = SQLAlchemy()

class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)

class PortfolioForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    file = FileField('File', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Bridal', 'Bridal'), ('Birthday', 'Birthday'), ('Fashion', 'Fashion')], validators=[DataRequired()])
    submit = SubmitField('Upload')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@portfolio_bp.errorhandler(RequestEntityTooLarge)
def handle_file_size_error(e):
    flash('File too large. Maximum size is 16 MB.', 'danger')
    return redirect(request.url)

@portfolio_bp.route('/', methods=['GET'])
def index():
    category = request.args.get('category')
    items = PortfolioItem.query.filter_by(category=category).all() if category and category != 'All' else PortfolioItem.query.all()
    categories = ['All', 'Bridal', 'Birthday', 'Fashion']
    form = PortfolioForm()  # Create an instance of the form
    return render_template('showcase.html', items=items, categories=categories, selected_category=category or 'All', form=form)

@portfolio_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    form = PortfolioForm()
    
    if db.session.query(PortfolioItem).count() >= MAX_ITEMS:
        flash(f'You can only upload up to {MAX_ITEMS} portfolio items.', 'warning')
        return redirect(url_for('portfolio.index'))

    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)  # Use absolute path
            
            file.save(file_path)

            new_item = PortfolioItem(title=form.title.data, filename=filename, category=form.category.data)
            db.session.add(new_item)
            db.session.commit()

            flash('Portfolio item uploaded successfully!', 'success')
            return redirect(url_for('portfolio.index'))
        else:
            flash('Invalid file type or upload error.', 'danger')

    return render_template('portfolioupload.html', form=form)

@portfolio_bp.route('/delete/<int:item_id>', methods=['GET','POST'])
def delete(item_id):
    item = PortfolioItem.query.get_or_404(item_id)
    file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, item.filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(item)
    db.session.commit()

    flash('Portfolio item deleted successfully!', 'success')
    return redirect(url_for('portfolio.index'))

@portfolio_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    item = PortfolioItem.query.get_or_404(item_id)
    form = PortfolioForm(obj=item)

    if form.validate_on_submit():
        item.title = form.title.data
        item.category = form.category.data

        if form.file.data:
            file = form.file.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
                file.save(file_path)
                item.filename = filename

        db.session.commit()
        flash('Portfolio item updated successfully!', 'success')
        return redirect(url_for('portfolio.index'))

    return render_template('portfolioedit.html', form=form, item=item)