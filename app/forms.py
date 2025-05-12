from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import PasswordField
from wtforms.validators import Email, EqualTo
from wtforms import (StringField, IntegerField, TextAreaField, SelectField,
                     BooleanField, DateField, SubmitField)
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from datetime import date




class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class StudySessionForm(FlaskForm):
    date = DateField('Date',
                     validators=[DataRequired()],
                     default=date.today)
    duration_minutes = IntegerField('Duration (minutes)',
                                    validators=[DataRequired(), NumberRange(min=1)])

    # Skills checkboxes - using BooleanField for each skill
    reading = BooleanField('Reading')
    writing = BooleanField('Writing')
    listening = BooleanField('Listening')
    speaking = BooleanField('Speaking')
    vocabulary = BooleanField('Vocabulary')
    grammar = BooleanField('Grammar')

    activity_type = SelectField('Activity Type',
                                choices=[
                                    ('', 'Select activity type'),
                                    ('textbook', 'Textbook Exercise'),
                                    ('conversation', 'Conversation Practice'),
                                    ('video_audio', 'Video/Audio Lesson'),
                                    ('reading_article', 'Reading Article'),
                                    ('writing_essay', 'Writing Essay'),
                                    ('vocabulary_practice', 'Vocabulary Practice'),
                                    ('grammar_exercise', 'Grammar Exercise'),
                                    ('other', 'Other')
                                ],
                                validators=[DataRequired()])

    notes = TextAreaField('Notes and Reflections')

    rating = IntegerField('How productive was this session?',
                          validators=[NumberRange(min=1, max=5)],
                          default=3)

    submit = SubmitField('Save Session')

    @property
    def skills(self):
        """Helper property to get all skill fields"""
        return [self.reading, self.writing, self.listening,
                self.speaking, self.vocabulary, self.grammar]

    def get_selected_skills(self):
        """Get list of selected skill names"""
        skill_names = ['reading', 'writing', 'listening',
                       'speaking', 'vocabulary', 'grammar']
        selected = []
        for i, skill_field in enumerate(self.skills):
            if skill_field.data:
                selected.append(skill_names[i])
        return selected


class BulkUploadForm(FlaskForm):
    file = FileField('Upload File',
                     validators=[
                         DataRequired(message='Please select a file'),
                         FileAllowed(['csv', 'xlsx', 'txt'], 'Only CSV, Excel, and text files allowed!')
                     ])
    overwrite = BooleanField('Overwrite existing data with same dates/identifiers')
    submit = SubmitField('Upload Files')


class AssessmentResultForm(FlaskForm):
    assessment_name = StringField('Assessment Name',
                                  validators=[DataRequired(), Length(min=1, max=200)])
    assessment_type = SelectField('Assessment Type',
                                  choices=[
                                      ('quiz', 'Quiz'),
                                      ('test', 'Test'),
                                      ('exam', 'Exam'),
                                      ('homework', 'Homework'),
                                      ('project', 'Project'),
                                      ('presentation', 'Presentation'),
                                      ('other', 'Other')
                                  ],
                                  validators=[DataRequired()])
    date_taken = DateField('Date Taken',
                           validators=[DataRequired()],
                           default=date.today)
    score = IntegerField('Score',
                         validators=[DataRequired(), NumberRange(min=0, max=100)])
    max_score = IntegerField('Max Score',
                             validators=[DataRequired(), NumberRange(min=1)],
                             default=100)
    skill_area = SelectField('Skill Area',
                             choices=[
                                 ('reading', 'Reading'),
                                 ('writing', 'Writing'),
                                 ('listening', 'Listening'),
                                 ('speaking', 'Speaking'),
                                 ('vocabulary', 'Vocabulary'),
                                 ('grammar', 'Grammar'),
                                 ('mixed', 'Mixed Skills')
                             ],
                             validators=[DataRequired()])
    feedback = TextAreaField('Feedback/Comments')
    submit = SubmitField('Save Assessment')


class VocabularyForm(FlaskForm):
    word = StringField('Word/Phrase',
                       validators=[DataRequired(), Length(min=1, max=100)])
    translation = StringField('Translation',
                              validators=[Optional(), Length(max=200)])
    definition = TextAreaField('Definition')
    context = TextAreaField('Example Sentence')
    category = StringField('Category/Topic',
                           validators=[Optional(), Length(max=50)])
    level = SelectField('Difficulty Level',
                        choices=[
                            ('beginner', 'Beginner'),
                            ('elementary', 'Elementary'),
                            ('intermediate', 'Intermediate'),
                            ('advanced', 'Advanced'),
                            ('expert', 'Expert')
                        ],
                        validators=[DataRequired()])
    submit = SubmitField('Add Vocabulary')


class LearningGoalForm(FlaskForm):
    goal_title = StringField('Goal Title',
                             validators=[DataRequired(), Length(min=1, max=200)])
    goal_type = SelectField('Goal Type',
                            choices=[
                                ('skill', 'Skill Improvement'),
                                ('vocabulary', 'Vocabulary Target'),
                                ('certification', 'Certification/Test'),
                                ('fluency', 'Fluency Level'),
                                ('time', 'Study Time'),
                                ('other', 'Other')
                            ],
                            validators=[DataRequired()])
    target_date = DateField('Target Date',
                            validators=[DataRequired()])
    current_level = IntegerField('Current Level (0-100)',
                                 validators=[NumberRange(min=0, max=100)],
                                 default=0)
    target_level = IntegerField('Target Level (0-100)',
                                validators=[NumberRange(min=0, max=100)],
                                default=100)
    description = TextAreaField('Description')
    action_plan = TextAreaField('Action Plan')
    submit = SubmitField('Save Goal')