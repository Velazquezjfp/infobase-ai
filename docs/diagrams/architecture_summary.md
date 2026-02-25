Zusammenfassung der System-Architektur

Benutzeroberfläche (Frontend): Die React-App schickt jede Nutzer-Aktion (mit Fall-ID, Ordner-ID und Dokument-Inhalt) über eine dauerhafte Verbindung (WebSocket).

Verteilung (Routing): 9 Router nehmen die Anfragen an und leiten sie an spezialisierte Dienste weiter.

Zentraler KI-Dienst: Es gibt einen Haupt-Dienst (GeminiService). Alle KI-Aufgaben wie Chatten, Suchen oder Übersetzen laufen über diesen Dienst.

Aufgaben-Vorbereitung: 4 zusätzliche Dienste bereiten spezielle Texte (Prompts) vor (z. B. für Validierungen oder Übersetzungen). Am Ende rufen aber alle Gemini auf.

Keine "Agenten": Die KI plant nicht selbst und nutzt keine externen Werkzeuge. Der Ablauf ist immer gleich: Text zusammenstellen → Gemini fragen → Antwort senden.

Kontext-Manager: Informationen werden erst beim Aufruf aus JSON-Dateien geladen und dynamisch in den Prompt eingebaut (bestehend aus 8 Abschnitten).

Chat-Verlauf: Der Verlauf wird pro Fall nur im Arbeitsspeicher behalten und nicht dauerhaft gespeichert.

Speicherung: Alle Daten liegen in einfachen JSON-Dateien auf der Festplatte. Es gibt keine Datenbank und keine komplexen Vektor-Speicher.

Das "schlaue" Prinzip: Das System ist deshalb intelligent, weil es Informationen hierarchisch ordnet (Fall > Ordner > Dokument). So weiß die KI immer genau, wo sich der Nutzer gerade befindet.