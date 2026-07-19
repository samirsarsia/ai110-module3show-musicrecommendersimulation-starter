import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_WEIGHT = 0.5
ARTIST_REPEAT_PENALTY = 1.0


@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _score_song_obj(user: UserProfile, song: Song) -> Tuple[float, List[str]]:
    """Scores a Song dataclass against a UserProfile, returning (score, reasons)."""
    score = 0.0
    reasons = []

    if song.genre == user.favorite_genre:
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT:.1f})")

    if song.mood == user.favorite_mood:
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT:.1f})")

    energy_closeness = 1 - abs(song.energy - user.target_energy)
    energy_points = ENERGY_WEIGHT * energy_closeness
    score += energy_points
    reasons.append(f"energy {song.energy:.2f} close to target {user.target_energy:.2f} (+{energy_points:.2f})")

    if user.likes_acoustic:
        acoustic_points = ACOUSTIC_WEIGHT * song.acousticness
        score += acoustic_points
        reasons.append(f"acousticness {song.acousticness:.2f} (+{acoustic_points:.2f})")

    return score, reasons


def _select_diverse(scored_items: List[Tuple[float, object]], k: int, artist_of) -> List:
    """Greedily picks the top k items by score, penalizing repeats from an already-picked artist."""
    remaining = list(scored_items)
    selected = []
    artist_counts: Dict[str, int] = {}

    for _ in range(min(k, len(remaining))):
        best_index = None
        best_adjusted = None
        for i, (score, item) in enumerate(remaining):
            artist = artist_of(item)
            adjusted = score - ARTIST_REPEAT_PENALTY * artist_counts.get(artist, 0)
            if best_adjusted is None or adjusted > best_adjusted:
                best_adjusted = adjusted
                best_index = i

        score, item = remaining.pop(best_index)
        artist_counts[artist_of(item)] = artist_counts.get(artist_of(item), 0) + 1
        selected.append(item)

    return selected


class Recommender:
    """OOP implementation of the recommendation logic."""
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Scores every song, applies a diversity penalty for repeat artists, and returns the top k Song objects."""
        scored = [(_score_song_obj(user, song)[0], song) for song in self.songs]
        selected = _select_diverse(scored, k, artist_of=lambda song: song.artist)
        return selected

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable, semicolon-joined list of reasons a song scored as it did."""
        _, reasons = _score_song_obj(user, song)
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file into a list of dicts with numeric fields converted."""
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a single song dict against user_prefs, returning (score, reasons)."""
    score = 0.0
    reasons = []

    if "genre" in user_prefs and song["genre"] == user_prefs["genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT:.1f})")

    if "mood" in user_prefs and song["mood"] == user_prefs["mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT:.1f})")

    if "energy" in user_prefs:
        energy_closeness = 1 - abs(song["energy"] - user_prefs["energy"])
        energy_points = ENERGY_WEIGHT * energy_closeness
        score += energy_points
        reasons.append(f"energy {song['energy']:.2f} close to target {user_prefs['energy']:.2f} (+{energy_points:.2f})")

    if user_prefs.get("likes_acoustic"):
        acoustic_points = ACOUSTIC_WEIGHT * song["acousticness"]
        score += acoustic_points
        reasons.append(f"acousticness {song['acousticness']:.2f} (+{acoustic_points:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song, applies a diversity penalty for repeat artists, and returns the top k as (song, score, explanation)."""
    explanations = {}
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanations[song["id"]] = "; ".join(reasons)
        scored.append((score, song))

    selected = _select_diverse(scored, k, artist_of=lambda song: song["artist"])
    original_scores = {song["id"]: score for score, song in scored}
    return [(song, original_scores[song["id"]], explanations[song["id"]]) for song in selected]
