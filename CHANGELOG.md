# CHANGELOG

## Tegnforklaring

### ✨ - Ny funksjonalitet

### ⚡ - Forbedret funksjonalitet

### 🦟 - Fikset en bug

### 🎨 - Designendringer

---

## Neste versjon
-✨ **Endring i permissions**. Endret hvordan vi håndterer tillatelser på nettsiden til å bruke våre nye grupper.

## Versjon 1.0.4 (15.03.2021)
- ✨ **Filopplastning**. Lagt til støtte for filopplastning til Azure gjennom eget endepunkt. Kun for medlemmer.
- ✨ **Forms**. Admins kan opprette, redigere og slette forms. Forms kan brukes i blant annet arrangement-påmelding.

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
