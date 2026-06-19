"""Per-destination restaurants, attractions, and hidden gems for Places MCP."""

from data.destinations import normalize_destination

PLACES_BY_DESTINATION = {
    "Goa": {
        "restaurants": [
            {"name": "Vinayak Family Restaurant", "description": "Authentic Goan fish thali and xacuti."},
            {"name": "Brittos", "description": "Iconic beachside shack at Baga with seafood."},
            {"name": "Gunpowder", "description": "South Indian coastal cuisine in Assagao."},
        ],
        "attractions": [
            {"name": "Basilica of Bom Jesus", "description": "UNESCO-listed Baroque church in Old Goa."},
            {"name": "Dudhsagar Falls", "description": "Majestic four-tiered waterfall in the Western Ghats."},
            {"name": "Fort Aguada", "description": "17th-century Portuguese fort with panoramic views."},
        ],
        "hidden_gems": [
            {"name": "Chorao Island", "description": "Quiet island with mangroves and birdwatching."},
            {"name": "Cabo de Rama", "description": "Secluded fort with dramatic cliff views."},
            {"name": "Fontainhas", "description": "Colorful Latin Quarter lanes in Panjim."},
        ],
    },
    "Jaipur": {
        "restaurants": [
            {"name": "LMB Hotel", "description": "Famous Rajasthani thali and sweets."},
            {"name": "Peacock Rooftop Restaurant", "description": "Views of Hawa Mahal with local cuisine."},
            {"name": "Spice Court", "description": "Laal maas and traditional Rajasthani dishes."},
        ],
        "attractions": [
            {"name": "Amber Fort", "description": "Hilltop fort with mirror palace and elephant rides."},
            {"name": "Hawa Mahal", "description": "Iconic pink sandstone Palace of Winds."},
            {"name": "City Palace", "description": "Royal residence with museums and courtyards."},
        ],
        "hidden_gems": [
            {"name": "Panna Meena ka Kund", "description": "Stunning stepwell away from tourist crowds."},
            {"name": "Galtaji Temple", "description": "Monkey temple with natural springs."},
            {"name": "Anokhi Museum", "description": "Block printing heritage in a restored haveli."},
        ],
    },
    "Munnar": {
        "restaurants": [
            {"name": "Rapsy Restaurant", "description": "Kerala parotta and appam with stew."},
            {"name": "Saravana Bhavan", "description": "South Indian vegetarian meals."},
            {"name": "Guru's Restaurant", "description": "Local Kerala fish curry and rice."},
        ],
        "attractions": [
            {"name": "Eravikulam National Park", "description": "Home to Nilgiri tahr and rolling grasslands."},
            {"name": "Mattupetty Dam", "description": "Scenic reservoir with boating."},
            {"name": "Tea Museum", "description": "History of Munnar's tea plantations."},
        ],
        "hidden_gems": [
            {"name": "Kolukkumalai", "description": "World's highest tea estate with sunrise views."},
            {"name": "Lockhart Gap", "description": "Misty viewpoint over valleys and tea gardens."},
            {"name": "Chinnar Wildlife Sanctuary", "description": "Dry deciduous forest with trekking trails."},
        ],
    },
    "Varkala": {
        "restaurants": [
            {"name": "Trattorias Restaurant", "description": "Cliff-top Italian and Kerala fusion."},
            {"name": "Little Tibet Cafe", "description": "Relaxed cliff cafe with sea views."},
            {"name": "Darjeeling Cafe", "description": "Breakfast and smoothies on the cliff."},
        ],
        "attractions": [
            {"name": "Varkala Cliff Beach", "description": "Dramatic red laterite cliffs above the Arabian Sea."},
            {"name": "Janardanaswamy Temple", "description": "2000-year-old Vishnu temple near the beach."},
            {"name": "Papanasam Beach", "description": "Sacred beach believed to wash away sins."},
        ],
        "hidden_gems": [
            {"name": "Kappil Beach", "description": "Quiet estuary beach where backwaters meet the sea."},
            {"name": "Anjengo Fort", "description": "Historic British-era coastal fort."},
            {"name": "Edava Beach", "description": "Secluded stretch south of the main cliff."},
        ],
    },
    "Coorg": {
        "restaurants": [
            {"name": "Coorg Cuisine", "description": "Pandi curry and bamboo shoot dishes."},
            {"name": "Taste of Coorg", "description": "Traditional Kodava home-style meals."},
            {"name": "East End Hotel", "description": "Local favorites in Madikeri town."},
        ],
        "attractions": [
            {"name": "Abbey Falls", "description": "Coffee-estate waterfall near Madikeri."},
            {"name": "Raja's Seat", "description": "Sunset viewpoint over misty valleys."},
            {"name": "Dubare Elephant Camp", "description": "Interact with elephants by the Kaveri river."},
        ],
        "hidden_gems": [
            {"name": "Mandalpatti", "description": "Off-road jeep ride to a stunning hilltop."},
            {"name": "Nalknad Palace", "description": "Remote heritage palace in the hills."},
            {"name": "Chelavara Falls", "description": "Less crowded waterfall amid coffee estates."},
        ],
    },
    "Shillong": {
        "restaurants": [
            {"name": "City Hut Family Dhaba", "description": "Northeast Indian and Chinese comfort food."},
            {"name": "Jadoh", "description": "Authentic Khasi jadoh rice and pork dishes."},
            {"name": "Cafe Shillong", "description": "Live music and local flavors."},
        ],
        "attractions": [
            {"name": "Umiam Lake", "description": "Scenic reservoir with boating and views."},
            {"name": "Elephant Falls", "description": "Three-tiered waterfall near the city."},
            {"name": "Don Bosco Museum", "description": "Cultural heritage of Northeast India."},
        ],
        "hidden_gems": [
            {"name": "Laitlum Canyon", "description": "Breathtaking gorge called the 'End of Hills'."},
            {"name": "Mawphlang Sacred Grove", "description": "Ancient preserved Khasi forest."},
            {"name": "David Scott Trail", "description": "Historic trekking route through villages."},
        ],
    },
    "Ooty": {
        "restaurants": [
            {"name": "Shinkows", "description": "Chinese and Indo-Chinese since 1956."},
            {"name": "Nahar's Sidewalk Cafe", "description": "Bakery and snacks on commercial street."},
            {"name": "Place To Bee", "description": "Organic Nilgiri honey and local produce."},
        ],
        "attractions": [
            {"name": "Nilgiri Mountain Railway", "description": "UNESCO toy train through tea country."},
            {"name": "Botanical Gardens", "description": "Terraced gardens with a fossil tree."},
            {"name": "Ooty Lake", "description": "Boating and horse rides on the lake."},
        ],
        "hidden_gems": [
            {"name": "Emerald Lake", "description": "Quiet lake surrounded by tea estates."},
            {"name": "Avalanche Lake", "description": "Secluded trek-friendly lake in the forest."},
            {"name": "Pykara Falls", "description": "Picturesque falls in the Pykara village area."},
        ],
    },
    "Manali": {
        "restaurants": [
            {"name": "Johnson's Cafe", "description": "Trout and apple pie by the river."},
            {"name": "Cafe 1947", "description": "Riverside dining in Old Manali."},
            {"name": "Madras Restaurant", "description": "South Indian meals for comfort food."},
        ],
        "attractions": [
            {"name": "Solang Valley", "description": "Paragliding, skiing, and adventure sports."},
            {"name": "Hadimba Temple", "description": "Wooden temple in a cedar forest."},
            {"name": "Rohtang Pass", "description": "High-altitude pass with snow views."},
        ],
        "hidden_gems": [
            {"name": "Jogini Falls", "description": "Short trek to a sacred waterfall."},
            {"name": "Vashisht Hot Springs", "description": "Natural sulphur baths and temple."},
            {"name": "Hampta Pass trek base", "description": "Gateway to dramatic alpine landscapes."},
        ],
    },
}


def _fallback_places(destination: str) -> dict:
    return {
        "restaurants": [
            {"name": f"{destination} Local Kitchen", "description": f"Regional cuisine in {destination}."},
            {"name": f"{destination} Spice House", "description": "Popular family restaurant."},
            {"name": f"{destination} Street Food Hub", "description": "Local street food specialties."},
        ],
        "attractions": [
            {"name": f"{destination} City Center", "description": "Main cultural and shopping area."},
            {"name": f"{destination} Heritage Walk", "description": "Guided walk through historic quarters."},
            {"name": f"{destination} Viewpoint", "description": "Scenic overlook of the region."},
        ],
        "hidden_gems": [
            {"name": f"{destination} Old Quarter", "description": "Quiet lanes with local life."},
            {"name": f"{destination} Riverside Spot", "description": "Peaceful escape from crowds."},
            {"name": f"{destination} Local Market", "description": "Authentic market experience."},
        ],
    }


def get_restaurants(destination: str) -> list[dict]:
    city = normalize_destination(destination)
    places = PLACES_BY_DESTINATION.get(city, _fallback_places(city))
    return places["restaurants"]


def get_attractions(destination: str) -> list[dict]:
    city = normalize_destination(destination)
    places = PLACES_BY_DESTINATION.get(city, _fallback_places(city))
    return places["attractions"]


def get_hidden_gems(destination: str) -> list[dict]:
    city = normalize_destination(destination)
    places = PLACES_BY_DESTINATION.get(city, _fallback_places(city))
    return places["hidden_gems"]
