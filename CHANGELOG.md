# CHANGELOG

## Tegnforklaring

### ✨ - Ny funksjonalitet

### ⚡ - Forbedret funksjonalitet

### 🦟 - Fikset en bug

### 🎨 - Designendringer

---

## Neste versjon
- ⚡ **Brukere**. Lagt til at superadmins kan nå slette brukere
- 🦟 **Arrangementer**. Fikset en bug hvor man ikke kunne hente ut tidligere Arrangementer
## Versjon 2022.01.15
- ⚡ **Botsystem**. Lovverket er bedre sortert ved at paragraf-nummer nå lagres separat.

## Versjon 2022.01.01
- ✨ **Gruppeskjemaer**. Admin/leder av gruppe kan styre om det tillates flere besvarelser, om skjemaet er åpent og begrense svar til kun gruppens medlemmer.
- ✨ **Botsystem**. Medlemmer får nå et varsl når de får en ny bot.
- ✨ **Botsjef**. Nye botsjefer får nå informasjon om sin nye roller på varsel og epost.
- ✨ **Botsystem**. Grupper kan nå ha et botsystem og lovverk. Det er kun åpent for medlemmene og medlemmer kan gi bøter til hverandre.

## Versjon 2021.11.30
- ✨ **Påmeldinger**. Brukere kan abonnere på sine påmeldinger til arrangementer gjennom kalenderen sin.
- ✨ **Sider**. Lagt til plassering og rekkefølge på sider.
- ✨ **Gruppeskjemaer** kan nå bli opprettet av alle medlemmer av gruppen.

## Versjon 2021.11.16
- ⚡ **Grupper** har nå bilder.
- ✨ **Brukere**. Studenter kan nå registrere kontoer med Informasjonsbehandling som studieprogram.
- ✨ **Arrangementer**. Endret tilgangshåndtering til arrangementer ved å knytte dem til grupper. Dermed kan også ledere av komitéer og interessegrupper opprette arrangementer.

## Versjon 2021.11.14
- ⚡ **Arrangement**. Om en usvart evaluering er over 30 dager gammel, vil den ikke hindre deg i å melde deg på et arrangement.
- ⚡ **Epost**. Støtter flere epost-leverandører gjennom mer universell formatering.
- ✨ **Prioriteringer** En innstilling på arrangementer som gjør at kun prioriterte studenter kan melde seg på.
- 🦟 **Svar på spørreskjemaer**. Fikset en bug der svar på spørreskjema ikke ble registrert.

## Versjon 2021.11.01
- 🦟 **Arrangement**. Fikset bug der admins ikke kunne melde påmeldte som ankommet hvis noen var på ventelisten.

## Versjon 2021.10.28
- ✨ **Digitalt fotalbum**. La til funksjonalitet for å legge til et fotoalbum.
- ✨ **Prikk**.  Nedtellingstiden til prikker settes på vent med ferier.
- ✨ **Rekkefølge på spørsmål** er nå lagt til.
- 🦟 **Tidssoner**. Standarisert tidssoner.

## Versjon 2021.10.19
- ⚡ **Arrangement** blir nå ikke overbooket når en person blir flyttet opp fra ventelisten.
- 🦟 **Bedrifter-skjema**. Fikset bug der bedrifts-skjema ikke ble sendt korrekt til NoK.
- ✨ **Skjemamaler**. La inn støtte for skjemamaler.
- ⚡ **Arrangementer**. Prioritet på arrangementer har blitt fjernet.
- ✨ **Jobbannonser** har nå stillingstype og år.
- ⚡ **Prikker**. På arrangement kan man nå velge om man ønsker å ignorere prikker / gi nye prikker.
- ⚡ **Prikker**. Kun Index og HS-medlemmer kan nå slette prikker.
- ✨ **Prikker**. Brukere mottar nå varsel om at de har fått en ny prikk.
- ⚡ **Spørreskjema**. Tekstfelt kan nå svares på med lengre tekst enn bare 255 tegn.

## Versjon 2021.10.11
- ⚡ **Ytelse**. Produksjon kjører nå med Gunicorn og Uvicorn med flere workers for å bli enda raskere.
- ⚡ **Avhengigheter**. Python er oppgradert til v3.9 og Django er oppdatert til v3.2.8.
- ✨ **Flower** Lagt til administrasjonspanel for Celery.

## Versjon 2021.10.06
- ⚡ **Ytelse**. Forbedret ytelsen på API'et gjennom blant annet mer caching, async eposter og andre forbedringer.

## Versjon 2021.09.30
- 🦟 **Arrangement**. Hent ut kun svar til spørreskjema for dem som ha plass på arrangementet.
- 🦟 **Spørreskjema**. Fikset bug der medlemmer av NoK ikke hadde tilgang til å redigere spørreskjemaer.
- 🦟 **Prikk**. Påmeldte på venteliste får nå ikke lenger prikk

## Versjon 2021.09.24
- ✨ **Svar på skjemaer** kan nå lastes ned som en csv-fil.
- ⚡ **Maksgrensen på arrangementer** økes nå hvis en admin melder på noen og det er fullt.

## Versjon 2021.09.21
- Skjemaer
    - ✨ **Evalueringer** må bli besvart før neste påmelding.
    - ⚡ **Alternativ på flervalgsspørsmål** er nå sortert etter tittel.
    - ✨ **Egne skjemaer** kan nå hentes ut i eget endepunkt.
    - ⚡ **Skjemaer**. Legg ved mer info om arrangementet i spørrskjemaer tilknyttet et arrangement.
    - ✨ **Skjemaer**. Legg ved info om bruker allerede har svart på et spørreskjema.

## Versjon 2021.09.15
- 🦟 **Tidssoner**. Fikset bug der tidspunkter i eposter blir formatert med feil tidssone.

## Versjon 2021.09.12
- ✨ **Svar på spørreskjemaer** blir nå sendt med sammen med påmeldingen.
- ✨ **Statistikk spørreskjemaer** Kan nå hente ut statistikk over svar på spørreskjemaer.

## Versjon 2021.09.06
- ✨ **Svar på spørreskjemaer** Medlemmer kan nå svare på spørreskjemaer.
- ✨ **Grupper** Ledere for undergrupper blir nå automagisk medlem av hs gruppen

## Versjon 2021.08.22
- 🦟 **Celery**. Fikset problem der oppdatering av arrangement førte til evig rekursjon.
- ✨ **Varsler**. Varsler kan nå inneholder linker til relevant innhold.
- ✨ **Arrangement-melding**. Arrangører av arrangementer kan sende ut epost/varsel til de påmeldte deltagerne.
- ⚡ **Bedrifter**. Finere epost fra bedrifter til mottager.
## Versjon 2021.08.11
- ✨ **Brukere**. Admins kan nå slette nye "ventende" brukere og legge ved en begrunnelse.
- 🦟 **Celery**. Fikset Celery tasks slik at man ikke kjører samme flere ganger lengre.
- 🦟 **Bruker**. Når admin oppdaterer egen bruker så kommer nå samme data tilbake som for vanlige medlemmer.
## Versjon 2021.05.10
- ⚡ **Bruker** Lagt til egne endpunkter for å hente ut relatert bruker data
## Versjon 2021.05.05
- ⚡ **Pages** Implementert søk i pages siden
- ⚡ **Medlemskap**.Lagt til pagination på listing av medlemskap, og filtrering for å hente ut list med bare medlemmer.
- ⚡ **Varsler**. Nye brukere får epost om at bruker er blitt godkjent. Brukere som blir lagt til i en gruppe får varsel.
- 🦟 **Tilganger**. Fikset bug der HS ikke hadde tilgang til å aktivere nye brukere.
- ✨ **Brukeradmin**. HS og Index har nå mulighet til å oppdatere brukerdata.

## Versjon 2021.05.01
- ⚡ **Brukere**. Fjernet felter fra brukere som hentes ut i liste, slik at forespørselen går raskere.
- 🦟 **Påmelding**. Fikset bug der brukere ikke kunne avslå å bli avbildet på arrangementer.
- 🦟 **Tilbakestilling av passord** tar brukeren til riktig side fremfor en som ikke finnes.

## Versjon 2021.04.26
- ⚡ **Azure**. Satt opp produksjon i Azure og automatisk oppdatering ved push til master.
- ✨ **Endring i permissions**. Endret hvordan vi håndterer tillatelser på nettsiden til å bruke våre nye grupper.
- ⚡ **Utvidede tillatelser**. Alle medlemmer av Sosialen og Promo kan nå legge ut arrangementer og nyheter.
- ⚡ **Medlemskap i TIHLDE**. Sjekk av medlemskap i TIHLDE bruker nå medlemskap til grupper.

## Versjon 2021.04.09
- 🦟 **Oppdatert arrangement**. Fikset bug der det ikke var mulig å oppdatere arrangement.
- ✨ **Azure**. Satt opp dev-miljø i Azure for å migrere vekk fra Drift og til skyen.
- ✨ **Venteliste nummer**. Henter nå ut hvilken plass du er på i ventelisten
- ✨ **Refusjons skjema**. Lagt til mulighet for å sende refusjons skjema rett til økonomiansvarlig, med kvittering.

## Versjon 2021.03.24
- 🦟 **Opprett arrangement**. Fikset feil der det ikke var mulig å opprette et arrangement.
- ✨ **Logging** av endringer skjer automatisk ved bruk.
- ✨ **Prikksystemet**. Da er det endelig laget endepunkter for prikksystemet, slik at admin kan nå hente, lage og slette prikker.

## Versjon 2021.03.15
- ✨ **Filopplastning**. Lagt til støtte for filopplastning til Azure gjennom eget endepunkt. Kun for medlemmer.
- ✨ **Spørreskjemaer**. Admins kan opprette, redigere og slette spørreskjemaer. Disse kan brukes i blant annet arrangement-påmelding.

## Versjon 2021.03.09
- ⚡ **Pagination i varsler**. Lagt til pagination i varsler, samt lagt til tester og fjernet admin's muligheter til å opprette/endre/slette andres varsler.
- ✨ **Korte URL's**. Opprettet en ny tjeneste der brukere kan lagre url'er bak korte, valgfrie slugs.
- ✨ **Ukens Bedrift**. Nå er det mulig for NoK å lage en kø med ukens bedrifter basert på ukenr

## Versjon 2021.02.22
- 🦟 **Lås påmeldingstid i registrering**. Hindre at tidspunktet for påmelding endres når påmeldingen endres. Dermed beholder påmeldte sin prioritet i listen.
- 🎨 **Nytt utseende i epost**. Oppdatert utseende i eposter som harmonierer med med resten av nettsiden.
- 🦟 **Begrens epost-domener**. Hindre brukere i å lage bruker med @ntnu.no-adresser siden vi ikke klarer å sende epost til slike adresser.
- ⚡ **Avmelding på venteliste**. Brukere kan melde seg av arrangementer etter avmeldingsfristen hvis de er på ventelisten.
- ⚡ **Sorter registrations**. Sortert registrations basert på id slik at de som meldte seg på først kommer øverst i listen.
- 🎨 **Valgfri ingress i annonser**. Det er nå valgfritt å legge inn en ingress i jobbannonser.
- ⚡ **Pagination i nyheter**. Lagt til pagination i nyheter
- 🦟 **Å melde seg av som adminbruker** flytter nå opp brukere på ventelisten, som forventet.
- ⚡ **Bruker får bilde** som kan brukes som profilbilde på TIHLDE siden

## Versjon 2021.02.09
- ⚡ **Ryddet opp i event-felter**. Fjernet åpent tilgjengelig liste over deltagere, samt redusert antall felter som returneres når man henter flere.
- 🦟 **Fikset utviklingsmiljø**. Fikset pipfile slik at Heroku-dev backend nå fungerer igjen.
