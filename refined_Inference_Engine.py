import os
import sqlite3
import pandas as pd


class RefinedInferenceEngine:
    def __init__(self, db_path):
        """
        Inicializa el motor de inferencia refinado, cargando la base de datos.
        """
        self.songs_df = None
        self.conn = None

        if not os.path.exists(db_path):
            print(f"Archivo de base de datos no encontrado: {db_path}")
            return

        try:
            self.conn = sqlite3.connect(db_path)
            print("Conexión a la base de datos establecida correctamente.")
            self.songs_df = pd.read_sql_query("SELECT * FROM songs", self.conn)

            # Convertir columnas relevantes a valores numéricos
            numeric_columns = [
                "duration", "popularity", "release_year", "bpm", "energy", 
                "valence", "acousticness", "danceability", "instrumentalness",
                "live_performance_factor", "recording_quality", "popularity_change"
            ]
            for col in numeric_columns:
                if col in self.songs_df.columns:
                    self.songs_df[col] = pd.to_numeric(self.songs_df[col], errors='coerce')
        except Exception as e:
            print(f"Error al conectar con la base de datos: {e}")
            self.songs_df = None

    def apply_preferences(self, preferences, weights=None, tolerance=None):
        """
        Aplica las preferencias del usuario y calcula puntuaciones para las canciones.
        """
        if self.songs_df is None:
            print("No se pueden aplicar preferencias: base de datos no cargada.")
            return pd.DataFrame()

        # Configurar pesos y tolerancia
        self.weights = weights or {
            "energy": 2.0, "valence": 1.5, "bpm": 1.5, "danceability": 1.2, "popularity": 1.0,
            "tempo_range": 1.5, "usage_context": 2.0, "explicitness": 1.0, "live_performance_factor": 1.2
        }
        self.tolerance = tolerance or {
            "energy": 1, "valence": 1, "bpm": 10, "danceability": 0.1, "popularity": 10,
            "tempo_range": 0.5, "usage_context": 0, "explicitness": 0, "live_performance_factor": 1
        }

        # Calcular puntuaciones
        self.songs_df["score"] = self.songs_df.apply(
            lambda song: self.calculate_score(song, preferences), axis=1
        )

        # Ordenar por puntuación
        return self.songs_df.sort_values(by="score", ascending=False)

    def calculate_score(self, song, preferences):
        """
        Calcula la puntuación para una canción en función de las preferencias.
        """
        score = 0.0

        for attribute, user_value in preferences.items():
            # Atributos numéricos con tolerancia
            if attribute in self.tolerance and isinstance(user_value, (int, float)):
                try:
                    song_value = float(song[attribute])
                    tolerance = self.tolerance.get(attribute, 0)
                    if user_value - tolerance <= song_value <= user_value + tolerance:
                        score += self.weights.get(attribute, 1.0) * (1 - abs(user_value - song_value) / (tolerance + 1))
                except (ValueError, TypeError):
                    print(f"Advertencia: No se pudo procesar {attribute}. Valor inválido.")

            # Atributos categóricos
            elif attribute in ["genre", "tempo_range", "usage_context", "language", "mood"]:
                if str(song[attribute]).strip().lower() == str(user_value).strip().lower():
                    score += self.weights.get(attribute, 1.0)

            # Atributos booleanos
            elif attribute in ["explicitness", "cover_or_original"]:
                if user_value == song[attribute]:
                    score += self.weights.get(attribute, 1.0)

            # Atributos basados en listas (ejemplo: genre_tags, streaming_platforms)
            elif attribute in ["genre_tags", "streaming_platforms"]:
                if any(tag.lower() in str(song[attribute]).lower() for tag in user_value):
                    score += self.weights.get(attribute, 1.0)

        return score


    def close(self):
        """
        Cierra la conexión a la base de datos si existe.
        """
        if self.conn:
            self.conn.close()
            print("Conexión cerrada correctamente.")
