"""Lexicon for rule-based multilingual attribute extraction.

Covers English plus Hindi, Punjabi, Gujarati, Bengali, Marathi, Tamil and Telugu
(native script and common romanisations). This is deliberately a transparent,
auditable baseline: it extracts product attributes from speech-to-text output. It does
NOT translate free-form speech. Extending a language = adding keywords here.
"""

SPEECH_LANGS = {  # BCP-47 codes used by the browser Web Speech API
    "hi-IN": "हिन्दी (Hindi)", "pa-IN": "ਪੰਜਾਬੀ (Punjabi)", "gu-IN": "ગુજરાતી (Gujarati)",
    "bn-IN": "বাংলা (Bengali)", "mr-IN": "मराठी (Marathi)", "ta-IN": "தமிழ் (Tamil)",
    "te-IN": "తెలుగు (Telugu)",
    "en-IN": "English (India)",
}

CATEGORIES = {
    "textile": {"en": "Handloom & textiles", "hi": "हथकरघा एवं वस्त्र"},
    "embroidery": {"en": "Embroidery & needlework", "hi": "कढ़ाई"},
    "pottery": {"en": "Pottery & terracotta", "hi": "मिट्टी के बर्तन / टेराकोटा"},
    "wood": {"en": "Woodcraft", "hi": "काष्ठ शिल्प"},
    "metal": {"en": "Metalcraft", "hi": "धातु शिल्प"},
    "bamboo_cane": {"en": "Bamboo, cane & grass", "hi": "बाँस, बेंत एवं घास शिल्प"},
    "leather": {"en": "Leather craft", "hi": "चमड़ा शिल्प"},
    "jewellery": {"en": "Handmade jewellery", "hi": "हस्तनिर्मित आभूषण"},
    "painting_print": {"en": "Painting & block print", "hi": "चित्रकला एवं छपाई"},
    "carpet_rug": {"en": "Carpets, rugs & dhurries", "hi": "कालीन एवं दरी"},
}

# key -> en, hi, hi_gender, category, keywords (lower-case; Indic as-is)
ITEMS = {
    "saree": ("saree", "साड़ी", "f", "textile", ["saree", "sari", "साड़ी", "साडी", "સાડી", "শাড়ি", "சேலை", "చీర", "paithani", "पैठणी"]),
    "shawl": ("shawl", "शॉल", "f", "textile", ["shawl", "शॉल", "ਸ਼ਾਲ", "શાલ", "শাল", "சால்வை", "శాలువా", "pashmina", "kullu"]),
    "dupatta": ("dupatta", "दुपट्टा", "m", "textile", ["dupatta", "दुपट्टा", "ਦੁਪੱਟਾ", "ચુંદડી", "ওড়না", "chunni", "ਚੁੰਨੀ"]),
    "stole": ("stole", "स्टोल", "m", "textile", ["stole", "scarf", "स्टोल", "muffler", "मफलर"]),
    "bedsheet": ("bedsheet", "चादर", "f", "textile", ["bedsheet", "bed sheet", "चादर", "ਚਾਦਰ", "ચાદર", "চাদর", "bedcover", "खेस", "ਖੇਸ"]),
    "fabric": ("handwoven fabric", "हाथ से बुना कपड़ा", "m", "textile", ["fabric", "cloth", "कपड़ा", "ਕੱਪੜਾ", "કાપડ", "কাপড়", "துணி", "బట్ట"]),
    "kantha": ("kantha throw", "कांथा", "m", "embroidery", ["kantha", "कांथा", "কাঁথা"]),
    "phulkari": ("phulkari", "फुलकारी", "f", "embroidery", ["phulkari", "फुलकारी", "ਫੁਲਕਾਰੀ"]),
    "embroidered": ("embroidered piece", "कढ़ाई वाला उत्पाद", "m", "embroidery", ["embroidery", "embroidered", "कढ़ाई", "कढाई", "ਕਢਾਈ", "ભરતકામ", "সেলাই", "भरतकाम", "எம்பிராய்டரி", "ఎంబ్రాయిడరీ", "zari", "ज़री"]),
    "pot": ("clay pot", "मिट्टी का घड़ा", "m", "pottery", ["pot", "matka", "मटका", "घड़ा", "ਘੜਾ", "માટલું", "হাঁড়ি", "பானை", "కుండ", "kulhad", "कुल्हड़"]),
    "pottery": ("terracotta piece", "टेराकोटा उत्पाद", "m", "pottery", ["terracotta", "टेराकोटा", "pottery", "मिट्टी", "ਮਿੱਟੀ", "માટી", "মাটি", "மண்", "మట్టి", "clay", "ceramic", "blue pottery"]),
    "box": ("wooden box", "लकड़ी का डिब्बा", "m", "wood", ["box", "डिब्बा", "casket"]),
    "wood_toy": ("wooden toy", "लकड़ी का खिलौना", "m", "wood", ["toy", "खिलौना", "channapatna", "ਖਿਡੌਣਾ", "રમકડું", "খেলনা", "பொம்மை", "బొమ్మ"]),
    "wood_item": ("wood carving", "लकड़ी की नक्काशी", "f", "wood", ["wood", "wooden", "लकड़ी", "ਲੱਕੜ", "લાકડું", "কাঠ", "लाकूड", "மரம்", "చెక్క", "sheesham", "शीशम", "carving", "नक्काशी"]),
    "brass": ("brass item", "पीतल की वस्तु", "f", "metal", ["brass", "पीतल", "ਪਿੱਤਲ", "પિત્તળ", "পিতল", "dhokra", "ढोकरा", "bell metal", "copper", "तांबा", "ताँबा", "ਤਾਂਬਾ", "metal", "धातु"]),
    "basket": ("handwoven basket", "हाथ से बुनी टोकरी", "f", "bamboo_cane", ["basket", "टोकरी", "ਟੋਕਰੀ", "ટોપલી", "ঝুড়ি", "கூடை", "బుట్ట", "डलिया"]),
    "bamboo": ("bamboo product", "बाँस का उत्पाद", "m", "bamboo_cane", ["bamboo", "बांस", "बाँस", "ਬਾਂਸ", "વાંસ", "বাঁশ", "बांबू", "மூங்கில்", "వెదురు", "cane", "बेंत", "grass", "sabai", "सबई", "moonj", "मूंज", "ਮੂੰਜ"]),
    "juti": ("handmade juti (footwear)", "हाथ की बनी जूती", "f", "leather", ["juti", "jutti", "जूती", "ਜੁੱਤੀ", "mojari", "mojri", "मोजड़ी", "kolhapuri", "कोल्हापुरी", "footwear", "चप्पल", "sandal"]),
    "leather_bag": ("leather bag", "चमड़े का बैग", "m", "leather", ["leather", "चमड़ा", "चमड़े", "ਚਮੜਾ", "ચામડું", "চামড়া", "चामडे", "தோல்", "తోలు", "bag", "बैग", "wallet", "पर्स"]),
    "necklace": ("necklace", "हार", "m", "jewellery", ["necklace", "हार", "ਹਾਰ", "jewellery", "jewelry", "गहना", "ज़ेवर", "जेवर", "bracelet", "कंगन", "earring", "झुमका", "bead", "मोती", "silver", "चांदी"]),
    "painting": ("hand-painted artwork", "हाथ से बनी पेंटिंग", "f", "painting_print", ["painting", "पेंटिंग", "चित्र", "madhubani", "मधुबनी", "warli", "वारली", "pattachitra", "पट्टचित्र", "gond", "गोंड", "kalamkari", "कलमकारी", "pichwai", "miniature"]),
    "block_print": ("block-printed textile", "ब्लॉक प्रिंट वस्त्र", "m", "painting_print", ["block print", "block-print", "ब्लॉक प्रिंट", "छपाई", "ajrakh", "अजरख", "bagru", "बगरू", "sanganeri", "bandhani", "बांधणी", "बाँधणी", "bandhej", "बंधेज", "ikat", "इकत", "batik", "बाटिक", "ਛਪਾਈ", "છાપકામ", "ছাপা"]),
    "rug": ("hand-knotted rug", "हाथ से बुना गलीचा", "m", "carpet_rug", ["rug", "carpet", "कालीन", "गलीचा", "दरी", "dhurrie", "durrie", "ਦਰੀ", "ਕਾਲੀਨ", "ગાલીચો", "কার্পেট", "கம்பளம்", "తివాచీ", "namda", "नमदा"]),
}

MATERIALS = {  # key: (en, hi, keywords)
    "cotton": ("cotton", "सूत (कॉटन)", ["cotton", "सूती", "कॉटन", "ਸੂਤੀ", "સુતરાઉ", "সুতি", "பருத்தி", "పత్తి", "khadi", "खादी", "ਖੱਦਰ"]),
    "silk": ("silk", "रेशम", ["silk", "रेशम", "ਰੇਸ਼ਮ", "રેશમ", "সিল্ক", "রেশম", "பட்டு", "పట్టు", "tussar", "तसर", "muga", "मूगा"]),
    "wool": ("wool", "ऊन", ["wool", "woollen", "ऊन", "ऊनी", "ਉੱਨ", "ઊન", "উল", "கம்பளி", "ఉన్ని", "pashmina", "पश्मीना"]),
    "jute": ("jute", "जूट", ["jute", "जूट", "ਪਟਸਨ", "શણ", "পাট"]),
    "clay": ("clay", "मिट्टी", ["clay", "मिट्टी", "terracotta", "टेराकोटा", "ਮਿੱਟੀ", "માટી", "মাটি", "மண்", "మట్టి"]),
    "brass": ("brass", "पीतल", ["brass", "पीतल", "ਪਿੱਤਲ", "પિત્તળ", "পিতল"]),
    "copper": ("copper", "तांबा", ["copper", "तांबा", "ताँबा", "ਤਾਂਬਾ"]),
    "wood": ("wood", "लकड़ी", ["wood", "लकड़ी", "ਲੱਕੜ", "લાકડું", "কাঠ", "लाकूड", "மரம்", "చెక్క", "sheesham", "शीशम"]),
    "bamboo": ("bamboo", "बाँस", ["bamboo", "बांस", "बाँस", "ਬਾਂਸ", "વાંસ", "বাঁশ", "बांबू", "மூங்கில்", "వెదురు"]),
    "cane": ("cane", "बेंत", ["cane", "बेंत", "rattan"]),
    "grass": ("natural grass", "प्राकृतिक घास", ["grass", "घास", "sabai", "सबई", "moonj", "मूंज", "ਮੂੰਜ", "kauna", "कौना"]),
    "leather": ("leather", "चमड़ा", ["leather", "चमड़ा", "चमड़े", "ਚਮੜਾ", "ચામડું", "চামড়া", "தோல்", "తోలు"]),
    "silver": ("silver", "चाँदी", ["silver", "चांदी", "चाँदी", "ਚਾਂਦੀ", "ચાંદી"]),
}

COLORS = {  # key: (en, hi, keywords)
    "red": ("red", "लाल", ["red", "लाल", "ਲਾਲ", "લાલ", "লাল", "சிவப்பு", "ఎరుపు", "ఎర్ర"]),
    "maroon": ("maroon", "मैरून", ["maroon", "मैरून", "marun"]),
    "blue": ("blue", "नीला", ["blue", "नीला", "नीले", "नीली", "ਨੀਲੀ", "ਨੀਲਾ", "વાદળી", "নীল", "நீலம்", "నీలం", "indigo", "इंडिगो"]),
    "green": ("green", "हरा", ["green", "हरा", "हरे", "हरी", "ਹਰੀ", "ਹਰਾ", "લીલો", "সবুজ", "பச்சை", "ఆకుపచ్చ"]),
    "yellow": ("yellow", "पीला", ["yellow", "पीला", "पीले", "पीली", "ਪੀਲੀ", "ਪੀਲਾ", "પીળો", "হলুদ", "மஞ்சள்", "పసుపు", "haldi"]),
    "orange": ("orange", "नारंगी", ["orange", "नारंगी", "ਸੰਤਰੀ", "કેસરી", "saffron", "केसरी"]),
    "pink": ("pink", "गुलाबी", ["pink", "गुलाबी", "ਗੁਲਾਬੀ", "ગુલાબી", "গোলাপি"]),
    "purple": ("purple", "बैंगनी", ["purple", "बैंगनी", "ਜਾਮਨੀ", "જાંબલી", "violet"]),
    "black": ("black", "काला", ["black", "काला", "काले", "काली", "ਕਾਲੀ", "ਕਾਲਾ", "કાળો", "কালো", "கருப்பு", "నలుపు"]),
    "white": ("white", "सफेद", ["white", "सफेद", "सफ़ेद", "ਚਿੱਟਾ", "સફેદ", "সাদা", "வெள்ளை", "తెలుపు"]),
    "brown": ("brown", "भूरा", ["brown", "भूरा", "ਭੂਰਾ", "natural", "earthy", "terracotta colour"]),
    "multicolour": ("multicolour", "बहुरंगी", ["multicolour", "multicolor", "multi colour", "बहुरंगी", "रंग-बिरंगी", "ਰੰਗ-ਬਿਰੰਗੀ"]),
}

TECHNIQUES = {  # key: (en, hi, keywords)
    "handloom": ("handwoven on a handloom", "हथकरघे पर हाथ की बुनाई", ["handloom", "हथकरघा", "हथकरघे", "handwoven", "hand woven", "हाथ से बुना", "ਹੱਥ ਖੱਡੀ", "હાથશાળ", "তাঁত", "கைத்தறி", "చేనేత"]),
    "embroidered": ("hand-embroidered", "हाथ की कढ़ाई", ["hand embroidery", "hand-embroidered", "हाथ की कढ़ाई", "कढ़ाई", "ਕਢਾਈ", "ભરતકામ", "সেলাই", "भरतकाम"]),
    "block_printed": ("hand block-printed", "हाथ की ब्लॉक प्रिंटिंग", ["block print", "block-print", "ब्लॉक प्रिंट", "छपाई", "ਛਪਾਈ", "છાપકામ"]),
    "hand_painted": ("hand-painted", "हाथ की चित्रकारी", ["hand painted", "hand-painted", "हाथ से बनी पेंटिंग", "पेंटिंग", "painting", "चित्र"]),
    "hand_carved": ("hand-carved", "हाथ की नक्काशी", ["carved", "carving", "नक्काशी", "तराश"]),
    "wheel_thrown": ("wheel-thrown and fired", "चाक पर निर्माण, भट्टी में पकाया", ["wheel", "चाक", "fired", "पकाया", "kiln", "भट्टी"]),
    "handmade": ("handmade", "हस्तनिर्मित", ["handmade", "hand made", "हाथ से बना", "हस्तनिर्मित", "ਹੱਥ ਨਾਲ", "હાથથી"]),
}

CARE = {  # material -> (en, hi)
    "cotton": ("Gentle hand wash in cold water; dry in shade.", "ठंडे पानी में हल्के हाथ से धोएँ; छाया में सुखाएँ।"),
    "silk": ("Dry clean recommended; avoid direct sunlight and harsh detergent.", "ड्राई क्लीन करवाएँ; सीधी धूप और तेज़ डिटर्जेंट से बचें।"),
    "wool": ("Dry clean or gentle cold hand wash; dry flat.", "ड्राई क्लीन करें या ठंडे पानी में हल्के हाथ से धोकर समतल सुखाएँ।"),
    "jute": ("Spot clean only; keep away from prolonged moisture.", "केवल दाग साफ़ करें; लंबे समय तक नमी से बचाएँ।"),
    "clay": ("Handle with care; wipe with a dry or slightly damp cloth.", "सावधानी से रखें; सूखे या हल्के नम कपड़े से पोंछें।"),
    "brass": ("Polish occasionally with a soft cloth and a little lemon or tamarind.", "नरम कपड़े और थोड़े नींबू या इमली से कभी-कभी चमकाएँ।"),
    "copper": ("Polish occasionally with a soft cloth and a little lemon or tamarind.", "नरम कपड़े और थोड़े नींबू या इमली से कभी-कभी चमकाएँ।"),
    "wood": ("Wipe with a dry cloth; keep away from water and direct heat.", "सूखे कपड़े से पोंछें; पानी और सीधी गर्मी से दूर रखें।"),
    "bamboo": ("Wipe with a dry cloth; keep away from prolonged moisture.", "सूखे कपड़े से पोंछें; लंबे समय तक नमी से बचाएँ।"),
    "cane": ("Wipe with a dry cloth; keep away from prolonged moisture.", "सूखे कपड़े से पोंछें; लंबे समय तक नमी से बचाएँ।"),
    "grass": ("Wipe with a dry cloth; keep away from prolonged moisture.", "सूखे कपड़े से पोंछें; लंबे समय तक नमी से बचाएँ।"),
    "leather": ("Wipe with a dry cloth; condition occasionally; avoid soaking.", "सूखे कपड़े से पोंछें; कभी-कभी पॉलिश करें; भिगोने से बचें।"),
    "silver": ("Store in a dry pouch; polish with a soft cloth.", "सूखी थैली में रखें; नरम कपड़े से चमकाएँ।"),
}

PRICE_WORDS = ["price", "cost", "rate", "mrp", "selling", "कीमत", "दाम", "मूल्य", "भाव", "ਕੀਮਤ", "ਭਾਅ", "ਮੁੱਲ", "કિંમત", "ભાવ", "দাম", "মূল্য", "விலை", "ధర"]
COST_WORDS = ["material", "raw", "yarn", "thread", "लागत", "कच्चा", "सामग्री", "धागा", "ਲਾਗਤ", "ਕੱਚਾ", "ખર્ચ", "સામગ્રી", "খরচ", "செலவு", "ఖర్చు", "kharcha", "kharch", "invest", "spent"]
CURRENCY_WORDS = ["₹", "rs", "rs.", "rupee", "rupees", "rupaye", "रुपये", "रुपए", "रुपया", "ਰੁਪਏ", "રૂપિયા", "টাকা", "ரூபாய்", "రూపాయలు", "रुपयांना", "inr"]
DAY_WORDS = ["day", "days", "din", "दिन", "ਦਿਨ", "દિવસ", "দিন", "நாள்", "రోజు", "दिवस"]
HOUR_WORDS = ["hour", "hours", "hr", "hrs", "घंटे", "घंटा", "ਘੰਟੇ", "ਘੰਟਾ", "કલાક", "ঘণ্টা", "மணி", "గంటలు"]
LENGTH_UNITS = {"meter": ["meter", "metre", "m", "मीटर", "ਮੀਟਰ", "મીટર", "মিটার"], "cm": ["cm", "centimeter", "सेंटीमीटर", "सेमी"],
                "inch": ["inch", "inches", "इंच", "ਇੰਚ", "ઇંચ"], "feet": ["feet", "foot", "ft", "फुट", "फीट", "ਫੁੱਟ"]}

GENERIC_ITEMS = {"pottery", "wood_item", "bamboo", "fabric", "embroidered", "brass", "block_print"}
