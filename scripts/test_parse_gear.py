#!/usr/bin/env python3
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("parse_gear.py")
sys.path.insert(0, str(SCRIPT.parent))

from parse_gear import parse_items  # noqa: E402

TITLE = "Etenwolf S1 inflator pumped up my truck tire"


def items_for(description, title=TITLE):
    gear = parse_items([{"id": "abc", "title": title, "description": description}])
    return gear[0]["items"] if gear else []


class ParseGear(unittest.TestCase):
    def test_label_becomes_name(self):
        self.assertEqual(
            items_for("Schumacher battery load tester (6/12 V): https://amzn.to/3VToctB"),
            [{"name": "Schumacher battery load tester (6/12 V)", "link": "https://amzn.to/3VToctB"}],
        )

    def test_generic_label_falls_back_to_title(self):
        for line in (
            "Amazon link:  https://geni.us/K142O",
            "Amazon: https://geni.us/K142O",
            "Link: https://geni.us/K142O",
            "Buy: https://geni.us/K142O",
        ):
            with self.subTest(line=line):
                self.assertEqual(items_for(line), [{"name": TITLE, "link": "https://geni.us/K142O"}])

    def test_storefront_is_skipped(self):
        self.assertEqual(items_for("My Amazon storefront: https://geni.us/8tngo"), [])
        self.assertEqual(items_for("Shop with me: https://www.amazon.com/shop/higgprojects"), [])

    def test_bare_link_falls_back_to_title(self):
        link = "https://www.amazon.com/dp/B0DJQF83C2?ref=t_ac&linkCode=tr1&tag=leehigginson-20"
        self.assertEqual(items_for(link), [{"name": TITLE, "link": link}])

    def test_full_label_is_kept(self):
        self.assertEqual(
            items_for(
                "397 Transmission Line Fitting (TESHITVLOG, the cooler line adapter): "
                "https://www.amazon.com/dp/B0FD9WYBD3?tag=leehigginson-20"
            ),
            [
                {
                    "name": "397 Transmission Line Fitting (TESHITVLOG, the cooler line adapter)",
                    "link": "https://www.amazon.com/dp/B0FD9WYBD3?tag=leehigginson-20",
                }
            ],
        )

    def test_code_and_deal(self):
        gear = parse_items(
            [
                {
                    "id": "abc",
                    "title": TITLE,
                    "description": "Wilde Trail Flashlight: https://amzn.to/4lHFRxh\n10% off with code HIGGPROJECTS",
                }
            ]
        )
        self.assertEqual(gear[0]["code"], "HIGGPROJECTS")
        self.assertEqual(gear[0]["deal"], "10% OFF")

    def test_every_product_line_is_read_and_storefront_dropped(self):
        description = "\n".join(
            [
                "Things I used:",
                "Magnetic helping hands: https://geni.us/PBd4eY",
                "Solder sucker: https://geni.us/roGT",
                "My Amazon storefront: https://geni.us/8tngo",
                "Solder sucker again: https://geni.us/roGT",
            ]
        )
        self.assertEqual(
            items_for(description),
            [
                {"name": "Magnetic helping hands", "link": "https://geni.us/PBd4eY"},
                {"name": "Solder sucker", "link": "https://geni.us/roGT"},
            ],
        )

    def test_video_without_links_is_left_out_and_limit_is_twelve(self):
        videos = [{"id": "none", "title": "No links", "description": "Just a story."}]
        videos += [
            {"id": f"v{n}", "title": f"Video {n}", "description": "https://geni.us/abc"} for n in range(15)
        ]
        gear = parse_items(videos)
        self.assertEqual([g["id"] for g in gear], [f"v{n}" for n in range(12)])

    def test_cli_reads_workflow_payload(self):
        payload = {"items": [{"id": "abc", "title": TITLE, "description": "Amazon: https://geni.us/K142O"}]}
        out = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertEqual(
            json.loads(out),
            [{"id": "abc", "title": TITLE, "items": [{"name": TITLE, "link": "https://geni.us/K142O"}]}],
        )


if __name__ == "__main__":
    unittest.main()
