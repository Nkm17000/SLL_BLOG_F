from app.topic_history import is_repeated_topic, normalize_topic

def test_exact_topic_rejected():
    h={"history":[{"technical_topic":"OpenBMC remote management on Nuvoton NPCM8XX", "source_url":"https://example.com/a"}]}
    assert is_repeated_topic("OpenBMC remote management on Nuvoton NPCM8XX",h)
    assert is_repeated_topic("Something else",h,source_url="https://example.com/a?utm_source=rss")

def test_new_topic_allowed():
    h={"history":[{"technical_topic":"OpenBMC remote management on Nuvoton NPCM8XX"}]}
    assert not is_repeated_topic("Oracle APEX AI report generation",h)

def test_title_normalization():
    assert normalize_topic("New: AI Agents in Windows!") == "ai agents windows"
