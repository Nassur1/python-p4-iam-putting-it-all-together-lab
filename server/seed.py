#!/usr/bin/env python3
from random import randint, choice as rc
from faker import Faker
from config import app, db
from models import User, Recipe

fake = Faker()

with app.app_context():
    print("Deleting all records...")
    Recipe.query.delete()
    User.query.delete()
    db.session.commit()

    print("Creating users...")
    users = []
    usernames = set()

    for i in range(20):
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        usernames.add(username)

        user = User(
            username=username,
            bio=fake.paragraph(nb_sentences=3),
            image_url=fake.url(),
        )
        user.password = username + "password"  # properly hashes password
        users.append(user)

    db.session.add_all(users)
    db.session.commit()

    print("Creating recipes...")
    recipes = []
    for i in range(100):
        recipe = Recipe(
            title=fake.sentence(),
            instructions=fake.paragraph(nb_sentences=8),
            minutes_to_complete=randint(15, 90),
            user=rc(users)
        )
        recipes.append(recipe)

    db.session.add_all(recipes)
    db.session.commit()
    print("Seeding complete!")
