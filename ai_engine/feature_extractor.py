import re
from typing import Dict, List

TUNISIAN_BANKS = ["biat", "attijari", "bna", "amen bank", "stb", "ubci", "zitouna", "post bank"]

URGENCY_WORDS = [
    "urgent", "immediately", "asap", "now", "hurry", "act now", 
    "limited time", "expire", "suspended", "verify now", "final notice", "last chance"
]

FINANCIAL_TERMS = [
    "bank", "account", "password", "credit card", "payment", "invoice", 
    "transaction", "verify", "update payment", "locked", "unusual activity", 
    "wire transfer", "otp", "code de vérification", "solde", "virement"
]

EMOTIONAL_TRIGGERS = [
    "threat", "hack", "compromised", "breach", "attack", "scared", "panic", 
    "congratulations", "winner", "inheritance", "lottery", "blackmail"
]

def extract_features(text: str) -> Dict[str, any]:
    """
    Converts raw text into measurable linguistic & statistical features.
    Output is a dictionary. Every key is traceable for XAI compliance.
    """
    text_lower = text.lower()         
    words = text_lower.split()         
    
    features = {
        "length": len(text),
        "word_count": len(words),
        "uppercase_ratio": sum(1 for c in text if c.isupper()) / max(len(text), 1),
        "exclamation_count": text.count("!"),
        "question_count": text.count("?"),
        "url_count": len(re.findall(r'https?://\S+|www\.\S+', text)),
        "email_count": len(re.findall(r'\S+@\S+\.\S+', text)),
        "digit_count": sum(c.isdigit() for c in text),
         "tunisian_phone": bool(re.search(r'(\+216|00216|216)[\s-]*\d{2}[\s-]*\d{3}[\s-]*\d{3}', text)),
        "tunisian_bank_mentions": sum(1 for bank in TUNISIAN_BANKS if bank in text_lower),
        
        "urgency_words": [w for w in URGENCY_WORDS if w in text_lower],
        "financial_terms": [w for w in FINANCIAL_TERMS if w in text_lower],
        "emotional_triggers": [w for w in EMOTIONAL_TRIGGERS if w in text_lower],
        
        "suspicious_tld": bool(re.search(r'\.(xyz|top|club|online|site|tk|ml|cc)\b', text_lower)),
        "multiple_domains": len(set(re.findall(r'https?://([a-z0-9.-]+)', text_lower))) > 1
    }
    
    features["urgency_score"] = len(features["urgency_words"])
    features["financial_score"] = len(features["financial_terms"])
    features["emotional_score"] = len(features["emotional_triggers"])
    features["link_density"] = features["url_count"] / max(features["word_count"], 1)
    
    return features
if __name__ == "__main__":
   
    test1 = "URGENT! Your BIAT account is suspended. Click immediately: http://fake-biat.xyz to verify or lose access!!!"
    print("🔹 TEST 1: Tunisian Phishing")
    print(extract_features(test1))
    print("-" * 50)
    
    test2 = "Hello team, meeting tomorrow at 10am in room B. Please bring laptops."
    print("🔹 TEST 2: Safe Message")
    print(extract_features(test2))
    print("-" * 50)
    
   
    test3 = "I have your private photos. Send 500 TND to +216 99 123 456 within 24 hours or I post them."
    print("🔹 TEST 3: Emotional/Local Threat")
    print(extract_features(test3))