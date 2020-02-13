from enumchoicefield import ChoiceEnum


class UserClass(ChoiceEnum):
    first = '1. Klasse'
    second = '2. Klasse'
    third = '3. Klasse'
    fourth = '4. Klasse'
    fifth = '5. Klasse'


class UserStudy(ChoiceEnum):
    dataIng = 'Dataingeniør'
    digFor = 'Digital forretningsutvikling'
    digInc = 'Digital infrastruktur og cybersikkerhet'
    digSam = 'Digital samhandling'
    drift = 'Drift'
