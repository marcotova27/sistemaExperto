import tkinter as tk
from tkinter import ttk, messagebox
from refined_Inference_Engine import RefinedInferenceEngine


class PlaylistExpertSystem:
    def __init__(self, db_path):
        self.inference_engine = RefinedInferenceEngine(db_path)
        self.preferences = {}

    def add_preference(self, key, value):
        """
        Agrega una preferencia al motor de inferencia.
        """
        self.preferences[key] = value

    def generate_playlist(self):
        """
        Genera una playlist basada en las preferencias acumuladas.
        """
        if not self.inference_engine:
            print("Motor de inferencia no inicializado.")
            return []

        return self.inference_engine.apply_preferences(self.preferences)

    def close(self):
        """
        Cierra el motor de inferencia.
        """
        if self.inference_engine:
            self.inference_engine.close()


class PlaylistApp:
    def __init__(self, root, db_path):
        self.root = root
        self.system = PlaylistExpertSystem(db_path)
        self.questions = [
            {
                "text": "¿Para qué ocasión o actividad estás buscando esta playlist?",
                "key": "usage_context",
                "options": {
                    "Estudio": {"energy": 3, "mood": "calmado", "danceability": 0.2, "tempo_range": "slow"},
                    "Trabajo": {"energy": 5, "mood": "neutral", "danceability": 0.4, "tempo_range": "moderate"},
                    "Entrenamiento": {"energy": 8, "mood": "motivador", "danceability": 0.8, "tempo_range": "fast"},
                    "Fiesta": {"energy": 9, "mood": "alegre", "danceability": 1.0, "tempo_range": "fast"}
                }
            },
            {
                "text": "¿Te gustaría que la música sea relajante, energizante o algo intermedio?",
                "key": "energy",
                "options": {"Relajante": 3, "Energizante": 8, "Intermedia": 5}
            },
            {
                "text": "¿Prefieres canciones alegres, nostálgicas o de tono neutro?",
                "key": "mood",
                "options": {"Alegres": "alegre", "Nostálgicas": "nostálgico", "Neutro": "neutral"}
            },
            {
                "text": "¿Quieres que las canciones sean enérgicas y rápidas, o más lentas y calmadas?",
                "key": "tempo_range",
                "options": {"Rápidas": "fast", "Lentas": "slow", "Intermedias": "moderate"}
            },
            {
                "text": "¿Prefieres canciones populares o descubrimientos poco conocidos?",
                "key": "popularity",
                "options": {"Populares": 80, "Descubrimientos": 40}
            },
            {
                "text": "¿Te gustaría música en vivo o prefieres grabaciones de estudio?",
                "key": "live_performance_factor",
                "options": {"En vivo": 7, "Estudio": 3}
            },
            {
                "text": "¿Te importa si las canciones tienen lenguaje explícito?",
                "key": "explicitness",
                "options": {"Sí": 1, "No": 0}
            },
            {
                "text": "¿Qué géneros musicales prefieres o quieres incluir en esta playlist?",
                "key": "genre",
                "options": {"Pop": "pop", "Rock": "rock", "Jazz": "jazz", "Clásica": "clasica"}
            },
            {
                "text": "¿Prefieres música en un idioma específico o explorar distintos idiomas?",
                "key": "language",
                "options": {"Español": "es", "Inglés": "en", "Multilingüe": "multi"}
            },
            {
                "text": "¿Te gustaría canciones clásicas o lanzamientos recientes?",
                "key": "release_year",
                "options": {"Clásicas": 1990, "Recientes": 2020}
            },
            {
                "text": "¿Prefieres canciones originales o versiones/covers de otras canciones?",
                "key": "cover_or_original",
                "options": {"Originales": "original", "Covers": "cover"}
            },
        ]
        self.current_question_index = 0
        self.setup_styles()
        self.create_welcome_screen()

    def setup_styles(self):
        """
        Configura estilos visuales.
        """
        self.root.configure(bg="#85005b")  # Fondo principal
        style = ttk.Style()

        # Botones
        style.configure("TButton",
                        font=("Helvetica", 14),
                        padding=10,
                        background="#865a19",
                        foreground="#0e002f")
        style.map("TButton",
                  background=[("active", "#c4b282"), ("disabled", "#cccccc")])

        # Etiquetas
        style.configure("TLabel",
                        font=("Helvetica", 16),
                        foreground="#0e002f",
                        padding=10)

    def create_welcome_screen(self):
        """
        Crea la pantalla de bienvenida.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root,
                 text="Bienvenido al Sistema Experto de Playlist Ideal",
                 font=("Helvetica", 18),
                 fg="#0e002f",
                 bg="#85005b").pack(pady=20)

        ttk.Button(self.root, text="Generar Playlist", command=self.start_questions).pack(pady=10)
        ttk.Button(self.root, text="Salir", command=self.close).pack(pady=10)

    def start_questions(self):
        """
        Inicia las preguntas.
        """
        self.current_question_index = 0
        self.show_question()

    def show_question(self):
        """
        Muestra cada pregunta.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

        question = self.questions[self.current_question_index]
        tk.Label(self.root, text=question["text"], font=("Helvetica", 14), fg="#0e002f", bg="#85005b").pack(pady=20)

        for option_text, option_value in question["options"].items():
            ttk.Button(self.root, text=option_text, command=lambda val=option_value: self.record_answer(question["key"], val)).pack(pady=5)

    def record_answer(self, key, value):
        self.system.add_preference(key, value)
        self.current_question_index += 1

        if self.current_question_index < len(self.questions):
            self.show_question()
        else:
            self.show_results()

    def show_results(self):
        """
        Muestra los resultados.
        """
        results = self.system.generate_playlist()
        for widget in self.root.winfo_children():
            widget.destroy()

        if results.empty:
            messagebox.showinfo("Resultados", "No se encontraron canciones que coincidan.")
            self.create_welcome_screen()
            return

        tk.Label(self.root, text="Playlist Recomendada", font=("Helvetica", 16), fg="#0e002f", bg="#85005b").pack(pady=10)

        tree = ttk.Treeview(self.root, columns=("Título", "Artista", "Score"), show="headings")
        tree.heading("Título", text="Título")
        tree.heading("Artista", text="Artista")
        tree.heading("Score", text="Puntuación")
        tree.pack(pady=10)

        for _, row in results.head(10).iterrows():
            tree.insert("", "end", values=(row["title"], row["artist"], round(row["score"], 2)))

        ttk.Button(self.root, text="Volver al Inicio", command=self.create_welcome_screen).pack(pady=10)

    def close(self):
        self.system.close()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = PlaylistApp(root, "C:/Users/marco/Desktop/sistema-experto/playlist_expert_system.db")
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
