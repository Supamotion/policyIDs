#!/usr/bin/env python3
"""Build the EP2 replacement shot files for pika/run-shot.js.

Writes pika/shots/*.json next to this tool's parent folder. The JSON files are
the deliverable; this script exists so a line can be changed in one place and
every file rebuilt consistently. Run:  python3 tools/build_shots.py
"""
import json
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parent.parent / "pika" / "shots"

VIDEO_API = "bytedance/seedance-2.5/reference-to-video"
VIDEO_INPUT = {"duration": 30, "resolution": "480p", "ratio": "21:9", "generate_audio": True,
               "watermark": False, "output_format": "mp4", "bitrate_mode": "high"}
PLATE_API = "openai/gpt-image-2/image-to-image"
PLATE_INPUT = {"aspect_ratio": "21:9", "resolution": "2K", "quality": "high", "num_images": 1}


def head(n):
    return (f"Live-action mythic modernism. Photoreal, tactile, cinematic, anamorphic widescreen, 24fps, "
            f"shallow depth of field. {n} SHOTS, cut in camera at the stated times, and no other coverage. "
            f"All spoken dialogue is in ENGLISH.")


NO_FX = ("No machinery, no gears, no runes, no magical light, no lens flare, no particles, no smoke, no digital "
         "element, no screens, no interface, no signage, no ornament, and no Victorian, Edwardian, medieval or "
         "steampunk detail.")

CROWD_VOICES = ("ALL BACKGROUND VOICES ARE LOW AND COMPLETELY INDISTINCT AND NO WORD IN THEM CAN BE MADE OUT; only "
                "the named lines in this film are intelligible.")

# --- canonical cast blocks (corrected to the sheets during EP2/EP3 production) -----------------------------

def beatrice(refs):
    return (f"{refs} BEATRICE MORD — a WOMAN in her early forties, dark hair in a TIGHT HIGH TOPKNOT, clean-shaven, "
            "in a BLACK ASYMMETRICAL WRAP COAT wrapped and belted across the body over a full-length "
            "OXBLOOD-AND-RUST underskirt panel. She has NO cream panel, NO tall collar, NO cuffs, NO ribbon, NO blue, "
            "NO rust sash, NO leather chest strap, NO glass cylinders, NO earrings and NO veil.")


def tomas(refs, lock):
    return (f"{refs} TOMAS GREY — a MAN in his thirties, tall, OLIVE-SKINNED, dark CURLY hair and a SHORT DARK BEARD. "
            f"{lock} IS THE ABSOLUTE AUTHORITY FOR TOMAS — his face, his collar, his cuffs, his coat and the black "
            "ribbon around him — AND IT OVERRIDES EVERY OTHER IMAGE AND EVERY WORD OF DESCRIPTION ON THAT SUBJECT. "
            "COPY HIS COSTUME FROM IT EXACTLY: a floor-length BLACK ROBE-COAT with ONE FLAT CREAM-OATMEAL LINEN PANEL "
            "down the centre front, TURNED-BACK CREAM CUFFS at both wrists, a TALL SMOOTH CYLINDRICAL CREAM COLLAR "
            "wrapped close around his throat with a level top edge — a smooth closed tube, never flared, never a wing, "
            "never a scallop, never two upright panels — and THE CLAUSE RIBBON, a long matte black band covered in "
            "fine pale engraved script, LOOPING AND SPIRALLING AROUND HIS BODY in large open curves and standing away "
            "from him in the air. THERE IS ONLY ONE TOMAS IN THIS FILM.")


def amina(refs):
    return (f"{refs} DR. AMINA VEY — a woman in her forties with LIGHT BROWN SKIN and DARK CURLY HAIR in a LOOSE "
            "MESSY BUN with strands escaping. Layered SLATE-BLUE technical workwear with a high draped cowl collar, a "
            "LEATHER STRAP across the chest, a WIDE OXBLOOD-RUST SASH, heavy laced BOOTS, small CLEAR GLASS-AND-CERAMIC "
            "SAMPLE PODS riding on thin dark articulated metal armatures off her harness, and an open field notebook. "
            "She is the ONLY person here in blue. She wears NO black column, NO rectangular panels, NO braided crown "
            "and NO drop earrings.")


def pikk(refs, hand):
    return (f"{refs} PIKK — compact, bald, LONG POINTED EARS, olive-grey skin, a deeply lined middle-aged adult face, "
            f"soot-grey workwear with flat tan-ochre panels; his ears are OPAQUE and MATTE, never backlit. {hand}")


PIKK_POCKET = ("HIS RIGHT HAND IS CLOSED INSIDE HIS COAT POCKET, visible only as a fist-shape pushing out the cloth; "
               "his LEFT hand does everything. Nobody looks at it and nobody mentions it.")

YSRA_FACE = ("a BLACK WOMAN IN HER LATE FIFTIES with a lean angular face, high cheekbones and a firm jaw; THICK "
             "SCULPTURAL BRAIDS streaked with grey wound into a RAISED BRAIDED CROWN; LONG THIN DARK DROP EARRINGS "
             "hanging to the jaw on both sides; a floor-length high-necked CHARCOAL-BLACK gown with a smooth funnel "
             "neck under a wide dark overrobe of OVERLAPPING FLAT RECTANGULAR PANELS, a WIDE COBALT-BLUE PANEL running "
             "the full height of the skirt at one side, and LONG DARK GLOVES")

KELL_COAT = ("a clean-shaven man in his fifties with GREY HAIR, in a HEAVY PALE GREY-OATMEAL WOOL OVERCOAT with wide "
             "notched lapels. HIS COAT IS PALE GREY — NOT black, NOT dark brown, NOT navy")

TWO_LIGHTS = ("TWO PRACTICAL LIGHT SOURCES, NEVER BLENDED, NEITHER WITH A VISIBLE FIXTURE: COLD blue-white 6500K "
              "daylight through the doorway, and WARM amber 3200K from deep inside the slots.")

CHAMBER = ("THE CHAMBER: a small round room of COARSE, COLD, WEATHERED DARK GREY GRANITE, almost charcoal in shadow, "
           "salt-stained and pitted, laid in large heavy irregular blocks — NOT pale, NOT cream, NOT limestone. A row "
           "of small HORIZONTAL openings, each a hand's width across and only a few centimetres high, is cut into the "
           "curved wall at waist height with a thin warm amber light deep inside each one. Directly under them the "
           "stone sill is hollowed into a long smooth trough by four hundred years of hands. One stone bench. One "
           "plain doorway onto a flat white sky and the frozen pier. NO MACHINERY ANYWHERE.")

SLOT_GRAMMAR = ("THE RULE OF THE SLOT LIGHT, established earlier and used here: when a slot is DRAWING from the hand "
                "in it, the amber light inside that slot DIMS for as long as the draw lasts; when a slot is taking "
                "NOTHING, its light stays STEADY and unchanged. It is a practical lamp on a dimmer: it never flashes, "
                "strobes, pulses or burns brighter.")

FROST_OUT = ("FROST GROWS OUTWARD FROM BODIES AND NEVER INWARD FROM ANYTHING: it starts on a person's skin or clothes "
             "and its fine needles spread AWAY from them. The stone, the windows and the air never frost.")


def video(id_, slug, scene, shot, refs, prompt, audio=None):
    d = {"id": id_, "slug": slug, "scene": scene, "shot": shot, "api_id": VIDEO_API,
         "reference_images": refs}
    if audio:
        d["reference_audio"] = audio
    d["input"] = dict(VIDEO_INPUT)
    d["prompt"] = prompt
    return d


def plate(id_, slug, scene, shot, refs, prompt):
    return {"id": id_, "slug": slug, "scene": scene, "shot": shot, "api_id": PLATE_API, "output_ext": "png",
            "reference_images": refs, "input": dict(PLATE_INPUT), "prompt": prompt}


def j(*parts):
    return "\n\n".join(p.strip("\n") for p in parts if p)


FILES = {}

# =====================================================================================================
# PLATE — Beatrice while the route draws from her
# =====================================================================================================
FILES["ep2_beatrice_frost_still"] = plate(
    "ASSET_EP2_BEATRICE_FROST", "ep2_beatrice_frost",
    "Episode 02 — asset: Beatrice while the route is drawing from her (frost at the knuckles and throat)",
    "Plate for Sc16 v4 Shot 4, Sc17 v4 and reel2 C2. Image-to-image from her sheet (§122); chamber from "
    "ep2_recip_lock_v3. Matched-state plate for the new 'Beatrice is the next source' thread (§173).",
    ["pika/refs/beatrice_turnaround.png", "pika/refs/ep2_recip_lock_v3.jpg"],
    j("ONE SINGLE CINEMA FRAME of photoreal live-action production photography, anamorphic 2.39:1, 50mm at T2, "
      "shallow depth of field.",
      "USE THE WOMAN IN REFERENCE 1 EXACTLY AS SHE IS — her exact face, her exact hair and her exact costume — and "
      "place her in the stone chamber of reference 2. COPY HER FACE, HAIR AND COSTUME PRECISELY FROM REFERENCE 1 AND "
      "CHANGE NOTHING ABOUT THEM: a WOMAN in her early forties, dark hair in a TIGHT HIGH TOPKNOT, in a BLACK "
      "ASYMMETRICAL WRAP COAT wrapped and belted across the body over a full-length OXBLOOD-AND-RUST underskirt panel. "
      "She has NO cream panel, NO tall collar, NO cuffs, NO ribbon, NO veil and NO jewellery.",
      "THE PLACE, EXACTLY AS REFERENCE 2: " + CHAMBER,
      "THE MOMENT: she stands at the slot wall, three-quarter on to the lens, her RIGHT SLEEVE PUSHED BACK OFF THE "
      "WRIST, her bare right hand raised at the mouth of one slot, a hand's width from going in. Her face is calm and "
      "decided — a professional doing the next necessary thing, not afraid and not heroic.",
      "ONE THING IS DIFFERENT FROM HER REFERENCE, AND IT IS THE POINT OF THIS PHOTOGRAPH: FINE WHITE FROST IS GROWING "
      "OUTWARD FROM HER BODY.\n"
      "— On the BACK OF HER RIGHT HAND, delicate white rime crystals feather outward from the KNUCKLES across the "
      "backs of the fingers, the needles pointing AWAY from the skin.\n"
      "— At the BASE OF HER THROAT, on the edge of her black collar, sits a small STARBURST of white rime about the "
      "size of a coin, its needles radiating outward from her.\n"
      "THE FROST IS ON HER AND NOWHERE ELSE. The stone, the slots, the sill and the air carry NO frost at all.",
      "HER BREATH IS VISIBLE as a soft white plume in front of her mouth.",
      "LIGHT: two practical sources, never blended — COLD blue-white 6500K daylight from the doorway on one side of "
      "her face, WARM amber 3200K from the slots on the other side.",
      "Palette: coat black #16181A, oxblood #6E2A22, slot amber #A9721F, frost white #E9F1F4, granite #4A4B48.",
      "SINGLE PHOTOGRAPH — no panels, no grid, no insets, no labels, no captions, no text. Photoreal, tactile wool, "
      "skin, stone and real frost. No glow, no magical light, no particles, no lens flare, no ornament, and no "
      "Victorian, Edwardian or steampunk detail."))

# =====================================================================================================
# PLATE — Kell alive, for the reconstruction (fixes Sc04 v4's dead reconstruction)
# =====================================================================================================
FILES["ep2_kell_alive_still"] = plate(
    "ASSET_EP2_KELL_ALIVE", "ep2_kell_alive",
    "Episode 02 — asset: Attaché Rovin Kell ALIVE at his table, writing, in the reconstruction's cold light",
    "Derived image-to-image from the Sc03 frame so face, coat, seat and carriage match; ONLY his condition changes. "
    "Authority for Sc04 v5 Shot 2 and the coat in reel1 P1. Fixes the v4 fault where the corpse frame owned his state.",
    ["pika/refs/ep2_kell_from_sc03.jpg"],
    j("ONE SINGLE CINEMA FRAME of photoreal live-action production photography, anamorphic 2.39:1, 65mm at T2.8.",
      "USE THE MAN, HIS COAT, HIS SEAT, HIS TABLE, THE LAMP AND THE CARRIAGE IN THE REFERENCE EXACTLY AS THEY ARE, AND "
      "CHANGE ONLY HIS CONDITION. In the reference he is dead and frozen. IN THIS PHOTOGRAPH IT IS EARLIER THAT "
      "MORNING AND HE IS ALIVE AND WELL.",
      "HIM, ALIVE: " + KELL_COAT + ". HIS EYES ARE OPEN and looking down at his work. His skin is a LIVING, WARM, "
      "NATURAL COLOUR with colour in his lips and cheeks, and his grey hair is ordinary dry hair. He sits upright at "
      "his RIGHT-HAND WINDOW TABLE, the clear dry window beside him onto a flat white frozen lake.",
      "HE IS WRITING: a PEN in his right hand, mid-stroke, on a cream printed form lying flat on the white "
      "tablecloth; his left hand rests flat on the form, holding it still. A calm, busy civil servant finishing a form "
      "before a deadline he has already calculated. Not sad, not afraid, not noble — busy.",
      "EVERYTHING ABOUT HIM IS ORDINARY AND ALIVE: his skin, his hands, his coat, the cloth and the table are clean and "
      "dry, with no rime, no white crystals, no white skin and no stiffened fabric anywhere.",
      "THE LIGHT ON HIM IS THE ONE OTHER CHANGE: he and his table are lit COLD, FLAT AND BLUE-WHITE FROM ABOVE — the "
      "even 6500K light of an overcast pier — while the walnut carriage around him keeps its warm amber lamps. He is a "
      "cold-lit man in a warm room.",
      "Palette: pale oatmeal #CFC6B6, cloth white #EEEAE0, pier blue #8FA3B0, carriage amber #B8801F.",
      "SINGLE PHOTOGRAPH — no panels, no grid, no insets, no labels, no captions, and no readable text on the form. "
      "Photoreal, tactile wool, skin, paper and linen. No glow, no magical light, no particles, no lens flare, no "
      "ornament, and no Victorian, Edwardian or steampunk detail."))

# =====================================================================================================
# SCENE 00 v3 — pre-intro: the aborted "I—" on a shot boundary (v2 text otherwise kept)
# =====================================================================================================
FILES["ep2_scene00_preintro_v3"] = video(
    "EP02_SC00_V3", "ep2_scene00_safety_information_v3",
    "Episode 02 · PRE-INTRO · Scene 00 — SAFETY INFORMATION (v3: the aborted 'I—' ends a shot)",
    "v3 = v2 with one structural change (§18/§66): Shot 3 ends on the aborted 'I—' and two seconds of silence; the "
    "permitted sentence opens Shot 4. v2 merged them into 'I, the Railway, regrets…'.",
    ["pika/refs/ep2_carriage_lock.jpg", "pika/refs/a13_ortho.png", "pika/refs/a13_hero.png", "pika/refs/a13_scale.png"],
    j(head("FOUR"),
      "VOICE — THIS IS IMPORTANT: @Audio1 is the voice of ARTICLE THIRTEEN. Match that voice exactly: the same MALE "
      "voice, the same pitch, the same timbre, the same dry unhurried delivery. Every spoken line in this scene is "
      "spoken by that same male voice. No other voice speaks at any point. No whisper, no rasp, no echo, no processing, "
      "no doubling, no chorus, no female voice, no child voice.",
      "@Image1 is the authority for the CARRIAGE ITSELF ONLY — its warm 3200K table lamps, walnut panelling, wool "
      "banquettes, white tablecloths and above all its WINDOWS. IMPORTANT PRECEDENCE: @Image1 shows an EMPTY carriage, "
      "and that is the one thing to ignore. This carriage is FULL OF PASSENGERS. @Image2, @Image3 and @Image4 are "
      "ARTICLE THIRTEEN's construction and scale.",
      "THE CARRIAGE IS CROWDED AND ALIVE. It is a busy first-class saloon carriage in service, full of travellers: "
      "people seated at every table, coats and scarves over seat backs, stacked luggage and cases in the racks, hats, "
      "folded newspapers, tea glasses, someone standing in the aisle, someone walking through, a porter passing. The "
      "passengers are a mixture of ordinary human travellers AND a few quietly impossible ones — a woman whose luggage "
      "floats a few centimetres above the rack, a passenger in a heavy diplomatic coat with a nested ring of black "
      "veils where a head should be, a small delegate whose hands are wrapped in paper labels. NOTHING about any of "
      "them is remarked on. Everyone is calm, warm, occupied, mid-journey. " + CROWD_VOICES,
      "THE WINDOWS, WHICH ARE THE EASIEST THING TO GET WRONG: every window shows one identical thing — a FLAT, "
      "FEATURELESS, MATTE PALE GREY SURFACE, like a blank sheet of grey card behind the glass. NO night, NO stars, NO "
      "landscape, NO passing scenery, NO motion, NO rain, NO weather, NO tunnel, NO black glass, NO reflection. The "
      "windows give off NO light; all light comes from the little table lamps. Nothing outside ever moves. Not one "
      "passenger ever looks at a window.",
      "ARTICLE THIRTEEN: a being over two metres tall, seated at a SIDE TABLE BY A WINDOW — an ordinary window seat "
      "like any other passenger, off to one side of the carriage, NEVER in the middle of the aisle and NEVER centred in "
      "the frame. It is a vertical column of folded bone-white parchment membrane creased like heavy handmade paper, "
      "rising to a tall peaked hood. Slender black branch limbs. Faint handwritten signatures across the membrane. ONE "
      "saturated red seam down the folds.",
      "ITS FACE IS BLACK. Set deep inside the hood is a real, living, expressive face with DEEP MATTE BLACK SKIN — an "
      "ordinary human face with human proportions, human eyes and a human mouth, dark-skinned and in shadow inside the "
      "hood. NOT an animal, NOT a primate, NOT a creature, NOT a mask, NOT symmetrical, NOT glowing. Its face is black "
      "in EVERY SHOT, including the first wide shot.",
      "NOBODY IN THE CARRIAGE EVER LOOKS AT IT. Passengers walk past it, sit near it and reach over it without "
      "registering that it is there.",
      "IT IS READING ALOUD FROM A CARD, NOT SPEAKING. A bone-coloured printed safety card is in its branch limb, in "
      "frame, for every line. It looks UP INTO THE LENS on the dry sentences and DOWN AT THE CARD on the accurate ones. "
      "It never winks, never smiles, never shares a joke. It is politely discharging an obligation to whoever is "
      "nearest.",
      "=== SHOT 1 — 0:00 to 0:08 — WIDE, 28mm, LOW, SLOW PUSH ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "ARTICLE THIRTEEN (looking up into the lens over the passengers' heads): \"Welcome aboard.\"\n"
      "ARTICLE THIRTEEN (looking down at the card): \"This service travels between worlds by becoming whatever "
      "building a world expects to find at the edge of departure.\"\n\n"
      "The camera is low, down at table height, standing IN the aisle among the passengers, angled obliquely down the "
      "length of the carriage — NOT square-on and NOT centred. In the near foreground, close to the lens and out of "
      "focus, is the dark shoulder and heavy coat of a standing passenger. THE CAMERA PUSHES IN SLOWLY AND CONTINUOUSLY "
      "down the aisle for the whole shot, and it does not stop before the cut. At a side table by a window on the "
      "left, among the other passengers and completely unremarked, sits ARTICLE THIRTEEN, hood brushing the luggage "
      "rack, black face turned toward us, an open card in one branch limb. It is not the first thing you notice.\n\n"
      "CUT at 0:08.",
      "=== SHOT 2 — 0:08 to 0:17 — MEDIUM, 50mm ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "ARTICLE THIRTEEN (up, into the lens): \"It is named for the three things it cannot prevent.\"\n"
      "ARTICLE THIRTEEN (down, at the card): \"A door opens when both ends agree to the journey. When one end "
      "withdraws, the door becomes a wall.\"\n\n"
      "ARTICLE THIRTEEN at its window table in three-quarter, the window of flat unprinted grey beside it, warm "
      "table-lamp key from the lamp on its own table. Its black face is clearly lit and clearly visible inside the "
      "hood. Its second branch limb rests flat and still on the white tablecloth. Behind it the carriage continues — "
      "passengers eating, reading, talking quietly, a porter moving through. PART WAY THROUGH THIS SHOT A PASSENGER "
      "WALKS BETWEEN THE CAMERA AND ARTICLE THIRTEEN, close to the lens, briefly wiping across the frame as a dark "
      "out-of-focus mass, and continues on without looking at it. Article Thirteen does not react and does not stop "
      "reading.\n\n"
      "CUT at 0:17.",
      "=== SHOT 3 — 0:17 to 0:25 — CLOSE-UP, 85mm — THIS SHOT ENDS ON THE STOP ===\n"
      "SPOKEN IN THIS SHOT — ONE TRUE SENTENCE, THEN ONE WORD THAT STOPS:\n"
      "ARTICLE THIRTEEN (reading carefully, looking down at the card, because this one is true): \"Your ticket is a "
      "promise made by somebody who is not on this train.\"\n"
      "ARTICLE THIRTEEN (its own word, looking at neither the lens nor the card): \"I—\"\n\n"
      "Tight on the BLACK FACE set deep inside the peaked hood, filling the frame. The fill is pulled almost to "
      "nothing so the black face sits far back in the hood shadow, lit only by warm lamplight from one side. Behind it, "
      "completely out of focus, the warm blur of the crowded carriage keeps moving — shapes passing, a shoulder, a "
      "hand, lamplight.\n\n"
      "After the true sentence its eyes leave the card and go to nothing at all, and it says ONE WORD of its own: the "
      "single word \"I\". AND THEN IT STOPS. NO OTHER WORD FOLLOWS IN THIS SHOT. It does not continue the sentence and "
      "says nothing else at all. It is NOT grief and NOT fear — no gasp, no tremble, no tears. It stops flatly, the way "
      "a person stops when they remember which form they are supposed to be filling in.\n"
      "HOLD ON THE STOPPED, SILENT FACE FOR TWO FULL SECONDS. THE SHOT CUTS IN THAT SILENCE, with the sentence "
      "unfinished.\n\n"
      "CUT at 0:25.",
      "=== SHOT 4 — 0:25 to 0:30 — MEDIUM, 65mm — THIS SHOT OPENS ON THE PERMITTED SENTENCE ===\n"
      "SPOKEN IN THIS SHOT, AS ITS VERY FIRST SOUND:\n"
      "ARTICLE THIRTEEN (evenly, reading, looking down at the card): \"The railway regrets nothing it has done "
      "correctly.\"\n\n"
      "It is a NEW sentence in a NEW shot, read from the card, flat and even. Then it slides the safety card back into "
      "the seat pocket beside it — an ordinary, tidy, unhurried gesture, a worker finishing a job they were required "
      "to do — folds both black branch limbs in its lap and turns its head away from camera to the window of flat "
      "unprinted grey. AS IT DOES SO, AN ORDINARY HUMAN PASSENGER SITS DOWN IN THE SEAT DIRECTLY OPPOSITE IT, settles "
      "their bag, and does not look at it even once. Article Thirteen does not move again. NOBODY ELSE SPEAKS. Nothing "
      "in the frame acknowledges that anything has ended. Hold on the stillness to the end.",
      "SOUND: the quiet interior murmur of a full carriage — low indistinct conversation, cutlery, a case being set "
      "down, all soft and far under the voice. The dry layered rustle of the paper card handled in paper limbs. NO "
      "music, NO score, NO swells, NO stingers, NO engine, NO wheels, NO wind, and no sound at all from outside the "
      "windows.",
      "Pronounce these words exactly and clearly: SERVICE, DEPARTURE, PREVENT, WITHDRAWS, PROMISE, REGRETS, "
      "CORRECTLY.",
      "PALETTE: membrane bone #EDE7DA, carriage amber #B8801F, signature red #8E2018, unprinted grey #9A968E.",
      "PHYSICS: the carriage is completely stationary and has never moved — nothing sways, rocks or vibrates, and "
      "nothing passes the windows. Nothing glows except the table lamps. " + NO_FX),
    audio=["pika/refs/a13_voice_ref.wav"])

# =====================================================================================================
# SCENE 04 v5 — Kell ALIVE inside the reconstruction
# =====================================================================================================
FILES["ep2_scene04_v5"] = video(
    "EP02_SC04_V5", "ep2_scene04_the_frost_grows_outward_v5",
    "Episode 02 · Scene 04 — INT. COLD CARRIAGE — CONTINUOUS — THE FROST GROWS OUTWARD",
    "v5 = v4 (aperture plane, Kell's pale coat, Tomas large) with the v4 fault fixed: the Sc03 corpse frame now owns "
    "his face/coat/seat only, and a matched ALIVE plate owns Shot 2. He is alive and writing while frost grows out "
    "of him.",
    ["pika/refs/ep2_kell_from_sc03.jpg", "pika/refs/ep2_kell_alive_lock.jpg", "pika/refs/ep2_coldcarriage_lock.jpg",
     "pika/refs/ep2_tomas_lock.png", "pika/refs/tomas_portrait.png", "pika/refs/beatrice_turnaround.png",
     "pika/refs/beatrice_portrait.png", "pika/refs/amina_turnaround.png", "pika/refs/evidence_plane.png"],
    j(head("FOUR"),
      "CAMERA DOCTRINE: SHOTS 1, 3 AND 4 EACH CARRY ONE slow, smooth, continuous, dead-steady MECHANICAL PUSH IN at a "
      "constant speed, beginning on the first frame and STILL MOVING WHEN THE SHOT CUTS — never accelerating, never "
      "easing, never stopping. NOT handheld: no shake, no wobble, no jitter. In each of those a named object sits CLOSE "
      "TO THE LENS and OUT OF FOCUS at one edge and slides faster than the background, giving parallax.\n"
      "SHOT 2 IS ABSOLUTELY LOCKED AND UNCUT and that is the point of the film — nothing may be suspected of hiding "
      "what happens inside it.",
      "REFERENCE PRECEDENCE — EACH IMAGE OWNS ONLY WHAT IS NAMED HERE:\n"
      "@Image1 IS A FRAME FROM THE PRECEDING SCENE. It is the authority for KELL'S FACE, HAIR, COAT AND SEAT and for "
      "THIS CARRIAGE. IT IS NOT THE AUTHORITY FOR HIS CONDITION: it shows him dead and frozen, which is correct for the "
      "room in Shots 1, 3 and 4 and WRONG for the picture inside the oval in Shot 2.\n"
      "@Image2 IS THE ABSOLUTE AUTHORITY FOR WHAT IS SEEN INSIDE THE OVAL IN SHOT 2: the same man in the same coat at "
      "the same table — ALIVE, eyes open, writing with a pen, lit cold and flat from above.\n"
      "@Image3 is a secondary reference for the carriage.\n"
      "@Image9 is a reference for the EVIDENCE PLANE's colour and matte chalky surface only.",
      "KELL, EVERYWHERE IN THIS FILM: " + KELL_COAT + ". He sits at his RIGHT-HAND WINDOW TABLE with a white "
      "tablecloth, an amber pleated table lamp beside him and a clear dry window onto a flat white frozen lake. The "
      "carriage around him is warm walnut panelling with amber lamps and occupied tables.",
      "THE EVIDENCE PLANE IS AN APERTURE. THIS IS THE MOST IMPORTANT INSTRUCTION ABOUT IT:\n"
      "It is a standing OVAL about forty-five centimetres tall, held upright in the air. ITS EDGE IS A HARD SATURATED "
      "MATTE RED RIM about two centimetres wide — chalky, zero gloss, and it NEVER GLOWS and emits no light at all.\n"
      "EVERYTHING INSIDE THAT RIM IS A DIFFERENT PICTURE. YOU SEE THROUGH THE OVAL, as through a hole cut in the air, "
      "into another moment. It is NOT a solid disc, NOT a paddle, NOT a plate, NOT a screen, NOT a mirror and NOT a "
      "coloured filter. It is a HOLE IN THE AIR WITH A RED EDGE.\n"
      "THE RED NEVER SPREADS BEYOND THAT RIM. OUTSIDE THE OVAL THE CARRIAGE IS COMPLETELY UNAFFECTED WARM WALNUT AND "
      "AMBER LAMPLIGHT. INSIDE THE OVAL THE IMAGE IS COLD, FLAT AND BLUE-WHITE — the light of an overcast pier at "
      "6500K, falling from above. Every frame containing the oval carries TWO LIGHTING STATES SIDE BY SIDE THAT NEVER "
      "BLEND, with one hard red line between them.",
      FROST_OUT + " In this film the only frost is on Kell and on the cloth and table immediately around him. The "
      "windows are CLEAR AND DRY.",
      "CAST:\n" + beatrice("@Image6 and @Image7 are") + "\n" + amina("@Image8 is") + "\n"
      + tomas("@Image4 and @Image5 are", "@Image4"),
      "=== SHOT 1 — 0:00 to 0:06 — MEDIUM, 40mm, SLOW PUSH ===\n"
      "NOBODY SPEAKS IN THIS SHOT.\n\n"
      "BEATRICE — the woman with the high topknot in the black wrap coat with the oxblood panel — RAISES THE RED OVAL "
      "with one hand and turns it in the air until its long axis is square to the seated frozen man. IT STOPS OF ITS "
      "OWN ACCORD and hangs there, upright, unsupported. As soon as it is square, THE INSIDE OF THE OVAL IS PLAINLY A "
      "DIFFERENT PICTURE FROM THE ROOM AROUND IT — cold and blue-white where the carriage is warm and amber. CLOSE TO "
      "THE LENS AND OUT OF FOCUS AT ONE EDGE, AMINA'S GLASS SAMPLE PODS ride past on their armatures. THE MOVE: the "
      "camera pushes in slowly and continuously and is still advancing at the cut.\n\n"
      "CUT at 0:06.",
      "=== SHOT 2 — 0:06 to 0:17 — INSERT SQUARE THROUGH THE OVAL, 65mm, ABSOLUTELY LOCKED, ONE UNBROKEN TAKE ===\n"
      "SPOKEN IN THIS SHOT (all off screen, over the picture):\n"
      "AMINA (off screen): \"That's the wrong direction.\"\n"
      "BEATRICE (off screen): \"Say more.\"\n"
      "AMINA (off screen): \"Cold enters a body. It doesn't leave one. There is no ecology in which that happens.\"\n\n"
      "The camera is square-on to the oval, close enough that the RED RIM RUNS AROUND THE EDGE OF THE FRAME with the "
      "warm walnut carriage and an amber lamp visible OUTSIDE it at the corners. THE CAMERA DOES NOT MOVE AT ALL AND "
      "THERE IS NO CUT ANYWHERE INSIDE THIS SHOT.\n\n"
      "SEEN THROUGH THE OVAL — EXACTLY @Image2: KELL, ALIVE, EARLIER THIS MORNING. The same man in the same PALE "
      "GREY-OATMEAL OVERCOAT at the same window table, lit COLD, FLAT AND BLUE-WHITE from above. HIS EYES ARE OPEN AND "
      "ON HIS WORK. HIS SKIN IS A LIVING WARM COLOUR, with colour in his lips and cheeks. AT THE START OF THE SHOT HIS "
      "COAT, HIS HANDS AND THE CLOTH ARE CLEAN AND DRY. He holds a PEN in his right hand and IS WRITING on a cream "
      "form, steadily, like a man finishing a form before a deadline he has already calculated. He is calm and busy — "
      "NOT shivering, NOT distressed, NOT gasping and NOT struggling.\n\n"
      "AND ACROSS THE WHOLE ELEVEN SECONDS, IN COMPLETE SILENCE, WHITE FROST GROWS OUTWARD FROM THE CENTRE OF HIS "
      "CHEST — starting as a small star at his sternum and advancing in fine crystal needles ACROSS HIS PALE COAT, then "
      "ONTO THE WHITE TABLECLOTH, then ACROSS THE BACKS OF HIS OWN WRITING HANDS, radiating AWAY from him in every "
      "direction at once. HE KEEPS WRITING THROUGH ALL OF IT, EYES OPEN, AND NEVER LOOKS AT IT. AT THE END OF THE SHOT "
      "HE IS STILL ALIVE AND STILL WRITING, his hands rimed white. That is the tragedy: he budgeted.\n"
      "SOUND INSIDE THE FIELD: NOTHING AT ALL — no chair, no paper, no pen, no breath. Only Amina's and Beatrice's "
      "voices from the room, and the carriage hum outside the field.\n"
      "Amina says her lines as a correct professional stating a correct professional fact — an anomaly in her data, "
      "NOT a revelation.\n\n"
      "CUT at 0:17.",
      "=== SHOT 3 — 0:17 to 0:23 — CLOSE-UP, 85mm, SLOW PUSH — HE IS LARGE IN THE FRAME ===\n"
      "NOBODY SPEAKS IN THIS SHOT.\n\n"
      "A LARGE FRONT-ON CLOSE-UP: TOMAS GREY steps in through the vestibule door from the pier and stops. HIS HEAD AND "
      "SHOULDERS FILL THE FRAME. THE TALL SMOOTH CREAM TUBE COLLAR IS PLAINLY VISIBLE ACROSS THE BOTTOM OF THE FRAME "
      "and THE ENGRAVED BLACK RIBBON LOOPS THROUGH THE FRAME BESIDE HIS HEAD. COLD blue-white spill from the open "
      "vestibule BEHIND him, warm amber in front.\n"
      "HE HAS COME IN FROM A PLATFORM AT MINUS FOURTEEN AND THE AIR DIRECTLY IN FRONT OF HIS FACE AND MOUTH IS "
      "COMPLETELY CLEAR AND TRANSPARENT. The walnut behind him stays crisp right up to his lips. He does not stamp his "
      "feet, rub his hands or remark on the cold, because he has not noticed it. Nobody looks at this. He looks off "
      "screen at the reconstruction. THE MOVE: a slow continuous push, still advancing at the cut.\n\n"
      "CUT at 0:23.",
      "=== SHOT 4 — 0:23 to 0:30 — MEDIUM TWO-SHOT, 50mm, SLOW PUSH ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "TOMAS: \"He was not chilled. He was withdrawn from.\"\n"
      "BEATRICE: \"By what?\"\n"
      "TOMAS: \"By something with an account.\"\n\n"
      "BEATRICE AND TOMAS STAND SIDE BY SIDE, BOTH AT FRAME LEFT AND BOTH TURNED TO FACE TOWARD FRAME RIGHT, both "
      "looking at the red oval which hangs at frame right with the cold blue-white picture inside it. NEITHER OF THEM "
      "TURNS TOWARD THE OTHER AND NEITHER LOOKS AT THE OTHER. Both faces are split: WARM AMBER from the room on one "
      "side, COLD BLUE-WHITE from inside the oval on the other. The red stays inside its rim and falls on neither of "
      "them. THE MOVE: a slow continuous push in, still advancing at the cut.\n"
      "HE THROWS THE LAST LINE AWAY COMPLETELY — an account is simply the most accurate available word. NOBODY REACTS "
      "TO IT. END on the two of them still watching the oval.",
      "SOUND: a low continuous carriage hum throughout. Small precise mechanical clicks from Amina's pod armatures, "
      "unsynchronised. The vestibule door closing on the wind. TOTAL SILENCE from inside the reconstruction. NO music, "
      "no score, no swells, no drone and no stingers at any point. " + CROWD_VOICES,
      "Pronounce these words exactly and clearly: DIRECTION, ECOLOGY, CHILLED, WITHDRAWN, ACCOUNT.",
      "PALETTE: evidence red #C7332B, rime white #E9F1F4, carriage amber #B8801F, pier blue #8FA3B0.",
      "PHYSICS: frost grows outward from a body and never inward from a window, an edge or a frame. The oval never "
      "glows and emits no light. Nothing glows anywhere. " + NO_FX))

# =====================================================================================================
# SCENE 08 v2 — the abort on a cut, nothing on Tomas, both jokes restored
# =====================================================================================================
FILES["ep2_scene08_v2"] = video(
    "EP02_SC08_V2", "ep2_scene08_three_seconds_to_the_wrist_v2",
    "Episode 02 · Scene 08 — EXT. HESSEL PIER — RECIPROCITY HOUSE — THREE SECONDS TO THE WRIST",
    "v2: the compliment is cut off BY A CUT (§66 — v1 completed it); the three seconds stay one unbroken take in "
    "their own shot; frost scoped to Pikk only (v1 leaked it onto Tomas's 'nothing' hand); 'It was not intended as "
    "a comfort.' restored as the button; Tomas large and on his verified plate; Amina to her sheet.",
    ["pika/refs/ep2_recip_lock_v3.jpg", "pika/refs/ep2_slotwall_from_sc01.jpg", "pika/refs/amina_pods.png",
     "pika/refs/pikk_turnaround.png", "pika/refs/pikk_portrait.png", "pika/refs/amina_turnaround.png",
     "pika/refs/ep2_tomas_lock.png", "pika/refs/tomas_portrait.png", "pika/refs/beatrice_turnaround.png"],
    j(head("FIVE"),
      "REFERENCE PRECEDENCE: @Image1 IS THE ABSOLUTE AUTHORITY for this chamber. @Image2 IS THE AUTHORITY FOR THE "
      "STONE ITSELF. @Image3 IS THE AUTHORITY FOR THE SAMPLE PODS: small clear glass-and-ceramic cylinders on thin dark "
      "articulated metal armatures.",
      CHAMBER, TWO_LIGHTS + " Every face is lit cold on one side and warm on the other. WHICH SIDE OF A FACE IS WARM "
      "IS INFORMATION.", SLOT_GRAMMAR,
      "CAST — FOUR PEOPLE:\n" + pikk("@Image4 and @Image5 are", "") + "\n" + amina("@Image6 is") + "\n"
      + tomas("@Image7 and @Image8 are", "@Image7") + "\n" + beatrice("@Image9 is"),
      "NOBODY INSIDE THIS CHAMBER PRODUCES VISIBLE BREATH. Out through the doorway on the pier, every waiting person's "
      "breath IS visible in white plumes.",
      "THE FROST IN THIS FILM BELONGS TO PIKK'S HAND AND NOTHING ELSE. It appears in SHOTS 3 AND 4 ONLY, on his hand "
      "only, growing outward from his knuckles into the air. In SHOT 5 TOMAS'S HAND STAYS PINK AND CLEAN FOR THE "
      "WHOLE SHOT.",
      "=== SHOT 1 — 0:00 to 0:05 — MEDIUM, 50mm, LOCKED, LOW AT SILL HEIGHT ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "AMINA (plainly, to the room, with the slightly apologetic courtesy of a scientist about to use a colleague as "
      "an instrument): \"Volunteers.\"\n"
      "PIKK (off screen, easy, bored, already walking): \"It's a warm hole in a wall, Doctor.\"\n\n"
      "The camera is LOW, its lens level with the hollowed stone trough, so the row of small warm slots sits at our "
      "own eye height. CLOSE TO THE LENS AND OUT OF FOCUS AT FRAME LEFT is THE BACK OF PIKK'S HEAD AND SHOULDER — we "
      "are standing behind him. In the middle distance at frame right AMINA has clamped her two glass pods on their "
      "armatures either side of ONE slot. DEEPEST IN THE SHOT, small, far from the wall and fully in the cold doorway "
      "light, stand BEATRICE and TOMAS. After Amina's one word NOBODY MOVES FOR ONE FULL SECOND. Then PIKK'S HEAD AND "
      "SHOULDER SIMPLY LEAVE THE FOREGROUND — he walks out of the near edge of frame toward the wall. THE CAMERA DOES "
      "NOT MOVE when he goes.\n\n"
      "CUT at 0:05.",
      "=== SHOT 2 — 0:05 to 0:08 — CLOSE-UP ON PIKK'S FACE, 85mm, LOCKED — THE LINE IS CUT OFF BY THE CUT ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "PIKK (throwing it away, half-audible, an ordinary workplace remark filling a silence): \"Honestly, this lot "
      "aren't the worst I've worked—\"\n\n"
      "Close on PIKK at the wall in three-quarter, warm amber from the slot below lighting his chin, cold doorway light "
      "on the back of his head. Below frame he is pushing his hand into the slot; we see only his face, his shoulder "
      "moving as he reaches. HIS FACE IS CASUAL AND BORED. THE SHOT ENDS WHILE HIS MOUTH IS STILL OPEN ON THE WORD "
      "\"worked\". The sentence is never finished — the cut takes it.\n\n"
      "CUT at 0:08.",
      "=== SHOT 3 — 0:08 to 0:12 — CLOSE-UP, 85mm, ABSOLUTELY LOCKED, REAL TIME — THE HAND ===\n"
      "NOBODY SPEAKS IN THIS SHOT. HE MAKES NO SOUND OF PAIN, BECAUSE IT DOES NOT HURT YET.\n\n"
      "Tight on ONE slot in the dark granite with PIKK'S HAND in it up to the wrist — compact, olive-grey, the "
      "soot-grey sleeve pushed back. HUGE AND COMPLETELY OUT OF FOCUS AT FRAME RIGHT, CLOSE TO THE LENS, is ONE of the "
      "two glass pods on its armature; the second pod sits sharp and small on the far side of the slot. A HARD WARM "
      "AMBER RAKE from inside the slot lies across the back of his hand at the start.\n"
      "ACROSS THREE SECONDS, IN ONE UNBROKEN TAKE, ALL OF THIS HAPPENS AT ONCE: THE AMBER RAKE INSIDE THE SLOT DIMS "
      "SMOOTHLY DOWN AND GOES OUT, so the hand ends lit only by flat cold daylight. HIS NAIL BEDS GO WHITE FIRST, then "
      "the whiteness travels up the fingers to the second knuckle, then across the back of the hand, then to the "
      "wrist. DELICATE WHITE FROST GROWS OUTWARD FROM HIS KNUCKLES INTO THE AIR in fine needles. The two pods CLICK "
      "HARD, TWICE.\n"
      "THE CAMERA DOES NOT MOVE AT ALL and THERE IS NO CUT INSIDE THIS SHOT.\n\n"
      "CUT at 0:12.",
      "=== SHOT 4 — 0:12 to 0:16 — MEDIUM, 40mm, HANDHELD ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "AMINA (fast, loud, two words, the only time she raises her voice all season): \"Out. Out.\"\n"
      "PIKK (flat, puzzled, unhurried, looking at his hand): \"That's my hand.\"\n\n"
      "HANDHELD, loose and alive. Never a whip pan, never a jolt. CLOSE TO THE LENS AND OUT OF FOCUS AT FRAME LEFT IS "
      "BEATRICE'S SHOULDER AND THE SIDE OF HER HEAD — we stand behind the person who did not step forward, and she "
      "does not move at all. TOMAS ENTERS AT FRAME RIGHT CLOSE TO THE LENS AND LARGE IN THE FRAME — his head, his "
      "tall cream tube collar and the looping engraved ribbon plainly visible — crossing from the cold doorway light "
      "into the warm slot light, and takes PIKK by the elbow and lifts his hand out of the wall with the unhurried "
      "competence of a man closing a drawer. PIKK'S HAND IS BLANCHED WHITE TO THE WRIST, rimed at the knuckles, frost "
      "still growing outward from it. He looks at it with mild professional annoyance, the way a man looks at "
      "something he has put down and cannot immediately find.\n\n"
      "CUT at 0:16.",
      "=== SHOT 5 — 0:16 to 0:30 — CLOSE-UP, 85mm, ABSOLUTELY LOCKED — THE SAME FRAME AS SHOT 3 ===\n"
      "SPOKEN IN THIS SHOT, IN THIS ORDER:\n"
      "AMINA (off screen, reading her own notebook back, clipped and appalled — the unit is JOULES, a unit of energy): "
      "\"Four hundred thousand joules. Three seconds. One person.\"\n"
      "(then FOUR SECONDS IN WHICH NOBODY SPEAKS)\n"
      "BEATRICE (off screen): \"Why not you?\"\n"
      "TOMAS (off screen, a diagnosis, flat, informative, entirely without malice): \"I don't like any of you.\"\n"
      "(ONE FULL SECOND OF SILENCE)\n"
      "TOMAS (off screen, a correction, because he cannot let an inaccurate impression stand): \"It was not intended "
      "as a comfort.\"\n\n"
      "THIS IS THE IDENTICAL CAMERA POSITION, LENS AND FRAMING AS SHOT 3: the same slot, the same out-of-focus pod "
      "huge at frame right, the same second pod sharp beyond it. The audience must recognise this frame. THE ONLY TWO "
      "DIFFERENCES ARE THE HAND AND THE LIGHT. TOMAS'S HAND — a tall man's pale hand with the black sleeve and the "
      "TURNED-BACK CREAM CUFF of his robe-coat at the wrist — goes into the SAME slot and stays there. Deep in the "
      "background, small and out of focus, PIKK holds his white hand against his chest, so both hands are in one "
      "frame.\n"
      "FOR FOUR FULL SECONDS NOTHING HAPPENS, AND THE NOTHING IS THE POINT: THE AMBER LIGHT INSIDE THE SLOT STAYS FULLY "
      "LIT, STEADY AND UNCHANGED. TOMAS'S FINGERS STAY PINK AND CLEAN. THE PODS STAY STILL AND SILENT. There is no "
      "cutaway, no music and no sound cue — the audience waits for something that never arrives. Then he takes his "
      "hand out, turns it over once, looks at it, and it is completely ordinary.\n"
      "THE LAST LINE, \"It was not intended as a comfort.\", IS THE LAST SOUND IN THE FILM. He finishes every word "
      "of it. Nothing is said after it.",
      "SOUND: a flat continuous cold wind at the doorway, unchanged and indifferent from the first frame to the last. "
      "Pod armatures clicking. A pencil on paper. THE SLOT ITSELF MAKES NO SOUND AT ALL AT ANY POINT. The chamber has "
      "a tight dry acoustic with NO reverb tail. NO MUSIC, no score, no swells, no drone, no stingers and no sound "
      "effect on any cut. " + CROWD_VOICES,
      "Pronounce these words exactly and clearly: VOLUNTEERS, DOCTOR, HONESTLY, WORKED, JOULES, INTENDED, COMFORT.",
      "PALETTE: slot amber #A9721F, frost white #E9F1F4, worn stone #B9B1A2, slate blue #5B6E7E, dark granite #4A4B48.",
      "PHYSICS: cold injury behaves as real cold injury — white at the nail beds first, then progressively up toward "
      "the body, no immediate pain, no reversal. The stone is never frosted. Nothing glows anywhere except the faint "
      "warm amber inside the slots. " + NO_FX))

# =====================================================================================================
# SCENE 14 v3 — the solution, the route still hungry, the pods turn to Beatrice
# =====================================================================================================
FILES["ep2_scene14_v3"] = video(
    "EP02_SC14_V3", "ep2_scene14_the_solution_v3",
    "Episode 02 · Scene 14 — EXT. HESSEL PIER — RECIPROCITY HOUSE — THE SOLUTION",
    "v3: Shot 1 keeps v2's lateral track (no dialogue — the blocking is the story); Beatrice delivers the solution "
    "OUTSIDE on the pier so no amber can key her (the v1/v2 fault); Tomas large; NEW BUTTON: Amina's pods swing round "
    "and lock onto Beatrice — the route's next source (the script's own Sc14 physics note, now shown). Built for the "
    "clue-replay inserts in the edit.",
    ["pika/refs/ep2_recip_lock_v3.jpg", "pika/refs/ep2_slotwall_from_sc01.jpg", "pika/refs/ep2_pier_lock.jpg",
     "pika/refs/beatrice_turnaround.png", "pika/refs/beatrice_portrait.png", "pika/refs/ep2_tomas_lock.png",
     "pika/refs/amina_turnaround.png", "pika/refs/amina_pods.png", "pika/refs/pikk_turnaround.png"],
    j(head("FOUR"),
      "CAMERA DOCTRINE: SHOTS 1, 2 AND 3 EACH CARRY ONE slow, smooth, continuous, dead-steady MECHANICAL DOLLY MOVE at "
      "a constant speed, beginning on the first frame and STILL MOVING WHEN THE SHOT CUTS — never accelerating, never "
      "stopping, never reversing. NOT handheld: no shake, no wobble, no whip pan. In each of those shots a named object "
      "sits CLOSE TO THE LENS and OUT OF FOCUS at one edge and slides across the frame faster than everything behind "
      "it, giving strong parallax. SHOT 4 IS ABSOLUTELY LOCKED: the camera stops because something is about to happen "
      "inside the frame.",
      "REFERENCE PRECEDENCE: @Image1 IS THE AUTHORITY FOR THE CHAMBER in Shots 1, 3 and 4. @Image2 IS THE AUTHORITY "
      "FOR THE STONE AND THE SLOTS. @Image3 IS THE AUTHORITY FOR THE PIER OUTSIDE in Shot 2 — the frozen white lake, "
      "the flat white sky and the waiting people with their roped cases. @Image8 IS THE AUTHORITY FOR AMINA'S GLASS "
      "PODS on their thin dark articulated armatures.",
      CHAMBER,
      "LIGHT: " + TWO_LIGHTS + " IN SHOTS 1, 3 AND 4 every face inside the chamber is lit cold on one side and warm on "
      "the other. SHOT 2 IS THE DELIBERATE EXCEPTION AND IT IS PART OF THIS RULE: Shot 2 happens OUTSIDE, on the open "
      "pier, with the chamber BEHIND THE CAMERA, so the only light in that shot is flat cold white daylight.",
      "ALL FOUR PEOPLE ARE STANDING ON THEIR FEET. NOBODY SITS DOWN AT ANY POINT and THE STONE BENCH STAYS EMPTY. "
      "Inside the chamber everyone stands A CLEAR METRE BACK FROM THE WALL, arms down, hands at their sides, and the "
      "band of stone floor between them and the slots stays empty. NOBODY TOUCHES THE WALL.",
      "CAST:\n" + beatrice("@Image4 and @Image5 are") + "\n" + tomas("@Image6 is", "@Image6") + "\n"
      + amina("@Image7 is") + "\n" + pikk("@Image9 is", PIKK_POCKET),
      "THE PODS — THE BUTTON OF THIS FILM, SET UP IN EARLIER SCENES: Amina's glass pods swing on their armatures to "
      "point at whatever the route is drawing from, the way they swung toward the frozen man. Until the last shot they "
      "hang loosely at her sides.",
      "=== SHOT 1 — 0:00 to 0:05 — MEDIUM, 50mm, LATERAL TRACK ALONG THE WALL — NO DIALOGUE ===\n"
      "NOBODY SPEAKS IN THIS SHOT.\n\n"
      "The camera is LOW, its lens level with the hollowed trough, looking ALONG the curved wall so the small amber "
      "slots and the worn trough recede in perspective, the bright doorway beyond. THE MOVE: THE CAMERA TRACKS SLOWLY "
      "AND CONTINUOUSLY SIDEWAYS along the wall, following the curve, THE WAY A HAND USED TO. Right up against the lens "
      "and out of focus, the worn trough and the near lip of the slots STREAM PAST, much faster than the people beyond "
      "them, and the four figures are revealed one after another: PIKK, his right hand a fist in his pocket; AMINA, "
      "her notebook open, her pencil moving steadily down the last column; TOMAS, still; and BEATRICE, nearest the "
      "doorway, who turns and walks out through it onto the pier as the shot ends.\n\n"
      "CUT at 0:05.",
      "=== SHOT 2 — 0:05 to 0:16 — CLOSE-UP, 85mm, OUTSIDE ON THE PIER, SLOW PUSH ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "BEATRICE (reporting, flat, procedural, throwing it away): \"Forty-one boarded. Forty of them were being polite. "
      "One of them meant it.\"\n"
      "(a beat in which she does not react to her own sentence)\n"
      "BEATRICE (the same flat voice): \"He wasn't murdered. He was the only thing plugged in.\"\n"
      "PIKK (off screen, from inside the chamber, a classification correction and the angriest he has been all day): "
      "\"He wasn't a passenger. He was infrastructure.\"\n\n"
      "BEATRICE STANDS OUTSIDE, ON THE OPEN PIER, a step beyond the doorway, FACING THE LENS. THE CAMERA IS OUT ON THE "
      "PIER WITH HER AND THE CHAMBER IS BEHIND THE CAMERA. Behind her head there is only the FLAT WHITE SKY and the "
      "FROZEN WHITE LAKE, with small out-of-focus waiting figures far along the pier. THE ONLY LIGHT ON HER IS FLAT "
      "COLD WHITE DAYLIGHT, keying her face fully and evenly from the front. No slot, no lamp and no warm source "
      "exists anywhere in this shot. Her breath is visible in the cold. Her whole head is inside the frame with clear "
      "space above it. THE MOVE: THE CAMERA PUSHES IN ON HER FACE VERY SLOWLY AND CONTINUOUSLY, and a roped suitcase "
      "close to the lens at one edge slides out of shot as it advances.\n"
      "SHE REPORTS; SHE DOES NOT PERFORM THE DEDUCTION. No triumph, no pause before any good line.\n\n"
      "CUT at 0:16.",
      "=== SHOT 3 — 0:16 to 0:25 — CLOSE-UP, 85mm, INSIDE, SLOW DOLLY IN ON TOMAS — HE IS LARGE ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "TOMAS (quietly, still looking at the wall, heavier than the first time he said it): \"He volunteered to a route "
      "that had closed every other door. That is not consent. That is the last option wearing a signature.\"\n\n"
      "Back inside the chamber. A LARGE FRONT-ON CLOSE-UP OF TOMAS, his head and shoulders filling the frame, THE TALL "
      "SMOOTH CREAM TUBE COLLAR plainly across the bottom of frame and THE ENGRAVED BLACK RIBBON arcing past his "
      "shoulder. Warm amber on the wall side of his face, cold on the doorway side. The air in front of his face is "
      "completely clear. THE MOVE: a slow continuous dolly in, the dark curve of the wall sliding past close to the "
      "lens, still advancing at the cut. NOBODY ARGUES WITH HIM AND NOBODY ANSWERS HIM.\n\n"
      "CUT at 0:25.",
      "=== SHOT 4 — 0:25 to 0:30 — MEDIUM CLOSE, 50mm, ABSOLUTELY LOCKED — THE PODS TURN ===\n"
      "SPOKEN IN THIS SHOT, AS ITS FIRST SOUND:\n"
      "BEATRICE (off screen, from the doorway, the next procedural step, without heat): \"Then I want the name on the "
      "consolidation order.\"\n"
      "AFTER THAT LINE NOBODY SPEAKS AGAIN.\n\n"
      "Inside the chamber. AMINA stands at FRAME RIGHT, close to the lens and large, her face sharp, her open notebook "
      "in her hands, her GLASS PODS on their armatures hanging at her shoulder in the near foreground. THE BRIGHT "
      "DOORWAY IS AT THE FAR LEFT EDGE OF THE FRAME, partially cropped by it, and BEATRICE STANDS IN IT — small, "
      "backlit by the white sky, a dark figure in a bright rectangle, her breath visible.\n"
      "AS BEATRICE FINISHES HER LINE, ALL OF AMINA'S GLASS PODS SWING ROUND ON THEIR ARMATURES AT ONCE — smoothly, "
      "all together, like a row of heads turning — AND LOCK WITH ONE HARD MECHANICAL CLICK, ALL OF THEM POINTING "
      "ACROSS THE CHAMBER AT THE DOORWAY, AT BEATRICE. Amina looks down at the pods. Then she looks up across the "
      "chamber at Beatrice in the doorway. HER PENCIL STOPS ON THE PAGE. She says nothing. Beatrice does not notice "
      "and does not look at the pods. END on Amina looking at Beatrice.",
      "SOUND: flat continuous cold wind at the doorway, cut off abruptly by the stone; outside on the pier the wind is "
      "open and wide. The chamber has a tight dry acoustic with NO reverb tail. THE SLOT RANK IS SILENT. The pods' "
      "single hard click in Shot 4. NO music, no score, no swells, no drone and no stingers at any point, and no sound "
      "cue on the pods. " + CROWD_VOICES,
      "Pronounce these words exactly and clearly: BOARDED, POLITE, MURDERED, PLUGGED, INFRASTRUCTURE, VOLUNTEERED, "
      "CONSENT, SIGNATURE, CONSOLIDATION.",
      "PALETTE: worn stone #B9B1A2, slot amber #A9721F, pier blue #8FA3B0, frost white #E9F1F4.",
      "PHYSICS: nothing glows anywhere except the faint amber inside the slots, which never changes in this film. The "
      "pods are mechanical, never glow and make no sound except their click. " + NO_FX))

# =====================================================================================================
# SCENE 16 v4 — Pikk refuses; Beatrice accepts; then she goes to pay it herself
# =====================================================================================================
FILES["ep2_scene16_v4"] = video(
    "EP02_SC16_V4", "ep2_scene16_the_crossing_begins_no_v4",
    "Episode 02 · Scene 16 — EXT. HESSEL PIER — THE CROSSING BEGINS — NO",
    "v4: handheld while the route fails, locked on Pikk's refusal (kept from v1); Beatrice's nod shares the frame "
    "with his white hand (v1's best deviation); NEW CLIFF: she walks to the Reciprocity House to pay it herself, frost "
    "at her throat (plate ep2_beatrice_frost_lock). Tomas and Ysra are out of this film (Ysra's exit is insert P3); "
    "ep2_breath_lock is not used because it contains a wrong-collar Tomas (§154).",
    ["pika/refs/ep2_pier_lock.jpg", "pika/refs/ep2_pikkhand_lock.png", "pika/refs/pikk_turnaround.png",
     "pika/refs/beatrice_turnaround.png", "pika/refs/beatrice_portrait.png", "pika/refs/ep2_beatrice_frost_lock.jpg",
     "pika/refs/amina_turnaround.png", "pika/refs/ep2_recip_lock_v3.jpg"],
    j(head("FOUR"),
      "CAMERA POLICY, AND IT IS THE POINT OF THIS FILM: THE CAMERA IS HANDHELD WHILE THE ROUTE IS FAILING, AND IT "
      "GOES COMPLETELY STILL THE INSTANT A MAN MAKES A CLEAR CHOICE. Shots 1 and 2 and the first part of Shot 3 are "
      "HANDHELD — loose, alive, breathing; never a whip pan, never a jolt. Then, on the one-word refusal in Shot 3, THE "
      "FRAME GOES ABSOLUTELY STILL AND STAYS STILL FOR THE REST OF THE FILM, including all of Shot 4.",
      "REFERENCE PRECEDENCE: @Image1 IS THE AUTHORITY FOR THE PIER — its low dark granite sea wall with the RANK OF "
      "SMALL WARM AMBER SLOTS set into it, the flat white overcast sky, the frozen white lake and the waiting "
      "population with their roped cases. @Image2 IS THE AUTHORITY FOR PIKK'S INJURED RIGHT HAND. @Image6 IS THE "
      "AUTHORITY FOR HOW BEATRICE LOOKS WHILE THE FROST IS ON HER — the rime on the back of her right hand and the "
      "small starburst at the base of her throat. @Image8 IS THE AUTHORITY FOR THE SMALL DARK GRANITE CHAMBER AT THE "
      "PIER HEAD (the Reciprocity House) and its doorway.",
      "THE SLOT RANK IS FAILING, AND ITS BRIGHTNESS IS A READOUT: the row of slots along the pier wall DIMS, HOLDS, AND "
      "COMES BACK — out of rhythm, at uneven intervals — AND EACH TIME IT COMES BACK DIMMER THAN BEFORE. All the slots "
      "do this together, never one at a time and never in a wave. A FAINT DRY TICK comes from the rank each time it "
      "draws — small, mechanical, unmusical. Nobody reacts to it.",
      "THE FORTY ARE COMPETENT AND NEVER A SPECTACLE. They board in an order they arranged themselves — CHILDREN "
      "FIRST, THEN THE OLDEST, THEN EVERYONE ELSE. Ropes come off cases. Nobody pushes, hurries, panics, shouts or "
      "begs. Among them are people with LONG POINTED EARS and OLIVE-GREY SKIN and TIRELESS TRAVELLERS in rust-brown "
      "layers carrying full-size panelled wooden DOORS on their backs. EVERY PERSON'S BREATH IS VISIBLE in white "
      "plumes. " + CROWD_VOICES,
      "CAST — THREE PEOPLE ARE NAMED IN THIS FILM:\n" + beatrice("@Image4 and @Image5 are") + "\n"
      + amina("@Image7 is") + "\n" + pikk("@Image3 is", "His RIGHT HAND is the injured one, exactly as @Image2: "
      "blanched dead chalk-white from the fingertips to a SHARP LINE AT THE WRIST, fine white rime on the knuckles, the "
      "fingers HALF-CURLED AND RIGID, stopped part-way between open and closed. It never moves, never pinks up and "
      "never closes."),
      "THE FROST ON BEATRICE — A NEW FACT IN THIS FILM, SHOWN AND NEVER MENTIONED: the route has started to draw from "
      "her. On the BACK OF HER RIGHT HAND fine white rime feathers outward from the knuckles, and at the BASE OF HER "
      "THROAT on the edge of her black collar there is a small starburst of rime, exactly as @Image6. It is SMALL, it "
      "is ONLY ON HER, and NOBODY LOOKS AT IT OR MENTIONS IT. HER BREATH IS STILL VISIBLE — she is alive and warm.",
      "=== SHOT 1 — 0:00 to 0:07 — WIDE, 32mm, HANDHELD, STANDING BACK — NO DIALOGUE ===\n"
      "NOBODY SPEAKS IN THIS SHOT.\n\n"
      "HANDHELD, wide, loose, standing well back from the boarding. Roped suitcases and a wool shoulder pass close to "
      "the lens, out of focus. The forty board through the open door of a warm-lit carriage in an orderly line, "
      "unhurried and calm, breath rising in many separate plumes. Along the granite wall behind them THE SLOT RANK "
      "DIMS, HOLDS, AND COMES BACK A LITTLE LESS, twice in this shot.\n\n"
      "CUT at 0:07.",
      "=== SHOT 2 — 0:07 to 0:14 — MEDIUM, 50mm, HANDHELD, TIGHT ON AMINA ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "AMINA (an engineer reading a number): \"Draw's climbing. Rank's at sixty and falling.\"\n"
      "BEATRICE (off screen): \"How many get through?\"\n"
      "AMINA: \"At this rate? Thirty-one.\"\n\n"
      "HANDHELD and close on AMINA, cold flat key, her breath fast and visible. She reads her glass pods. A boarding "
      "passenger crosses close to the lens. There are forty people on this pier and NOBODY SAYS SO.\n\n"
      "CUT at 0:14.",
      "=== SHOT 3 — 0:14 to 0:24 — MEDIUM, 40mm, HANDHELD AND THEN LOCKED ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "PIKK: \"No.\"\n"
      "(a beat of silence)\n"
      "PIKK (flat, giving the reason once and then stopping): \"You spent me last week. I'm not a battery with a union "
      "card.\"\n"
      "(Beatrice nods; a small pause)\n"
      "PIKK (quiet, surprised, quickly covered): \"Thank you.\"\n\n"
      "THE COMPOSITION: BEATRICE IS IN THE NEAR FOREGROUND AT FRAME LEFT, close to the lens and large, her face in "
      "three-quarter, looking at Pikk; her own breath visible. PIKK stands in the middle distance at FRAME RIGHT. The "
      "boarding queue keeps moving behind him and nobody in it looks round.\n"
      "HANDHELD at first. PIKK TAKES HIS RIGHT HAND OUT OF HIS COAT POCKET AND HOLDS IT UP AT CHEST HEIGHT, exactly as "
      "@Image2. His face is calm and matter-of-fact — not angry, not pleading, not apologetic, not making a speech. ON "
      "HIS ONE-WORD REFUSAL THE FRAME GOES COMPLETELY STILL, and it stays still for the rest of the film.\n"
      "BEATRICE looks at his hand. She looks at his face. THEN SHE NODS ONCE — one small downward nod — AND HER MOUTH "
      "STAYS CLOSED. She asks nothing, offers nothing and looks at nobody else. At her side, in the lower left of frame, "
      "the rime on the back of her own right hand is visible, and nobody looks at it.\n\n"
      "CUT at 0:24.",
      "=== SHOT 4 — 0:24 to 0:30 — MEDIUM, 35mm, ABSOLUTELY LOCKED, FROM INSIDE THE CHAMBER DOORWAY — NO DIALOGUE ===\n"
      "NOBODY SPEAKS IN THIS SHOT.\n\n"
      "THE CAMERA IS JUST INSIDE THE DOORWAY OF THE SMALL DARK GRANITE CHAMBER (@Image8), low, LOOKING OUT along the "
      "bright pier. Far behind, small and out of focus, the boarding queue moves and the dim slot rank runs along the "
      "pier wall. THE CAMERA DOES NOT MOVE.\n"
      "BEATRICE WALKS TOWARD THE CAMERA, out of the bright pier, unhurried and decided, PUSHING HER RIGHT SLEEVE BACK "
      "OFF HER WRIST AS SHE COMES. Her breath is visible. As she comes close to the lens, THE SMALL STARBURST OF RIME "
      "AT THE BASE OF HER THROAT AND THE FROST ON THE BACK OF HER RIGHT HAND BECOME PLAIN — exactly @Image6. She does "
      "not look back. She does not look at the camera. She walks past the lens at frame right, into the chamber, and "
      "out of frame. CUT AS SHE PASSES THE LENS.",
      "SOUND: boarding — cases on stone, hemp ropes, forty people breathing, a child's voice, a step plate. Flat "
      "continuous cold wind. THE FAINT DRY TICK of the slot rank each time it draws. Beatrice's boots on stone in Shot "
      "4. NO music, no score, no swells, no drone and no stingers — and NO sound cue on the refusal, on the moment the "
      "camera stops, or on her walk.",
      "Pronounce these words exactly and clearly: CLIMBING, SIXTY, THIRTY-ONE, BATTERY, UNION.",
      "PALETTE: ice white #EEF3F5, slot amber #A9721F, frost white #E9F1F4, coat soot #2C2A27.",
      "PHYSICS: severe cold injury does not reverse — Pikk's hand stays white and rigid for the entire film. " + FROST_OUT
      + " Slot brightness only ever decreases across the film. Nothing glows anywhere except the failing amber in the "
      "slots. " + NO_FX + " Nobody in this film is in distress."))

# =====================================================================================================
# SCENE 17 v4 — Tomas lifts her hand out, pays, and says the six words
# =====================================================================================================
FILES["ep2_scene17_v4"] = video(
    "EP02_SC17_V4", "ep2_scene17_the_true_sentence_v4",
    "Episode 02 · Scene 17 — EXT. HESSEL PIER — RECIPROCITY HOUSE — THE TRUE SENTENCE",
    "v4: opens on Beatrice's hand in the slot with the light dying (the threat, finally visible); Tomas lifts her hand "
    "out the way he lifted Pikk's in Sc08, puts his own in, and nothing happens; the six words; his breath; the slot "
    "takes it; the doorway rises to white. Tomas large in Shot 3 (§143); doorway named in both states (§147).",
    ["pika/refs/ep2_recip_lock_v3.jpg", "pika/refs/ep2_slotwall_from_sc01.jpg", "pika/refs/ep2_pier_lock.jpg",
     "pika/refs/ep2_beatrice_frost_lock.jpg", "pika/refs/beatrice_turnaround.png", "pika/refs/beatrice_portrait.png",
     "pika/refs/ep2_tomas_lock.png", "pika/refs/tomas_portrait.png"],
    j(head("FOUR"),
      "CAMERA DOCTRINE: SHOTS 1 AND 3 EACH CARRY ONE slow, smooth, continuous, dead-steady MECHANICAL DOLLY MOVE at a "
      "constant speed, still moving when the shot cuts; NOT handheld. SHOT 2 IS LOCKED. SHOT 4 IS ABSOLUTELY LOCKED "
      "and REFUSES TO MOVE TO THE GOOD NEWS HAPPENING BEHIND IT.",
      "REFERENCE PRECEDENCE: @Image1 IS THE AUTHORITY FOR THE CHAMBER. @Image2 IS THE AUTHORITY FOR THE STONE AND THE "
      "SLOTS. @Image3 IS THE AUTHORITY FOR THE PIER seen through the doorway. @Image4 IS THE AUTHORITY FOR HOW "
      "BEATRICE LOOKS WITH THE FROST ON HER — rime on the back of her right hand, a small starburst at the base of her "
      "throat.",
      CHAMBER, TWO_LIGHTS, SLOT_GRAMMAR,
      "THE SLOTS BEGIN THIS FILM DIM — barely lit, about a third of their normal strength. A FAINT DRY TICK comes from "
      "the rank each time it draws; it runs from the first frame until the moment stated in Shot 4, and then it stops.",
      "CAST — ONLY TWO PEOPLE APPEAR. A woman's voice is heard from outside and she is never seen.\n"
      + beatrice("@Image5 and @Image6 are") + " THE FROST IS ON HER, exactly as @Image4.\n"
      + tomas("@Image7 and @Image8 are", "@Image7"),
      "THE BREATH RULE — THE DEVICE OF THE WHOLE FILM: BEATRICE'S BREATH IS VISIBLE IN EVERY SHOT SHE IS IN. TOMAS'S "
      "BREATH: BEFORE HIS LAST SENTENCE IN SHOT 3, THE AIR IN FRONT OF HIS FACE IS COMPLETELY CLEAR AND TRANSPARENT; "
      "ON THAT SENTENCE A WHITE PLUME OF BREATH APPEARS IN FRONT OF HIS MOUTH AND HANGS IN THE COLD AIR. It is the only "
      "time he produces breath. NOBODY LOOKS AT IT, nobody mentions it, and the camera does not move toward it.",
      "NOBODY RAISES THEIR VOICE, HURRIES, PLEADS OR SHOUTS. There is no build and no gathering of courage.",
      "=== SHOT 1 — 0:00 to 0:07 — MEDIUM, 50mm, THE CAMERA GOES WITH HER ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "AMINA (off screen, from out on the pier, distant, urgent, unheroic): \"Thirty per cent. Twenty-eight through. "
      "Twelve on the pier.\"\n\n"
      "BEATRICE crosses the chamber to the slot rank, her right sleeve already pushed back, the frost on her knuckles "
      "and at her throat as in @Image4, and PUSHES HER RIGHT HAND INTO ONE OF THE SLOTS up to the wrist. She does it "
      "deliberately and unhurriedly. THE MOVE: the camera travels slowly and continuously with her toward the wall and "
      "keeps creeping after she stops. The worn trough slides past close to the lens.\n"
      "THE SLOT IS DRAWING FROM HER: THE AMBER LIGHT INSIDE IT BEGINS TO DIM, and white begins at her nail beds. Her "
      "face stays calm. Her breath is visible.\n\n"
      "CUT at 0:07.",
      "=== SHOT 2 — 0:07 to 0:13 — CLOSE-UP, 85mm, LOCKED — ONE HAND OUT, ANOTHER IN ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "BEATRICE (off screen, one word): \"Tomas.\"\n\n"
      "Close on the slot in the dark granite with BEATRICE'S HAND IN IT, the light inside dimming. A MAN'S HAND enters "
      "from frame right — the BLACK SLEEVE and TURNED-BACK CREAM CUFF of a robe-coat at the wrist — CLOSES ON HER "
      "WRIST AND LIFTS HER HAND OUT OF THE WALL with the unhurried competence of a man closing a drawer. Her "
      "fingertips are white only at the nail beds. Her hand leaves the frame.\n"
      "THEN HIS OWN HAND, cream cuff pushed back, GOES INTO THE SAME SLOT and stays there. THE SLOT'S DIM AMBER LIGHT "
      "COMES BACK UP TO ITS LEVEL AND HOLDS STEADY. HIS FINGERS STAY PINK. Nothing happens.\n\n"
      "CUT at 0:13.",
      "=== SHOT 3 — 0:13 to 0:22 — MEDIUM TWO-SHOT BY DEPTH, 40mm, SLOW PUSH — THE SENTENCE ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "TOMAS (flat, precise): \"It cannot take what is not there.\"\n"
      "BEATRICE: \"Then come away from the wall.\"\n"
      "TOMAS (he turns his head and looks at her; the same volume and the same voice he has used all day; he does not "
      "lean into it): \"I would prefer you did not die.\"\n\n"
      "TOMAS IS THE NEAR FIGURE: at FRAME RIGHT, CLOSE TO THE LENS AND LARGE, in sharp focus, his hand in the slot, warm "
      "amber on one side of his face and cold on the other; HIS TALL SMOOTH CREAM TUBE COLLAR AND THE LOOPING ENGRAVED "
      "RIBBON ARE PLAINLY VISIBLE AT THIS SIZE. BEATRICE IS THE FAR FIGURE: at FRAME LEFT, two metres deeper, a step "
      "back from the wall, holding the white fingertips of her right hand in her left, the starburst of rime at her "
      "throat, her breath visible. NEITHER OF THEM MOVES A STEP IN THIS SHOT. THE MOVE: the camera pushes in very "
      "slowly on the two of them, still advancing at the cut.\n"
      "ON HIS LAST SENTENCE, A WHITE PLUME OF BREATH APPEARS IN FRONT OF HIS FACE. Beatrice does not reply.\n\n"
      "CUT at 0:22.",
      "=== SHOT 4 — 0:22 to 0:30 — CLOSE-UP MACRO, 100mm, ABSOLUTELY LOCKED — THE PRICE ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "AMINA (off screen, distant, from the pier): \"Rank's at full. Get them on.\"\n\n"
      "Extreme close-up of HIS HAND IN THE SLOT, sharp, the black sleeve and cream cuff at the wrist. TWO THINGS HAPPEN "
      "AT ONCE, AT DIFFERENT DEPTHS, AND THE CAMERA STAYS ON THE NEAR ONE:\n"
      "IN THE FOREGROUND, SHARP: THE AMBER LIGHT INSIDE THAT SLOT DIMS SMOOTHLY AND GOES COMPLETELY OUT, and HIS "
      "FINGERS BLANCH WHITE from the NAIL BEDS up to the second knuckle, with fine white rime forming outward from the "
      "knuckles.\n"
      "IN THE TOP CORNER OF THE FRAME, DEEP AND OUT OF FOCUS, THE BRIGHT DOORWAY: it BEGINS as a DIM PALE GREY "
      "RECTANGLE and RISES SMOOTHLY TO A BLOWN-OUT GLARING WHITE and STAYS THAT WAY, with pale blurred shapes of people "
      "moving across it, boarding. THE CAMERA DOES NOT PAN, RACK OR REFRAME TOWARD IT.\n"
      "AT THE MOMENT THE DOORWAY GOES WHITE, THE DRY TICKING STOPS and does not return; the silence reads as relief.\n"
      "HOLD ON THE HAND. Then, at the very bottom edge of the frame, the hem of BEATRICE'S black coat and one boot step "
      "into the picture — ONE step toward him. CUT ON THAT STEP.",
      "SOUND: flat cold wind at the doorway, cut off abruptly by the stone. A tight dry acoustic with NO reverb tail. "
      "The dry tick, stopping dead when the doorway goes white. A woman's voice calling numbers from outside, distant "
      "and flat. NO music, no score, no swells, no drone and no stingers at any point, and NO sound cue on the sentence "
      "or on the moment the slot takes.",
      "Pronounce these words exactly and clearly: THIRTY, TWENTY-EIGHT, TWELVE, PREFER, RANK.",
      "PALETTE: slot amber #A9721F, frost white #E9F1F4, worn stone #B9B1A2, doorway white #EEF3F5.",
      "PHYSICS: cold injury behaves as real cold injury — white at the nail beds first, then up the finger, no "
      "reversal. " + FROST_OUT + " Slot brightness only ever changes by dimmer. Nothing glows anywhere except the amber "
      "inside the slots. " + NO_FX))

# =====================================================================================================
# INSERT REEL 1 — PIER: P1 Kell's knuckles (Sc01) · P2 "And nobody looked up." (Sc06) · P3 Ysra boards last
# =====================================================================================================
FILES["ep2_inserts_reel1"] = video(
    "EP02_INSERTS_REEL1", "ep2_inserts_reel1_pier",
    "Episode 02 · INSERT REEL 1 — EXT. HESSEL PIER — three inserts for the edit",
    "Three separate 10s inserts cut in camera, to be split in Resolve: P1 Kell's hand comes out of the cold slot "
    "with rime on it (Sc01 tag) · P2 CU Beatrice 'And nobody looked up.' (replaces the garbled Sc06 button) · P3 Ysra "
    "boards last with the veil in her hand and looks back (between Sc17 and Sc18).",
    ["pika/refs/ep2_pier_lock.jpg", "pika/refs/ep2_slotwall_from_sc01.jpg", "pika/refs/ep2_kell_alive_lock.jpg",
     "pika/refs/ep2_board_lock.jpg", "pika/refs/beatrice_portrait.png", "pika/refs/beatrice_turnaround.png",
     "pika/refs/ep2_unveiled_lock_v2.png", "pika/refs/ysra_turnaround.png"],
    j(head("THREE"),
      "THIS FILM IS THREE SEPARATE INSERT SHOTS FOR AN EDIT. EACH SHOT IS ITS OWN MOMENT ON THE SAME FROZEN PIER, AT "
      "A DIFFERENT MOMENT OF THE DAY, WITH ITS OWN PERSON. NOTHING AND NOBODY CARRIES OVER FROM ONE SHOT TO THE NEXT. "
      "Each shot holds steady on its subject from its first frame to its last.",
      "THE WORLD OF ALL THREE SHOTS, from @Image1: a low grey pier on a vast frozen brackish lake under a FLAT WHITE "
      "OVERCAST SKY of one single value — no sun, no cloud detail, cold 6500K daylight with no shadows. A low sea wall "
      "of COARSE DARK GREY SALT-STAINED GRANITE (@Image2) carries a rank of small HORIZONTAL slots, each a hand's width "
      "across, with warm amber light deep inside. Everyone's breath is visible in the cold.",
      "REFERENCE PRECEDENCE: @Image3 is the authority for KELL'S COAT SLEEVE AND HAND in Shot 1 only. @Image4 is the "
      "authority for the DESTINATION BOARD in Shot 2 only. @Image5 and @Image6 are BEATRICE in Shot 2 only. @Image7 is "
      "the authority for YSRA'S FACE, HAIR AND COSTUME in Shot 3 only — not for the table, the veil's position or the "
      "frozen hand that also appear in it. @Image8 is Ysra's sheet.",
      "=== SHOT 1 — 0:00 to 0:10 — P1 · CLOSE-UP, 100mm, LOCKED · DAWN · KELL'S HAND ===\n"
      "NOBODY SPEAKS IN THIS SHOT.\n\n"
      "Tight on ONE slot in the dark granite wall. On either side of it, the neighbouring slots glow warm amber. THIS "
      "ONE SLOT IS DARK AND COLD INSIDE — the only dark one in the frame. A man's hand is in it — the sleeve of a HEAVY "
      "PALE GREY-OATMEAL WOOL OVERCOAT at the wrist, exactly @Image3 — and it comes OUT of the slot into the flat white "
      "daylight. ON HIS KNUCKLES THERE IS A FINE FRESH WHITE RIME, and as we watch it grows OUTWARD a little further "
      "across the backs of his fingers. He turns the hand over once and holds it still for a moment, looking at it the "
      "way a man looks at a card that has been declined. Then he closes it into a fist, and the fist goes down out of "
      "the bottom of the frame into his coat pocket. The dark slot stays dark; its neighbours stay warm.\n"
      "SOUND: flat continuous cold wind, many people breathing nearby, boots on frozen concrete. No music.\n\n"
      "CUT at 0:10.",
      "=== SHOT 2 — 0:10 to 0:20 — P2 · CLOSE-UP, 85mm, LOCKED · UNDER THE BOARD · BEATRICE ===\n"
      "SPOKEN IN THIS SHOT, ONE LINE ONLY:\n"
      "BEATRICE (flat, procedural, to the board, not to anybody): \"And nobody looked up.\"\n"
      "AFTER THAT LINE THERE ARE TWO FULL SECONDS OF SILENCE TO THE END OF THE SHOT, AND NOBODY SAYS ANYTHING ELSE.\n\n"
      + beatrice("@Image5 and @Image6 are") + "\n"
      "Close on her face in three-quarter, her whole head inside the frame, LOOKING UP AND OUT OF FRAME at a "
      "mechanical destination board above her. Behind her, high and soft, the bone-coloured letters of the board "
      "(@Image4) are out of focus against the white sky. Cold flat key. HER BREATH IS VISIBLE. She says her four words "
      "to the board, at the emotional volume of a delayed connection, and then simply keeps looking up. Her face does "
      "not change.\n"
      "SOUND: wind; forty people breathing behind her; nothing else.\n\n"
      "CUT at 0:20.",
      "=== SHOT 3 — 0:20 to 0:30 — P3 · MEDIUM, 50mm, VERY SLOW PUSH · LATE MORNING · YSRA BOARDS LAST ===\n"
      "NOBODY SPEAKS IN THIS SHOT.\n\n"
      "AMBASSADOR YSRA SABLE — " + YSRA_FACE + ". HER HEAD IS BARE: the coiled black ring of her veil is NOT on her "
      "head; her braided crown is plainly uncovered, with a ring-shaped dent pressed into it where the veil sat for "
      "eleven years. SHE CARRIES THE VEIL IN HER LEFT GLOVED HAND, down at her side, the way a person carries a hat "
      "they have taken off: a heavy flat coil of many layered matte black bands, about the size of a dinner plate. It "
      "does not glow and does not float.\n"
      "She stands alone at the foot of the step of an open carriage door at FRAME RIGHT; the door shows the WARM "
      "AMBER-LIT WALNUT INTERIOR of the carriage. Everyone else has boarded. SHE TURNS HER HEAD AND LOOKS BACK DOWN "
      "THE PIER, past the lens at frame left, for a long moment. Her face is UNMANAGED — composed and completely "
      "exposed at once, dry-eyed, carrying something heavy. Then she turns and STEPS UP INTO THE DOORWAY, and AS SHE "
      "CROSSES THE THRESHOLD HER FACE CHANGES FROM COLD BLUE-WHITE DAYLIGHT TO WARM AMBER LAMPLIGHT. She does not look "
      "back again. THE MOVE: a very slow continuous push toward the door, still moving at the cut.\n"
      "SOUND: wind; a step plate; the faint warm murmur of the carriage interior, indistinct. No music.",
      "PALETTE: ice white #EEF3F5, brine grey #7E8A90, slot amber #A9721F, coat soot #2C2A27, veil black #101215, "
      "cobalt #1E2A5A.",
      FROST_OUT + " Nothing glows anywhere except the faint amber inside the slots and the carriage lamps. " + NO_FX))

# =====================================================================================================
# INSERT REEL 2 — C1 the cold-open hook · C2 Beatrice's hand rimes (Sc15) · C3 PASSENGERS: KELL (Sc14)
# =====================================================================================================
FILES["ep2_inserts_reel2"] = video(
    "EP02_INSERTS_REEL2", "ep2_inserts_reel2_carriage_macros",
    "Episode 02 · INSERT REEL 2 — the cold-open hook and two macro inserts",
    "Three separate 10s inserts cut in camera, to be split in Resolve: C1 HOOK — a passenger borrows the frozen "
    "man's sugar at breakfast (opens the episode) · C2 Beatrice's hand rimes on the counter (Sc15 button) · C3 Amina "
    "writes KELL under PASSENGERS (Sc14 payoff of the Sc03 plant).",
    ["pika/refs/ep2_coldcarriage_lock.jpg", "pika/refs/ep2_kell_from_sc03.jpg", "pika/refs/ep2_booth_plate.png",
     "pika/refs/beatrice_portrait.png", "pika/refs/ep2_beatrice_frost_lock.jpg", "pika/refs/ep2_notebook_passengers.jpg",
     "pika/refs/amina_hero.png"],
    j(head("THREE"),
      "THIS FILM IS THREE SEPARATE INSERT SHOTS FOR AN EDIT, IN THREE DIFFERENT PLACES. NOTHING AND NOBODY CARRIES "
      "OVER FROM ONE SHOT TO THE NEXT.",
      "REFERENCE PRECEDENCE: @Image1 IS THE AUTHORITY FOR SHOT 1 — the warm, occupied walnut first-class carriage with "
      "the frozen white man at his RIGHT-HAND WINDOW TABLE. @Image2 IS THE AUTHORITY FOR THAT MAN in Shot 1: his face, "
      "his PALE GREY-OATMEAL OVERCOAT and his frozen state, which is correct for this shot. @Image3 IS THE AUTHORITY FOR "
      "THE TIMBER BOOTH in Shot 2. @Image4 and @Image5 are the authority for BEATRICE'S SLEEVE AND HAND in Shot 2, and "
      "@Image5 for THE RIME ON THE BACK OF HER HAND. @Image6 IS THE ABSOLUTE AUTHORITY FOR THE NOTEBOOK PAGE in Shot 3 — "
      "its hand-drawn columns and the last column headed PASSENGERS. @Image7 is the authority for AMINA'S SLATE-BLUE "
      "SLEEVE AND GLOVED HAND in Shot 3.",
      "=== SHOT 1 — 0:00 to 0:10 — C1 · THE HOOK · WIDE TO MEDIUM, 32mm, SLOW DOLLY DOWN THE AISLE ===\n"
      "SPOKEN IN THIS SHOT:\n"
      "A PASSENGER (a well-dressed woman, cheerful, absent-minded, to the frozen man): \"Thank you.\"\n"
      "ANNOUNCEMENT (a calm, warm, exact railway voice over the carriage speakers): \"The Hessel crossing is warm and "
      "will remain warm. Passengers are thanked for their continued regard.\"\n\n"
      "Breakfast service in a warm, busy, first-class walnut saloon carriage at 3200K: passengers at every table, a "
      "porter pouring tea, steam rising from cups and teapots, cutlery, folded newspapers, low warm lamps, clear dry "
      "windows onto a white frozen lake. Some passengers are quietly impossible — long pointed ears and olive-grey "
      "skin at one table, a very tall thin traveller whose hands are wrapped in paper labels at another — and nobody "
      "remarks on them.\n"
      "THE MOVE: the camera travels slowly and continuously down the aisle at seated-eye height, past a passenger's "
      "shoulder close to the lens, toward the RIGHT-HAND WINDOW TABLE.\n"
      "AT THAT TABLE SITS A MAN WHO IS FROZEN SOLID — exactly @Image2: upright, chalk-white skin, his PALE GREY-OATMEAL "
      "COAT stiff, A STARBURST OF WHITE RIME RADIATING OUTWARD FROM HIS STERNUM across his lapels, both hands flat on "
      "the cloth. HE IS COMPLETELY MOTIONLESS. His teapot beside him is STILL STEAMING. The window beside him is clear "
      "and dry. NOBODY IN THE CARRIAGE LOOKS AT HIM.\n"
      "AS THE CAMERA ARRIVES, A PASSENGER AT THE NEXT TABLE LEANS ACROSS WITHOUT LOOKING AT HIM, TAKES THE LITTLE "
      "SUGAR BOWL FROM HIS TABLE, says her two words to him pleasantly, and goes back to her breakfast. He does not "
      "move. The announcement plays over the end of the shot.\n"
      "SOUND: the warm hum of the carriage, cutlery, cups, low conversation. " + CROWD_VOICES + " NO music.\n\n"
      "CUT at 0:10.",
      "=== SHOT 2 — 0:10 to 0:20 — C2 · MACRO, 100mm, LOCKED · THE MANIFEST BOOTH · BEATRICE'S HAND ===\n"
      "NOBODY SPEAKS IN THIS SHOT.\n\n"
      "Extreme close-up on a worn timber counter inside a cramped wooden booth, lit by ONE HARD LOW WARM BULB raking "
      "across it. A cream form with a fresh ink signature lies on the counter. A WOMAN'S RIGHT HAND — the cuff of a "
      "BLACK WRAP-COAT sleeve at the wrist — lays a pen down beside the form and then rests flat and still on the "
      "timber.\n"
      "ACROSS THE SHOT, FINE WHITE RIME GROWS OUTWARD FROM HER KNUCKLES in delicate needles across the backs of her "
      "fingers, exactly like @Image5 — the same outward frost as on the frozen man — while the hand itself stays "
      "relaxed and still. The frost throws its own tiny hard shadows under the warm bulb. The counter, the pen and the "
      "paper carry NO frost. The hand never reacts to it.\n"
      "SOUND: wind outside the hatch; the bulb's faint tick; a rubber stamp being put away off screen. No music.\n\n"
      "CUT at 0:20.",
      "=== SHOT 3 — 0:20 to 0:30 — C3 · MACRO, 100mm, LOCKED · AMINA'S NOTEBOOK ===\n"
      "NOBODY SPEAKS IN THIS SHOT.\n\n"
      "Extreme close-up of AMINA'S OPEN FIELD NOTEBOOK, exactly @Image6: hand-drawn ruled columns densely filled with "
      "pencil figures, and the LAST COLUMN, headed PASSENGERS, EMPTY under its heading. Warm raking light across the "
      "paper. The heading PASSENGERS stays fully inside the frame for the whole shot; the camera does not move and "
      "only the pencil moves.\n"
      "HER PENCIL ENTERS — her gloved hand and SLATE-BLUE sleeve at the edge of frame — and, under the heading "
      "PASSENGERS, in neat small pencil capitals, WRITES ONE WORD OF FOUR LETTERS: K, E, L, L. Then the pencil lifts "
      "and rests on the page beside the word. The word KELL sits alone in the column that was empty.\n"
      "SOUND: graphite on paper; wind beyond a stone doorway. No music.",
      "Pronounce these words exactly and clearly: HESSEL, CROSSING, CONTINUED, REGARD.",
      "PALETTE: carriage amber #B8801F, walnut #4A3122, rime white #E9F1F4, bulb amber #B8801F, graphite #3A3733, "
      "paper bone #DED5C2.",
      FROST_OUT + " Nothing glows anywhere except the lamps and the bulb. " + NO_FX))


# =====================================================================================================
def check(name, d):
    refs = d["reference_images"]
    used = sorted({int(n) for n in re.findall(r"@Image(\d+)", d["prompt"])})
    problems = []
    if used and max(used) > len(refs):
        problems.append(f"cites @Image{max(used)} but has {len(refs)} refs")
    if d["api_id"] == VIDEO_API:
        unused = [i + 1 for i in range(len(refs)) if (i + 1) not in used]
        if unused:
            problems.append(f"refs never cited: {unused}")
        if len(refs) > 9:
            problems.append(f"{len(refs)} refs (keep <= 9 for the ~10 MB payload limit, §194)")
        if "@Audio1" in d["prompt"] and not d.get("reference_audio"):
            problems.append("cites @Audio1 but has no reference_audio")
    for bad in ("kilojoule", "Attaché Kell", "Attache Kell", "Deputy Registrar"):
        if bad.lower() in d["prompt"].lower():
            problems.append(f"contains unpromptable term: {bad}")
    return problems


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ok = True
    for name, d in FILES.items():
        problems = check(name, d)
        path = OUT / f"{name}.json"
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        status = "OK " if not problems else "!! "
        ok &= not problems
        print(f"{status}{path.name:40s} refs={len(d['reference_images'])} prompt={len(d['prompt']):5d} chars "
              f"{'; '.join(problems)}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
