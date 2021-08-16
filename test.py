from dateparser.search_dates import search_dates
# from dateparser.search import search_dates

# THIS IS TEMPORARY for Debugging

article = """

Caesar Augustus (23 September 63 BC – 19 August AD 14), also known as Octavian (Latin: Octavianus) when referring to his early career, was the first Roman emperor, reigning from 27 BC until his death in AD 14.[a] His status as the founder of the Roman Principate (the first phase of the Roman Empire) has consolidated a legacy as one of the most effective leaders in human history.[4] The reign of Augustus initiated an era of relative peace known as the Pax Romana. The Roman world was largely free from large-scale conflict for more than two centuries, despite continuous wars of imperial expansion on the Empire's frontiers and the year-long civil war known as the "Year of the Four Emperors" over the imperial succession.
Originally named Gaius Octavius, he was born into an old and wealthy equestrian branch of the plebeian gens Octavia. His maternal great-uncle Julius Caesar was assassinated in 44 BC and Octavius was named in Caesar's will as his adopted son and heir; as a result, he inherited Caesar's name, estate, and the loyalty of his legions. He, Mark Antony and Marcus Lepidus formed the Second Triumvirate to defeat the assassins of Caesar. Following their victory at the Battle of Philippi (42 BC), the Triumvirate divided the Roman Republic among themselves and ruled as de facto dictators. The Triumvirate was eventually torn apart by the competing ambitions of its members; Lepidus was exiled in 36 BC and Antony was defeated by Octavian at the Battle of Actium in 31 BC.
After the demise of the Second Triumvirate, Augustus restored the outward façade of the free Republic, with governmental power vested in the Roman Senate, the executive magistrates and the legislative assemblies, yet maintained autocratic authority by having the Senate grant him lifetime tenure as supreme military command, tribune and censor. A similar ambiguity is seen in his chosen names, the implied rejection of monarchical titles whereby he called himself Princeps Civitatis (First Citizen) juxtaposed with his adoption of the ancient title Augustus.
Augustus dramatically enlarged the Empire, annexing Egypt, Dalmatia, Pannonia, Noricum and Raetia, expanding possessions in Africa, and completing the conquest of Hispania, but suffered a major setback in Germania. Beyond the frontiers, he secured the Empire with a buffer region of client states and made peace with the Parthian Empire through diplomacy. He reformed the Roman system of taxation, developed networks of roads with an official courier system, established a standing army, established the Praetorian Guard, official police and fire-fighting services for Rome, and rebuilt much of the city during his reign. Augustus died in AD 14 at the age of 75, probably from natural causes. Persistent rumors, substantiated somewhat by deaths in the imperial family, have claimed his wife Livia poisoned him. He was succeeded as emperor by his adopted son Tiberius, Livia's son and also former husband of Augustus' only biological daughter Julia. """ * 1

import time
start = time.process_time()

a = search_dates(article)
print(a)

print(time.process_time() - start)

# tox -e py -- tests/test_search_dates.py
