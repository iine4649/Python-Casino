from flask import Flask, render_template

app = Flask(__name__, template_folder="../assets", static_folder="../assets")


@app.route("/")
def login():
    return render_template("secure_login.html")


@app.route("/sign-up")
def sign_up():
    return render_template("secure_sign_up.html")


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
