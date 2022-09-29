import fastapi
from fastapi import Depends, FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import redis

from app.model import UserSchema, UserLoginSchema
from app.auth.auth_handler import sign_jwt
from app.auth.auth_bearer import JWTBearer

# se connecte à la bdd Redis
r = redis.Redis(host='localhost', port=6379, db=0)
redis_max_entries = 200

users = []

dev = UserSchema(
    username="dev",
    password="1234",
    email="dev@localhost.com")

users.append(dev)

app = FastAPI()

# origines autorisées de l'API
origins = [
    "http://localhost:5000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#################
# Racine
#################

@app.get("/", tags=["root"])
def read_root():
    return "it's alive!"


#################
# Gestion des utilisateurs
#################

def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False


@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return sign_jwt(user.email)
    else:
        raise fastapi.HTTPException(status_code=401, detail="Wrong login details !")


#################
# Coordonées
#################

# obtient toutes les coordonées
@app.get("/coordinates", tags=["coordinates"])
def get_all_coordinates():
    try:
        coordinates = r.geosearch(name='coordinates', sort="ASC", longitude="0", latitude="0", radius="20000", unit="km", withcoord=True)

        # vérifie présence coordonées, rend erreur si aucune n'est trouvée
        if not coordinates:
            raise fastapi.HTTPException(status_code=410, detail="No coordinates were found !")
        else:
            return sorted(coordinates)

    except redis.exceptions.ConnectionError:
        raise fastapi.HTTPException(status_code=500, detail="Couldn't connect to database !")


# ajoute une nouvelle paire de coordonées
@app.post("/coordinates/add", dependencies=[Depends(JWTBearer())], tags=["coordinates"])
def add_new_coordinate(longitude: float, latitude: float, timestamp: int):
    try:
        geoadd = r.geoadd(name='coordinates', values=[longitude, latitude, int(timestamp)], nx=True, xx=False, ch=False)

        # if coordinates were added
        if geoadd == 1:
            # supprime anciennes entrées jusqu'à total < redis_max_entries:
            while r.zcount(name='coordinates', min="-inf", max="+inf") > redis_max_entries:
                # enlève entrée la plus vieille
                r.zremrangebyrank(name='coordinates', min=-1, max=-1)

            return "successfully added '{0}: [{1}, {2}]' to database".format(timestamp, latitude, longitude)

        # if coordinates were NOT added - another coordinate pairs had same timestamp value
        elif geoadd == 0:
            raise fastapi.HTTPException(status_code=400, detail="Error! Coordinates corresponding to the timestamp '{0}' were already present !".format(timestamp))

    except redis.exceptions.ConnectionError:
        raise fastapi.HTTPException(status_code=500, detail="Couldn't connect to database !")

    except redis.exceptions.ResponseError:
        raise fastapi.HTTPException(status_code=400, detail="Coordinates are not valid - supported longitude are from -180° to 180° degrees and supported latitude are from -85.05112878° to 85.05112878°.")
