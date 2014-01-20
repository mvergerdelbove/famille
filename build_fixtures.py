import datetime
import random
import json


def boolean():
    return bool(random.randint(0, 1))


def language_level():
    return random.choice([None, "mid", "bil", "deb", "pro"])


def types():
    return random.choice(["part", "pro"])


def description():
    return "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."


def first_name():
    return random.choice(["Jean", "Romain", "Louis", "Loic", "Margaux", "Jacques", "Hugues", "Tiphaine", "Maxime", "Alain", "Yvette"])


def name():
    return random.choice(["Martin", "Dupond", "Dupont", "Dupontel", "De la maison", "De la rue", "Durand", "Valjean", "Rousseau"])


def diploma():
    return random.choice([None, "cap", "deaf", "ast", "deeje"])

postal_codes = {
    "Paris": ["75001", "75010", "75017"],
    "Marseille": ["13011", "13001", "13005"],
    "Meudon": ["92190", "92360"]
}


def city_code():
    city = random.choice(["Paris", "Meudon", "Marseille"])
    return city, random.choice(postal_codes[city])


def tarif():
    return random.uniform(0, 80)


booleans = [
    "baby", "cdt_periscolaire", "devoirs", "menage", "non_fumeur", "nuit",
    "permis", "psc1", "repassage", "sortie_ecole", "urgence"
]

languages = [
    "level_de", "level_en", "level_es", "level_it"
]


def generate_users():
    data = []
    for i in xrange(15, 35):
        data.append(generate_user(i))
        data.append(generate_presta(i))

    return data

def generate_user(i):
    return {
        "model": "auth.user",
        "pk": i,
        "fields": {
            "username": "presta%s@gmail.com" % i,
            "password": "presta",
            "email": "presta%s@gmail.com" % i,
        }
    }


def generate_presta(i):
    city, code = city_code()
    fields = {
        "user": i,
        "email": "presta%s@gmail.com" % i,
        "first_name": first_name(),
        "name": name(),
        "description": description(),
        "tarif": tarif(),
        "city": city,
        "postal_code": code,
        "country": "France",
        "diploma": diploma(),
        "type": types(),
        "created_at": str(datetime.date.today()),
        "updated_at": str(datetime.date.today()),
    }
    for b in booleans:
        fields[b] = boolean()

    for l in languages:
        fields[l] = language_level()

    return {
        "model": "famille.prestataire",
        "pk": i,
        "fields": fields
    }


if __name__ == "__main__":
    data = json.dumps(generate_users())
    with open("famille/fixtures/prestataires.json", "w+") as f:
        f.write(data)
