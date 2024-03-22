from wtforms import StringField, PasswordField, SubmitField, SelectField, validators
from flask_wtf import FlaskForm


questions = [
    ('pet', 'What is the name of your first pet?'),
    ('city', 'In which city was your mother born?'),
    ('dream', 'What did you dream about in childhood?'),
    ('insta', 'Instagram username of your favorite Instagram person?'),
    ('parents', "What was the place of your parents' first date?")
]


class ForgotPasswordForm(FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=3, max=29)
    ])
    secret_question = SelectField('Choose Question', choices=questions)
    secret_answer = StringField('Secret Answer', [validators.DataRequired()])

    new_password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.Length(min=4, max=100),
        validators.EqualTo('new_confirm_password', message='Passwords must match')
    ])
    new_confirm_password = PasswordField('Confirm New Password', [
        validators.DataRequired(),
        validators.Length(min=4, max=100),
        validators.EqualTo('new_password', message='Passwords must match')
    ])

    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=3, max=29)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=4, max=100),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.Length(min=4, max=100),
        validators.EqualTo('password', message='Passwords must match')
    ])

    secret_question = SelectField('Choose Question', choices=questions)
    secret_answer = StringField('Secret Answer', [
        validators.DataRequired(),
        validators.Length(min=1, max=300)
    ])

    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=29)])
    password = PasswordField('Password', [validators.DataRequired()])
    submit = SubmitField('Sign In')


class InstagramCredentialsForm(FlaskForm):
    instagram_email = StringField('Instagram Username')
    instagram_password = PasswordField('Instagram Password')
    security_code = PasswordField('Security Code')
    submit = SubmitField('Update Credentials')
