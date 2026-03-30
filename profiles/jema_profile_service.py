# profiles/jema_profile_service.py
"""
Jema Profile Service
====================
Provides get_user_profile_context() for Jema to personalise
recipe suggestions and generation based on the user's profile.

Intentionally separate from profiles/services.py to avoid
any interference with the PoaPoints system.
"""
from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_profile_context(user_id) -> dict:
    """
    Accepts a user_id integer from the chat request body.
    Fetches the user's Profile and returns a structured
    context dict for Jema to personalise recipe output.

    Returns safe empty defaults if:
    - user_id is None or invalid
    - User does not exist
    - Profile does not exist
    - Profile fields are incomplete

    Jema works normally with defaults — no personalisation
    is applied but nothing breaks.
    """
    if not user_id:
        return _default_profile_context()

    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
    except (User.DoesNotExist, Exception):
        return _default_profile_context()

    context = {
        # ── BASIC INFO ─────────────────────────────────────────
        "name": profile.name or "User",
        "age": profile.age,
        "gender": profile.gender or None,
        "location": profile.location or None,

        # ── HEALTH METRICS ─────────────────────────────────────
        "current_weight_kg": profile.current_weight_kg,
        "current_height_cm": profile.current_height_cm,
        "target_weight_kg": profile.target_weight_kg,
        "bmi": profile.bmi,
        "bmi_category": profile.bmi_category,
        "bmr": profile.bmr,
        "tdee": profile.tdee,

        # ── GOALS AND LIFESTYLE ────────────────────────────────
        "goal": profile.goal or None,
        "activity_level": profile.activity_level or None,
        "diet": profile.diet or None,
        "cooking_skills": profile.cooking_skills or None,
        "eating_realities": profile.eating_realities or None,
        "occupational_status": profile.occupational_status or None,

        # ── RESTRICTIONS (parsed into clean lists) ─────────────
        "medical_restrictions": _parse_list_field(
            profile.medical_restrictions
        ),
        "allergies": _parse_list_field(profile.allergies),
        "dislikes": _parse_list_field(profile.dislikes),
        "religion": profile.religion or None,

        # ── DERIVED FLAGS ──────────────────────────────────────
        # Boolean flags Jema uses directly for filtering and
        # prompt injection — avoids string matching everywhere
        "is_halal": _is_halal(profile.religion),
        "is_vegetarian": _is_vegetarian(profile.diet),
        "is_vegan": _is_exact_diet(profile.diet, "vegan"),
        "is_pescatarian": _is_exact_diet(profile.diet, "pescatarian"),
        "is_keto": _is_exact_diet(profile.diet, "keto"),
        "is_low_carb": _is_low_carb(profile.diet),
        "has_diabetes": _has_condition(
            profile.medical_restrictions, "diabetes"
        ),
        "has_hypertension": _has_condition(
            profile.medical_restrictions, "hypertension"
        ),
        "is_gluten_free": _has_allergy(profile.allergies, "gluten"),
        "is_dairy_free": _has_allergy(profile.allergies, "dairy"),
        "is_nut_free": _has_allergy(profile.allergies, "nut"),
        "is_shellfish_free": _has_allergy(
            profile.allergies, "shellfish"
        ),
    }

    # Build dietary_restrictions list from individual flags
    dietary_restrictions = []
    if context.get("is_vegetarian"):
        dietary_restrictions.append("vegetarian")
    if context.get("is_vegan"):
        dietary_restrictions.append("vegan")
    if context.get("is_pescatarian"):
        dietary_restrictions.append("pescatarian")
    if context.get("is_keto"):
        dietary_restrictions.append("keto")
    if context.get("is_low_carb"):
        dietary_restrictions.append("low carb")
    if context.get("is_gluten_free"):
        dietary_restrictions.append("gluten free")
    if context.get("is_dairy_free"):
        dietary_restrictions.append("dairy free")
    if context.get("is_nut_free"):
        dietary_restrictions.append("nut free")
    if context.get("is_shellfish_free"):
        dietary_restrictions.append("shellfish free")
    if context.get("is_halal"):
        dietary_restrictions.append("halal")

    # Build health_conditions list from individual flags
    health_conditions = []
    if context.get("has_diabetes"):
        health_conditions.append("diabetes")
    if context.get("has_hypertension"):
        health_conditions.append("hypertension")

    # Build preferred_cuisines from location and profile
    preferred_cuisines = ["east_african"]
    location = context.get("location", "")
    if location:
        location_lower = str(location).lower()
        if any(c in location_lower for c in ["kenya", "nairobi", "mombasa"]):
            preferred_cuisines = ["kenyan", "east_african"]
        elif any(c in location_lower for c in ["tanzania", "dar"]):
            preferred_cuisines = ["tanzanian", "east_african"]
        elif any(c in location_lower for c in ["uganda", "kampala"]):
            preferred_cuisines = ["ugandan", "east_african"]
        elif any(c in location_lower for c in ["nigeria", "lagos", "abuja"]):
            preferred_cuisines = ["nigerian", "west_african"]
        elif any(c in location_lower for c in ["ghana", "accra"]):
            preferred_cuisines = ["ghanaian", "west_african"]

    # Add computed keys to context before returning
    context["dietary_restrictions"] = dietary_restrictions
    context["health_conditions"] = health_conditions
    context["preferred_cuisines"] = preferred_cuisines

    return context


# ── PRIVATE HELPERS ────────────────────────────────────────────────────


def _default_profile_context() -> dict:
    """
    Safe defaults when user has no profile or profile
    retrieval fails. All flags False, all lists empty.
    Jema behaves as normal with no personalisation.
    """
    return {
        "name": "User",
        "age": None,
        "gender": None,
        "location": None,
        "current_weight_kg": None,
        "current_height_cm": None,
        "target_weight_kg": None,
        "bmi": None,
        "bmi_category": None,
        "bmr": None,
        "tdee": None,
        "goal": None,
        "activity_level": None,
        "diet": None,
        "cooking_skills": None,
        "eating_realities": None,
        "occupational_status": None,
        "medical_restrictions": [],
        "allergies": [],
        "dislikes": [],
        "religion": None,
        "is_halal": False,
        "is_vegetarian": False,
        "is_vegan": False,
        "is_pescatarian": False,
        "is_keto": False,
        "is_low_carb": False,
        "has_diabetes": False,
        "has_hypertension": False,
        "is_gluten_free": False,
        "is_dairy_free": False,
        "is_nut_free": False,
        "is_shellfish_free": False,
        "dietary_restrictions": [],
        "health_conditions": [],
        "preferred_cuisines": ["east_african"],
    }


def _parse_list_field(value: str) -> list:
    """
    Converts comma-separated Profile string field to
    a clean lowercase list.
    "Diabetes, Hypertension" → ["diabetes", "hypertension"]
    "" or None              → []
    """
    if not value or not value.strip():
        return []
    return [
        item.strip().lower()
        for item in value.split(",")
        if item.strip()
    ]


def _is_halal(religion: str) -> bool:
    if not religion:
        return False
    return religion.strip().lower() in ["muslim", "islam"]


def _is_vegetarian(diet: str) -> bool:
    if not diet:
        return False
    return diet.strip().lower() in [
        "vegetarian", "vegan", "flexitarian", "pescatarian"
    ]


def _is_exact_diet(diet: str, target: str) -> bool:
    if not diet:
        return False
    return diet.strip().lower() == target.lower()


def _is_low_carb(diet: str) -> bool:
    if not diet:
        return False
    return diet.strip().lower() in ["low carb", "keto"]


def _has_condition(medical_restrictions: str, condition: str) -> bool:
    if not medical_restrictions:
        return False
    return condition.lower() in medical_restrictions.lower()


def _has_allergy(allergies: str, allergen: str) -> bool:
    if not allergies:
        return False
    return allergen.lower() in allergies.lower()
