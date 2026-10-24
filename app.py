import json
from pathlib import Path

from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "destinations.json"


def load_destinations():
    """Load destination information from the JSON file."""
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def home():
    destinations = load_destinations()

    return render_template(
        "index.html",
        destinations=destinations[:3]
    )


@app.route("/explore")
def explore():
    destinations = load_destinations()

    category = request.args.get("type", "All")
    query = request.args.get("q", "").strip().lower()

    filtered = destinations

    if category != "All":
        filtered = [
            place for place in filtered
            if place["type"] == category
        ]

    if query:
        filtered = [
            place for place in filtered
            if query in place["name"].lower()
            or query in place["district"].lower()
            or query in place["description"].lower()
        ]

    return render_template(
        "explore.html",
        destinations=filtered,
        selected_type=category,
        search_query=query
    )


@app.route("/planner", methods=["GET", "POST"])
def planner():
    if request.method == "GET":
        return render_template("planner.html")

    starting_city = request.form.get(
        "starting_city", "Bengaluru"
    ).strip()

    interest = request.form.get("interest", "Any")

    try:
        budget = float(request.form.get("budget", 5000))
        duration = int(request.form.get("duration", 2))
        travellers = int(request.form.get("travellers", 1))
    except (ValueError, TypeError):
        return render_template(
            "planner.html",
            error="Please enter valid trip details."
        ), 400

    if (
        not starting_city
        or budget < 500
        or duration not in [1, 2, 3, 4, 5, 7]
        or not 1 <= travellers <= 20
    ):
        return render_template(
            "planner.html",
            error="Please check your city, budget, duration and travellers."
        ), 400

    destinations = load_destinations()

    # The cost field represents an illustrative estimate
    # per person for a two-day trip.
    matches = []

    for place in destinations:
        if interest != "Any" and place["type"] != interest:
            continue

        estimated_cost = (
            place["cost"] * duration / 2 * travellers
        )

        if estimated_cost <= budget:
            matches.append({
                **place,
                "estimated_cost": round(estimated_cost)
            })

    if matches:
        # Recommend the least expensive matching destination.
        selected = min(
            matches,
            key=lambda place: place["estimated_cost"]
        )

        itinerary = []

        for day in range(1, duration + 1):
            if duration == 1:
                activity = (
                    f"Travel from {starting_city} to "
                    f"{selected['name']}, explore local attractions, "
                    "and plan your return."
                )
            elif day == 1:
                activity = (
                    f"Travel from {starting_city} to "
                    f"{selected['name']} and explore nearby attractions."
                )
            elif day == duration:
                activity = (
                    "Visit remaining attractions and plan "
                    "your return journey."
                )
            else:
                activity = (
                    "Explore local attractions, enjoy regional food, "
                    "and discover nearby places."
                )

            itinerary.append({
                "day": day,
                "activity": activity
            })

        result = {
            "found": True,
            "destination": selected,
            "starting_city": starting_city,
            "budget": budget,
            "duration": duration,
            "travellers": travellers,
            "estimated_cost": selected["estimated_cost"],
            "itinerary": itinerary
        }

    else:
        result = {
            "found": False,
            "budget": budget,
            "interest": interest,
            "duration": duration,
            "travellers": travellers
        }

    return render_template("results.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)