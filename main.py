from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
import os

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class TeamModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    league = db.Column(db.String(20), nullable=False)
    division = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f'Team(name={self.name}, city={self.city}, league={self.league}, division={self.division})'
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    
    def __repr__(self) -> str:
        return f"User('{self.name}')"
    
#db.create_all()



team_put_args = reqparse.RequestParser()
team_put_args.add_argument('name', type=str, help='Team name required', required=True)
team_put_args.add_argument('city', type=str, help='Team city required', required=True)
team_put_args.add_argument('league', type=str, help='Team league required', required=True)
team_put_args.add_argument('division', type=str, help='Team division required', required=True)

team_patch_args = reqparse.RequestParser()
team_patch_args.add_argument('name', type=str, help='Team name required')
team_patch_args.add_argument('city', type=str, help='Team city required')
team_patch_args.add_argument('league', type=str, help='Team league required')
team_patch_args.add_argument('division', type=str, help='Team division required')

resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'city': fields.String,
    'league': fields.String,
    'division': fields.String
}

@auth.verify_password
def verify(username, password):
    user = User.query.filter_by(name=username).first()
    if not user:
        return False
    user_password = user.password
    return user_password == password

class Team(Resource):
    @marshal_with(resource_fields)
    def get(self, team_id):
        result = TeamModel.query.filter_by(id=team_id).first()
        if not result:
            abort(404, message='Could not find team with that ID.')
        return result
    
    @auth.login_required
    @marshal_with(resource_fields)
    def put(self, team_id):
        args = team_put_args.parse_args()
        result = TeamModel.query.filter_by(id=team_id).first()
        if result:
            abort(409, message='Team ID already exists.')
        team = TeamModel(id=team_id, name=args.name, city=args.city, league=args.league, division=args.division)
        db.session.add(team)
        db.session.commit()
        return team, 201
    
    @auth.login_required
    @marshal_with(resource_fields)
    def patch(self, team_id):
        args = team_patch_args.parse_args()
        result = TeamModel.query.filter_by(id=team_id).first()
        if not result:
            abort(404, message="Team ID doesn't exist, cannot update")
        if args.name:
            result.name = args.name
        if args.city:
            result.city = args.city
        if args.league:
            result.league = args.league
        if args.division:
            result.division = args.division
        db.session.commit()
        return result
    
    @auth.login_required
    @marshal_with(resource_fields)
    def delete(self, team_id):
        result = TeamModel.query.filter_by(id=team_id).first()
        if not result:
            abort(404, message="Team ID doesn't exist, cannot delete")
        db.session.delete(result)
        db.session.commit()
        return {'message': 'Team deleted'}

api.add_resource(Team, '/team/<int:team_id>')



if __name__ == '__main__':
    app.run()