import logging

from babs_kg.nodes.person import User
from neomodel import DoesNotExist
from pycountry import countries

kg_countries = {}
logger = logging.getLogger(__name__)


def update_kg_with_user(user: dict):
  try:
    kg_user = User.nodes.get_or_none(uuid=user["uuid"])

    if not kg_user:
      kg_user = User(uuid=user["uuid"], first_name=user["first_name"],
                     last_name=user.get("last_name", None),
                     user=True, email=user["email"]).save()

    # Add country
    kg_user.country.connect(kg_countries[user["country"]])

  except DoesNotExist as e:
    logger.error(e)


def initialize_kg_countries():
  from babs_kg.nodes.location import Country
  for _country in countries:
    country = Country.get_or_create(
      {"code": _country.alpha_2,
       "name": _country.name})[0]
    kg_countries[_country.alpha_2] = country
