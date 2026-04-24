from typing import Optional
from app.models import Meal, MealRecipe, RecipeIngredient, IngredientNutrition
from app.schemas.schemas import MealNutritionOut


async def compute_meal_nutrition(meal: Meal) -> Optional[MealNutritionOut]:
    """
    Compute per-serving nutrition for a meal by summing ingredient contributions.
    If any ingredient is missing nutrition data, nutrition_complete is set to False.
    """
    if not meal.recipe or not meal.recipe.ingredients:
        return None

    servings = meal.recipe.servings or 1
    totals = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0}
    nutrition_complete = True

    for ri in meal.recipe.ingredients:
        ing = ri.ingredient
        if not ing or not ing.nutrition:
            nutrition_complete = False
            continue

        n = ing.nutrition
        qty = ri.quantity or 0

        # Convert quantity to grams for the calc
        qty_g = _to_grams(qty, ri.unit, ing)

        factor = qty_g / 100.0
        totals["calories"] += (n.calories_per_100g or 0) * factor
        totals["protein_g"] += (n.protein_g or 0) * factor
        totals["carbs_g"] += (n.carbs_g or 0) * factor
        totals["fat_g"] += (n.fat_g or 0) * factor
        totals["fiber_g"] += (n.fiber_g or 0) * factor

    # Scale to per-serving
    return MealNutritionOut(
        calories=round(totals["calories"] / servings, 1),
        protein_g=round(totals["protein_g"] / servings, 1),
        carbs_g=round(totals["carbs_g"] / servings, 1),
        fat_g=round(totals["fat_g"] / servings, 1),
        fiber_g=round(totals["fiber_g"] / servings, 1),
        nutrition_complete=nutrition_complete,
    )


def _to_grams(quantity: float, unit: Optional[str], ingredient) -> float:
    """
    Convert a quantity in the given unit to grams.
    Falls back to 1:1 if unit is g or unknown.
    """
    if not unit or unit.lower() in ("g", "grams"):
        return quantity

    if unit.lower() in ("kg", "kilogram", "kilograms"):
        return quantity * 1000

    if unit.lower() in ("ml", "milliliter", "milliliters"):
        return quantity  # rough approximation: 1ml ≈ 1g for most food liquids

    if unit.lower() in ("l", "liter", "liters"):
        return quantity * 1000

    # Unit-based conversion using ingredient's grams_per_unit
    if ingredient and ingredient.grams_per_unit and unit.lower() in ("piece", "pieces", "pcs", "whole"):
        return quantity * ingredient.grams_per_unit

    # Common kitchen units (rough averages)
    unit_map = {
        "cup": 240,
        "cups": 240,
        "tbsp": 15,
        "tablespoon": 15,
        "tablespoons": 15,
        "tsp": 5,
        "teaspoon": 5,
        "teaspoons": 5,
        "oz": 28.35,
        "ounce": 28.35,
        "ounces": 28.35,
        "lb": 453.6,
        "pound": 453.6,
        "pounds": 453.6,
    }
    multiplier = unit_map.get(unit.lower())
    if multiplier:
        return quantity * multiplier

    # Default fallback — treat as grams
    return quantity
