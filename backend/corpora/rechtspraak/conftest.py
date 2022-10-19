from addcorpus.load_corpus import load_corpus
import ianalyzer.config_fallback as config
from ianalyzer.factories.app import flask_app
import pytest
import os.path as op
from operator import itemgetter
here = op.abspath(op.dirname(__file__))


class UnittestConfig:
    SECRET_KEY = b'dd5520c21ee49d64e7f78d3220b2be1dde4eb4a0933c8baf'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # in-memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    TESTING = True
    CORPORA = {
        'rechtspraak': op.join(here, 'rechtspraak.py')
    }

    SERVERS = {
        'default': config.SERVERS['default']
    }
    CORPUS_SERVER_NAMES = {
        'rechtspraak': 'default'
    }

    RECHTSPRAAK_DATA = op.join(here, 'tests', 'data')
    RECHTSPRAAK_IMAGE = 'troon.jpg'
    RECHTSPRAAK_ES_INDEX = 'rechtspraak'
    RECHTSPRAAK_ES_DOCTYPE = 'article'

    # ?? apparantly needed to not crash
    SAML_FOLDER = "saml"
    SAML_SOLISID_KEY = "uuShortID"
    SAML_MAIL_KEY = "mail"


@pytest.fixture(scope='session')
def test_app(request):
    """ Provide an instance of the application with Flask's test_client. """
    app = flask_app(UnittestConfig)
    app.testing = True

    with app.app_context():
        yield app


@pytest.fixture
def test_corpus(test_app):
    return load_corpus('rechtspraak')


@pytest.fixture
def corpus_test_data():
    return {
        'name': 'rechtspraak',
        'docs': sorted([
            {
                'id': 'ECLI:NL:PHR:2016:1475',
                'date': '2016-12-20',
                'issued': '2017-02-07',
                'publisher': 'Raad voor de Rechtspraak',
                'creator': 'Parket bij de Hoge Raad',
                'zaaknr': '16/03212',
                'type': 'Conclusie',
                'subject': 'Strafrecht',
                'spatial': None,
                'procedure': None,
                'title': 'ECLI:NL:PHR:2016:1475 Parket bij de Hoge Raad , 20-12-2016 / 16/03212',
                'url': 	'http://deeplink.rechtspraak.nl/uitspraak?id=ECLI:NL:PHR:2016:1475',
                'abstract': 'Herziening, geuridentificatieproef, aanvraag ongegrond. HR herhaalt relevante overwegingen uit ECLI:NL:HR:2008:BC8789 m.b.t. een onregelmatig uitgevoerde geuridentificatieproef door de geurhondendienst Noord- en Oost-Gelderland in de periode van september 1997 tot en met maart 2006 en oordeelt dat m.b.t. geuridentificatieproeven in de onderhavige zaak in gelijke zin dient te worden geoordeeld. I.c. is echter geen sprake van een gegeven a.b.i. art. 457.1.c Sv; geen ernstig vermoeden dat de rechtbank de aanvrager zou hebben vrijgesproken.',
                'content': 'Nr. 16/03212 HS Zitting: 20 december 2016\nMr. P.C. Vegter\nConclusie inzake:\n [aanvrager] \nDe aanvrager is bij onherroepelijk vonnis van de rechtbank Zutphen van 19 oktober 2005 wegens 1. en 2. telkens “diefstal”, 3. “diefstal, waarbij de schuldige zich de toegang tot de plaats van het misdrijf heeft verschaft en het weg te nemen goed onder zijn bereik heeft gebracht door middel van braak, verbreking of inklimming”, 6. “diefstal, waarbij de schuldige zich de toegang tot de plaats van het misdrijf heeft verschaft en het weg te nemen goed onder zijn bereik heeft gebracht door middel van braak, verbreking of inklimming” en 7. “poging tot diefstal, waarbij de schuldige zich de toegang tot de plaats van het misdrijf heeft verschaft of het weg te nemen goed onder zijn bereik heeft gebracht door middel van braak, verbreking of inklimming” veroordeeld tot een gevangenisstraf voor de duur van tien maanden met aftrek als bedoeld in artikel 27 Sr, met de bijkomende beslissingen als weergegeven in dat vonnis.\nNamens de aanvrager heeft mr. J.J.J. van Rijsbergen, advocaat te Breda, een aanvraag tot herziening ingediend.\nDe aanvraag steunt op de omstandigheid dat sprake is van een gegeven als bedoeld in art. 457, eerste lid onder c, Sv. Daartoe wordt aangevoerd dat de rechtbank de aanvrager zou hebben vrijgesproken, indien zij bekend zou zijn geweest met de omstandigheid dat de in deze zaak uitgevoerde geuridentificatieproeven in strijd met het daarvoor geldende protocol zijn verricht. De aanvrager zou een brief van het openbaar ministerie hebben gekregen waarin werd aangegeven dat de in deze zaak verrichte geurproeven mogelijk niet geheel volgens de regels zijn uitgevoerd en waarin werd gewezen op de mogelijkheid om een herzieningsverzoek in te dienen bij de Hoge Raad. Deze brief is echter kwijtgeraakt.\nDe Hoge Raad heeft eerder geoordeeld dat in de gevallen waarin in de periode van september 1997 tot en met maart 2006 een geuridentificatieproef door de geurhondendienst Noord- en Oost-Gelderland in de desbetreffende strafzaak is uitgevoerd, dit onderzoek - behoudens concrete aanwijzingen van het tegendeel - moet worden geacht te hebben plaatsgevonden in strijd met het voorschrift dat de hondengeleider de volgorde van de geurdragers niet kent, hetgeen met zich brengt dat ervan moet worden uitgegaan dat het resultaat van die geuridentificatieproef in die gevallen niet als voldoende betrouwbaar kan gelden en dat aldus moet worden aangenomen dat het resultaat van de geuridentificatieproef niet zou zijn gebruikt voor het bewijs indien de rechter met de opgetreden onregelmatigheid bekend was geweest.\n5. Als grondslag voor een herziening kan krachtens het eerste lid, aanhef en onder c van art. 457 Sv slechts dienen een door bescheiden gestaafd gegeven dat bij het onderzoek op de terechtzitting aan de rechter niet bekend was en dat het ernstige vermoeden wekt dat indien dit gegeven bekend zou zijn geweest het onderzoek van de zaak zou hebben geleid tot, voor zover hier van belang, tot een vrijspraak van de gewezen verdachte. \n6. Uit de hiervoor bedoelde rechtspraak volgt dat wanneer het resultaat van een onregelmatige geurproef voor het bewijs van het tenlastegelegde feit is gebezigd, dat een ernstig vermoeden als hiervoor bedoeld kan opleveren. Daarvan is echter slechts sprake als niet aannemelijk is dat de rechter zonder dat resultaat op grond van het (andere) beschikbare bewijsmateriaal tot een bewezenverklaring zou zijn gekomen.\n7. Ten laste van de aanvrager is bewezenverklaard dat: “1. hij op 15 mei 2005 te Emst met het oogmerk van wederrechtelijke toe-eigening heeft weggenomen een herenfiets, merk Gazelle, toebehorende aan [betrokkene 1];\n2. hij in de nacht van 14 op 15 mei 2005 in de gemeente Heerde met het oogmerk van wederrechtelijke toe-eigening heeft weggenomen een herenfiets, merk Batavus, toebehorende aan [betrokkene 2];\n3. hij in de periode van 12 mei 2005 tot en met 13 mei 2005 in de gemeente Hattem, met het oogmerk van wederrechtelijke toe-eigening in/uit een kerkgebouw, gelegen aan de Markt, heeft weggenomen geld en een antieke Statenbijbel (met prenten/kaarten) toebehorende aan de Nederlands Hervormde Kerk, waarbij verdachte zich de toegang tot de plaats des misdrijfs heeft verschaft en de weg te nemen goederen onder zijn bereik heeft gebracht door middel van braak, verbreking en/of inklimming;\n6. hij in de periode van 4 mei 2005 tot en met 5 mei 2005 te Beerzerveld, met het oogmerk van wederrechtelijke toe-eigening in/uit een kerkgebouw, gelegen aan de Westerweg, heeft weggenomen muntgeld toebehorende aan de Nederlands Hervormde Kerk, waarbij verdachte zich de toegang tot plaats des misdrijfs heeft verschaft en het weg te nemen goed onder zijn bereik heeft gebracht door middel van braak, verbreking en/of inklimming.\n7. hij in periode van 4 mei 2005 tot en met 5 mei 2005 te Bergentheim, ter uitvoering van het door verdachte voorgenomen misdrijf om met het oogmerk van wederrechtelijke toe-eigening in/uit een kerkgebouw, gelegen aan de Kanaalweg Oost, weg te nemen geld en/of goederen, toebehorende aan de Nederlands Hervormde Kerk, en zich daarbij de toegang tot voornoemd gebouw te verschaffen en die/dat weg te nemen geld en/of goederen onder zijn bereik te brengen door middel van braak, verbreking en/of inklimming, met behulp van een dakpan een ruit van dat gebouw heeft ingegooid, terwijl de uitvoering van dat voorgenomen misdrijf niet is voltooid;\n8. hij in de periode van 4 mei 2005 tot en met 5 mei 2005 te Sibculo, met het oogmerk van wederrechtelijke toe-eigening in/uit een kerkgebouw, gelegen aan de Kloosterdijk, heeft weggenomen drie collectebussen, toebehorende aan een ander dan aan verdachte, waarbij verdachte zich de toegang tot de plaats des misdrijfs heeft verschaft door middel van braak”.\n8. De Rechtbank heeft volstaan met een vonnis waarin de bewijsmiddelen niet zijn opgenomen. Dat is niet ongebruikelijk, aangezien de aanvrager kennelijk geen reden heeft gezien van het vonnis hoger beroep in te stellen. Het vonnis waarvan herziening wordt gevraagd bevat wel de navolgende bewijsoverweging: “De raadsman heeft ter zitting de betrouwbaarheid van de door de speurhonden uitgevoerde sorteerproeven in twijfel getrokken. Hij heeft zich daarbij beroepen op een uitspraak van deze rechtbank contra verdachte d.d. 24 juni 2003 (06.060491-02), waarin wordt overwogen dat de sorteerproef tot op heden als een valide instrument voor het leveren van bewijs kan worden beschouwd, maar dat het desalniettemin voorkomt dat een hond een persoon ten onrechte als verdachte aanwijst.\nDe rechtbank constateert dat in de onderliggende strafzaak sprake is van sorteerproeven door verschillende honden waarvan de uitkomsten, op één na, de betrokkenheid van verdachte aangeven. Dit gegeven in onderlinge samenhang bezien met andersoortig bewijs, dwingt redelijkerwijs tot de conclusie dat verdachte de feiten - behoudens de onder 4 en 5 ten laste gelegde feiten - heeft begaan, waarbij de rechtbank mede heeft betrokken: -het relaas van een van de verbalisanten die verdachte twee maal korte tijd na elkaar heeft getroffen met verschillende fietsen en die heeft geconstateerd dat verdachte uit dichtbegroeide bosjes een van de straat niet zichtbare tas tevoorschijn haalde, met daarin een beitel die bij een inbraak gebruikt is, zoals blijkt uit de uitkomst van een verfspooronderzoek; -de op twee verschillende locaties aangetroffen schoensporen die met het schoeisel van verdachte corresponderen; -de bij verdachte in vorenbedoelde tas aangetroffen lijst waarop, plaatsen en/of adressen van kerkgebouwen stonden vermeld waar reeds was ingebroken; -de bij verdachte aangetroffen treinkaartjes met een vertrekplaats of bestemming die overeenkomt met de directe omgeving van een aantal plaatsen waar de misdrijven zijn gepleegd; -de opeenvolgende pleegdata en pleegplaatsen en de soortgelijke modus operandi; en waarvan zij een grote graad van toevalligheid niet aannemelijk acht”.\n9. Uit de aangehaalde overweging van de rechtbank wordt duidelijk dat zij inderdaad, zoals in de aanvraag tot uitgangspunt wordt genomen, de in deze zaak verrichte geurproeven in de bewijsvoering heeft betrokken. De processen-verbaal die zijn opgemaakt van het uitvoeren van deze geurproeven bevinden zich in het dossier. Het gaat hier echter niet om door geurhondendienst Noord- en Oost-Gelderland uitgevoerde onderzoeken, maar om onderzoeken van de interregionale speurhondendienst geuridentificatie van de regiopolitie ressort Arnhem. Nu deze onderzoeken evenwel zijn uitgevoerd in 2005 (mede) door ambtenaren verbonden aan de eerstgenoemde geurhondendienst, moet worden aangenomen dat ook de in deze zaak verrichte geurproeven mogelijk niet volgens de regels hebben plaatsgevonden. Uit de processen-verbaal blijkt voorts niet van concrete aanwijzingen dat die regels wel in acht zijn genomen. Aangenomen mag dan ook worden dat de rechtbank wanneer zij van de hiervoor bedoelde rechtspraak op de hoogte was geweest, de resultaten van de geurproeven niet voor het bewijs had gebezigd. \n10. Ik betwijfel echter of, zoals in de aanvraag wordt gesteld, de rechtbank aan de resultaten van de proeven bij de bewezenverklaring doorslaggevende betekenis heeft toegekend. De hiervoor aangehaalde overweging houdt in dat de rechtbank de resultaten in samenhang met de overige voor het bewijs gebezigde bewijsmiddelen heeft bezien. Tot de conclusie dat de rechtbank zonder die resultaten tot een vrijspraak was gekomen, dwingt de overweging niet. Die conclusie is bovendien niet gerechtvaardigd wanneer het dossier wordt beschouwd. Daarin bevindt zich ander bewijsmateriaal op grond waarvan de rechtbank met voldoende mate van aannemelijkheid kan hebben afgeleid dat de aanvrager de hem onder 1, 2, 3, 6, 7 en 8 tenlastegelegde feiten heeft gepleegd. Van een ernstig vermoeden als hiervoor bedoeld is dan ook geen sprake.\n11. Bij de gedingstukken bevindt zich een politieproces-verbaal met bijlagen van de politie Noord- en Oost-Gelderland, team recherche, unit Epe, met nummer PL0615/05-204825 gesloten op 27 juni 2005. In dit proces-verbaal wordt een elftal “incidenten” beschreven en is het grootste deel van het in dit dossier voorhanden zijnde bewijsmateriaal opgenomen en gerangschikt per incident. Een gedeelte van deze incidenten correspondeert met de in de uitspraak waarvan herziening wordt gevraagd bewezenverklaarde feiten (incident 1 met feit 1; incident 2 met feit 2; incident 3 met feit 3; incident 8 met feit 6, incident 9 met feit 7 en incident 10 met feit 8).\n12. Dat geen sprake is van een redelijk vermoeden dat de rechtbank tot vrijspraak was gekomen als de resultaten van de geurproeven buiten beschouwing worden gelaten, wordt het meest duidelijk ten aanzien van de onder 1 en 2 bewezenverklaarde fietsendiefstallen. Uit het dossier blijkt immers niet dat in dit verband geurproeven hebben plaatsgevonden. Ik ga op deze feiten dan ook niet verder in.\n13. Ten aanzien van de onder 6 bewezenverklaarde kerkinbraak, heeft wel een geurproef plaatsgevonden aan de hand van op de plaats delict veiliggestelde geurmonsters. Een match met de aanvrager heeft de geurproef echter niet opgeleverd. De resultaten van een geurproef hebben hier dus niet een directe rol gespeeld bij een bewezenverklaring. Uit het dossier kan worden afgeleid dat de aanvrager aan dit feit kan worden gelinkt door een schoenspoor dat op de plaats delict werd veiliggesteld en een match opleverde met de schoen van de aanvrager. Voorts blijkt uit de hiervoor aangehaalde overweging dat de rechtbank op grond van een vorm van schakelbewijs heeft vastgesteld dat sprake was van een modus operandi: bij de feiten 3, 6, 7 en 8 gaat het ook om kerkinbraken, die in een periode van enkele dagen (bij de feiten 6, 7 en 8 gaat het zelfs om in dezelfde nacht gepleegde) op relatief korte afstand van elkaar hebben plaatsgevonden. Bij al die inbraken sneuvelde een raam of ruit. Bij het beantwoorden van de vraag of ten aanzien van feit 6 sprake is van een ernstig vermoeden als hiervoor bedoeld, kunnen de geurproeven die hebben plaatsgevonden bij het onderzoek naar de feiten 3, 7 en 8 indirect een rol spelen. Met name gelet op hetgeen hierna ten aanzien van de feiten 3 en 7 wordt opgemerkt, meen ik evenwel dat de redenering betreffende het schakelbewijs stand kan houden ook wanneer de resultaten van de geurproeven buiten beschouwing worden gelaten en van een dergelijk ernstig vermoeden dus geen sprake is.\n14. In het onderzoek naar feit 3 heeft een geurproef plaatsgevonden, die een match met de aanvrager heeft opgeleverd. Het gaat hier niet om onderzoek naar geurmonsters die zijn genomen op de plaats delict, maar om een geurovereenkomst tussen de aanvrager en voorwerpen (een schroevendraaier, een beitel en een afbreekmesje) die zijn aangetroffen in een zwarte tas die de aanvrager op het moment van zijn aanhouding bij zich had. De aanvrager heeft bij zijn aanhouding geroepen dat de tas niet van hem was. Het geuronderzoek heeft kennelijk plaatsgevonden om dat verweer te ontkrachten. Het oordeel van de rechtbank dat de zwarte tas (wel) van de aanvrager was, steunt naast de resultaten van het geuronderzoek ook op de vaststelling dat de aanvrager van het bestaan van de tas en de vindplaats ervan op de hoogte moet zijn geweest. De aanhoudende verbalisanten hebben gezien dat de verdachte de tas doelgericht uit de bosjes haalde, terwijl die bosjes zodanig dichtbegroeid waren dat van buitenaf niet was waar te nemen dat zich daarin een tas zou bevinden. De resultaten van het geuronderzoek hebben hier dus niet een doorslaggevende rol gespeeld. Het oordeel dat de aanvrager de onder 3 bewezenverklaarde kerkinbraak moet hebben gepleegd heeft de rechtbank voorts niet alleen gebaseerd op het in de zwarte tas aangetroffen inbrekersgereedschap en de daarin aangetroffen lijst waarop (ook) (adressen van) kerken stonden vermeld waar kort daarvoor inbraken plaatsvonden en waarop ook Hattem stond, maar ook op het bij de kerk in Hattem aangetroffen schoenspoor dat een match opleverde met de schoen van de aanvrager. Van een redelijk vermoeden dat de rechtbank de aanvrager zou hebben vrijgesproken van dit feit, wanneer het de resultaten van de geurproef buiten beschouwing had gelaten, is geen sprake.\n15. Ook ten aanzien van feit 7 heeft een geurproef plaatsgevonden, die een match opleverde met de aanvrager. Het gaat hier om een geurovereenkomst tussen de aanvrager en geurmonsters die zijn genomen van een op de plaats delict aangetroffen dakpan. Feit 7 betreft een poging tot inbraak in een kerk in Bergentheim door het inslaan van een ruit, vermoedelijk met een dakpan. Wanneer het resultaat van deze geurproef wordt weggedacht, steunt het oordeel van de rechtbank dat de aanvrager dit feit moet hebben gepleegd op een match tussen een bij de kerk in Bergentheim aangetroffen schoenspoor met de schoen van de aanvrager, alsook op de door de rechtbank vastgestelde modus operandi. Het gaat om een (poging tot) kerkinbraak gepleegd in dezelfde nacht en op korte afstand van de onder 6 bewezenverklaarde inbraak enkele dagen voordat de onder 3 bewezenverklaarde inbraak plaatsvond.\n16. Bij feit 8 tot slot gaat het om een inbraak in Sibculo, in dezelfde nacht en in dezelfde regio als de feiten 6 en 7. Wanneer de uitslag van de ten aanzien van dit feit uitgevoerde geurproef wordt weggedacht, steunt deze veroordeling geheel op de door de rechtbank vastgestelde modus operandi. Blijkens haar overweging zag de rechtbank steun voor deze bewezenverklaring in de uit de eerder genoemde lijst blijkende interesse van de verdachte in kerken en kerkinbraken.\n17. Ook zonder de resultaten van de onregelmatige geurproeven zou de rechtbank met voldoende mate van aannemelijkheid uit het andere beschikbare bewijsmateriaal hebben afgeleid dat de aanvrager de onder 1, 2, 3, 6, 7 en 8 tenlastegelegde feiten heeft gepleegd. Van het ernstige vermoeden dat de rechtbank de aanvrager zou hebben vrijgesproken is dus geen sprake.\n18. De conclusie strekt ertoe dat de aanvraag ongegrond wordt verklaard en wordt afgewezen.\nDe Procureur-Generaal bij de Hoge Raad der Nederlanden\nAG\n HR 22 april 2008, ECLI:NL:HR:2008:BC8789, NJ 2008/591. Sindsdien is een groot aantal herzieningszaken behandeld waarin (mogelijk) niet correct uitgevoerde geurproeven een rol speelden. Zie meest recent HR 11 oktober 2016, ECLI:NL:HR:2016:2292.\n In het dossier bevinden zich een Akte afstand rechtsmiddel van 24 oktober 2005, waarin een door de aanvrager daartoe gemachtigde namens de verdachte afstand doet van de bevoegdheid tot het instellen van een rechtsmiddel, en een afschrift van de door de verdachte getekende machtiging. \n Deze zijn gevoegd als bijlage bij het hierna te noemen politieproces-verbaal van 27 juni 2005; verwezen wordt naar de doorgenummerde pagina’s van dat politieproces-verbaal. Het gaat om een proces-verbaal van 19 mei 2005 opgesteld door J. Smid, J.G. Schaafsma en K. Dedden, p. 77 (feit 3), een proces-verbaal van 6 juni 2005 door J. Smid en J.G. Schaafsma, p. 219 (feit 7) en een proces-verbaal van 6 juni 2005 door J. Smid en J.G. Schaafsma, p. 230 (feit 8). \n Zie daarover ook HR 11 oktober 2016, ECLI:NL:HR:2016:2292, onder 4.\n Aan de vermelding in die processen-verbaal dat de proeven hebben plaatsgevonden conform de daarvoor geldende protocollen, komt in dit verband geen betekenis toe. Zie daarover de conclusie van ambtgenoot Hofstee voor HR 8 juli 2014, ECLI:NL:HR:2014:1694 (ECLI:NL:PHR:2014:724), onder 14.\n Proces-verbaal van 6 juni 2006 opgemaakt door S. Brugman en J.G. Schaafsma (bijlage bij genoemd politieproces-verbaal, doorgenummerde pagina 208).\n Proces-verbaal vergelijkend schoensporenonderzoek 28 juni 2005.\n Proces-verbaal van 19 mei 2005 opgesteld door J. Smid, J.G. Schaafsma en K. Dedden (bijlage bij genoemd politieproces-verbaal, doorgenummerde pagina 77).\n Politieproces-verbaal, doorgenummerde pagina 72.\n Op de lijst (p. 81-82) staan ook “Aalten”, “Oosterkerk” en “Zonnebrink 61 Winterswijk”. Op 10-11 mei 2005 (p. 133-157) respectievelijk 10-11 maart 2005 (p. 166-201) vonden in die kerken inbraken plaats. Die inbraken hebben niet tot een veroordeling van de aanvrager geleid. Uit de in tas aangetroffen lijst kan in ieder geval worden afgeleid dat de aanvrager in mei 2005 een bovenmatige interesse in kerkgebouwen en kerkinbraken had. \n Doorgenummerde dossierpagina 86.\n Doorgenummerde dossierpagina 214.\n Proces-verbaal historie veiliggestelde sporen van 15 juni 2005 opgemaakt door P.G.J.M. Martijn.'
            },
            {
                'id': 'ECLI:NL:CBB:2022:1',
                'issued': '2022-01-07',
                'date': '2022-01-11',
                'publisher': 'Raad voor de Rechtspraak',
                'creator': 'College van Beroep voor het bedrijfsleven',
                'zaaknr': '20/1063',
                'type': 'Uitspraak',
                'procedure': 'Eerste aanleg - meervoudig',
                'spatial': 'Den Haag',
                'subject': 'Bestuursrecht',
                'url': 'http://deeplink.rechtspraak.nl/uitspraak?id=ECLI:NL:CBB:2022:1',
                'title': 'ECLI:NL:CBB:2022:1 College van Beroep voor het bedrijfsleven , 11-01-2022 / 20/1063',
                'abstract': 'Artikel 2:3, eerste lid, van de Algemene wet bestuursrecht artikel 4.5.12, eerste lid, aanhef en onder f, van de Regeling nationale EZ-subsidies\nHet College acht het aannemelijk dat appellant de bedoeling heeft gehad om ISDE subsidie voor een warmtepomp aan te vragen. Uit de aanvraag hadden de beoordelaars van SEEH-aanvragen kunnen afleiden dat appellant niet alleen voor vloer- en gevelisolatie en een aantal aanvullende energiebesparende maatregelen subsidie wilde aanvragen, maar ook voor een warmtepomp. Het lag daarom op de weg van de beoordelaars van SEEH-aanvragen om niet alleen een beoordeling op grond van de SEEH te doen, maar ook de aanvraag op grond van artikel 2:3, eerste lid, van de Awb onmiddellijk door te sturen naar de beoordelaars van ISDE-aanvragen. Het kan appellant in dit geval niet worden tegengeworpen dat zijn ISDE-aanvraag te laat bij verweerder is ingediend. Verweerder moet de ISDE-aanvraag dan ook opnieuw in behandeling nemen, uitgaande van de datum van indiening van de SEEH-aanvraag.',
                'content': 'uitspraak \nCOLLEGE VAN BEROEP VOOR HET BEDRIJFSLEVEN\nZaaknummer: 20/1063\nuitspraak van de meervoudige kamer van 11 januari 2022 in de zaak tussen\n [naam 1] , te [woonplaats] , appellant,\nen\nde minister van Economische Zaken en Klimaat, verweerder (gemachtigde: mr. M. Wullink).\nProcesverloop \nBij besluit van 2 oktober 2020 (het primaire besluit) heeft verweerder beslist op de aanvraag van appellant om een investeringssubsidie duurzame energie (ISDE) voor een warmtepomp in het kader van de Regeling nationale EZ-subsidies (Regeling).\nBij besluit van 2 november 2020 (het bestreden besluit) heeft verweerder het bezwaar tegen het primaire besluit ongegrond verklaard en het primaire besluit gehandhaafd. \nAppellant heeft tegen het bestreden besluit beroep ingesteld. \nVerweerder heeft een verweerschrift ingediend.\nHet onderzoek ter zitting heeft plaatsgevonden op 17 augustus 2021. Appellant is verschenen, vergezeld door [naam 2] . Verweerder heeft zich laten vertegenwoordigen door zijn gemachtigde. \nHet College heeft het onderzoek heropend en verweerder gevraagd om nadere stukken in te dienen.\nBij brief van 4 oktober 2021 heeft verweerder nadere stukken ingediend.\nBij brief van 20 oktober 2021 heeft het College verweerder verzocht zijn standpunt nader toe te lichten.\nBij brief van 29 oktober 2021 heeft verweerder zijn standpunt nader toegelicht.\nNadat, desgevraagd, geen van de partijen heeft verklaard gebruik te willen maken van het recht om te worden gehoord op een nadere zitting, heeft het College het onderzoek gesloten. \nOverwegingen \n1.1 Appellant heeft op 10 mei 2020 een aanvraag ingediend voor subsidie op grond van de Subsidieregeling energiebesparing eigen huis (SEEH) bij de minister van Binnenlandse Zaken en Koninkrijkrelaties (BZK). In de aanvraag heeft appellant vloer- en gevelisolatie, een energiedisplay en het waterzijdig inregelen verwarmingssysteem als energiebesparende maatregelen opgegeven. Appellant heeft als bijlage bij het aanvraagformulier foto’s van een warmtepomp, een thermostaat, slimme thermostaatknoppen, vloer- en muurisolatie en een energielabel van de warmtepomp gevoegd. Daarnaast heeft appellant als bijlage de kostenraming voor de gehele verbouwing, de factuur voor een warmtepomp en de productkenmerken van een warmtepomp toegevoegd. Op 12 augustus 2020 en 27 augustus 2020 heeft een medewerker van de Rijksdienst voor Ondernemend Nederland (RVO) om nadere informatie gevraagd. Op 27 augustus 2020 en 31 augustus 2020 heeft appellant de benodigde informatie verschaft en gemeld dat het hem vooral ging om een subsidie voor een warmtepomp. Bij e-mail van 2 september 2020 heeft de betreffende medewerker van RVO aan appellant medegedeeld dat onder de SEEH geen subsidie kan worden aangevraagd voor een warmtepomp en dat appellant voor de overige energiebesparende maatregelen ook niet in aanmerking komt voor een subsidie omdat niet aan alle vereisten voor de SEEH wordt voldaan. Appellant is erop gewezen dat hij voor de warmtepomp gebruik kan maken van de ISDE op grond van titel 4.5 van de Regeling. De minister van BZK heeft bij besluit van 8 september 2020 aan appellant meegedeeld dat hij niet in aanmerking komt voor SEEH-subsidie. \n1.2 In navolging van het e-mailbericht van 2 september 2020 van RVO heeft appellant op 5 september 2020 een ISDE-aanvraag ingediend bij verweerder. Als datum van ingebruikname van de warmtepomp heeft appellant 6 februari 2020 ingevuld. \n1.3 Bij het primaire besluit, dat is gehandhaafd bij het bestreden besluit, heeft verweerder de aanvraag van 5 september 2020 met toepassing van artikel 4.5.12, eerste lid, aanhef en onder f, van de Regeling afgewezen omdat deze niet binnen zes maanden na het installeren van de warmtepomp, te weten uiterlijk 6 augustus 2020, is ingediend.\n2. Appellant voert, samengevat, in beroep aan dat het hem niet kan worden aangerekend dat hij de aanvraag voor de ISDE te laat heeft ingediend. Hij heeft die aanvraag pas op 5 september 2020 ingediend, omdat hij ervan uitging dat hij op grond van de al op 10 mei 2020 ingediende aanvraag voor de SEEH aanspraak kon maken op een subsidie voor de warmtepomp. Appellant werd gesterkt in zijn vertrouwen doordat hij na de indiening van de aanvraag voor de SEEH telefonisch de bevestiging van verweerder kreeg dat hij het aanvraagformulier goed had ingevuld voor de aanvraag van een subsidie voor een warmtepomp. Volgens appellant werd op de website van verweerder geen duidelijk onderscheid gemaakt tussen de SEEH en de ISDE. Pas na het e-mailbericht van 2 september 2020 werd het voor appellant duidelijk dat hij de verkeerde subsidieaanvraag had ingediend. Appellant rekent het de minister van BZK aan dat hij de aanvraag voor de SEEH niet heeft opgevat als een aanvraag in het kader van de ISDE. Volgens appellant had zijn aanvraag intern moeten worden doorgestuurd naar de juiste afdeling. Verder voert appellant aan dat door de niet adequate handelswijze zoveel vertraging is opgelopen dat hij niet meer in staat was om de achteraf gebleken onjuiste aanvraag te herstellen. Appellant voelt zich benadeeld door de trage handelswijze van verweerder. Hij vindt het bovendien onrechtvaardig dat hij wordt afgerekend op een te late indiening van de aanvraag terwijl het verweerder niet wordt aangerekend dat er laat is beslist op de aanvraag. \n3. Verweerder stelt zich op het standpunt dat hij de ISDE-aanvraag terecht heeft afgewezen. De SEEH en de ISDE zijn verschillende regelingen. De SEEH ziet met name op subsidies voor isolatiemaatregelen in particuliere woningen, terwijl de ISDE ziet op het aanbrengen van technische installaties. De regelingen hebben een eigen beoordelingskader en het uitvoerende bestuursorgaan verschilt. Verweerder is verantwoordelijk voor de ISDE en de minister van BZK is verantwoordelijk voor de SEEH. Het is de verantwoordelijkheid van de aanvrager om zich te verdiepen in de vereisten en voorwaarden die horen bij de regeling waarvoor hij subsidie wil aanvragen. Uit de aanvraag van 10 mei 2020 blijkt dat appellant subsidie heeft aangevraagd voor vloer- en gevelisolatie en een aantal aanvullende energiebesparende maatregelen. Verweerder heeft het door appellant ingevulde en ingediende aanvraagformulier als uitgangspunt gehanteerd bij de beoordeling van de aanvraag. Verweerder stelt dat, gezien de vragen die in het aanvraagformulier worden gesteld en de wijze waarop het SEEH-formulier is ingevuld, duidelijk had kunnen zijn voor appellant dat hij geen subsidieaanvraag deed voor een warmtepomp. Voor de medewerkers van de minister van BZK hoefden de wijze waarop het SEEH-formulier is ingevuld en de bijlages die appellant heeft toegevoegd ook geen vragen op te roepen. Pas in de reactie (op 27 augustus 2020) op de gevraagde nadere informatie over de SEEH-aanvraag maakte appellant expliciet kenbaar dat hij een subsidie wilde aanvragen voor een warmtepomp. De medewerkers van de minister van BZK konden er dus niet eerder dan 27 augustus 2020 op bedacht zijn dat het appellant ging om de warmtepomp en niet om de andere energiebesparende maatregelen. \nOp dat moment was de termijn van zes maanden na de installatie uit de ISDE al verstreken. Voor de ISDE-aanvraag geldt dat op grond van artikel 4.5.12, eerste lid, aanhef en onder f, van de Regeling, dwingend is voorgeschreven dat een te laat ingediende aanvraag om subsidie moet worden afgewezen. De Regeling bevat geen hardheidsclausule en biedt verweerder dus geen ruimte voor een belangenafweging als bedoeld in artikel 3:4, eerste lid, van de Algemene wet bestuursrecht (Awb). Verweerder was daarom gehouden de aanvraag van appellant af te wijzen. \n4. Aritkel 2:3, eerste lid van de Awb, luidt als volgt: \nHet bestuursorgaan zendt geschriften tot behandeling waarvan kennelijk een ander bestuursorgaan bevoegd is, onverwijld door naar dat orgaan, onder gelijktijdige mededeling daarvan aan de afzender.\n5. Anders dan verweerder acht het College het aannemelijk dat appellant kennelijk ook de bedoeling heeft gehad om subsidie voor een warmtepomp aan te vragen. De bijlagen die appellant bij de SEEH-aanvraag heeft meegestuurd, zien vrijwel allemaal op een warmtepomp. Uit de aanvraag hadden de beoordelaars van SEEH-aanvragen kunnen afleiden dat appellant niet alleen voor vloer- en gevelisolatie en een aantal aanvullende energiebesparende maatregelen subsidie wilde aanvragen, maar ook voor een warmtepomp. Het lag daarom op de weg van de beoordelaars van SEEH-aanvragen om niet alleen een beoordeling op grond van de SEEH te doen, maar ook – eventueel na het stellen van nadere vragen aan appellant – de aanvraag op grond van artikel 2:3, eerste lid, van de Awb onmiddellijk door te sturen naar de beoordelaars van ISDE-aanvragen. Dat de SEEH en de ISDE aan verschillende bestuursorganen zijn opgedragen, zoals verweerder naar voren brengt, maakt het voorgaande, gelet op het bepaalde in artikel 2:3, eerste lid, van de Awb, niet anders. Daar komt nog bij dat de beide regelingen feitelijk worden uitgevoerd door RVO.\nHet College stelt vast dat de aanvraag niet is doorgezonden en dat pas in augustus, toen de termijn voor de ISDE op grond van artikel 4.5.12, eerste lid, aanhef en onder f, van de Regeling al was verstreken, door de beoordelaar van de SEEH-aanvraag nadere vragen aan appellant zijn gesteld over zijn aanvraag. Appellant heeft die vragen direct beantwoord. \nOnder deze omstandigheden kan appellant niet worden tegengeworpen dat zijn ISDE-aanvraag te laat bij verweerder is ingediend. Verweerder moet de ISDE-aanvraag dan ook opnieuw in behandeling nemen, uitgaande van de datum van indiening van de SEEH-aanvraag. \n6. Het beroep is gegrond en het College vernietigt het bestreden besluit. Het College ziet geen aanleiding zelf in de zaak te voorzien, omdat het aan verweerder is om op de aanvraag te beslissen en de hoogte van de subsidie vast te stellen. Verweerder zal daarom een nieuw besluit moeten nemen met inachtneming van deze uitspraak. Het College stelt hiervoor een termijn van zes weken. \n7. Voor een veroordeling in de proceskosten is geen aanleiding, omdat niet is gebleken van te vergoeden proceskosten.\nBeslissing\nHet College:\n- verklaart het beroep gegrond; - vernietigt het bestreden besluit; - draagt verweerder op binnen 6 weken na de dag van verzending van deze uitspraak een nieuw besluit te nemen op het bezwaar met inachtneming van deze uitspraak; - draagt verweerder op het betaalde griffierecht van € 178,- aan appellant te vergoeden.\nDeze uitspraak is gedaan door mr. J.H. de Wildt, mr. M. van Duuren en mr. B. Bastein, in aanwezigheid van mr. N.C.H. Vrijsen, griffier. De beslissing is in het openbaar uitgesproken op 11 januari 2022.\nDe voorzitter en de griffier zijn niet in de gelegenheid de uitspraak te ondertekenen.'
            }
        ], key=itemgetter('date'))
    }
