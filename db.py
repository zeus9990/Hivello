import motor.motor_asyncio
from datetime import datetime, timezone, timedelta
from config import DB_URL, CHECK_IN, GAME_COOLDOWN, Color
import random, csv, json

"""
(Database collections data structure schema)

User_data = {
                "_id": 0,
                "username": "",
                "wallet_address": "",
                "points": 0,
                "daily": {
                    "checked_in": False,
                    "last_checkin": None,
                    "total_checkins": 0,
                    "streak": 0
                    },
                "game": {
                    "game_points": 0,
                    "last_game_at": None,
                    "games_played": 0,
                    "games_won": 0
                    }
            }

Stats = {
            "date": None,
            "total_points": 0,
            "total_game_points": 0,
            "total_games_played": 0,
            "total_games_won": 0
        }

"""

database = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
Hivello = database["Hivello_S3"]
userdata = Hivello["userdata"]
stats = Hivello["stats"]


## Get rank
async def get_rank(userid: int) -> dict:
    user_doc = await userdata.find_one({"_id": userid})
    if not user_doc:
        return {
            "success": False,
            "message": f"Sorry <@{userid}> you're not registered yet. Please do a check in to get started.",
            "color": Color(False)
        }

    user_points = user_doc.get("points", 0) + user_doc.get("game", {}).get("game_points", 0)
    higher_count = await userdata.count_documents({
        "$expr": {
            "$gt": [{"$add": ["$points", "$game.game_points"]}, user_points]
        }
    })

    return {
        "success": True,
        "message": {
            "username": user_doc["username"],
            "points": user_points,
            "rank": higher_count + 1
        },
        "color": Color(True)
    }


## Get Leaderboard and rank
async def get_leaderboard() -> dict:
    pipeline_top_50 = [
        {
            "$project": {
                "_id": 1,
                "username": 1,
                "points": {
                    "$add": ["$points", "$game.game_points"]
                }
            }
        },
        {
            "$sort": {
                "points": -1
            }
        },
        {
            "$limit": 50
        }
    ]
    top_users = await userdata.aggregate(pipeline_top_50).to_list(length=50)

    pages = []
    for i in range(0, len(top_users), 10):
        chunk = top_users[i:i + 10]
        lines = [
            f"> • **{str(i + j + 1).zfill(2)}. {user['username']} - `{user['points']}` Points**"
            for j, user in enumerate(chunk)
        ]
        pages.append("\n".join(lines))
    if pages:
        return {
            "success": True,
            "message": pages,
            "color": Color(True)
        }
    else:
        return {
            "success": False,
            "message": None,
            "color": Color(False)
        }

## Add Points
async def add_points(userid: int, points: int) -> dict:
    updated = await userdata.update_one({'_id': userid}, {'$inc': {'points': points}})
    if updated.matched_count == 0:
        return {
            "success": False,
            "message": "User not found!",
            "color": Color(False)
        }
    return {
        "success": True,
        "message": f"{points} Hive points added to <@{userid}>!",
        "color": Color(True)
        }

## Remove Points
async def remove_points(userid: int, points: int) -> dict:
    updated = await userdata.update_one({'_id': userid}, {'$inc': {'points': -points}})
    if updated.matched_count == 0:
        return {
            "success": False,
            "message": "User not found!",
            "color": Color(False)
        }
    return {
        "success": True,
        "message": f"{points} Hive points removed from <@{userid}>!.",
        "color": Color(True)
    }

## Get user info
async def get_user(userid: int) -> dict:
    user_details = await userdata.find_one({'_id': userid})
    if user_details:
        return {
            "success": True,
            "message": user_details,
            "color": Color(True)
        }
    else:
        return {
            "success": False,
            "message": "User not Found.",
            "color": Color(False)
        }

# Daily Check in
async def daily_checkin(userid: int, username: str) -> dict:
    today = datetime.now(timezone.utc).date()
    today_str = datetime.now(timezone.utc).date().isoformat()
    user = await userdata.find_one({"_id": userid})
    earned = random.randint(CHECK_IN['min'], CHECK_IN['max'])

    if user:
        last_checkin_str = user.get("daily", {}).get("last_checkin")
        last_streak = user.get("daily", {}).get("streak", 0)

        if last_checkin_str:
            last_checkin = datetime.fromisoformat(last_checkin_str).date()
            if last_checkin == today:
                return {
                    "success": False,
                    "message": f"Hey <@{userid}>! you've already checked in for today, try again tomorrow.",
                    "color": Color(False)
                }

            elif (today - last_checkin) == timedelta(days=1):
                streak = last_streak + 1

            else:
                streak = 1
        else:
            streak = 1

        await userdata.update_one(
            {"_id": userid},
            {
                "$inc": {
                    "points": earned,
                    "daily.total_checkins": 1
                },
                "$set": {
                    "daily.checked_in": True,
                    "daily.last_checkin": today_str,
                    "daily.streak": streak
                }
            }
        )

    else:
        await userdata.insert_one({
            "_id": userid,
            "username": username,
            "points": earned,
            "wallet": None,
            "daily": {
                "checked_in": True,
                "last_checkin": today_str,
                "total_checkins": 1,
                "streak": 1
            },
            "game": {
                "game_points": 0,
                "last_game_at": None,
                "games_played": 0,
                "games_won": 0
            }
        })

    return {
        "success": True,
        "message": (
            f"Congratulations <@{userid}>! Check-in successful.\n"
            f"You received **{earned} Hive points** and your current streak is now **{streak}**."
        ),
        "color": Color(True)
    }

# Update_games
async def update_games(userid: int, bet: int = 0, points: int = 0, won: bool = None) -> dict:
    user = await userdata.find_one({"_id": userid})
    if not user:
        return {"success": False, "message": f"Sorry <@{userid}>! you are not registered please do a check in and try again.", "color": Color(False)}

    now = datetime.now(timezone.utc)
    now_str = now.isoformat()
    last_game_str = user.get("game", {}).get("last_game_at", None)

    if last_game_str:
        last_game_time = datetime.fromisoformat(last_game_str)
        elapsed = now - last_game_time
        cooldown = timedelta(minutes=GAME_COOLDOWN)

        if elapsed < cooldown:
            remaining = cooldown - elapsed
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return {
                "success": False,
                "message": (
                    f"Sorry <@{userid}>! you must wait {hours}h {minutes}m {seconds}s before playing again."
                ),
                "color": Color(False)
            }
        
    if points == 0:
        user_points = user.get("points", 0)
        game_points = user.get("game", {}).get("game_points", 0)
        total_points = user_points + game_points

        if bet > total_points:
            return {
                "success": False,
                "message": f"❌ <@{userid}> You don't have enough balance to play! You need **{bet}** Hive points but your balance is **{total_points}** Hive points only.",
                "color": Color(False)
            }

        return {
            "success": True,
            "message": {
                "last_game_at": last_game_time,
                "points": total_points,
                "can_play": True
            },
            "color": Color(True)
        }

    if won is True:
        update_fields = {
            "$inc": {
                "game.games_played": 1,
                "game.games_won": 1,
                "game.game_points": points
            },
            "$set": {
                "game.last_game_at": now_str
            }
        }
    elif won is False:
        update_fields = {
            "$inc": {
                "game.games_played": 1,
                "game.game_points": -points
            },
            "$set": {
                "game.last_game_at": now_str
            }
        }

    await userdata.update_one({"_id": userid}, update_fields)

    return {
        "success": True,
        "message": f"Added {points} points to the user.",
        "color": Color(True)
    }

# Checks for new date, updates stats, resets daily fields, and exports snapshot CSV.
async def date_check() -> dict:
    today = datetime.now(timezone.utc).date()
    today_str = today.isoformat()

    last_stats = await stats.find_one(sort=[("date", -1)])
    if not last_stats:
        await stats.insert_one({
            "date": today_str,
            "total_points": 0,
            "total_game_points": 0,
            "total_games_played": 0,
            "total_games_won": 0
        })
        return {
            "success": True,
            "message": "Initialized daily stats with zero values."
        }

    last_date = datetime.fromisoformat(last_stats["date"]).date()
    if last_date >= today:
        return {
            "success": False,
            "message": "No new day yet."
        }

    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_points": {"$sum": "$points"},
                "total_game_points": {"$sum": "$game.game_points"},
                "total_games_played": {"$sum": "$game.games_played"},
                "total_games_won": {"$sum": "$game.games_won"}
            }
        }
    ]

    result = await userdata.aggregate(pipeline).to_list(length=1)
    totals = result[0] if result else {
        "total_points": 0,
        "total_game_points": 0,
        "total_games_played": 0,
        "total_games_won": 0
    }
    totals.pop("_id", None)
    totals["date"] = today_str

    await stats.insert_one(totals)
    await userdata.update_many({}, {"$set": {"daily.checked_in": False}})

    users_cursor = userdata.find({})
    users = await users_cursor.to_list(None)
    users.sort(
        key=lambda u: u.get("points", 0) + u.get("game", {}).get("game_points", 0),
        reverse=True
    )

    # Prepare CSV
    csv_file = f"{today_str}.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "_id", "username", "total_points"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for user in users:
            row = {
                "_id": user.get("_id"),
                "username": user.get("username", ""),
                "total_points": (user.get("points", 0)+user.get("game", {}).get("game_points", 0))
            }
            writer.writerow(row)

    return {
        "success": True,
        "message": f"New day detected. Stats updated and snapshot saved as {csv_file}.",
        "file": csv_file,
        "color": Color(True)
    }

# Monthly reset and json export
async def monthly_reset() -> dict:
    today = datetime.now(timezone.utc)
    if today.day != 1:
        return {
            "success": False,
            "message": "Not the first day of the month — skipping reset."
        }

    users_cursor = userdata.find({})
    users = await users_cursor.to_list(None)

    if not users:
        return {
            "success": False,
            "message": "No users found to reset."
        }

    snapshot_file = f"userdata_snapshot_{today.date().isoformat()}.json"
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

    reset_fields = {
        "points": 0,
        "game": {
            "game_points": 0
        }
    }

    await userdata.update_many({}, {"$set": reset_fields})
    return {
        "success": True,
        "message": f"Monthly reset completed successfully. Backup saved to {snapshot_file}.",
        "file": snapshot_file
    }