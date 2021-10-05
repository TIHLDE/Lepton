# CHANGELOG

## Tegnforklaring

### ✨ - Ny funksjonalitet

### ⚡ - Forbedret funksjonalitet

### 🦟 - Fikset en bug

### 🎨 - Designendringer

---

## Neste versjon
- ✨ **Skjemamaler**. La inn støtte for skjemamaler.
- ⚡ **Ytelse**. Forbedret ytelsen på API'et gjennom blant annet mer caching, async eposter og andre forbedringer.

## Versjon 1.0.18 (30.09.2021)
- 🦟 **Arrangement**. Hent ut kun svar til spørreskjema for dem som ha plass på arrangementet.
- 🦟 **Spørreskjema**. Fikset bug der medlemmer av NoK ikke hadde tilgang til å redigere spørreskjemaer.
- 🦟 **Prikk**. Påmeldte på venteliste får nå ikke lenger prikk

## Versjon 1.0.17 (24.09.2021)
- ✨ **Svar på skjemaer** kan nå lastes ned som en csv-fil.
- ⚡ **Maksgrensen på arrangementer** økes nå hvis en admin melder på noen og det er fullt.

## Versjon 1.0.16 (21.09.2021)
- Skjemaer
    - ✨ **Evalueringer** må bli besvart før neste påmelding.
    - ⚡ **Alternativ på flervalgsspørsmål** er nå sortert etter tittel.
    - ✨ **Egne skjemaer** kan nå hentes ut i eget endepunkt.
    - ⚡ **Skjemaer**. Legg ved mer info om arrangementet i spørrskjemaer tilknyttet et arrangement.
    - ✨ **Skjemaer**. Legg ved info om bruker allerede har svart på et spørreskjema.

## Versjon 1.0.15 (15.09.2021)
- 🦟 **Tidssoner**. Fikset bug der tidspunkter i eposter blir formatert med feil tidssone.

## Versjon 1.0.14 (12.09.2021)
- ✨ **Svar på spørreskjemaer** blir nå sendt med sammen med påmeldingen.
- ✨ **Statistikk spørreskjemaer** Kan nå hente ut statistikk over svar på spørreskjemaer.

## Versjon 1.0.13 (06.09.2021)
- ✨ **Svar på spørreskjemaer** Medlemmer kan nå svare på spørreskjemaer.
- ✨ **Grupper** Ledere for undergrupper blir nå automagisk medlem av hs gruppen

## Versjon 1.0.12 (22.08.2021)
- 🦟 **Celery**. Fikset problem der oppdatering av arrangement førte til evig rekursjon.
- ✨ **Varsler**. Varsler kan nå inneholder linker til relevant innhold.
- ✨ **Arrangement-melding**. Arrangører av arrangementer kan sende ut epost/varsel til de påmeldte deltagerne.
- ⚡ **Bedrifter**. Finere epost fra bedrifter til mottager.
## Versjon 1.0.11 (11.08.2021)
- ✨ **Brukere**. Admins kan nå slette nye "ventende" brukere og legge ved en begrunnelse.
- 🦟 **Celery**. Fikset Celery tasks slik at man ikke kjører samme flere ganger lengre.
- 🦟 **Bruker**. Når admin oppdaterer egen bruker så kommer nå samme data tilbake som for vanlige medlemmer.
## Versjon 1.0.10 (10.05.2021)
- ⚡ **Bruker** Lagt til egne endpunkter for å hente ut relatert bruker data
## Versjon 1.0.9 (05.05.2021)
- ⚡ **Pages** Implementert søk i pages siden
- ⚡ **Medlemskap**.Lagt til pagination på listing av medlemskap, og filtrering for å hente ut list med bare medlemmer.
- ⚡ **Varsler**. Nye brukere får epost om at bruker er blitt godkjent. Brukere som blir lagt til i en gruppe får varsel.
- 🦟 **Tilganger**. Fikset bug der HS ikke hadde tilgang til å aktivere nye brukere.
- ✨ **Brukeradmin**. HS og Index har nå mulighet til å oppdatere brukerdata.

## Versjon 1.0.8 (01.05.2021)
- ⚡ **Brukere**. Fjernet felter fra brukere som hentes ut i liste, slik at forespørselen går raskere.
- 🦟 **Påmelding**. Fikset bug der brukere ikke kunne avslå å bli avbildet på arrangementer.
- 🦟 **Tilbakestilling av passord** tar brukeren til riktig side fremfor en som ikke finnes.

## Versjon 1.0.7 (26.04.2021)
- ⚡ **Azure**. Satt opp produksjon i Azure og automatisk oppdatering ved push til master.
- ✨ **Endring i permissions**. Endret hvordan vi håndterer tillatelser på nettsiden til å bruke våre nye grupper.
- ⚡ **Utvidede tillatelser**. Alle medlemmer av Sosialen og Promo kan nå legge ut arrangementer og nyheter.
- ⚡ **Medlemskap i TIHLDE**. Sjekk av medlemskap i TIHLDE bruker nå medlemskap til grupper.

## Versjon 1.0.6 (09.04.2021)
- 🦟 **Oppdatert arrangement**. Fikset bug der det ikke var mulig å oppdatere arrangement.
- ✨ **Azure**. Satt opp dev-miljø i Azure for å migrere vekk fra Drift og til skyen.
- ✨ **Venteliste nummer**. Henter nå ut hvilken plass du er på i ventelisten
- ✨ **Refusjons skjema**. Lagt til mulighet for å sende refusjons skjema rett til økonomiansvarlig, med kvittering.

## Versjon 1.0.5 (24.03.2021)
- 🦟 **Opprett arrangement**. Fikset feil der det ikke var mulig å opprette et arrangement.
- ✨ **Logging** av endringer skjer automatisk ved bruk.
- ✨ **Prikksystemet**. Da er det endelig laget endepunkter for prikksystemet, slik at admin kan nå hente, lage og slette prikker.

## Versjon 1.0.4 (15.03.2021)
- ✨ **Filopplastning**. Lagt til støtte for filopplastning til Azure gjennom eget endepunkt. Kun for medlemmer.
- ✨ **Spørreskjemaer**. Admins kan opprette, redigere og slette spørreskjemaer. Disse kan brukes i blant annet arrangement-påmelding.

## Versjon 1.0.3 (09.03.2021)
- ⚡ **Pagination i varsler**. Lagt til pagination i varsler, samt lagt til tester og fjernet admin's muligheter til å opprette/endre/slette andres varsler.
- ✨ **Korte URL's**. Opprettet en ny tjeneste der brukere kan lagre url'er bak korte, valgfrie slugs.
- ✨ **Ukens Bedrift**. Nå er det mulig for NoK å lage en kø med ukens bedrifter basert på ukenr

## Versjon 1.0.2 (22.02.2021)
- 🦟 **Lås påmeldingstid i registrering**. Hindre at tidspunktet for påmelding endres når påmeldingen endres. Dermed beholder påmeldte sin prioritet i listen.
- 🎨 **Nytt utseende i epost**. Oppdatert utseende i eposter som harmonierer med med resten av nettsiden.
- 🦟 **Begrens epost-domener**. Hindre brukere i å lage bruker med @ntnu.no-adresser siden vi ikke klarer å sende epost til slike adresser.
- ⚡ **Avmelding på venteliste**. Brukere kan melde seg av arrangementer etter avmeldingsfristen hvis de er på ventelisten.
- ⚡ **Sorter registrations**. Sortert registrations basert på id slik at de som meldte seg på først kommer øverst i listen.
- 🎨 **Valgfri ingress i annonser**. Det er nå valgfritt å legge inn en ingress i jobbannonser.
- ⚡ **Pagination i nyheter**. Lagt til pagination i nyheter
- 🦟 **Å melde seg av som adminbruker** flytter nå opp brukere på ventelisten, som forventet.
- ⚡ **Bruker får bilde** som kan brukes som profilbilde på TIHLDE siden

## Versjon 1.0.1 (09.02.2021)
- ⚡ **Ryddet opp i event-felter**. Fjernet åpent tilgjengelig liste over deltagere, samt redusert antall felter som returneres når man henter flere.
- 🦟 **Fikset utviklingsmiljø**. Fikset pipfile slik at Heroku-dev backend nå fungerer igjen.

## Versjon 1.0.0 (01.02.2021)
