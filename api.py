import main

from flask import request, Flask


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/currency_converter', methods=['GET'])
def convert():

    out = main.convert(
        request.args.get('input_currency'),
        request.args.get('output_currency'),
        float(request.args.get('amount'))
    )

    return out

if __name__ == "__main__":

    app.run(port=5000)