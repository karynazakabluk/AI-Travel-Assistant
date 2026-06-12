# Systemarkitektur

[Bruker]

↓

[Flask Webapplikasjon]

↓

[SQLite Database]

## Beskrivelse

Brukeren kommuniserer med systemet gjennom en nettleser.

Flask fungerer som backend og håndterer innlogging, brukeradministrasjon, bestillinger, AI-anbefalinger og kommunikasjon med databasen.

SQLite brukes til lagring av brukere og reisebestillinger.

AI-funksjonen analyserer brukerens ønsker og foreslår passende reisemål basert på nøkkelord og preferanser.

Systemet benytter rollebasert tilgangskontroll. Vanlige brukere kan opprette og kansellere egne bestillinger, mens administrator kan se, redigere og slette alle bestillinger i systemet.

Innlogging og sesjoner brukes for å sikre at brukere kun får tilgang til funksjoner de har rettigheter til.

## Viktige funksjoner

- /login
- /register
- /bookings
- /admin
- /assistant
- /about

### Frontend

* HTML
* CSS

### Backend

* Python
* Flask

### Database

* SQLite
