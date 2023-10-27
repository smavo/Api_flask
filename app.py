from flask import Flask

app = Flask(__name__)

stores = [
    {
        "name": "My Steore",
        "items": {
            "name": "Dynamo Soft",
            "price": 18.00
        }
    }
]


@app.route("/store")
def get_store():
    return {"Store": stores}
