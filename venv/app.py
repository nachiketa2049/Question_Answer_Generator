from flask import Flask, render_template, request
import model

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        text = request.form.get('text_area')
        ls = list(model.generate_qa(text))
        return render_template('generated.html', qa=ls)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
