from flask import Flask
from flask import request, jsonify, redirect
import stripe
import json
app = Flask(__name__)
from flask_cors import CORS

app.config.from_pyfile('config.py')
stripe.api_key = app.config['SECRET_KEY_STRIPE']
cors = CORS(app)
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
def calculate_order_amount(items):
    return 1400

@app.post("/create-checkout-session")
def create_checkout_session():
    post_data = request.json
    price = post_data['price']
    product_name = post_data['product_name']
    try:
        checkout_session = stripe.checkout.Session.create(
        line_items =[{
        'price_data' :{
            'currency' : 'usd',  
            'product_data': {
                'name': product_name,
            },
            'unit_amount': price
        },
        'quantity' : 1
        }],
        mode= 'payment',
        success_url= "http://localhost:9099/success",
        cancel_url= "http://localhost:9099/cancel",
        )
        return redirect(checkout_session.url , code=303)
    except Exception as e:
        print('ok')
        print(e)
        return e

@app.post('/create-payment-intent')
def create_payment():
    try:
        data = json.loads(request.data)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(data['items']),
            currency='inr',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        print(intent['client_secret'])
        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        print("asd")
        return jsonify(error=str(e)), 403


@app.post("/stripe-webhook")
def webhook_received():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError as e:
        # Invalid payload
        return jsonify(ok=False, message="Invalid Request")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify(ok=False, message="Invalid Request")

    if event['type'] == 'payment_intent.succeeded':
      payment_intent = event['data']['object']
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))
      return jsonify(ok=False, message="Unknown Error")
    return jsonify(ok=True)


if __name__ == '__main__':
    app.run(port=6105)