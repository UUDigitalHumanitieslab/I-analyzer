import os
import warnings
import pytest
from datetime import datetime

from addcorpus.python_corpora.load_corpus import load_corpus_definition

CORPUS_TEST_DATA = [
    {
        'name': 'parliament-canada',
        'docs': [
        {
            'date': '2015-02-02',
            'country': 'Canada',
            'debate_title': 'Government Orders',
            'debate_id': 'ca.proc.d.2015-02-02',
            'chamber': 'House of Commons',
            'party': 'New Democratic Party',
            'role': 'Interjection',
            'speaker': 'Jack Harris',
            'speaker_id': 'c846297d-8bc7-4e69-b6eb-31d0e19f7ec1',
            'speaker_constituency': 'St. John\'s East',
            'speech': 'Mr. Speaker, I suppose I could ask the member for Nanaimo—Alberni why the Government of Canada would put $280 million into last year\'s budget if it was intended to compensate for something that would happen in 2020.',
            'id': 'ca.proc.d.2015-02-02.16582.214',
            'topic': 'Business of Supply',
            'subtopic': 'Opposition Motion—Newfoundland and Labrador Fisheries Investment Fund',
        }],
        'n_documents': 3
    },
    {
        'name': 'parliament-france',
        'docs': [
        {
            "book_id" : "37531030876685 37531030876685/1/58 37531030876685_1_58_7",
            "chamber" : "Assemblee Nationale",
            "country" : "France",
            "date" : "1881-01-11",
            "date_is_estimate" : False,
            "debate_id" : "1881-01-11",
            "debate_type" : None,
            "era" : "3Rd Republic",
            "legislature" : None,
            "page" : "7",
            "page_source" : "X0000007.xml",
            "sequence" : "0",
            "speech" : """SOMMAIRE

Constitution du bureau provisoire.

Excuses. — Demande de congé.

Communication par M. le président de deux lettres par lesquelles MM. Lou;s Legrand et Drumel déclinent toute candidature aux fonctions de secrétaire.

Tirage au sort des bureaux.

Fixation de l'ordre du jour : MM. Georges Perin, de Colbert-Laplace, Guichard, Janvier de La Motte (Eure). — Demande de renvoi au 20 janvier de la prochaine séance : M. Laroche-Joubert. Adoption.

PRÉSIDBNCE DE M. DESSEAUX, DOYEN D'AGE La séance est ouverte à deux heures un quart.

M. le président. Aux termes de l'article 1er de la loi constitutionnelle du 16 juillet 1875, je déclare ouverte la session ordinaire de la Chambre des députés pour 1881.

J'invite lts six membres les plus jeunes de ''Assemblée à vouloir bien répondre à 'l'appel de leur nom pour prendre place au bureau en qualité de secrétaires provisoires.

(L'appel des noms des députés les plus jeunes est fait par un huissier.)

Sont successivement appelés : MM. Georges de Cassagnac, né le 17 févrièr 1855; Adrien Bastii, né Je 1er octobre 1853; Jules André, né le 23 août 1852 ; René Gautier, né le '25 avril 1852 ; Emile Réaux, né le 20 juin 1851 ; Le Provost de Launay fils, né le 8 juin 1850; René Eschasseriaux, né le 1. 1 mai 1850; Louis Janvier de La Motte, né le 23 août 1849; Lanauve, né le 24 mai 1849; Dreyfus, né le 5 mai 1849 ; Marcellin Pellet, né le 4 mars 1849 ; De Loqueyssip, né le 1er octobre 1848; Le comte de Breteuil, né le 17 septembre 1848; Roy de Loulay, né le 8 août 1848; D3 La Porte, né le 20 juin 1848 ; Thomson, né le 21 janvier 1848.

MM Georges de Cassagnac, Adrien Bstid, limile Réaux, Dreyfus, de Loqueyssie et Thomson répondent à l'appel de leurs noms et prennent placn au bureau.

M. le président. Le bureau probatoire est constitué.

MM. Fourot, de Douville-Maillefeu et Laisant s'excusent de ne pouvoir assister à la séance de ce jour.

M. Laumond demande un congé de vingt jours.

La demande sera renvoyéa à la commission des congés.

J'ai reçu de M. Louis Legrand la lettre suivante, dont je donne connaissance à la Chambré : « Valenciennes, 9 janvier 1881.

c Monsieur le président, « Je vous prie de vouloir bien annoncer à mes collègues que je ne me représente pas à leurs suffrages pour les fonctions de secrétaile.

« je saisis cette occasion pour remercier la Chambre de l'honneur qu'elle m'a fait en me choisissant comme l'un des membres de son bureau.

« Agréez, monsieur je président, i assurance de ma haute considération.

c Lotis LEGRAND, « Député du Nord. »

J'ai reçu également de M. Drumel la lettre suivante:

« Neuvizy (Ardennes', 10 janvier 1881.

c Monsieur le président, « Depuis deux ans, 1* Chambre m'a fait l'honneur de m'appeler à siéger, comme secrétaire, dans son bureau. Je lui en suis profondément reconnaissant; et, en la priant de charger un autre de ses membres des fonctions que je tenais de sa confiance, je lui exprime ma vive gratitude pour les témoignages d'estime et de sympathie qu'à différentes reprises elle a bien voulu me donner.

c Veuillez croire, monsieur le président, à mes sentiments respectueux et dévoués.

« DRUMEL. »

M. le président. L'ordre du jour appelle le tirage au sort des bureaux.

Il va y être procédé.

(Il est procédé au tirage au sort des bureaux dans les formes réglementaires.) M. le président. Messieurs, il y aurait lieu de procéder maintenant à la fixation de l'ordre du jour, mais je crois devoir faire remarquer à la Chambre qu'elle n'est pas en très-grand nombre. (81! si! à droite, — Non!

non ! sur un grand nombre de bancs à gauche.) M. Clémenceau. Il n'est pas nécessaire que la Chambre soit en très-grand nombre, il suffit qu'elle soit en nombre.

M. le président. Je n'ai pas dit que U Chambre n'était pas en nombre, j'ai dit qu'elld n'était pas en très-grand nombre.

M. Haentjens. "Etm n'a jamais été aussi nombreuse à une première séance !

M. le président. La date de l'ouverture dela session, qui est fixée par la loi constitutionnelle, se place cette année entre les deux scrutins relatifs aux élections municipales.

A droite. Qu'est-ce que cela fait?

M. le président beaucoup de nos collègues som encore retenus dans leurs d^oL^rtements.

A droite. Mais non ! mais non !

M. Laroche Joubert Il ne fallait pas nous convoquer alors ! (Interruptions diverses à droite et sur plusieurs bancs à gauche.) M. de Baudry-d'Asson. N.Jus sommes revenus exprès pour procéder à la nomination du bureau ; nous demandons que le bureau soit nommé aujourd'hui!M. le président. Il a paru à beaucoup d'entre vous que l'élection du bureau définitif doit se faire par le plus grand nombre possible de membres. (Interruptions à dro te et sur quelques bancs à gauche.) Je soumets donc à la Chambre la proposi.

tion de s'ajourner. (Bruyantes exclamations à droite.) Sur divers bancs à droite el à l'extrême oauchu. Non 1 non l Sur un grand nombre d'autres bancs. Mais si 1 c'est nécessaire 1 M. Georges Perin. Je demande la parole.

M. Laroche-Joubert. Je demande la pa.

role.

M le comte de Colbert-Laplace. Je demande la parole.

M. le président. La parole est à M.

Perin.

M. Georges Perin. Messieurs, je viens, au nom d'un certain nombre de mes amis et en mon nom personnel, demander à la Chambre de repousser la proposition d'ajournement qui vient d'être faLe pac noire honorable président. (Très bien ! très bien ! à droite et à l'extrême gauche.) Autant qu'il m'a été permis de l'entendre au milieu du bruit, je crois que la seule raison que notre honorable président ait fait valoir 7our justifier sa proposition, c'est que nous n enous pas en nombre.""",
            "id" : "3rd_republic_0",
            "url" : "http://gallica.bnf.fr/ark:/12148/bpt6k64418203",
            "url_html": None
        }],
        'n_documents': 5
    },
    {
        'name': 'parliament-germany-new',
        'docs': [
        {
            'country': 'Germany',
            'chamber': 'Bundestag',
            'date': '1949-09-22',
            'debate_id': '7',
            'speaker': 'Gebhard Seelos',
            'speaker_id': '11002141',
            'speaker_aristocracy': None,
            'speaker_academic_title': 'Dr.',
            'speaker_birth_country': 'Deutschland',
            'speaker_birthplace': 'München',
            'speaker_birth_year': 1901,
            'speaker_death_year': 1984,
            'speaker_gender': 'male',
            'speaker_profession': 'Dipl.-Volkswirt, Jurist, Diplomat, Staatsrat a. D.',
            'role': 'Member of Parliament',
            'role_long': None,
            'party': 'BP',
            'party_full': 'Bayernpartei',
            'party_id': '2',
            'speech': 'Baracken sind etwas Vorübergehendes; sie halten aber immer länger, als eigentlich geplant.',
            'id': '94',
            'url': 'https://dip21.bundestag.de/dip21/btp/01/01007.pdf',
            'sequence': '94'
        }],
        'n_documents': 2
    },
    {
        'name': 'parliament-germany-old',
        'docs': [
        {
            'country': 'Germany',
            'book_id': 'bsb00000436',
            'book_label': '1867/70,1 ( Protokolle mit Sach- und Sprechregister )',
            'era': 'Reichstag (Norddeutscher Bund/Zollparlamente) 1867 - 1895 Norddeutscher Bund',
            'date': '1867-02-25',
            'date_is_estimate': 'true',
            'page': '27',
            'url': 'https://api.digitale-sammlungen.de/iiif/image/v2/bsb00000436_00027/full/full/0/default.jpg',
            'speech': "Nach vorangegangenem Gottesdienste in der Königlichen Schloßcapelle und der St. Hedwigskirche versammelten sich Heute- Nachmittags 11 Uhr die durch Allerhöchstes Patent vom 13. d. M. einberufenen Mitglieder des Reichstages des Norddeutschen Bundes im Weißen Saale des Königlichen Schlosses. Bald daraus traten die Reichstags-Commifsarien ein. Nachdem dieselben links vom Throne sich ausgestellt und die Versammlung sich -geordnet hatte, machte der Vorsitzende der Reichstags-Commissarien, Gras von Bismarck, Seiner Majestät dem Könige davon Meldung. Allerhöchst dieselben begaben Sich daraus in Begleitung Ihrer Königlichen Hoheiten des Kronprinzen und der Prinzen des Königlichen Hauses in dem nach dem Programm geordneten Zuge, unter 'Vortragung der Reichs-Insignien, nach dem Weißen Saale und nahmen, mit einem lebhaften dreimaligen Hoch, welches der Wirkliche Geheime Rath von Frankenberg ausbrachte, von der Versammlung empfangen, auf dem Throne Platz, während Seine Königliche Hoheit der Kronprinz guf der mittleren Stufe desselben, Ihre Königlichen Hoheiten die Prinzen des Königlichen Hauses zur Rechten des Thrones sich aufstellten. Seine Majestät der König verlasen hierauf, das Haupt mit dem Helme bedeckt, die nachfolgende Rede:",
            'id': '0',
        }],
        'n_documents': 1
    },
    {
        'name': 'parliament-netherlands',
        'docs': [
            {
                'country': 'Netherlands',
                'date': '2000-01-18',
                'chamber': 'Eerste Kamer',
                'debate_title': 'Presentie en opening (dinsdag 18 januari 2000)',
                'debate_id': 'nl.proc.ob.d.h-ek-19992000-493-493',
                'topic': 'Presentie en opening',
                'speech': '\n'.join([
                    'Ik deel aan de Kamer mede, dat zijn ingekomen berichten van verhindering van de leden:',
                    'Kohnstamm, wegens ziekte;',
                    'Boorsma, wegens verblijf buitenslands.',
                ]),
                'id': 'nl.proc.ob.d.h-ek-19992000-493-493.1.5.1',
                'source_archive': 'PoliticalMashup',
                'speaker': 'De voorzitter Jurgens',
                'speaker_id': 'nl.m.01992',
                'speaker_gender': None,
                'role': 'Chair',
                'party': None,
                'party_id': None,
                'party_full': None,
                'page': '493',
                'url': 'https://zoek.officielebekendmakingen.nl/h-ek-19992000-493-493.pdf',
                'sequence': 1,
            }
        ],
        'n_documents': 4,
        'end': datetime(2015, 1, 1),
    },
    {
        'name': 'parliament-netherlands',
        'docs': [
            {
                'country': 'Netherlands',
                'date': '2017-01-31',
                'chamber': 'Tweede Kamer',
                'debate_title': 'Report of the meeting of the Dutch Lower House, Meeting 46, Session 23 (2017-01-31)',
                'debate_id': 'ParlaMint-NL_2017-01-31-tweedekamer-23',
                'topic': 'Rapport "Welvaart in kaart"',
                'speech': 'Ik heet de minister van Economische Zaken van harte welkom.',
                'id': 'ParlaMint-NL_2017-01-31-tweedekamer-23.u1',
                'speaker': 'Khadija Arib',
                'speaker_id': '#KhadijaArib',
                'speaker_gender': 'vrouw',
                'role': 'Chair',
                'party': 'PvdA',
                'party_id': '#party.PvdA',
                'party_full': 'Partij van de Arbeid',
                'page': None,
                'url': None,
                'sequence': 1,
            }
        ],
        'n_documents': 98,
        'start': datetime(2015, 1, 1),
    },
    {
        'name': 'parliament-uk',
        'docs': [
        {
            'country': 'United Kingdom',
            'date': '1872-02-06',
            'chamber': 'House of Commons',
            'debate_title': 'New Writs During The Recess',
            'debate_id': None,
            'speech': "acquainted the House, —that he had issued Warrants for New Writs, for Truro, v. Hon. John Cranch Walker Vivian, Under Secretary to the Eight hon. Edward Cardwell; for Plymouth, Sir Robert Porrett Collier, knight, one of the Justices of the Court of Common Pleas; Dover, George Jessel, esquire, Solicitor General; York County (West Riding, Northern Division), Sir Francis Crossley, baronet, deceased; Limerick City, Francis William Russell, esquire, deceased; Galway County, Eight hon. William Henry Gregory, Governor and Commander in Chief of the Island of Ceylon and its dependencies; Kerry, Eight hon. Valentine Augustus Browne, commonly called Viscount Castlerosse, now Earl of Kenmare.",
            'id': 'guldi_c19_365565',
            'speaker': 'Mr. Speaker',
            'speaker_id': None,
            'speech_type': None,
            'topic': None,
            'subtopic': None,
            'sequence': '365565'
        },
        {
            'country': 'United Kingdom',
            'date': '2020-01-14',
            'chamber': 'House of Commons',
            'debate_title': 'House Of Commons Debate On 14/01/2020',
            'debate_id': 'debates2020-01-14c',
            'speech': "What steps his Department is taking to ensure that legal aid is accessible to people who need it.",
            'id': 'uk.org.publicwhip/debate/2020-01-14c.865.4',
            'speaker': 'Sarah Dines',
            'speaker_id': 'uk.org.publicwhip/person/25877',
            'speech_type': 'Start Question',
            'topic': 'The Secretary of State was asked—',
            'subtopic': 'Legal Aid Access',
            'sequence': '0'
        }],
        'n_documents': 2
    },
    {
        'name': 'parliament-sweden',
        'docs': [
            {
                'date': '2021-09-14',
                'date_is_estimate': None,
                'chamber': 'Riksdag',
                'country': 'Sweden',
                'speech': 'Ärade ledamöter! Varmt välkomna tillbaka till riksdagen! Det känns stort att få välkomna er här på tröskeln till det fjärde riksmötet den här mandatperioden. Vi har ännu ett mycket speciellt arbetsår bakom oss, till stor del präglat av pandemin. Även om vi visste att det inte var helt över för ett år sedan tror jag att vi var många som hoppades att en tydligare vändning var på väg. Så blev det inte. I stället fick vi ytterligare ett riksdagsår med ett reducerat antal ledamöter vid voteringar och utskottsarbete till stor del på distans. Men förhoppningsvis börjar vi nu gå tillbaka mot mer normala arbetsformer. Ett tydligt tecken på detta är att alla 349 ledamöter kommer att vara med vid riksmötets öppnande i eftermiddag. Jag tycker att det är angeläget att riksdagens och regeringens alla ledamöter kan vara på plats vid denna högtidliga och viktiga ceremoni, särskilt som detta är det sista öppnandet under den här mandatperioden. Däremot genomförs inget upprop nu på förmiddagen, och vi vidtar den försiktighetsåtgärden att drygt en tredjedel av ledamöterna och statsråden får sitta på läktaren under ceremonin. Formerna beslutades av mig efter diskussion med gruppledarna och de vice talmännen redan i början av augusti, alltså långt innan det blev bestämt att alla ledamöter får delta i voteringar efter riksmötets öppnande. Jag såg inget skäl att med kort varsel börja ändra i planeringen för riksmötets öppnande, så just denna speciella dag får inte alla ledamöter sitta nere på golvet här i kammaren . M en från och med riksmötets första votering sitter var och en på sin plats och röstar igen på vanligt sätt. Även om pandemin inte är över är situationen i Sverige ändå en helt annan nu än för ett år sedan. Därför har vi – talmanspresidiet och gruppledarna – gjort bedömningen att det är möjligt att samla fler personer än förra året men ändå långt färre än ett vanligt år. Vi har försökt finna en så god balans som möjligt mellan nödvändiga säkerhetsåtgärder, riksdagsordningens bestämmelser och respekt för traditionen. Den sedvanliga mottagningen i Sammanbindningsbanan är som bekant inställd, och det genomförs heller inte någon konsert i Konserthuset. Jag är glad över att vi också kommer att få hjälp att minnas dessa föregångare och förebilder genom att de får en permanent plats på Riksplan i form av en staty. Här tillkommer det att det i trapphallen i Östra riksdagshuset kommer att invigas en tavla som föreställer de här fem pionjärerna. Statyn dröjer ett tag – den kommer att invigas nästa år – men redan i kväll vill riksdagen på dagen för riksmötets öppnande, denna demokratins högtidsdag, uppmärksamma demokratijubileet med att lysa upp Stockholmsnatten med ett ljusspel. Jag kommer att tända en fasadbelysning på Östra riksdagshuset vid en webbsänd ceremoni klockan 20. Ljusspelet kan sedan ses varje kväll till och med den 20 september. Men demokratifirandet tar inte slut där. Vad passar väl bättre på FN:s demokratidag den 15 september än att fira med ett seminarium? I morgon anordnar riksdag och regering seminariet 100 år av demokrati – vilka lärdomar tar vi med oss? Se det gärna på riksdagen.se! Efter riksmötets öppnande tror jag att vi alla ser fram emot ett nytt arbetsår i riksdagen under något mer normala former. Jag har ju, som ni alla vet, tillsammans med gruppledarna slutit en ny överenskommelse om arbetsformerna under hösten, och gruppledarna har också beslutat att inte förlänga överenskommelsen om 55 närvarande ledamöter vid voteringar. Alla ledamöter kan alltså delta vid voteringarna, men vi behåller möjligheten att delta på distans vid utskottens sammanträden. Varje utskott avgör när det är motiverat att hålla fysiska sammanträden, och när man deltar fysiskt planerar vi för att det ska gå att hålla avstånd. Vi ska däremot fortsätta hjälpas åt att hålla antalet externa besök i riksdagens hus nere. Externa åhörare vid olika arrangemang bör undvikas liksom guidade visningar och mingelsituationer. Pandemin är inte över. Vi fortsätter att anpassa verksamheten när och om det behövs, men förhoppningsvis går vi mot ett mer normalt läge. Ärade ledamöter! Det här har varit en mandatperiod som ingen annan. Jag tror inte att någon hade kunnat förutse de många olika, oväntade och delvis dramatiska händelser som har inträffat. Jag tänker naturligtvis i första hand på pandemin och alla dess konsekvenser men även på de två regeringsbildningarna. Och då är det ändå ett helt år kvar av mandatperio ­ den. Jag tror att vi alla kan se fram emot ännu ett händelserikt och spännan ­ de riksdagsår fram till valet. Vi vet i alla fall att det i början av november blir den tredje regeringsbildningen under den här mandatperioden. Oavsett hur man ser på det politiska läget vill jag framhålla, apropå just demokratijubileet, att regeringsbildningarna inte har inneburit någon kris för demokratin. Svensk demokrati står stark, och den är värd att fira. Alla aktörer har i regeringsbildningsprocesserna använt de olika verktyg som finns i den demokratiska, parlamentariska verktygslådan. Misstroendeomröstning, beslut att inte utlysa extraval och talmansrundor – allt sådant följer av de lagar som vi har skapat för vår demokrati. Skeendet må vara turbulent i vissa stycken, men det följer demokratins spelregler. Ärade ledamöter! Jag vill avsluta med några rader ut dikten Sommaren i Sverige av Werner Aspenström. Den skildrar på ett fint sätt vemodet och skönheten när sommaren går mot sitt slut. Då landar på min hand den förgänglighetens tanke som vi kallar trollslända. Ett gult löv lösgör sig och faller klingande mot marken. Sommaren måste hastigt bärgas. … Ty hösten närmar sig med toppeld i asparna. Låt mig nu önska er en fin höst och ett produktivt arbetsår. På återseende här i kammaren klockan 14! Stockholms kommun Stockholms län Södermanlands län Jönköpings län Kronobergs län Blekinge län Hallands län Göteborgs kommun Värmlands län Jämtlands län Norrbottens län EU-dokument Åttaveckorsfristen för att avge ett motiverat yttrande skulle gå ut den 5 november . EU-dokument Följande frågor för skriftliga svar hade framställts: 2020/21:3636 Amorteringskravet och ojämställd bostadsmarknad 2020/21:3637 Den kinesiske ambassadörens agerande 2020/21:3638 Vaccin 2020/21:3639 Lukasjenkos tillgång till 1 miljard dollar från IMF 2020/21:3640 Markering mot Irans idrottsminister 2020/21:3642 Kriminalitet på bostadsmarknaden Skriftliga svar på följande frågor hade kommit in: 2020/21:3535 Barns rätt till säkerställda skyddade boenden 2020/21:3537 Elbrist som hotar investeringar i Sverige 2020/21:3538 Åtgärder för att trygga boende',
                'sequence': '0',
                'id': 'i-2a00eff84ce04676-0',
                'speaker': 'Andreas Norlén',
                'speaker_gender': 'man',
                'role': 'Sveriges riksdags talman',
                'ministerial_role': None,
                'party': None,
                'speaker_birth_year': 1973,
                'speaker_death_year': None,
                'speaker_constituency': None,
                'speaker_id': 'Q4755577'
            },
        ],
        'n_documents': 5,
    },
    {
        'name': 'parliament-sweden-old',
        'docs': [{}] * 5 + [
            {
                'book_id': 'bn_1828-30_1__01',
                'book_label': 'Hederwärda bonde-ståndets protokoller wid lagtima riksdagen i Stockholm åren 1828 och 1829. Första bandet.',
                'country': 'Sweden',
                'era': 'Ståndsriksdagen',
                'chamber': 'Bönder',
                'date_earliest': '1828-01-01',
                'date_latest': '1828-12-31',
                'speech': '''Hederwärdo

Bonde-Ständcts

Protokoller

wid

LagMa Riksdagen i Stockhol».

Ä«tt 1828 och I82t,

första Lander.

STOCKHOLM,

Kongl. Ordens-Böktryckeriet, I8Z9.''',
                'page': '0',
                'sequence': 1,
                'url': 'https://weburn.kb.se/riks/ståndsriksdagen/pdf/bn_1828-30_1_/bn_1828-30_1__01.pdf',
                'url_xml': 'https://weburn.kb.se/riks/ståndsriksdagen/xml/bn_1828-30_1_/bn_1828-30_1__01.xml',
            }
        ],
        'n_documents': 10
    },
        {
        'name': 'parliament-denmark',
        'docs': [
            {
                'speech': """6546 F. t. beslutn. vedr. udbetaling af sygedagpenge

Beslutningsforslag nr. B 142. Fremsat den 3. juni 2008 af Thomas Adelskov (S), Lennart Damsbo-Andersen (S),

Egil Andersen (SF), Margrethe Vestager (RV), Morten Østergaard (RV) og Line Barfod (EL)

Forslag til folketingsbeslutning

om ophævelse af varighedsbegrænsningen for udbetaling af sygedagpenge

Folketinget pålægger regeringen at fremsætte lovforslag, som ophæver varighedsbegrænsnin- gen for udbetaling af sygedagpenge, således at

lovforslaget kan træde i kraft den 1. januar 2009.""",
                'page': '546',
                'date_earliest': '2007-01-01',
                'date_latest': '2007-12-31',
                'book_label': 'Folketingstidende 2007/8 (2. samling) Tillæg A side 6001 - 6565',
                'book_id': '20072A6546',
                'id': '20072A6546_546',
                'chamber': 'Folketinget',
                'country': 'Denmark',
                'sequence': 546,
            }
        ],
        'n_documents': 5,
    }, {
        'name': 'parliament-denmark-new',
        'docs': [
            {
                'country': 'Denmark',
                'id': '20100128100025',
                'date': '2010-01-28',
                'speech': 'Mødet er åbnet. I dag er der følgende anmeldelser: Kirkeministeren (Birthe Rønn Hornbech): Lovforslag nr. L 115 (Forslag til lov om ændring af lov om udnævnelse af biskopper og om stiftsbåndsløsning og forskellige andre love.) og  L 116 (Forslag til lov om ændring af lov om begravelse og ligbrænding og lov om folkekirkens økonomi.) Beskæftigelsesministeren (Inger Støjberg): Lovforslag nr. L 117 (Forslag til lov om ændring af lov om sygedagpenge, lov om ret til orlov og dagpenge ved barsel, lov om aktiv socialpolitik og lov om arbejdsløshedsforsikring m.v. Transportministeren (Lars Barfoed): Lovforslag nr. L 118 (Forslag til lov om ændring af lov om taxikørsel m.v.) Videnskabsministeren (Helge Sander): Lovforslag nr. L 119 (Forslag til lov om ændring af universitetsloven.) Titler på de fremsatte forslag vil fremgå af www.folketingstidende.dk (jf. ovenfor). Mens vi får de sidste medlemmer ind i salen, kan jeg lige oplyse, at vi er vidende om, at der er problemer med, hvordan urene går på Christiansborg. Det er et lidt større problem end som så blot at justere urene, for det er hele styringssystemet – det styres af 23 V strøm – der gør, at der er problemer med overhovedet at styre urene. Nogle er slidt ned, så man skal ikke regne med tiden. Min opfordring er, at man bruger soluret og kun tæller de lyse timer. Munterhed Men det afgørende er altså, at vi er opmærksomme på det og gør, hvad vi overhovedet kan for at udskifte, hvor der skal udskiftes, og i øvrigt at få et system, så urene altid går korrekt. Jeg går nemlig ud fra, at de, der kommer for sent, her nu hvor vi skal stemme, udelukkende gør det, fordi urene går forkert.',
                'speaker': 'Thor Pedersen',
                'speaker_gender': 'Male',
                'speaker_birth_year': 1945,
                'role': 'formand',
                'party': 'Venstre',
                'topic': 'Punkt 0',
                'subject': 'other',
                'sequence': '100025',
            }
        ],
        'n_documents': 4,
    },
        {
        'name': 'parliament-norway',
        'docs': [
            {
                'speech': """KONGERIKET NORGES 149. STORTINGS FORHANDLINGER 2004 - 2005

9. del

INNEHOLDENDE REGISTER TIL FORHANDLINGER I STORTINGET OG DETS AVDELINGER

OSLO LOBO MEDIA AS 2005""",
                'page': '2',
                'book_id': 'digistorting_2004_part9_vol-a',
                'book_label': 'Stortingsforhandlinger; 2004/2005 Vol. 149 Nr. 9',
                'date_earliest': '2004-01-01',
                'date_latest': '2004-12-31',
                'sequence': '2',
                'chamber': 'Stortinget',
                'country': 'Norway',
            }
        ],
        'n_documents': 5,
    },
    {
        'name': 'parliament-norway-new',
        'docs': [
            {}, {}, {}, {
                'subject': 'Statsbudsjettet',
            }, # skip a few introductory speeches to one with more metadata
            {
                'country': 'Norway',
                'chamber': 'Stortinget',
                'date': '1998-10-20',
                'debate_title': 'Sak  nr. 2',
                'debate_type': 'interpellasjon',
                'party': 'Høyre',
                'party_id': 'H',
                'party_role': 'Opposition',
                'role': 'Representant',
                'speaker': 'Sonja Irene Sjøli',
                'speaker_id': 'SONS',
                'speaker_gender': 'kvinne',
                'speaker_birth_year': 1949,
                'speaker_death_year': None,
                'speaker_constituency': 'Akershus',
                'speech': 'Det er en bred forståelse blant fagfolk og politikere om at norsk sykehusvesen ikke bare lider under mangel på ressurser, men at det først og fremst er behov for organisatoriske og strukturelle forandringer. Offentlige utredninger om eierskap, organisering og ledelse i sykehus viser at det er behov for en rekke endringer for å nå målet om et bedre og mer tilgjengelig helsetilbud til befolkningen. Erkjennelsen av at vi har brukt gamle og lite hensiktsmessige virkemidler i helsepolitikken, har også nådd Regjeringen. Helseministeren uttalte til Dagens Næringsliv i sommer at det ville tjene pasientene hvis vi kunne være mer dristig i bruken av etterspørselsteknikker og private bidrag innenfor sykehussektoren. Denne uttalte dristighet ser jeg fram til med spenning. Stortinget har i de siste år, etter sterkt påtrykk fra Høyre, vedtatt innsatsbasert finansiering og fritt sykehusvalg. Den naturlige konsekvens av dette er at sykehusene organiserer seg annerledes enn før. Vi er langt fra alene om disse tankene. En rekke svenske fagforbund krever en ny modell for det svenske helsevesenet. Den svenske legeforening og det svenske sykepleierforbundet har gått sammen og krever at markedet i større grad må styre helsetilbudet. De mener at fylkeskommunen har utspilt sin rolle i styringen av helsesektoren og krever en total omlegging av helsevesenet. Det er mulig at Norge har sterkere økonomi og bedre skiløpere enn svenskene, men helsedebatten i Sverige har i den senere tid vært langt mer dynamisk og spennende enn hos oss. Tankene om at sykehus ikke nødvendigvis må være eid og drevet av det offentlige, vinner terreng i stadig flere land og er allerede utviklet i flere miljøer også her i Norge. Til og med Jan Grund, Norges fremste helseøkonom, professor på BI og en svoren sosialdemokrat, mener at flertallet av norske politikere befinner seg i skyttergravene i debatten om private helsetjenester. Problemet er ifølge Grund at det ikke er definert hvilke grunnleggende helsetjenester vi har krav på, og hvilke tjenester som kan tilbys oss som forbrukere og kunder. Derfor er det så vanskelig å håndtere diskusjonen om privat kontra offentlig helsetilbud. Han uttrykker sterk støtte til å få private aktører inn i det offentlige helsevesen. Stiftelsen SINTEF Unimed er utpekt av Næringsdepartementet og Helsedepartementet til å lede næringsutvikling i helsesektoren. Lederen Paul Hellandsvik mener det er på høy tid å tenke nytt og utradisjonelt om hvordan det offentlige kan dra nytte av private aktører, og at det gjelder å komme i gang med noen prøveprosjekter. Erfaringer fra Sverige og andre land viser at en modell for helsevesenet hvor det offentlige drar nytte av private aktører til utbygging og drift av sykehus, gir store økonomiske gevinster og høy kvalitet på tjenestene. Forutsetningen for modellen er at det offentlige finansierer tjenestene, og at de fordeles etter behov i befolkningen. Den svenske sosialdemokratiske helseminister velsigner dette arbeidet og mener at det frigjør ressurser til å behandle enda flere pasienter, og at det gir bedre kvalitet på tjenestene. Og det er iallfall fem gode grunner til at vi bør se nærmere på disse ideene. For det første: Avstanden mellom befolkningens etterspørsel etter helsetjenester og det helsevesenet har kapasitet til å tilby, er økende. Lange helsekøer taler sitt tydelige språk. For det andre: De ideologiske motforestillingene er gledelig nok i ferd med å avta både i Arbeiderpartiet og i det såkalte sentrum. Som helseminister Høybråten uttrykte det i Dagens Næringsliv tidligere i sommer: «Spørsmålet om å bruke etterspørselsteknikker er … ikke først og fremst en ideologisk problemstilling, men heller et spørsmål om hvor mye og på hvilken måte det er hensiktsmessig å bruke teknikken.» Stadig flere mennesker har fått erfaring med private legesentre og private klinikker. Folk har forstått at helsepersonell som jobber i det private, er like opptatt av pasientenes beste og kvaliteten på behandlingen som helsepersonell i de offentlige sykehus. Det som måtte være igjen av ideologiske begrunnelser her i Norge, har mistet sin kraft, ikke minst fordi folk ser med egne øyne at det ikke er grunn til å frykte private tilbud som et supplement – tvert imot. I tillegg har betalingsviljen for mindre omfattende behandlingstilbud økt. For det tredje: Det offentlige har gjennom mange år brukt gamle og lite hensiktsmessige virkemidler i helsepolitikken. Offentlig monopol, hierarkiske styringssystemer, spillet mellom forvaltningsnivåene og manglende fokusering på service og kvalitet i behandlingen har skapt tillitskrise i helsevesenet, og – det må jeg si – med berettigelse. Ikke minst er inntrykket av uklare roller og uklar ansvarsfordeling mellom aktørene i helsevesenet frustrerende for pasientene. For det fjerde: Den demografiske utviklingen i den vestlige verden. Vi lever lenger, og presset på helsevesenet vil øke betraktelig i årene fremover. Teknologiutviklingen er en femte faktor. Sykehusene har nå, med den rette teknologi og de moderne medisiner, mulighet til å behandle sykdommer bedre og derigjennom gi pasienter lengre levetid og bedre livskvalitet. Jeg har registrert gjennom media i sommer at helseministeren er skeptisk til å skille mellom tilbyder- og etterspørselsrollen i helsevesenet. Han frykter at for mange private sykehus vil kanalisere tjenester og arbeidskraft bort fra de offentlige sykehusene, og at det vil bli ulik tilgang til helsetjenester. Men dersom ansvaret for funksjonsfordelingen mellom sykehusene ligger hos staten gjennom godkjenning av de regionale helseplaner, vil det bestemme hva som tilbys hvor. En nasjonal helseplan, slik Høyre ønsker, ville vært et enda bedre redskap. Dersom det offentlige har ansvar for finansieringen av tjenestene til den enkelte pasient, vil det sikre lik tilgang til tjenestene. Hvis pengene kunne følge pasienten direkte til sykehusene, slik Høyre vil, og slik Kristelig Folkeparti ville i opposisjon, ville vi unngå at fylkeskommunen tar deler av bevilgningen på veien. Sykehusene får klare insentiver til å behandle flere pasienter, og vi sikrer at pasientene settes først. En modell hvor man lar det offentlige og private konkurrere om å utføre tjenestene, er også den modell som best vil sikre pasientene en sterkere posisjon i forhold til sykehusvesenet. Når de politiske prioriteringer i helsesektoren, funksjonsfordelingen mellom sykehusene, kontrollsystemer og den offentlige finansieringen er på plass, blir det etter Høyres syn mindre viktig hvem som eier og driver sykehusene. Unntaket er universitets- og regionsykehusene, som etter Høyres oppfatning er i en spesiell situasjon. Private kan godt eie og ha driftsansvar for bygningene. Men selve sykehusdriften må være i offentlig regi, slik at man har en tilfredsstillende og god kontroll med universitetsfunksjonene. Vi er inne i en tid med stadig større ubalanse mellom tilbud og etterspørsel. Derfor må vi forholde oss til virkeligheten. Det er snart ingen grenser for hvilke tjenester helsevesenet skal utføre. I denne situasjonen må vi styre slik at vi får mest mulig ut av ressursene. Det offentlige må konsentrere seg om å sikre de grunnleggende helsetjenestene og lage spilleregler for de private aktørene. De bør også få en mulighet til å utføre oppgaver det offentlige definerer som «grunnleggende helsetjenester», slik man gjør i Sverige. Men det må, som jeg har sagt tidligere, være en forutsetning at det offentlige skal betale tjenestene, og at kontrollmekanismene er gode, slik at tjenestene holder kvalitetsmessige mål. Det viktigste er likevel at vi gir sykehusene frihet i forhold til det tungrodde politiske system, slik at det blir mulig å lede sykehusene mer profesjonelt og prøve ut ulike selskapsformer, slik en nå ser ut til å få politisk flertall for her i Oslo. Som politikere bør vi heller være opptatt av å fristille de offentlige sykehusene enn å begrense de private. Et samarbeid mellom det offentlige og det private helsevesen har vi tro på. Etter Høyres mening gjelder det å få i gang noen prøveprosjekter, for uten det tror jeg ikke vi kommer videre. Hvordan ser helseministeren på dette, og vil han ta initiativ og stimulere til et slikt samarbeid?',
                'topic': 'om en modell for helsevesenet hvor det offentlige drar nytte av _private aktører til utbygging og drift av sykehus_',
                'sequence': '4',
                'id': 'tale000004',
                'ministerial_role': None,
                'legislature': 'Bondevik I',
                'subject': None,
                'language': 'Norwegian (Bokmål)',
                'debate_id': 'Saker-og-publikasjoner/Publikasjoner/Referater/Stortinget/1998-1999/981020/2/'
            },
            {}, {},
            {
                # test special case of ministers answering questions
                'ministerial_role': 'helseministeren',
                'speaker': 'Presidenten',
                'speaker_id': 'DH',
                'party': None,
                'party_role': None,
                'speech': "Representanten Sjøli nevnte et forslag. Betyr det at hun tar opp dette forslaget?"
            }
        ],
        'n_documents': 10,
    },
    {
        'name': 'parliament-finland',
        'docs': [
            {
                'country': 'Finland',
                'speech': 'Täysistunto alkaa. Toivotan kaikki tervetulleiksi tänne Sibelius-taloon Sibeliuksen juhlavuotena aloittamaan vastuullista työtämme isänmaan hyväksi. Iältäni vanhimpana eduskunnan jäsenenä johdan puhetta tässä valtiopäivien ensimmäisessä täysistunnossa, kunnes eduskunta on työjärjestyksen 4 §:n mukaan valinnut puhemiehen ja kaksi varapuhemiestä ja nämä ovat antaneet eduskunnalle juhlallisen vakuutuksen. Plenum börjar. Som den riksdagsledamot som är äldst till åren är det min uppgift att föra ordet vid första plenum under riksmötet till dess att riksdagen enligt 4 § i riksdagens arbets-ordning inom sig valt talman och två vice talmän och dessa har avgett högtidlig försäkran inför riksdagen.',
                'speaker_id': 'Pertti_Salolainen',
                'speaker': 'Pertti Salolainen',
                'role': 'Ikäpuhemies',
                'party_id': '#party.KOK',
                'party': 'KOK',
                'party_role': 'Hallituspuolue',
                'speaker_gender': 'Male',
                'speaker_birth_year': 1940,
                'speech_type': 'PuhemiesPuheenvuoro',
                'id': '2015_1_1',
                'url': 'https://www.eduskunta.fi/FI/vaski/PoytakirjaAsiakohta/Sivut/PTK_1+2015+1.aspx',
                'sequence': '1',
                'topic': 'Nimenhuuto',
                'debate_id': 'ptk_1_2015',
                'debate_title': 'PTK 1/2015',
                'date': '2015-04-28',
            },
        ],
        'n_documents': 22,
    },
    {
        'name': 'parliament-finland-old',
        'docs': [
            {
                'country': 'Finland',
                'speech': """FÖUDT HOS

FINLANDS RIDDERSKAP OCR ADEL

VID

LANDTDAGEN ÅR 1877.

TREDJE HÄFTET.

Från den 1 till den 31 Oktober.

FINSKA LITTERATUR-SÄLLBKAPETS TRYCKERl,

1878.""",
                'id': 'Adeln_Prot_1877_III.pdf_0',
                'speech_type': 'minutes',
                'chamber': 'nobility',
                'date_earliest': '1877-01-01',
                'date_latest': '1877-12-31',
                'page': '0',
                'language': 'swe',
                'source_archive': 'Adeln_Prot_1877_III.pdf'
            },
        ],
        'n_documents': 4,
    },
    {
        'name': 'parliament-ireland',
        'end': datetime(1999, 12, 31),
        'docs': [
            {
                'country': 'Ireland',
                'id': '1',
                'date': '1919-01-21',
                'speaker': 'Count George Noble, Count Plunkett',
                'speaker_id': '977',
                'speaker_constituency': 'Roscommon North',
                'party': 'Sinn Féin',
                'party_id': '22',
                'speech': 'Molaimse don Dáil Cathal Brugha, an Teachta ó Dhéisibh Phortláirge do bheith mar Cheann Comhairle againn indiu.',
                'topic': '1. CEANN COMHAIRLE I gCOIR AN LAE.',
                'chamber': 'Dáil',
                'sequence': 1,
                'source_archive': '1919-2013',
                'url': None,
                'ministerial_role': None,
                'role': None,
                'debate_type': None,
                'committee': None,
            },
        ],
        'n_documents': 5,
    },
    {
        'name': 'parliament-ireland',
        'start': datetime(2000, 1, 1),
        'end': datetime(2013, 12, 31),
        'docs': [
            {
                'country': 'Ireland',
                'id': '3088872',
                'date': '2000-01-26',
                'speaker': 'Mr. Ruairí Quinn',
                'speaker_id': '985',
                'speaker_constituency': 'Dublin South-East',
                'party': 'The Labour Party',
                'party_id': '14',
                'speech': 'asked the Taoiseach if he will make a statement on his visit to South Africa and Lesotho.',
                'topic': 'Ceisteanna &ndash Questions. - Official Engagements.',
                'chamber': 'Dáil',
                'sequence': 3088872,
                'source_archive': '1919-2013',
                'url': None,
                'ministerial_role': None,
                'role': None,
                'debate_type': None,
                'committee': None,
            },
        ] +
        [ {} ] * 13 + # skip ahead to the first speech from a minister
        [
            {
                'id': '3088886',
                'speaker_id': '5',
                'speaker': 'Mr. Bertie Ahern',
                'ministerial_role': 'Taoiseach, Minister for Foreign Affairs',
            }
        ]
        ,
        'n_documents': 15,
    },
    {
        'name': 'parliament-ireland',
        'start': datetime(2014, 1, 1),
        'docs': [
            {
                'country': 'Ireland',
                'sequence': 1,
                'speaker_id': '#AndrewDoyle',
                'date': '2014-12-09',
                'topic': 'Vote 30 - Agriculture, Food and the Marine (Supplementary)',
                'speaker': 'Andrew Doyle',
                'chamber': 'Dáil',
                'url': 'https://data.oireachtas.ie/akn/ie/debateRecord/select_committee_on_agriculture_food_and_the_marine/2014-12-09/debate/mul@/main.xml',
                'source_archive': '2014-2020',
                'party': None,
                'party_id': None,
                'speaker_constituency': None,
                'role': 'Chair',
                'ministerial_role': None,
                'debate_type': 'committee',
                'committee': 'Select Committee on Agriculture, Food and the Marine',
                'id': 'debateRecord#select_committee_on_agriculture_food_and_the_marine#2014-12-09#debate#main#spk_1',
                'speech': '''As we have a quorum, we will commence in public session.  All mobile phones should be switched off because they cause interference.  I have apologies from Deputies Michael McNamara and Martin Heydon.  This meeting has been convened to consider a Supplementary Estimate on Vote 30 - Agriculture, Food and the Marine, which was referred by the Dáil to the committee on 3 December with an instruction to report back to the Dáil not later than 11 December.
I welcome the Minister, Deputy Simon Coveney, and his officials.  I thank them for the briefing material provided, which has been circulated to the members of the committee.  I invite the Minister to make his opening statement.'''
            }, {
                'speaker_id': '#SimonCoveney',
                'speaker': 'Simon Coveney',
                'role': None,
                'ministerial_role': 'Minister for Agriculture, Food and the Marine',
            }
        ],
        'n_documents': 25,
    },
    {
        'name': 'parliament-euparl',
        'start': datetime(1999, 7, 20),
        'docs': [{
            'id': '1999-07-20-Speech-2-001',
            'date': '1999-07-20',
            'speaker': 'President',
            'party': None,
            'speech': "I declare resumed the session of the European Parliament adjourned on 7 May 1999, and I declare open the sitting provided for in Article 10(3) of the Act concerning the election of the representatives to the European Parliament by direct universal suffrage and Rule 10(3) of the Parliament\"s Rules of Procedure.\nBefore the start of the proceedings, Mr Crowley asked to take the floor.",
            'source_language': None,
            'url': 'http://purl.org/linkedpolitics/eu/plenary/1999-07-20-Speech-2-001'
        }] +
        [{}] * 8 +  # skip ahead to speech with party & language info
        [{
            'id': '1999-07-20-Speech-2-010',
            'date': '1999-07-20',
            'speaker': 'Wurtz',
            'party': 'GUE/NGL',
            'speech': "Mr President, for the first time in ten years, we shall actually be voting for the President of the European Parliament without any of those prior agreements between social-democratic and socialist groups which always seemed to represent, to my mind, a kind of condominium, stifling democratic debate. Today, more by chance than political will on the part of the two principal groups, we have a Left and Right at loggerheads with one another. The Confederal Group of the European United Left...",
            'source_language': 'FR',
            'url': 'http://purl.org/linkedpolitics/eu/plenary/1999-07-20-Speech-2-010'
        }],
        'n_documents': 10
    }
]

def corpus_test_name(corpus_spec):
    return corpus_spec['name']

@pytest.mark.parametrize("corpus_object", CORPUS_TEST_DATA, ids=corpus_test_name)
def test_imports(parliament_corpora_settings, corpus_object):
    corpus = load_corpus_definition(corpus_object.get('name'))
    assert len(os.listdir(os.path.abspath(corpus.data_directory))) != 0

    start = corpus_object['start'] if 'start' in corpus_object else corpus.min_date
    end = corpus_object['end'] if 'end' in corpus_object else corpus.max_date

    tested_fields = set()
    resulted_fields = set()

    docs = get_documents(corpus, start, end)
    for target in corpus_object.get('docs'):
        doc = next(docs)
        for key in target:
            tested_fields.add(key)
            assert key in doc
            assert doc[key] == target[key]

        for key in doc:
            resulted_fields.add(key)

    for key in resulted_fields:
        if not key in tested_fields:
            message = 'Key "{}" is included in the result for {} but has no specification'.format(key, corpus_object.get('name'))
            warnings.warn(message)

    docs = get_documents(corpus, start, end)
    assert len(list(docs)) == corpus_object.get('n_documents')

def get_documents(corpus, start, end):
    sources = corpus.sources(
        start=start,
        end=end
    )
    return corpus.documents(sources)
