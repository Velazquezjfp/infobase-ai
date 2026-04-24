# Prompt-Vergleich: Aktuell vs. Ontologie-angereichert

## Das Dokument (gleich für beide Prompts)

Dies ist ein eingescanntes Antragsformular, das in Text umgewandelt wurde:

```
Bundesamt für Migration und Flüchtlinge
Antrag auf Zulassung zum Integrationskurs

Aktenzeichen: ACTE-2024-001
Datum: 12.03.2024

Angaben zur Person:
Name: Ahmad Ali
Geboren am: 15.05.1990
Geburtsort: Kabul
Staatsangehörigkeit: Afghanistan
Aufenthaltsstatus: Flüchtling mit Aufenthaltserlaubnis

Begründung des Antrags:
Hiermit beantrage ich die Zulassung zum Integrationskurs gemäß §44 AufenthG.
Ich bin seit 2022 in Deutschland und möchte meine Deutschkenntnisse verbessern,
um mich beruflich zu integrieren. Ich habe bisher keinen Sprachkurs besucht.
```

---

## AKTUELLER Ansatz (was form_parser.py heute macht)

Die Formularfelder werden nur mit Label, Typ und einem gekürzten semantischen Hinweis gesendet:

```
# Aufgabe: Formularfeld-Werte extrahieren

Extrahiere die folgenden Formularfeld-Werte aus dem Dokumenttext.

## Formularfelder:

- referenceNumber (Reference Number)
  Typ: text
  Pflichtfeld: Ja
  Semantik: Text

- candidateName (Candidate Name)
  Typ: text
  Pflichtfeld: Ja
  Semantik: name

- placeOfBirth (Place of Birth)
  Typ: text
  Pflichtfeld: Ja
  Semantik: Text

- reasonForApplication (Reason for Application)
  Typ: textarea
  Pflichtfeld: Ja
  Semantik: description

## Dokumentinhalt:
...

## Anweisungen:
Gib NUR ein JSON-Objekt mit Feld-IDs als Schlüssel zurück.
```

### Probleme mit diesem Ansatz:
- `Semantik: Text` für referenceNumber — **nutzlos**, das LLM weiß nicht, was dieses Feld bedeutet
- `Semantik: Text` für placeOfBirth — **gleiches Problem**, nur Label-basierte Zuordnung möglich
- Das LLM muss **raten**, dass "Geburtsort" = "Place of Birth" aus seinen Trainingsdaten
- Das LLM muss **raten**, dass "Aktenzeichen" = "Reference Number"
- Kein Validierungskontext — das LLM kennt das erwartete Format nicht

---

## BESSERER Ansatz (Ontologie-Metadaten im Prompt eingebettet)

Das Formular trägt seinen Ontologie-Kontext mit sich. Jedes Feld enthält
die Beschreibung, mehrsprachige Labels und Einschränkungen aus Ontologie UND SHACL-Shape:

```
# Aufgabe: Formularfeld-Werte extrahieren

Extrahiere Werte aus dem untenstehenden Dokument in die beschriebenen
Formularfelder. Jedes Feld enthält seine semantische Definition — nutze
sie, um zu verstehen, was das Feld BEDEUTET, nicht nur wie es heißt.

## Formularfelder:

- referenceNumber
  Label: "Reference Number" (en), "Aktenzeichen" (de)
  Definition: "Das offizielle Aktenzeichen, das vom BAMF für diesen
               Antrag vergeben wurde (z.B. ACTE-2024-001)."
  Typ: text (xsd:string)
  Pflichtfeld: Ja
  Format: muss dem Muster ACTE-JJJJ-NNN entsprechen
  Ontologie: bamf:referenceNumber
  Domäne: bamf:IntegrationCourseApplication

- candidateName
  Label: "Candidate Name" (en), "Name des Antragstellers" (de)
  Definition: "Der vollständige rechtliche Name des Antragstellers,
               wie er auf offiziellen Dokumenten erscheint."
  Typ: text (xsd:string)
  Pflichtfeld: Ja
  Länge: 2-200 Zeichen
  Ontologie: bamf:candidateName (subPropertyOf schema:name)
  Domäne: bamf:Applicant

- placeOfBirth
  Label: "Place of Birth" (en), "Geburtsort" (de)
  Definition: "Die Stadt oder der Ort, an dem der Antragsteller
               geboren wurde."
  Typ: text (xsd:string)
  Pflichtfeld: Ja
  Länge: mindestens 2 Zeichen
  Ontologie: bamf:birthPlace (equivalentProperty schema:birthPlace)
  Domäne: bamf:Applicant

- reasonForApplication
  Label: "Reason for Application" (en), "Antragsgrund" (de)
  Definition: "Freitexterklärung, warum der Antragsteller die Teilnahme
               am Integrationskurs beantragt, einschließlich der
               Rechtsgrundlage (z.B. AufenthG §44, §44a)."
  Typ: textarea (xsd:string)
  Pflichtfeld: Ja
  Länge: mindestens 10 Zeichen
  Ontologie: bamf:reasonForApplication (subPropertyOf schema:description)
  Domäne: bamf:IntegrationCourseApplication

## Dokumentinhalt:

Bundesamt für Migration und Flüchtlinge
Antrag auf Zulassung zum Integrationskurs

Aktenzeichen: ACTE-2024-001
Datum: 12.03.2024

Angaben zur Person:
Name: Ahmad Ali
Geboren am: 15.05.1990
Geburtsort: Kabul
Staatsangehörigkeit: Afghanistan
Aufenthaltsstatus: Flüchtling mit Aufenthaltserlaubnis

Begründung des Antrags:
Hiermit beantrage ich die Zulassung zum Integrationskurs gemäß §44 AufenthG.
Ich bin seit 2022 in Deutschland und möchte meine Deutschkenntnisse verbessern,
um mich beruflich zu integrieren. Ich habe bisher keinen Sprachkurs besucht.

## Anweisungen:
- Nutze die Definition und Labels, um zu verstehen, was jedes Feld bedeutet
- Zuordnung nach BEDEUTUNG, nicht nur nach Stichwort
- Beachte die Format-/Längeneinschränkungen
- Gib NUR ein JSON-Objekt zurück: {"feld_id": "extrahierter_wert"}
```

### Warum das besser ist:

| Aspekt | Aktuell | Ontologie-angereichert |
|--------|---------|------------------------|
| "Aktenzeichen" → referenceNumber | LLM rät anhand des Labels | LLM liest das deutsche Label "Aktenzeichen" direkt in der Felddefinition |
| "Geburtsort" → placeOfBirth | LLM rät, `Semantik: Text` hilft nicht | LLM liest `Label: "Geburtsort" (de)` + Definition "Stadt, an dem geboren" |
| Format-Validierung | Keine — LLM gibt beliebigen Text zurück | LLM weiß, Format muss `ACTE-JJJJ-NNN` sein |
| Begründung extrahieren | LLM rät, "description" meint den Grund | LLM liest "Erklärung warum... einschließlich Rechtsgrundlage (AufenthG §44)" — weiß, dass der gesetzliche Verweis einbezogen werden soll |
| Arabische/Französische Dokumente | Hängt von LLM-Trainingsdaten ab | `@ar` / `@fr` Labels zur Ontologie hinzufügen — Prompt enthält sie automatisch |

### Erwartete Ausgabe des angereicherten Prompts:

```json
{
  "referenceNumber": "ACTE-2024-001",
  "candidateName": "Ahmad Ali",
  "placeOfBirth": "Kabul",
  "reasonForApplication": "Zulassung zum Integrationskurs gemäß §44 AufenthG. Seit 2022 in Deutschland, möchte Deutschkenntnisse verbessern für berufliche Integration. Bisher keinen Sprachkurs besucht."
}
```

---

## Zentrale Erkenntnis

Das Formular trägt seinen semantischen Kontext selbst mit sich.
Die Ontologie-Metadaten (Beschreibungen, mehrsprachige Labels,
Einschränkungen) werden IN den Prompt eingebettet — so hat das LLM
das vollständige Bild davon, was jedes Feld bedeutet, in jeder Sprache,
mit Validierungsregeln.

Das aktuelle System übergibt `Semantik: Text` für nicht-zugeordnete Felder.
Das ontologie-angereicherte System kann keine nicht-zugeordneten Felder haben,
weil jedes Feld VON der Ontologie ausgehend erstellt wurde.
