"""
run_session.py -- drive ONE demonstration session through app/server.py's own
endpoints (Flask test client), exactly the sequence the browser performs:
    /api/session/start -> /api/task/upload (x4) -> /api/task/transcript (x4)
    -> /api/session/analyze
Input audio is the project's SYNTHETIC sample recording (data/samples/
sample_control.wav, made by scripts/make_sample.py). Transcripts are operator-
typed, composed for this demonstration; no participant exists. The saved
session JSON in data/sessions/ is the Appendix E source.
"""
import io, json, os, sys
os.environ.setdefault("DHIKRA_DEMO", "1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
import server  # noqa: E402  (loads the frozen model at import)

TRANSCRIPTS = {
    # story-recall transcript is filled in after the app picks the story
    "procedure": (
        "First fill the kettle with water and put it on the stove. While it is "
        "heating take the teapot down and put in the tea leaves, about two "
        "spoons, and some mint if there is any. When the water boils pour it "
        "over the leaves and let it sit for a few minutes. Then add the sugar, "
        "quite a lot, and stir it. Pour it into the small glasses from high up "
        "so it gets a bit of foam on top, and then serve it on the tray."
    ),
    "picture": (
        "This is a kitchen. There is a woman standing at the sink washing the "
        "dishes and the water is running over the edge of the sink onto the "
        "floor, she has not noticed. Behind her a boy is standing on a stool "
        "reaching up to a high shelf for a jar, it looks like a jar of biscuits, "
        "and the stool is tipping over. A little girl is standing next to him "
        "with her hand up, she wants one too, or maybe she is trying to stop "
        "him. There is a cat on the floor watching. On the stove there is a "
        "teapot with steam coming out of it. There is a cloth hanging over the "
        "edge of the counter, and through the window there is a palm tree "
        "and the curtains are open."
    ),
    "fluency": (
        "cat dog horse cow sheep goat camel donkey lion tiger elephant giraffe "
        "monkey zebra rabbit mouse rat chicken duck goose pigeon eagle snake "
        "lizard fish dolphin whale shark bear wolf fox deer"
    ),
}

STORY_RETELL = {
    "well": (
        "A man left his village in the morning with some bread, three loaves, "
        "and a jug of water. On the way he met an old woman sitting under a "
        "palm tree and he gave her a loaf of bread and she drank some of his "
        "water. She thanked him and said he would find the thing he had lost at "
        "the well. When he got to the well he found his mother's ring that had "
        "been lost for years."
    ),
    "fisherman": (
        "A fisherman went out to the sea early in the morning with his old net "
        "and some dates. While he was throwing the net he saw a boy crying on "
        "the beach because he had lost his shoe. The fisherman gave the boy some "
        "dates and helped him look for the shoe and they found it in the rocks. "
        "That day he went home with the biggest catch he ever had."
    ),
    "teacher": (
        "A teacher lived in a small house near the school and she had a garden "
        "with an olive tree. One stormy night a big branch broke off and fell on "
        "the neighbour's wall. In the morning she said sorry and offered to fix "
        "the wall herself, but the neighbour said no, the tree had fed his "
        "children for years. The next spring they planted a new tree together."
    ),
}

def main():
    app = server.app
    app.config["TESTING"] = True
    c = app.test_client()
    cfg = c.get("/api/config").get_json()
    print("CONFIG:", json.dumps(cfg, ensure_ascii=False)[:600])

    r = c.post("/api/session/start", json={
        "language": "en", "code": "DEMO-E1", "age": 68, "sex": "female",
        "education": 12, "referral_context": "population",
        "family_history": "unknown", "known_surahs": None,
    }).get_json()
    sid = r["session_id"]; tasks = r["tasks"]
    print("SESSION:", sid, "stimuli:", r["stimuli"], "session_number:", r["session_number"])
    print("BATTERY:", [(t["id"], t.get("seconds")) for t in tasks])
    story_id = r["stimuli"]["story"]
    TRANSCRIPTS["story"] = STORY_RETELL[story_id]

    wav_path = os.path.join(os.path.dirname(__file__), "..", "data", "samples", "sample_control.wav")
    wav_bytes = open(wav_path, "rb").read()
    for t in tasks:
        tid = t["id"]
        if tid == "recitation":
            continue  # Arabic-only; not offered in an English session
        up = c.post("/api/task/upload", data={
            "session_id": sid, "task_id": tid, "language": "en",
            "audio": (io.BytesIO(wav_bytes), f"{tid}.wav"),
        }, content_type="multipart/form-data").get_json()
        print(f"UPLOAD {tid}: acoustic_ok={up.get('acoustic_ok')} quality={up.get('quality',{}).get('severity')} "
              f"asr_available={up.get('asr_available')} msg={str(up.get('asr_message'))[:80]}")
        tr = c.post("/api/task/transcript", json={"session_id": sid, "task_id": tid,
                                                  "text": TRANSCRIPTS[tid]}).get_json()
        assert tr.get("ok"), tr

    rep = c.post("/api/session/analyze", json={"session_id": sid}).get_json()
    out = os.path.join(os.path.dirname(__file__), "..", "data", "sessions", "appendix_e_report.json")
    json.dump(rep, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("REPORT keys:", list(rep.keys()))
    print("mode:", rep.get("mode"), "band:", rep.get("band"), "prob:", rep.get("probability"), "threshold:", rep.get("threshold"))
    print("saved:", out)

if __name__ == "__main__":
    main()
