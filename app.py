from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from models import db,Bmi
from dataset import dSet
import openai 
  
openai.api_key = 'sk-proj-RngpeIFwWwyH6NuWobw7T3B1bkFJs5pdgYy37NjgBvYUZafc'

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bmi_calc.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

Migrate(app, db)
ma = Marshmallow(app)
db.init_app(app)
with app.app_context():
    db.create_all()

class BmiSchema(ma.Schema):
    class Meta:
        fields = ("id","name","weight","height","bmi")
bmi_schema = BmiSchema()
bmis_schema = BmiSchema(many=True)

@app.route('/')
def index():
    return {"msg": "Welcome Dashboard"}

# BMI Calculation Layer
@app.route('/calcBmi', methods=['POST'])
def calculateBmi():
    try:
        name = request.json['name']
        weight = request.json['weight'] #kg
        height = request.json['height'] #m^2
        bmi = (weight/(height**2))*10000 # kg/cm2
        res=''
        if bmi <= 18.5:
            res="You are under weight as per your BMI"
        elif (bmi >= 18.5) and (bmi <= 24.9):
            res = 'Perfect! You are fit'
        elif (bmi >= 25) and (bmi <= 29.9):
            res = 'You are overweight as per your BMI'
        elif bmi >= 30:
            res = 'You are highly obese as per your BMI'

        
        bmiObj = Bmi(name,weight,height,bmi)
        db.session.add(bmiObj)
        db.session.commit()
       
        result = {
            "bmi": bmiObj.bmi,
            "height": bmiObj.height,
            "id": bmiObj.id,
            "name": bmiObj.name,
            "weight": bmiObj.weight,
            "result":res
        }

        return jsonify(result)
    except:
        return "Exception Raised"

@app.route('/getBmis', methods=['GET'])
def getBmis():
    try:
        bmis = Bmi.query.all()
        if bmis:
            bmis = bmis_schema.dump(bmis)
            return jsonify(bmis)
        else:
            return "No records in DB. Please ADD."
    except:
        return "Exception Raised"

# Local GPT Layer
def getReply(question):
    question = question.split(' ')
    for i in question:
        if i in dSet:
            return dSet[i]

def validateReply(reply):
    if reply == None:
        reply = 'Not able to find the answer :('
    return reply

@app.route('/localGpt', methods=['POST'])
def localGpt():
    ques = request.json['question']
    reply = getReply(ques)
    reply = validateReply(reply)
    return {"Question":ques,"Response":reply}
        
@app.route('/chatGpt', methods=['POST'])
def chatGptIntg():
    ques = request.json['question']
    messages = [{"role": "system", "content": "You are a intelligent assistant."}] 

    if ques: 
        messages.append({"role": "user", "content": ques}) 
        chat = openai.chat.completions.create( 
            model="gpt-3.5-turbo",
            messages=messages 
        ) 
    reply = chat.choices[0].message.content 
    print(f"ChatGPT: {reply}")
    return {"Question":ques,"Response":reply}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')