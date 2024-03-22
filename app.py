from flask import Flask, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap

from forms import *
from scrapers import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-secret-key'
Bootstrap(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

global driver
driver = ''


@login_manager.user_loader
def load_user(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instalikes.users WHERE id=%s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()

    if user_data:
        return User(*user_data)
    return None


class User(UserMixin):
    def __init__(self, id, username, password, secret_question, secret_answer):
        self.id = id
        self.username = username
        self.password = password
        self.secret_question = secret_question
        self.secret_answer = secret_answer


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()
        secret_question = form.secret_question.data.strip()
        secret_answer = form.secret_answer.data.strip()

        # Check if the username is already taken
        existing_user = get_user(username)

        if existing_user:
            flash('Username is already taken. Please choose a different one.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Insert the new user into the database
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO instalikes.users (username, password, question, answer) VALUES (%s, %s, %s, %s)", 
                (username, hashed_password, secret_question, secret_answer))
            conn.commit()
            cursor.close()

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # If the user is already logged in, redirect to the 'stats' page
        return redirect(url_for('stats'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()

        user_data = get_user(username)

        if user_data and bcrypt.check_password_hash(user_data[2], password):
            user = User(*user_data)
            login_user(user)
            # Redirect to the 'stats' page after successful login
            return redirect(url_for('stats'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    global driver
    if driver:
        driver.quit()
        driver = ''
    flash('You have been logged out.', 'success')

    return redirect(url_for('login'))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        secret_question = form.secret_question.data.strip()
        secret_answer = form.secret_answer.data.strip()
        new_password = form.new_password.data

        # Check if the provided answer matches the stored answer
        user_data = get_user(username)

        if user_data and user_data[3] == secret_question and user_data[4] == secret_answer:
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

            cursor = conn.cursor()
            cursor.execute(
                "UPDATE instalikes.users SET password=%s WHERE username=%s", 
                (hashed_password, username))
            conn.commit()
            cursor.close()

            flash('Password updated successfully. You can now log in with the new password.', 'success')
        else:
            flash('Wrong username or secret question/answer.', 'danger')

    return render_template('forgot_password.html', form=form)


@app.route('/details/<id>/')
def details(id):
    all_likes = get_all_likes()[int(id)-1]
    username = all_likes[1]
    caption = all_likes[2]
    images = all_likes[5:]

    comments = all_likes[3].split('\nReply\n')
    comments_data = []

    for i in comments:
        comment = i.split('\n')
        if len(comment) < 3:
            continue

        user = comment[0]
        comm = comment[2]

        if 'View all ' in user and ' replies' in user or 'Hide all replies' in user:
            user = comment[1]
            comm = comment[3]

        if comm.startswith('@'):
            comments_data.append((user, comm, ' '))
        else:
            comments_data.append((user, comm))

    return render_template('details.html', 
        images=images, user=username, caption=caption, comments=comments_data)


@app.route('/stats', methods=['GET', 'POST'])
@login_required
def stats():
    form = InstagramCredentialsForm()
    all_likes = get_all_likes()
    all_comments = get_all_comments()

    if form.validate_on_submit():
        username = form.instagram_email.data.strip()
        password = form.instagram_password.data.strip()
        code = form.security_code.data.strip()

        global driver
        if not driver:
            driver = driver_init()

        if code and 'instagram.com/challenge/action/' in driver.current_url:
            security_code = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'security_code')))
            submit = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    'section > div > div > div._ad-m > form > span > button')))

            security_code.send_keys(code)
            submit.click()
            time.sleep(10)
        else:
            if "'name': 'sessionid'" not in str(driver.get_cookies()):
                driver.get('https://www.instagram.com/accounts/login/')

                email = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'username')))
                passw = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.NAME, 'password')))

                email.send_keys(username)
                passw.send_keys(password)
                passw.send_keys(Keys.ENTER)

                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'section._aa55')))
                except TimeoutException:
                    try:
                        driver.find_element(By.CSS_SELECTOR, 
                            'section > div > div > div._ad-m > form > span > button').click()
                        return jsonify({'likes': [], 'comments': [], 
                            'message': 'Instagram asks for a security code which have been sent to your email. '
                            'Please check your email, enter the code and press Backup Likes again'})
                    except NoSuchElementException:
                        pass

        if "'name': 'sessionid'" in str(driver.get_cookies()):
            likes = scrape_likes(driver, current_user.id)
            comments = scrape_comments(driver, current_user.id)
            return jsonify({'likes': likes, 'comments': comments, 'message': ''})
        else:
            return jsonify({'likes': [], 'comments': [], 
                'message': 'Instagram login failed, check your Instagram username and password'})

    return render_template('stats.html', form=form, 
        data={'all_likes': all_likes, 'all_comments': all_comments})


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=7000)
