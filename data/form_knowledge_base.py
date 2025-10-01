"""
COMPLETE Form Knowledge Base for German Jobcenter Forms
ALL sections and ALL fields documented
"""

FORM_SCHEMAS = {
    "HA": {
        "name": "Hauptantrag Bürgergeld",
        "code": "HA",
        "purpose": "First-time application for Bürgergeld benefits",
        "total_pages": 8,
        "total_fields": 87,
        "sections": {
            "A": {
                "name": "Persönliche Daten der antragstellenden Person",
                "fields": {
                    "1": {
                        "label": "Vorname",
                        "description": "Your first/given name",
                        "required": True,
                        "tips": ["Use official name from ID", "Include all first names if on passport"],
                        "example": "Max Martin"
                    },
                    "2": {
                        "label": "Nachname",
                        "description": "Your last/family name",
                        "required": True,
                        "tips": ["Must match passport/ID exactly", "Use current legal name"],
                        "example": "Müller"
                    },
                    "3": {
                        "label": "Geburtsdatum",
                        "description": "Your date of birth",
                        "format": "DD.MM.YYYY",
                        "required": True,
                        "example": "15.03.1985",
                        "tips": ["Use German format DD.MM.YYYY", "Use dots, not slashes"],
                        "mistakes": ["Using MM.DD.YYYY", "Using YYYY-MM-DD"]
                    },
                    "4": {
                        "label": "Geburtsname/früherer Name",
                        "description": "Birth name or former name if changed",
                        "required": False,
                        "tips": [
                            "Maiden name for married women",
                            "Previous name if legally changed",
                            "Leave blank if never changed"
                        ]
                    },
                    "5": {
                        "label": "Geburtsort",
                        "description": "City/town where you were born",
                        "required": True,
                        "tips": ["City name only, not hospital", "Use German spelling if available"],
                        "example": "München"
                    },
                    "6": {
                        "label": "Geburtsland",
                        "description": "Country where you were born",
                        "required": True,
                        "tips": ["Use German country name", "Deutschland, Polen, Türkei, etc."],
                        "example": "Deutschland"
                    },
                    "7": {
                        "label": "Staatsangehörigkeit",
                        "description": "Your citizenship/nationality",
                        "required": True,
                        "tips": [
                            "Write in German: deutsch, polnisch, türkisch",
                            "If dual citizenship, list both",
                            "Separate with comma if multiple"
                        ],
                        "example": "deutsch"
                    },
                    "8": {
                        "label": "Geschlecht",
                        "description": "Your gender",
                        "required": True,
                        "options": ["männlich", "weiblich", "divers", "keine Angabe"],
                        "tips": ["keine Angabe = prefer not to say", "No disadvantage for any choice"]
                    },
                    "9": {
                        "label": "Straße",
                        "description": "Street name of your residence",
                        "required": True,
                        "tips": ["Just street name, no house number here"],
                        "example": "Hauptstraße"
                    },
                    "10": {
                        "label": "Hausnummer",
                        "description": "House/building number",
                        "required": True,
                        "tips": ["Include letter if applicable", "Include 'a', 'b' suffixes"],
                        "example": "45a"
                    },
                    "11": {
                        "label": "Postleitzahl",
                        "description": "Postal code (ZIP code)",
                        "required": True,
                        "format": "5 digits",
                        "tips": ["German postal codes are 5 digits", "No spaces"],
                        "example": "80331"
                    },
                    "12": {
                        "label": "Wohnort",
                        "description": "City/town where you live",
                        "required": True,
                        "tips": ["Official city name", "Use German spelling"],
                        "example": "München"
                    },
                    "13": {
                        "label": "Postfachanschrift",
                        "description": "PO Box address (if applicable)",
                        "required": False,
                        "tips": ["Only if you use a PO Box", "Leave blank if normal address"]
                    },
                    "14": {
                        "label": "Telefon",
                        "description": "Phone number for contact",
                        "required": False,
                        "tips": [
                            "OPTIONAL - but helps processing",
                            "Mobile or landline acceptable",
                            "Include country code if calling from abroad"
                        ],
                        "format": "0176 12345678 or +49 176 12345678"
                    },
                    "15": {
                        "label": "Gegebenenfalls wohnhaft bei",
                        "description": "Living at (if staying with someone)",
                        "required": False,
                        "tips": [
                            "Fill if staying with friend/family temporarily",
                            "Include name and full address",
                            "Leave blank if own address"
                        ]
                    },
                    "16": {
                        "label": "Kontoinhaberin/Kontoinhaber",
                        "description": "Bank account holder name",
                        "required": "conditional",
                        "tips": [
                            "Should match applicant name",
                            "If joint account, write both names",
                            "If different person, explain in separate letter"
                        ]
                    },
                    "17": {
                        "label": "IBAN",
                        "description": "International Bank Account Number",
                        "required": "conditional",
                        "format": "DE + 20 digits (total 22 characters)",
                        "example": "DE89370400440532013000",
                        "tips": [
                            "Must be exactly 22 characters",
                            "German IBANs start with DE",
                            "No spaces or dashes",
                            "Check box below if no account"
                        ],
                        "mistakes": ["Including spaces", "Using BIC instead", "Wrong number of digits"]
                    },
                    "18": {
                        "label": "Sozial-/Rentenversicherungsnummer",
                        "description": "Social insurance number",
                        "required": False,
                        "format": "12 345678 A 123",
                        "tips": [
                            "Found on pension letters",
                            "Found on health insurance card",
                            "Found on payslips",
                            "If don't have: check 'Nein' box"
                        ]
                    },
                    "19": {
                        "label": "Sozialversicherungsnummer angeben",
                        "description": "Enter your social insurance number",
                        "required": False,
                        "tips": ["Only if you checked 'Ja' in field 18"]
                    },
                    "20": {
                        "label": "Gesetzlicher Betreuer/Vormund",
                        "description": "Legal guardian or conservator",
                        "required": True,
                        "tips": [
                            "Only for people with legal guardian",
                            "Must attach Bestellungsurkunde",
                            "Most people select 'Nein'"
                        ]
                    },
                    "21": {
                        "label": "Datum der Einreise nach Deutschland",
                        "description": "Date of entry to Germany",
                        "required": "conditional",
                        "format": "DD.MM.YYYY",
                        "tips": [
                            "Only if non-German citizen",
                            "Only if previously lived abroad",
                            "Approximate date acceptable if exact unknown"
                        ]
                    },
                    "22": {
                        "label": "Gültige Aufenthaltsgenehmigung",
                        "description": "Valid residence permit",
                        "required": "conditional",
                        "tips": [
                            "Only for non-German citizens",
                            "Must attach copy of permit",
                            "Check expiration date"
                        ]
                    },
                    "23": {
                        "label": "Verpflichtungserklärung",
                        "description": "Sponsorship declaration",
                        "required": "conditional",
                        "tips": [
                            "If someone sponsored your visa",
                            "Attach copy of Verpflichtungserklärung",
                            "May affect benefit eligibility"
                        ]
                    },
                    "24": {
                        "label": "Familienstand",
                        "description": "Marital status",
                        "required": True,
                        "critical": True,
                        "options": [
                            "ledig (single/never married)",
                            "verheiratet (married)",
                            "verwitwet (widowed)",
                            "eingetragene Lebenspartnerschaft (registered partnership)",
                            "dauernd getrennt lebend (permanently separated)",
                            "geschieden (divorced)",
                            "aufgehobene Lebenspartnerschaft (dissolved partnership)"
                        ],
                        "triggers": {
                            "dauernd getrennt lebend": ["Must complete Anlage UH1"],
                            "geschieden": ["Must complete Anlage UH1"],
                            "aufgehobene Lebenspartnerschaft": ["Must complete Anlage UH1"]
                        },
                        "tips": [
                            "Separated/divorced = additional form required",
                            "Living together = married/partnership",
                            "Choose most recent status"
                        ]
                    },
                    "25": {
                        "label": "Seit wann getrennt/geschieden",
                        "description": "Date of separation/divorce",
                        "required": "conditional",
                        "format": "DD.MM.YYYY or MM.JJJJ",
                        "tips": [
                            "Only if field 24 = separated/divorced",
                            "Month and year sufficient if exact date unknown",
                            "Separation date = when stopped living together"
                        ]
                    }
                }
            },
            "B": {
                "name": "Antragstellung",
                "fields": {
                    "26": {
                        "label": "Ab welchem Zeitpunkt Bürgergeld beantragen",
                        "description": "Start date for benefits",
                        "required": True,
                        "critical": True,
                        "options": [
                            "ab sofort (immediately)",
                            "ab einem späteren Zeitpunkt (specific future date)"
                        ],
                        "tips": [
                            "Most choose 'ab sofort'",
                            "Benefits start from application date, NOT backdated",
                            "Apply 1-2 weeks before you need money",
                            "Later date only if you know exact future need"
                        ]
                    }
                }
            },
            "C": {
                "name": "Angaben zur Lebenssituation",
                "fields": {
                    "27": {
                        "label": "Erwerbsfähig",
                        "description": "Capable of working",
                        "required": True,
                        "critical": True,
                        "tips": [
                            "Yes = can work at least 3 hours daily",
                            "Even with health issues, if CAN work 3+ hours = Yes",
                            "No = may need Sozialhilfe instead of Bürgergeld",
                            "Temporary illness still counts as Yes"
                        ]
                    },
                    "28": {
                        "label": "Schüler/Student/Auszubildender",
                        "description": "In school/university/training",
                        "required": True,
                        "critical": True,
                        "triggers": {
                            "Ja": ["Must provide enrollment proof", "May need BAföG ineligibility proof"]
                        },
                        "tips": [
                            "Students usually NOT eligible for Bürgergeld",
                            "Some training programs are exceptions",
                            "Must prove not eligible for BAföG/BAB"
                        ]
                    },
                    "29": {
                        "label": "Kosten für Schulbücher/Arbeitshefte",
                        "description": "Costs for school books",
                        "required": "conditional",
                        "tips": [
                            "Only if field 28 = Ja",
                            "Attach receipts or cost estimate",
                            "May get additional support"
                        ]
                    },
                    "30": {
                        "label": "Während Ausbildung untergebracht",
                        "description": "Accommodated during training",
                        "required": "conditional",
                        "tips": [
                            "Dormitory, barracks, special facility",
                            "Living with trainer with full board",
                            "Different rules apply"
                        ]
                    },
                    "31": {
                        "label": "Alter zwischen 18-24",
                        "description": "Age 18-24 years old",
                        "required": True,
                        "tips": ["Important for additional support rules"]
                    },
                    "32": {
                        "label": "Elternteil außerhalb Bedarfsgemeinschaft",
                        "description": "Parent outside benefit community",
                        "required": "conditional",
                        "tips": ["Only if under 25", "Affects benefit calculation"]
                    },
                    "33": {
                        "label": "Schul-/Berufsausbildung",
                        "description": "School or vocational training",
                        "required": "conditional",
                        "triggers": {
                            "Ja": ["Must complete Anlage UH3"]
                        }
                    },
                    "34": {
                        "label": "Asylbewerberleistungsgesetz",
                        "description": "Asylum seeker benefits",
                        "required": True,
                        "tips": [
                            "If receiving asylum seeker benefits",
                            "Attach Bewilligungsbescheid",
                            "Different eligibility rules"
                        ]
                    },
                    "35": {
                        "label": "Bis wann Asylbewerberleistungen",
                        "description": "Until when asylum benefits",
                        "required": "conditional",
                        "format": "DD.MM.YYYY"
                    },
                    "36": {
                        "label": "Personenidentifikationsnummer",
                        "description": "Personal identification number",
                        "required": False,
                        "tips": ["If you have one from asylum process"]
                    },
                    "37": {
                        "label": "Ausländerzentralregisternummer",
                        "description": "Foreign nationals register number",
                        "required": False,
                        "tips": ["AZR number if assigned"]
                    },
                    "38": {
                        "label": "Bürgergeld/Sozialhilfe in letzten 3 Jahren",
                        "description": "Benefits in last 3 years",
                        "required": True,
                        "tips": [
                            "List ANY previous Bürgergeld/Sozialhilfe",
                            "Helps process application faster",
                            "Include Jobcenter name"
                        ]
                    },
                    "39": {
                        "label": "Art der Leistung",
                        "description": "Type of benefit received",
                        "required": "conditional",
                        "tips": ["Only if field 38 = Ja", "Bürgergeld, Sozialhilfe, etc."]
                    },
                    "40": {
                        "label": "Zeitraum der Leistungen",
                        "description": "Period of benefits",
                        "required": "conditional",
                        "format": "MM.YYYY - MM.YYYY"
                    },
                    "41-45": {
                        "label": "Name und Anschrift Leistungsträger",
                        "description": "Name and address of benefit provider",
                        "required": "conditional",
                        "tips": ["Complete Jobcenter/Sozialamt details"]
                    },
                    "46": {
                        "label": "Bei Arbeitgeber beschäftigt (letzte 5 Jahre)",
                        "description": "Employed in last 5 years",
                        "required": True,
                        "tips": [
                            "Include ALL employment",
                            "Mini-jobs, side jobs, seasonal work",
                            "Even short-term employment"
                        ]
                    },
                    "47": {
                        "label": "Zeitraum der Beschäftigungen",
                        "description": "Employment periods",
                        "required": "conditional",
                        "format": "MM.YYYY - MM.YYYY",
                        "tips": ["List all periods", "Use multiple lines if needed"]
                    },
                    "48": {
                        "label": "Ausstehende Lohnansprüche",
                        "description": "Outstanding wage claims",
                        "required": "conditional",
                        "tips": [
                            "If employer owes you money",
                            "Final paycheck not received",
                            "Jobcenter may help recover"
                        ]
                    },
                    "49-53": {
                        "label": "Arbeitgeber Details",
                        "description": "Employer name and address",
                        "required": "conditional"
                    },
                    "54": {
                        "label": "Selbständig/freiberuflich tätig",
                        "description": "Self-employed/freelance",
                        "required": True,
                        "triggers": {
                            "Ja": ["Must complete Anlage EKS"]
                        },
                        "tips": ["Include ANY self-employment in last 5 years"]
                    },
                    "55": {
                        "label": "Entgeltersatzleistungen erhalten",
                        "description": "Received wage replacement benefits",
                        "required": True,
                        "tips": [
                            "Krankengeld, Arbeitslosengeld",
                            "Elterngeld, Übergangsgeld",
                            "Any income replacement"
                        ]
                    },
                    "56": {
                        "label": "Art der Entgeltersatzleistung",
                        "description": "Type of replacement benefit",
                        "required": "conditional"
                    },
                    "57": {
                        "label": "Zeitraum Entgeltersatzleistung",
                        "description": "Period of replacement benefit",
                        "required": "conditional",
                        "format": "MM.YYYY - MM.YYYY"
                    },
                    "58": {
                        "label": "Wehrdienst oder freiwilliger Dienst",
                        "description": "Military or voluntary service",
                        "required": True,
                        "tips": ["FSJ, Bundesfreiwilligendienst, military service"]
                    },
                    "59": {
                        "label": "Angehörige gepflegt",
                        "description": "Cared for relatives",
                        "required": True,
                        "tips": ["Care under SGB XI", "Pflege von Familienangehörigen"]
                    },
                    "60": {
                        "label": "Lebensunterhalt bestritten",
                        "description": "How you supported yourself",
                        "required": "conditional",
                        "tips": [
                            "If no employment/benefits in last 5 years",
                            "Examples: family support, savings, inheritance",
                            "Be specific and honest"
                        ]
                    },
                    "61": {
                        "label": "Andere Leistungen beantragt",
                        "description": "Applied for other benefits",
                        "required": True,
                        "tips": [
                            "Must apply for primary benefits first",
                            "BAföG, Wohngeld, BAB take priority",
                            "Bürgergeld is last resort"
                        ]
                    },
                    "62": {
                        "label": "Welche Leistungen beantragt",
                        "description": "Which benefits applied for",
                        "required": "conditional",
                        "options": [
                            "BAföG",
                            "BAB",
                            "Wohngeld",
                            "Arbeitslosengeld",
                            "Rente",
                            "Krankengeld",
                            "Kindergeld",
                            "Kinderzuschlag",
                            "Sonstiges"
                        ]
                    },
                    "63": {
                        "label": "Gesundheitlicher Schaden durch Dritten",
                        "description": "Health damage by third party",
                        "required": True,
                        "triggers": {
                            "Ja": ["Must complete Anlage UF"]
                        },
                        "tips": [
                            "Work accident, traffic accident",
                            "Medical malpractice",
                            "Assault"
                        ]
                    },
                    "64": {
                        "label": "Anspruch gegenüber Dritten",
                        "description": "Claim against third parties",
                        "required": True,
                        "tips": [
                            "Compensation claims",
                            "Inheritance",
                            "Any money owed to you"
                        ]
                    }
                }
            },
            "D": {
                "name": "Besondere Lebenssituation",
                "fields": {
                    "65": {
                        "label": "Alleinerziehend",
                        "description": "Single parent",
                        "required": True,
                        "tips": [
                            "Other parent NOT in household",
                            "Living with children",
                            "Extra Mehrbedarf allowance",
                            "12-60% additional based on children"
                        ]
                    },
                    "66": {
                        "label": "Schwanger",
                        "description": "Pregnant",
                        "required": True,
                        "triggers": {
                            "Ja": ["Need Mutterpass or doctor's letter", "May need Anlage UH2 if not married"]
                        }
                    },
                    "67": {
                        "label": "Voraussichtlicher Entbindungstermin",
                        "description": "Expected delivery date",
                        "required": "conditional",
                        "format": "DD.MM.YYYY",
                        "tips": ["From 13th week = pregnancy Mehrbedarf (17%)"]
                    },
                    "68": {
                        "label": "Kostenaufwändige Ernährung",
                        "description": "Expensive diet for medical reasons",
                        "required": True,
                        "critical": True,
                        "triggers": {
                            "Ja": ["Must complete Anlage MEB", "Need doctor's certificate"]
                        },
                        "tips": [
                            "Medical certification REQUIRED",
                            "Celiac disease, kidney disease, severe allergies",
                            "NOT for lifestyle/preference diets"
                        ]
                    },
                    "69": {
                        "label": "Behinderung",
                        "description": "Disability",
                        "required": True,
                        "tips": ["Any recognized disability", "May qualify for Mehrbedarf"]
                    },
                    "70": {
                        "label": "Teilhabe am Arbeitsleben/Eingliederungshilfen",
                        "description": "Work integration benefits",
                        "required": "conditional",
                        "tips": [
                            "§49 SGB IX benefits",
                            "§112 SGB IX integration help",
                            "Attach Bescheid"
                        ]
                    },
                    "71": {
                        "label": "Unabweisbarer besonderer Bedarf",
                        "description": "Unavoidable special need",
                        "required": True,
                        "triggers": {
                            "Ja": ["Must complete Anlage BB"]
                        },
                        "tips": [
                            "Cannot cover by savings",
                            "Example: visitation rights costs",
                            "Must prove necessity"
                        ]
                    },
                    "72": {
                        "label": "Stationäre Einrichtung",
                        "description": "Inpatient facility",
                        "required": True,
                        "tips": [
                            "Hospital, nursing home, prison",
                            "Different rules apply",
                            "Benefits may be reduced/suspended"
                        ]
                    },
                    "73": {
                        "label": "Art der stationären Einrichtung",
                        "description": "Type of facility",
                        "required": "conditional"
                    },
                    "74": {
                        "label": "Dauer des Aufenthaltes",
                        "description": "Duration of stay",
                        "required": "conditional",
                        "format": "DD.MM.YYYY - DD.MM.YYYY"
                    }
                }
            },
            "E": {
                "name": "Kranken- und Pflegeversicherung",
                "fields": {
                    "75": {
                        "label": "Gesetzlich kranken-/pflegeversichert",
                        "description": "Statutory health insurance",
                        "required": True,
                        "tips": [
                            "Family-insured or obligatory insured",
                            "Most people: Yes",
                            "Attach insurance card copy"
                        ]
                    },
                    "76": {
                        "label": "Name der Krankenkasse",
                        "description": "Health insurance company name",
                        "required": "conditional",
                        "tips": ["AOK, TK, Barmer, DAK, etc."]
                    },
                    "77": {
                        "label": "Krankenversichertennummer",
                        "description": "Health insurance number",
                        "required": False,
                        "tips": ["Found on insurance card", "10 digits"]
                    },
                    "78": {
                        "label": "Krankenkasse wechseln",
                        "description": "Switch health insurance",
                        "required": "conditional",
                        "tips": [
                            "Only if strong reason",
                            "Current insurer usually continues",
                            "Need proof from new insurer"
                        ]
                    },
                    "79": {
                        "label": "Privat/freiwillig versichert/nicht versichert",
                        "description": "Private/voluntary/uninsured",
                        "required": True,
                        "triggers": {
                            "Ja": ["Must complete Anlage SV"]
                        },
                        "tips": [
                            "Private insurance has different rules",
                            "Voluntary statutory = special calculation",
                            "Uninsured = must get insurance"
                        ]
                    }
                }
            },
            "F": {
                "name": "Wohnsituation",
                "fields": {
                    "80": {
                        "label": "Wohnen Sie allein",
                        "description": "Do you live alone",
                        "required": True,
                        "critical": True,
                        "tips": [
                            "Determines Bedarfsgemeinschaft",
                            "Critical for benefit calculation",
                            "Be accurate - will be verified"
                        ]
                    },
                    "81": {
                        "label": "Mit welchen Personen wohnen Sie",
                        "description": "Who do you live with",
                        "required": "conditional",
                        "critical": True,
                        "options": [
                            "Ehegatte/Partner (Anlage WEP)",
                            "Kinder 15-24 (Anlage WEP pro Kind)",
                            "Kinder unter 15 (Anlage KI pro Kind)",
                            "Eltern unter 25 (Anlage WEP pro Elternteil)",
                            "Eltern 25+ (Anlage HG pro Elternteil)",
                            "Verwandte (Anlage HG)",
                            "Sonstige Personen (evtl. Anlage VE)"
                        ],
                        "triggers": {
                            "Spouse/partner": ["Anlage WEP required"],
                            "Children 15-24": ["Anlage WEP per child"],
                            "Children under 15": ["Anlage KI per child"],
                            "Parents (under 25)": ["Anlage WEP per parent"],
                            "Parents (25+)": ["Anlage HG per parent"],
                            "Other relatives": ["Anlage HG"],
                            "Roommates": ["May need Anlage VE"]
                        },
                        "tips": [
                            "Each person needs separate form",
                            "Determines who is in benefit community",
                            "Affects benefit amount significantly"
                        ]
                    },
                    "82": {
                        "label": "Bedarfe für Unterkunft und Heizung",
                        "description": "Housing and heating costs",
                        "required": True,
                        "critical": True,
                        "triggers": {
                            "Ja": ["MUST complete Anlage KDU"]
                        },
                        "tips": [
                            "Yes = pay rent, utilities, or own home",
                            "No = only if completely rent-free",
                            "KDU form required for cost details"
                        ]
                    },
                    "83": {
                        "label": "Warmwasser dezentral erzeugt",
                        "description": "Decentralized water heating",
                        "required": "conditional",
                        "tips": [
                            "Durchlauferhitzer, Boiler = dezentral",
                            "Central building heating = zentral",
                            "Dezentral = extra Mehrbedarf (~2.3%)",
                            "Check utility bill if unsure"
                        ]
                    }
                }
            },
            "G": {
                "name": "Erforderliche Anlagen",
                "description": "Required attachments checklist",
                "is_checklist": True,
                "items": [
                    "Anlage VM (Vermögen) - for entire household",
                    "Kontoauszüge last 3 months - all accounts, all persons",
                    "Anlage EK - per person",
                    "Anlage EKS - if self-employed",
                    "Additional forms as triggered in sections A-F"
                ]
            },
            "H": {
                "name": "Hinweise und Unterschrift",
                "fields": {
                    "84": {
                        "label": "Datum",
                        "description": "Date of signature",
                        "required": True,
                        "format": "DD.MM.YYYY",
                        "tips": ["Today's date", "Must be filled to be valid"]
                    },
                    "85": {
                        "label": "Unterschrift antragstellende Person",
                        "description": "Applicant signature",
                        "required": True,
                        "critical": True,
                        "tips": [
                            "Must sign personally",
                            "If minor: parent/guardian signs",
                            "Digital signature NOT accepted",
                            "Form invalid without signature"
                        ]
                    },
                    "86-87": {
                        "label": "Betreuer/Vormund Datum und Unterschrift",
                        "description": "Guardian date and signature",
                        "required": "conditional",
                        "tips": ["Only if you have legal guardian"]
                    }
                }
            }
        },
        "required_documents": [
            "ID or passport copy",
            "Last 3 months bank statements (all accounts, all persons)",
            "Anlage VM (asset declaration)",
            "Anlage EK (income per person)",
            "Residence permit (if non-German)",
            "Lease contract (if renting)",
            "Health insurance card copy",
            "Proof of previous benefits (if applicable)",
            "Employment documents (if applicable)",
            "Student ID and BAföG rejection (if student)"
        ]
    },

    "VM": {
        "name": "Anlage Vermögen",
        "code": "VM",
        "purpose": "Asset declaration for entire benefit community",
        "total_pages": 3,
        "total_fields": 28,
        "critical_note": "ONE form for ENTIRE household, not per person",
        "sections": {
            "A": {
                "name": "Persönliche Daten der antragstellenden Person",
                "fields": {
                    "1": {"label": "Vorname", "required": True},
                    "2": {"label": "Nachname", "required": True},
                    "3": {"label": "Geburtsdatum", "required": True, "format": "DD.MM.YYYY"},
                    "4": {"label": "Nummer der Bedarfsgemeinschaft", "required": False, "tips": ["Leave blank if first application"]}
                }
            },
            "B": {
                "name": "Grundstücke, Wohneigentum und/oder Eigentumsanteile",
                "fields": {
                    "5": {
                        "label": "Nicht selbstgenutzte Grundstücke/Immobilien",
                        "description": "Property you don't live in",
                        "required": True,
                        "tips": [
                            "Include: rental properties, vacation homes, land",
                            "Exclude: Your current residence",
                            "Select No if you only own home you live in"
                        ]
                    },
                    "6": {
                        "label": "Art des Grundstücks",
                        "description": "Type of property",
                        "required": "conditional",
                        "options": ["Hausgrundstück", "Eigentumswohnung", "Unbebautes Grundstück"],
                        "tips": ["Can select multiple if you own different types"]
                    },
                    "7": {
                        "label": "Miteigentumsanteil in Prozent",
                        "description": "Ownership percentage",
                        "required": "conditional",
                        "tips": ["If joint ownership", "Example: 50% if shared equally with spouse"],
                        "example": "50"
                    },
                    "8": {
                        "label": "Verkehrswert in Euro",
                        "description": "Market value",
                        "required": "conditional",
                        "tips": [
                            "Online estimate sufficient initially",
                            "Use Immobilienscout24, Immowelt",
                            "Local Gutachterausschuss website",
                            "Professional appraisal may be requested later"
                        ]
                    },
                    "9": {
                        "label": "Miet-/Pachteinnahmen in Euro",
                        "description": "Rental income",
                        "required": "conditional",
                        "triggers": {
                            "If filled": ["Must also complete Anlage EK"]
                        },
                        "tips": ["Monthly rental income", "If rented out to others"]
                    }
                }
            },
            "C": {
                "name": "Kraftfahrzeuge",
                "fields": {
                    "10": {
                        "label": "Kraftfahrzeuge mit Wert",
                        "description": "Vehicles with value",
                        "required": True,
                        "format": "Name - Value",
                        "exemptions": [
                            "ONE car up to €15,000 per adult exempt",
                            "Motorcycles usually exempt",
                            "Bicycles exempt",
                            "Second car or car over €15,000 counts as wealth"
                        ],
                        "tips": [
                            "List ALL vehicles in household",
                            "Use Schwacke-Liste for valuation",
                            "Check mobile.de for market prices",
                            "Include: make, model, year, value",
                            "If over €15,000: attach Zulassungsbescheinigung and photos"
                        ],
                        "example": "Max Müller - VW Golf 2020 - 12,000€"
                    }
                }
            },
            "D": {
                "name": "Schenkungen/Spenden/Übertragungen",
                "fields": {
                    "11": {
                        "label": "Vermögen verschenkt/gespendet/übertragen",
                        "description": "Gifted/donated/transferred assets",
                        "required": True,
                        "critical": True,
                        "lookback": "10 years",
                        "tips": [
                            "10-year lookback period",
                            "Include: gifts to children, donations, property transfers",
                            "Even well-intentioned transfers matter",
                            "Be honest - will be discovered in data matching"
                        ]
                    },
                    "12-14": {
                        "label": "Person und Betrag",
                        "description": "Person name and amount",
                        "required": "conditional",
                        "tips": [
                            "First and last name",
                            "Relationship to you",
                            "Amount in Euro",
                            "Date of transfer"
                        ]
                    }
                }
            },
            "E": {
                "name": "Konten, Geldanlagen und sonstiges Vermögen",
                "fields": {
                    "15": {
                        "label": "Vermögenstabelle",
                        "description": "Complete asset table",
                        "required": True,
                        "critical": True,
                        "format": "Table - one column per person",
                        "instructions": [
                            "Write EACH person's full name at top",
                            "Fill EVERY row for EACH person",
                            "If person doesn't have item: write 0",
                            "Never leave cells blank",
                            "Include children's accounts too"
                        ],
                        "rows": {
                            "Bargeld": {
                                "description": "Cash on hand",
                                "tips": ["All cash at home", "In wallet, safe, etc."],
                                "example": "500"
                            },
                            "Girokonten": {
                                "description": "All checking accounts",
                                "tips": ["Current balance of ALL checking accounts", "Add them together if multiple"],
                                "example": "1200"
                            },
                            "Kreditkartenkonten, PayPal": {
                                "description": "Credit cards, PayPal, online accounts",
                                "tips": [
                                    "PayPal balance",
                                    "Credit card available credit NOT counted",
                                    "Revolut, N26, other online banks",
                                    "Crypto exchange accounts"
                                ],
                                "example": "150"
                            },
                            "Spareinlagen": {
                                "description": "Savings accounts, time deposits",
                                "tips": [
                                    "Savings accounts (Sparkonto)",
                                    "Fixed deposits (Festgeld)",
                                    "Savings books (Sparbuch)",
                                    "Premium savings (Prämiensparen)"
                                ],
                                "example": "5000"
                            },
                            "Sparbriefe, Wertpapiere": {
                                "description": "Savings bonds, securities",
                                "tips": [
                                    "Stocks (Aktien)",
                                    "Bonds (Anleihen)",
                                    "Mutual funds (Fonds)",
                                    "ETFs",
                                    "Current market value"
                                ],
                                "example": "3000"
                            },
                            "Bausparverträge": {
                                "description": "Building savings contracts",
                                "tips": ["Bausparkasse contracts", "Current balance", "Include all contracts"],
                                "example": "8000"
                            },
                            "Kapitallebensversicherungen": {
                                "description": "Life insurance (non-pension)",
                                "tips": [
                                    "Cash value, not death benefit",
                                    "Only if NOT for retirement",
                                    "Retirement life insurance goes in row 17"
                                ],
                                "example": "10000"
                            },
                            "Versicherungen mit Prämienrückgewähr": {
                                "description": "Insurance with premium return",
                                "tips": [
                                    "Disability insurance",
                                    "Accident insurance",
                                    "Funeral insurance",
                                    "If they return premiums"
                                ],
                                "example": "2000"
                            },
                            "Sonstiges Vermögen": {
                                "description": "Other assets",
                                "tips": [
                                    "Cryptocurrency (Bitcoin, Ethereum, etc.)",
                                    "Gold, silver, precious metals",
                                    "Valuable jewelry (over €500 per item)",
                                    "Art, collectibles, antiques",
                                    "Everyday jewelry exempt",
                                    "Family heirlooms usually exempt"
                                ],
                                "example": "1500"
                            }
                        },
                        "common_mistakes": [
                            "Leaving cells blank instead of writing 0",
                            "Forgetting PayPal and online accounts",
                            "Not including children's savings",
                            "Forgetting old accounts with small balances",
                            "Not listing cryptocurrency",
                            "Underestimating cash at home"
                        ]
                    },
                    "16": {
                        "label": "Befreiung von Rentenversicherungspflicht",
                        "description": "Exempt from pension insurance",
                        "required": True,
                        "tips": [
                            "Self-employed may be exempt",
                            "Civil servants may be exempt",
                            "Affects next questions about retirement savings"
                        ]
                    },
                    "17": {
                        "label": "Vermögen für Alterssicherung",
                        "description": "Assets for retirement",
                        "required": "conditional",
                        "tips": [
                            "Only if exempt from pension insurance",
                            "Riester, Rürup protected",
                            "Private pension insurance",
                            "Certain life insurance contracts"
                        ]
                    },
                    "18-20": {
                        "label": "Person und Vermögensgegenstand",
                        "description": "Person and asset type",
                        "required": "conditional",
                        "tips": ["Name person", "Describe asset", "May be exempt from counting"]
                    },
                    "21": {
                        "label": "Selbständige Tätigkeit",
                        "description": "Self-employed activity",
                        "required": True,
                        "tips": ["Current or past self-employment", "Affects asset exemptions"]
                    },
                    "22-24": {
                        "label": "Person und Jahre selbständig",
                        "description": "Person and years self-employed",
                        "required": "conditional",
                        "tips": [
                            "Total years of self-employment",
                            "Not just current",
                            "Affects protected asset amounts"
                        ]
                    }
                }
            },
            "F": {
                "name": "Hinweise und Unterschrift",
                "fields": {
                    "25": {"label": "Datum", "required": True, "format": "DD.MM.YYYY"},
                    "26": {
                        "label": "Unterschrift",
                        "required": True,
                        "critical": True,
                        "tips": ["Must sign", "Form invalid without signature"]
                    },
                    "27-28": {
                        "label": "Betreuer Datum/Unterschrift",
                        "required": "conditional"
                    }
                }
            }
        },
        "critical_notes": [
            "This is for ENTIRE household, not per person",
            "Complete honesty critical - automated data matching will find discrepancies",
            "Include ALL assets domestic and foreign",
            "10-year lookback for gifts/transfers",
            "Bank statements from last 3 months also required"
        ]
    },

    "KDU": {
        "name": "Anlage KDU - Kosten der Unterkunft und Heizung",
        "code": "KDU",
        "purpose": "Document housing and heating costs",
        "total_pages": 3,
        "total_fields": 40,
        "sections": {
            "A": {
                "name": "Persönliche Daten",
                "fields": {
                    "1": {"label": "Vorname", "required": True},
                    "2": {"label": "Nachname", "required": True},
                    "3": {"label": "Geburtsdatum", "required": True, "format": "DD.MM.YYYY"},
                    "4": {"label": "Nummer der Bedarfsgemeinschaft", "required": False}
                }
            },
            "B": {
                "name": "Allgemeine Angaben zur Unterkunft",
                "fields": {
                    "5": {"label": "Straße", "required": True},
                    "6": {"label": "Hausnummer", "required": True},
                    "7": {"label": "Postleitzahl", "required": True, "format": "5 digits"},
                    "8": {"label": "Ort", "required": True},
                    "9": {
                        "label": "Wie viele Personen wohnen in der Unterkunft",
                        "description": "Total people in housing",
                        "required": True,
                        "tips": [
                            "Count EVERYONE, not just benefit community",
                            "Example: 4 live here, but only 3 apply for benefits",
                            "Include all residents"
                        ]
                    },
                    "10": {
                        "label": "Baujahr der Unterkunft",
                        "description": "Year building was built",
                        "required": False,
                        "tips": ["If known", "Affects energy costs assessment"]
                    },
                    "11": {
                        "label": "Anzahl der Räume",
                        "description": "Number of rooms",
                        "required": True,
                        "tips": [
                            "Room = bedroom, living room",
                            "NOT kitchen, bathroom, hallway",
                            "Helps determine appropriate size"
                        ]
                    },
                    "12": {
                        "label": "Anzahl der Küchen",
                        "description": "Number of kitchens",
                        "required": True,
                        "tips": ["Usually 1", "Separate kitchen counts"]
                    },
                    "13": {
                        "label": "Anzahl der Bäder",
                        "description": "Number of bathrooms",
                        "required": True,
                        "tips": ["Full bathrooms", "Half-baths count as 0.5"]
                    },
                    "14": {
                        "label": "Gesamtfläche in m²",
                        "description": "Total area in square meters",
                        "required": True,
                        "tips": [
                            "From rental contract",
                            "Or property documents if owner",
                            "Wohnfläche, not Grundfläche"
                        ]
                    },
                    "15": {
                        "label": "Selbst bewohnter Anteil in m²",
                        "description": "Area you personally occupy",
                        "required": True,
                        "tips": [
                            "Usually same as total if renting entire place",
                            "Less if subletting or sharing"
                        ]
                    },
                    "16": {
                        "label": "Vermieteter/Verpachteter Anteil in m²",
                        "description": "Area you rent out",
                        "required": False,
                        "tips": ["If you sublet part of home", "Must report rental income"]
                    },
                    "17": {
                        "label": "Leer stehender Anteil in m²",
                        "description": "Empty/unused area",
                        "required": False,
                        "tips": ["Unused rooms", "May be asked to use or move"]
                    },
                    "18": {
                        "label": "Gewerberäume in m²",
                        "description": "Commercial space",
                        "required": False,
                        "tips": ["Home office if significant", "Business use"]
                    },
                    "19": {
                        "label": "Wohnsituation",
                        "description": "Living situation",
                        "required": True,
                        "critical": True,
                        "options": [
                            "Zur Miete (renting)",
                            "Im Eigentum (homeownership)"
                        ],
                        "tips": ["Determines which section (C or D) to complete"]
                    }
                }
            },
            "C": {
                "name": "Wohnen zur Miete",
                "fields": {
                    "20": {
                        "label": "Bedarfe für Unterkunft und Heizung",
                        "description": "Housing and heating costs",
                        "required": "conditional",
                        "critical": True,
                        "cost_types": {
                            "Grundmiete": {
                                "label": "Base rent (cold rent)",
                                "description": "Kaltmiete from contract",
                                "tips": [
                                    "Rent WITHOUT utilities",
                                    "From Mietvertrag",
                                    "Don't include Nebenkosten here"
                                ],
                                "mistakes": ["Including utilities", "Including heating"]
                            },
                            "Nebenkosten": {
                                "label": "Utilities (without heating)",
                                "description": "Betriebskosten",
                                "tips": [
                                    "Water, garbage, building maintenance",
                                    "Elevator, cleaning, property tax",
                                    "NOT heating",
                                    "From Nebenkostenabrechnung"
                                ],
                                "mistakes": ["Including heating", "Confusing with total utilities"]
                            },
                            "Heizkosten": {
                                "label": "Heating costs only",
                                "description": "Gas/oil for heating",
                                "tips": [
                                    "ONLY for space heating",
                                    "Not hot water (unless central)",
                                    "From utility bill",
                                    "Heating (Heizung) line item"
                                ],
                                "mistakes": ["Including hot water", "Including electricity"]
                            },
                            "Pauschalmiete": {
                                "label": "All-inclusive rent",
                                "description": "Everything in one price",
                                "tips": [
                                    "RARE - only if contract says Pauschalmiete",
                                    "One price includes rent + utilities + heating",
                                    "Don't use if you have separate costs"
                                ],
                                "mistakes": ["Using when costs are separate"]
                            },
                            "Sonstige Wohnkosten": {
                                "label": "Other housing costs",
                                "description": "Additional costs",
                                "tips": [
                                    "Garage rental",
                                    "Parking space",
                                    "Storage unit",
                                    "Must be necessary"
                                ]
                            }
                        },
                        "required_documents": [
                            "Mietvertrag (rental contract)",
                            "Recent rent receipt or bank transfer proof",
                            "Nebenkostenabrechnung (utility bill)",
                            "Heating bill if separate"
                        ]
                    }
                }
            },
            "D": {
                "name": "Wohnen im Eigentum",
                "fields": {
                    "21": {
                        "label": "Mehrere Wohneinheiten",
                        "description": "Multiple residential units",
                        "required": "conditional",
                        "tips": ["Multi-family home", "Apartment building"]
                    },
                    "22": {
                        "label": "Anzahl Wohneinheiten",
                        "description": "Number of units",
                        "required": "conditional"
                    },
                    "23": {
                        "label": "Bedarfe für Eigenheim",
                        "description": "Homeownership costs",
                        "required": "conditional",
                        "covered_costs": {
                            "Schuldzinsen": {
                                "label": "Mortgage INTEREST only",
                                "tips": [
                                    "NOT principal payments",
                                    "Only interest portion",
                                    "From bank statement"
                                ]
                            },
                            "Heizkosten": "Heating costs",
                            "Heizungswartung": "Heating maintenance",
                            "Grundsteuern": "Property tax",
                            "Gebäudeversicherung": "Building insurance",
                            "Wasser": "Water",
                            "Abwasser": "Sewage",
                            "Müllgebühren": "Garbage fees",
                            "Schornsteinfegergebühren": "Chimney sweep",
                            "Straßenreinigung": "Street cleaning",
                            "Sonstige Nebenkosten": "Other utilities"
                        },
                        "not_covered": [
                            "Mortgage principal",
                            "Renovations/improvements",
                            "Cosmetic repairs",
                            "Most HOA fees"
                        ]
                    }
                }
            },
            "E": {
                "name": "Energiequellen",
                "fields": {
                    "24": {
                        "label": "Brennstoff zum Heizen",
                        "description": "Heating fuel type",
                        "required": True,
                        "options": ["Strom", "Gas", "Heizöl", "Fernwärme", "Holz", "Sonstiges"],
                        "tips": ["Check utility bill", "May affect cost assessment"]
                    },
                    "25": {
                        "label": "Beschaffung der Brennstoffe selbst",
                        "description": "Do you purchase fuel yourself",
                        "required": True,
                        "tips": ["Yes if you buy oil/wood", "No if utility company provides"]
                    },
                    "26": {
                        "label": "Art der Heizung",
                        "description": "Type of heating system",
                        "required": True,
                        "options": [
                            "Zentralheizung (central heating)",
                            "Einzelofen (individual stove)",
                            "Nachtspeicherofen (night storage heater)"
                        ]
                    },
                    "27": {
                        "label": "Energiequelle zum Kochen",
                        "description": "Cooking energy source",
                        "required": True,
                        "options": ["Strom", "Gas", "Sonstiges"]
                    },
                    "28": {
                        "label": "Warmwassererzeugung",
                        "description": "Hot water generation method",
                        "required": True,
                        "critical": True,
                        "options": {
                            "zentral": {
                                "label": "Central",
                                "description": "Part of building heating system"
                            },
                            "dezentral": {
                                "label": "Decentralized",
                                "description": "Separate boiler/heater",
                                "benefit": "Extra Mehrbedarf allowance (~2.3% of standard rate)"
                            }
                        },
                        "tips": [
                            "CRITICAL FIELD",
                            "Dezentral = Durchlauferhitzer, Boiler",
                            "Zentral = included in building heating",
                            "Check utility bill if unsure",
                            "Dezentral gives you extra money"
                        ]
                    },
                    "29": {
                        "label": "Brennstoff für dezentrales Warmwasser",
                        "description": "Fuel for decentralized hot water",
                        "required": "conditional",
                        "options": ["Strom", "Gas", "Heizöl", "Holz", "Kohle", "Sonstiges"],
                        "tips": ["Only if field 28 = dezentral"]
                    }
                }
            },
            "F": {
                "name": "Überweisung an Vermieterin/Vermieter",
                "fields": {
                    "30": {
                        "label": "Miete direkt an Vermieter überweisen",
                        "description": "Pay rent directly to landlord",
                        "required": True,
                        "tips": [
                            "Jobcenter pays landlord directly",
                            "Useful if risk of eviction",
                            "Useful if trouble managing money",
                            "Landlord can request this"
                        ]
                    },
                    "31-36": {
                        "label": "Vermieter Name, Anschrift, IBAN",
                        "description": "Landlord details",
                        "required": "conditional",
                        "tips": ["Complete all landlord information", "IBAN must be correct"]
                    }
                }
            },
            "G": {
                "name": "Hinweise und Unterschrift",
                "fields": {
                    "37": {"label": "Datum", "required": True, "format": "DD.MM.YYYY"},
                    "38": {"label": "Unterschrift", "required": True, "critical": True},
                    "39-40": {"label": "Betreuer", "required": "conditional"}
                }
            }
        },
        "appropriateness_standards": {
            "note": "Jobcenter checks if housing size/cost is appropriate",
            "size_guidelines": {
                "1_person": "45-50 m²",
                "2_persons": "60 m²",
                "3_persons": "75 m²",
                "4_persons": "85-90 m²",
                "each_additional": "+10-15 m²"
            },
            "cost_limits": "Vary by city - ask your local Jobcenter for 'Mietobergrenze'"
        }
    },

    "WEP": {
        "name": "Anlage WEP - Weitere Person ab 15 Jahren",
        "code": "WEP",
        "purpose": "Information for each adult/teen (15+) in household",
        "total_pages": 7,
        "total_fields": 87,
        "usage": "ONE FORM PER PERSON over 15 years old",
        "note": "Sections C-E largely mirror HA form - refer to HA guidance",
        "sections": {
            "A": {
                "name": "Persönliche Daten der antragstellenden Person",
                "note": "This is YOU (the main applicant)",
                "fields": {
                    "1-4": {
                        "label": "Ihre Daten",
                        "description": "Your personal information",
                        "tips": ["Same as HA form fields 1-4"]
                    }
                }
            },
            "B": {
                "name": "Persönliche Daten der Person",
                "note": "This is about the OTHER PERSON",
                "fields": {
                    "5-12": {
                        "label": "Daten der weiteren Person",
                        "description": "Other person's personal data",
                        "tips": ["Complete fields like HA Section A", "For THIS specific person"]
                    },
                    "22": {
                        "label": "Verwandtschaftsverhältnis",
                        "description": "Relationship to you",
                        "required": True,
                        "critical": True,
                        "examples": [
                            "Ehemann/Ehefrau (spouse)",
                            "Lebensgefährte/in (partner)",
                            "Sohn/Tochter (child)",
                            "Mutter/Vater (parent)",
                            "Bruder/Schwester (sibling)",
                            "Großeltern (grandparents)"
                        ],
                        "tips": [
                            "Exact relationship critical for calculation",
                            "Determines if they're in Bedarfsgemeinschaft",
                            "Use German terms"
                        ]
                    }
                }
            },
            "C-E": {
                "name": "Life Situation, Special Situations, Health Insurance",
                "note": "Fields 23-76 mirror HA form fields 27-79",
                "reference": "See HA form guidance for detailed field explanations",
                "differences": [
                    "Questions are about THIS person, not main applicant",
                    "Field 61: May need Anlage VE if not related",
                    "Field 65: Disability with 'G' marking = extra Mehrbedarf"
                ]
            },
            "F": {
                "name": "Erforderliche Anlagen",
                "note": "Same as HA - checklist of required forms"
            },
            "G": {
                "name": "Hinweise und Unterschrift",
                "fields": {
                    "77-80": {
                        "label": "Unterschrift",
                        "description": "Signature section",
                        "required": True,
                        "tips": ["Main applicant signs for household member"]
                    }
                }
            }
        }
    },

    "WBA": {
        "name": "Weiterbewilligungsantrag",
        "code": "WBA",
        "purpose": "Renewal application to continue benefits",
        "total_pages": 5,
        "total_fields": 28,
        "key_principle": "Only report CHANGES since last application",
        "sections": {
            "A": {
                "name": "Persönliche Daten",
                "fields": {
                    "1-4": {
                        "label": "Ihre Daten",
                        "tips": ["Same as always", "Should already be in system"]
                    }
                }
            },
            "B": {
                "name": "Angaben zur Wohnsituation",
                "fields": {
                    "5-8": {
                        "label": "Aktuelle Anschrift",
                        "description": "Current address",
                        "required": True,
                        "tips": [
                            "Update if moved",
                            "Otherwise confirm it's still current"
                        ]
                    },
                    "9": {
                        "label": "Wohnen Sie allein",
                        "description": "Live alone",
                        "required": True,
                        "tips": ["Update if changed since last time"]
                    },
                    "10": {
                        "label": "Personen im Haushalt",
                        "description": "People in household",
                        "required": "conditional",
                        "tips": [
                            "ONLY fill if someone moved in/out",
                            "If no change: leave blank or write 'unverändert'",
                            "List names, birthdates, relationship"
                        ]
                    },
                    "11": {
                        "label": "Bedarfe für Unterkunft und Heizung",
                        "description": "Housing costs",
                        "required": True,
                        "tips": ["Update if costs changed"]
                    },
                    "12-15": {
                        "label": "Wohnsituation und Kosten",
                        "description": "Living situation and costs",
                        "required": "conditional",
                        "tips": [
                            "Only update if changed",
                            "New rent amount",
                            "Moved to new place",
                            "Bought/sold property"
                        ]
                    }
                }
            },
            "E": {
                "name": "Einkommensverhältnisse",
                "fields": {
                    "16": {
                        "label": "Einkommen aus Erwerbstätigkeit",
                        "description": "Employment income",
                        "required": True,
                        "tips": [
                            "Started new job",
                            "Ended job",
                            "Salary changed",
                            "Hours changed"
                        ]
                    },
                    "17": {
                        "label": "Geänderte Ausgaben",
                        "description": "Changed expenses",
                        "required": "conditional",
                        "tips": [
                            "New commute costs",
                            "Changed childcare",
                            "New work equipment",
                            "Include date of change"
                        ]
                    },
                    "18": {
                        "label": "Selbständige/freiberufliche Tätigkeit",
                        "description": "Self-employment",
                        "required": True,
                        "triggers": {
                            "Ja": ["Must complete Anlage EKS"]
                        }
                    },
                    "19": {
                        "label": "Aufwandsentschädigungen",
                        "description": "Expense allowances",
                        "required": True,
                        "tips": [
                            "Volunteer work compensation",
                            "Honorary position allowances",
                            "Must be tax-free",
                            "Attach proof"
                        ]
                    },
                    "20": {
                        "label": "Einkommen von Sozialleistungsträgern",
                        "description": "Income from benefit providers",
                        "required": True,
                        "tips": [
                            "Started receiving pension",
                            "Child support began",
                            "Sickness benefits",
                            "Any new social benefits"
                        ]
                    },
                    "21": {
                        "label": "Andere Einnahmen",
                        "description": "Other income",
                        "required": True,
                        "tips": [
                            "Rental income",
                            "Investment income",
                            "Gifts",
                            "Inheritance"
                        ]
                    },
                    "22": {
                        "label": "Art der Einnahme",
                        "description": "Type of income",
                        "required": "conditional"
                    }
                }
            },
            "F": {
                "name": "Änderungen in der Vergangenheit",
                "fields": {
                    "23": {
                        "label": "Unreported changes",
                        "description": "Changes you forgot to report",
                        "required": True,
                        "critical": True,
                        "tips": [
                            "HONESTY CRITICAL",
                            "Even months-old changes",
                            "Better to self-report than be caught",
                            "Examples: inheritance, sold car, side job",
                            "Pregnancy, disability recognition, marriage"
                        ]
                    }
                }
            },
            "G": {
                "name": "Absehbare Änderungen in der Zukunft",
                "fields": {
                    "24": {
                        "label": "Predictable future changes",
                        "description": "Changes you know will happen",
                        "required": True,
                        "examples": [
                            "Planning to move (within 6 months)",
                            "Someone moving in/out",
                            "Starting new job/education",
                            "Getting married/divorced",
                            "Health insurance change",
                            "Disability status change"
                        ],
                        "benefit": "Jobcenter can plan, avoid payment disruptions"
                    }
                }
            },
            "H": {
                "name": "Erforderliche Anlagen",
                "required_documents": [
                    "Last 3 months bank statements (all accounts, all persons)",
                    "Anlage EKS (if self-employed)",
                    "Proof of any changes mentioned"
                ],
                "note": "Less documents needed than initial application if no major changes"
            },
            "I": {
                "name": "Hinweise und Unterschrift",
                "fields": {
                    "25-28": {
                        "label": "Unterschrift",
                        "required": True,
                        "critical": True
                    }
                }
            }
        },
        "tips": [
            "Much shorter than HA - focus on changes only",
            "If nothing changed, say 'keine Änderungen'",
            "Submit 1-2 months before current period ends",
            "Process usually faster than initial application"
        ]
    }
}

# Form triggers (when one field requires another form)
FORM_TRIGGERS = {
    "HA": {
        "24": {
            "separated/divorced": ["Anlage UH1"]
        },
        "28": {
            "student_under_25": ["Anlage UH3 if parent outside household"]
        },
        "66": {
            "pregnant_not_married": ["Anlage UH2"]
        },
        "68": {
            "expensive_diet": ["Anlage MEB"]
        },
        "71": {
            "special_need": ["Anlage BB"]
        },
        "79": {
            "private_insurance": ["Anlage SV"]
        },
        "81": {
            "spouse": ["Anlage WEP"],
            "children_15_24": ["Anlage WEP per child"],
            "children_under_15": ["Anlage KI per child"],
            "parents_under_25": ["Anlage WEP per parent"],
            "parents_25_plus": ["Anlage HG per parent"],
            "other_relatives": ["Anlage HG"],
            "roommates": ["Anlage VE maybe"]
        },
        "82": {
            "housing_costs": ["Anlage KDU"]
        }
    }
}

# Common mistakes
COMMON_MISTAKES = {
    "all_forms": [
        "Leaving fields blank instead of 'no'/'0'/'not applicable'",
        "Wrong date format (must be DD.MM.YYYY)",
        "Incomplete/non-consecutive bank statements",
        "Not signing the form",
        "Sending originals instead of copies",
        "Inconsistent information across forms"
    ],
    "HA": [
        "Forgetting triggered forms (UH1, KDU, etc.)",
        "Not listing all household members",
        "Underestimating work history gaps"
    ],
    "VM": [
        "Leaving table cells blank",
        "Forgetting PayPal/crypto",
        "Not including children's accounts",
        "Hiding gifts/transfers (will be found)"
    ],
    "KDU": [
        "Mixing Kaltmiete with Warmmiete",
        "Including heating in Nebenkosten",
        "Missing dezentral hot water Mehrbedarf",
        "Confusing central vs decentralized heating"
    ],
    "WEP": [
        "Forgetting this form is per person",
        "Not specifying relationship clearly"
    ],
    "WBA": [
        "Reporting unchanged items",
        "Not mentioning past unreported changes"
    ]
}

# Required documents
REQUIRED_DOCUMENTS = {
    "always": [
        "Last 3 months bank statements (ALL accounts, ALL persons)",
        "Anlage VM (for entire household)",
        "Anlage EK (per person)",
        "ID/passport copy (main applicant)"
    ],
    "conditional": {
        "non_german": ["Residence permit", "Verpflichtungserklärung if applicable"],
        "housing": ["Rental contract", "Recent rent receipts", "Utility bills"],
        "employed": ["Last 3 payslips", "Employment contract"],
        "student": ["Enrollment certificate", "BAföG rejection proof"],
        "pregnant": ["Mutterpass or doctor's letter"],
        "separated": ["Separation agreement if available"],
        "disabled": ["Schwerbehindertenausweis"],
        "self_employed": ["Tax returns", "Profit/loss statements", "Business registration"]
    }
}