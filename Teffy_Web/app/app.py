from flask import Flask, render_template, redirect, request, session, url_for, jsonify, make_response
import firebase_admin
from firebase_admin import credentials, auth, db, storage
import os
from werkzeug.utils import secure_filename
import sys
from blockfrost import ApiError, ApiUrls, BlockFrostApi, BlockFrostIPFS
from dotenv import load_dotenv
from datetime import datetime
from pycardano import *
import json
app = Flask(__name__, static_folder='static')
app.secret_key = '1111'
cred = credentials.Certificate("app/cred.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tchat-af17d-default-rtdb.firebaseio.com',
    'storageBucket': 'tchat-af17d.appspot.com'
})
def is_logged_in():
    return 'uid' in session
@app.route('/')
def home():
    return render_template('Teffy-Home.html')
@app.route('/set_cookie', methods=["POST"])
def set_cookie_uid():
    if request.method =="POST":
         data = request.get_json()
         uid = data.get("uid")
         print(uid)   
         response = make_response(jsonify({'message': 'UID set in cookie'}))
         response.set_cookie('uid', uid)
         return response
@app.route('/login', methods=["POST", "GET"])
def login():    
    if request.method == "POST":
        user_id = request.cookies.get('uid')
        ref = db.reference(f'users/{user_id}')
        user_data = ref.get()
        if user_data:
            return jsonify({'user_data': user_data})
        else:
            return jsonify({'message': 'User not found'}), 404  
    return render_template('Teffy_Login.html')
@app.route('/select_farm', methods=['POST'])
def select_farm():
    data = request.get_json()
    farm_id = data.get('farmId')
    if not farm_id:
        return jsonify({"message": "Farm ID is required"}), 400
    response = make_response(redirect('/Search_details_farmers'))
    response.set_cookie('selectedFarmId', farm_id, max_age=60*60*24*30)
    return response
@app.route('/get_farm', methods=['GET'])
def get_farm():
    farm_id = request.cookies.get('selectedFarmId')
    if not farm_id:
        return jsonify({"message": "No farm selected. Please select a farm first."}), 400
    return jsonify({"farmId": farm_id})   
@app.route('/register_farm_land', methods=['POST', 'GET'])
def register_farm_form():
    if(request.method == "POST"):
        user_id = request.cookies.get('uid')
        print(user_id)
        form_data = {
            'owner_user_id': user_id,
            'farmName': request.form['farmName'],
            'ownerName': request.form['ownerName'],
            'contactPhone': request.form['contactPhone'],
            'contactEmail': request.form['contactEmail'],
            'nationality': request.form['nationality'],
            'region': request.form['region'],
            'farmAddress': request.form['farmAddress'],
            'latitude': request.form['latitude'],
            'longitude': request.form['longitude'],
            'elevation': request.form['elevation'],
            'totalArea': request.form['totalArea'],
            'accessRoads': request.form['accessRoads'],
            'farmType': request.form['farmType'],
            'mainCrops': request.form['mainCrops'],
            'farmingPractice': request.form['farmingPractice'],
            'waterSource': request.form['waterSource'],
            'soilType': request.form['soilType'],
            'infrastructure': request.form['infrastructure'],
            'fundAmount': request.form['fundAmount'],
            'fundingPurpose': request.form['fundingPurpose'],
            'returnRate': request.form['returnRate'],
            'paybackPeriod': request.form['paybackPeriod'],
            'collateral': request.form['collateral'],
            'currentRevenue': request.form['currentRevenue'],
        }
        load_dotenv()
        network = os.getenv("network")
        wallet_mnemonic = os.getenv("wallet_mnemonic")
        blockfrost_api_key = os.getenv("blockfrost_api_key")
        if network == "testnet":
            base_url = ApiUrls.preprod.value
            cardano_network = Network.TESTNET
        else:
            base_url = ApiUrls.mainnet.value
            cardano_network = Network.MAINNET    
        new_wallet = crypto.bip32.HDWallet.from_mnemonic(wallet_mnemonic)
        payment_key = new_wallet.derive_from_path(f"m/1852'/1815'/0'/0/0")
        staking_key = new_wallet.derive_from_path(f"m/1852'/1815'/0'/2/0")
        payment_skey = ExtendedSigningKey.from_hdwallet(payment_key)
        staking_skey = ExtendedSigningKey.from_hdwallet(staking_key)
        main_address = Address(
            payment_part=payment_skey.to_verification_key().hash(),
            staking_part=staking_skey.to_verification_key().hash(),
            network=cardano_network,
        )
        api = BlockFrostApi(project_id=blockfrost_api_key, base_url=base_url)
        try:
            utxos = api.address_utxos(main_address)
        except Exception as e:
            if e.status_code == 404:
                print("Address does not have any UTXOs. ")
                if network == "testnet":
                    print(
                        "lease rq https://docs.cardano.org/cardano-testnets/tools/faucet/"
                    )
            else:
                print(e.message)
            sys.exit(1)
        cardano = BlockFrostChainContext(project_id=blockfrost_api_key, base_url=base_url)
        builder = TransactionBuilder(cardano)
        for i in range(20):
            output = TransactionOutput(main_address, Value(4000000))
            builder.add_output(output)
        builder.add_input_address(main_address)
        metadata = Metadata()
        metadata[10000] = {
            form_data
        }
        aux_data = AuxiliaryData(metadata)
        aux_data.metadata = metadata
        builder.auxiliary_data = aux_data
        signed_tx = builder.build_and_sign([payment_skey], change_address=main_address)
        result = cardano.submit_tx(signed_tx.to_cbor())
        print(f"Number of inputs: \t {len(signed_tx.transaction_body.inputs)}")
        print(f"Number of outputs: \t {len(signed_tx.transaction_body.outputs)}")
        print(f"Fee: \t\t\t {signed_tx.transaction_body.fee/1000000} ADA")
        print(f"Transaction submitted! ID: {result}")
        output_dir = 'Transaction-Validation'
        Special_Tag_UID = request.cookies.get('uid')
        output_filename = f"{output_dir}/{Special_Tag_UID}.json"
        os.makedirs(output_dir, exist_ok=True)
        with open(output_filename, 'w') as json_file:
         json.dump({"transaction_id": result}, json_file)
        hardcoded_url = "https://www.istockphoto.com/photo/aerial-view-of-fields-and-farmland-gm1263711041-369949935?utm_source=pixabay&utm_medium=affiliate&utm_campaign=sponsored_image&utm_content=srp_topbanner_media&utm_term=farmland"
        land_title_url = hardcoded_url
        farm_image_urls = hardcoded_url
        certification_urls = hardcoded_url  
        form_data['landTitle'] = land_title_url
        form_data['farmImages'] = farm_image_urls
        form_data['certifications'] = certification_urls
        ref = db.reference(f'users/{user_id}/land').push()
        ref.set(form_data)
        farm_id = ref.key
        farm_ref = db.reference(f'farms/{farm_id}')
        farm_ref.set(form_data)
        return jsonify({"message": "Farm registration successful!"}), 200
    return render_template("Farmer-Dash-RegisterLand.html")
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        uid = data.get('uid')
        if not uid:
            return jsonify({'message': 'UID missing'}), 400
        response = make_response(jsonify(url_for("login")))
        response.set_cookie('uid', uid)
        return response
    return render_template('Teffy_Sign-Up.html')
@app.route('/User_fetch_request', methods=["POST", "GET"])
def User_fetch_uid():
    if request.method == "POST":
        user_id = request.cookies.get('uid')
        if user_id:
            return jsonify({'user_id': user_id})
        else:
            return jsonify({'message': 'User not found'}), 404
    return render_template('Teffy_Login.html')
@app.route('/Role_fetch_request', methods=["POST", "GET"])
def Role_fetch_uid():
    if request.method == "POST":
        user_id = request.cookies.get('uid')
        user_ref = db.reference(f'users/{user_id}/role')
        role = user_ref.get()
        print(role)
        if(role == "farmer"):
            return jsonify({"role":"farmer"})
        if (role == "investor"):
            return jsonify({"role":"investor"})
        else:
            return jsonify({'message': 'Role not found'}), 404
    return render_template('Teffy_Login.html')
@app.route('/farmer-dashboard')
def farmer_dashboard():
    return render_template('Farmer-Dash.html')
@app.route('/invester-dashboard')
def invester_dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('Investor-Dash.html')
@app.route('/learn-more')
def learn_more():
    return render_template('Teffy_ult.html')
@app.route('/register-farm')
def register_farm():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('Farmer-Dash-RegisterLand.html')
@app.route('/signin-selection')
def signin_selection():
    return render_template('Teffy_Sign-Up.html')
@app.route('/my-lands')
def my_lands_route():
    return render_template('Farmer-Dash_My-Land-landing.html')
@app.route('/investor-dashboard')
def Ivestor_dashboard():
    return render_template('Investor-Dash.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
@app.route('/reports', methods=["POST", "GET"])
def report_fetch_R():
    return render_template('Farmer-Dash_Report.html')
@app.route('/investor_profile', methods=["POST", "GET"])
def investor_profile():
    return render_template('Investor-Dash_Profile.html')
@app.route('/api/validation/<uid>', methods=['GET'])
def get_validation_data(uid):
    output_dir = 'Transaction-Validation'
    filename = f"{output_dir}/{uid}.json"
    if not os.path.exists(filename):
        pass
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return jsonify(data)
@app.route('/funds', methods=["POST", "GET"])
def funds_cardano_base_main():
    return render_template('Farmer_funds.html')
@app.route('/Search_farmers', methods=["POST", "GET"])
def Search_farmers():
    return render_template('Investor-Dash-Connective.html')
@app.route('/Search_details_farmers', methods=['POST', 'GET'])
def Search_detial_farmers():
    return render_template('Investor-UIT.html')
@app.route('/invest_investor', methods=['POST', 'GET'])
def Invest():
    return render_template('Investor-Dash-Investement-form.html')
@app.route('/Notification_farmer', methods=["POST", "GET"])
def Notification_farmer():
    return render_template('Farmer-Dash-Notfication.html')
if __name__ == '__main__':
    app.run(debug=True)
