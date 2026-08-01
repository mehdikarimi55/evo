"""Unit tests for cached Persian journal content localization."""

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import MagicMock

from evo.content_i18n import (
    TranslationCache,
    TranslationError,
    apply_translations,
    collect_translatable_texts,
    looks_latin_dominant,
    translate_missing,
)
from evo.providers.base import ModelReply


class ContentI18nTests(unittest.TestCase):
    def test_looks_latin_dominant_skips_persian(self):
        self.assertTrue(looks_latin_dominant("Explore digital abiogenesis"))
        self.assertFalse(looks_latin_dominant("کاوش زایش دیجیتال"))
        self.assertFalse(looks_latin_dominant("ab"))

    def test_collect_and_apply_round_trip(self):
        entries = [
            {
                "event_type": "autonomy.generation",
                "payload": {
                    "summary": "Grow a safer founder",
                    "rationale": "Protect the founders",
                    "target_path": "organisms/prompt.md",
                },
            }
        ]
        texts = collect_translatable_texts(entries)
        self.assertEqual(
            texts,
            ["Grow a safer founder", "Protect the founders"],
        )
        mapping = {
            "Grow a safer founder": "بنیان‌گذار امن‌تری بساز",
            "Protect the founders": "از بنیان‌گذاران محافظت کن",
        }
        localized = apply_translations(entries[0], mapping)
        payload = localized["payload"]
        self.assertEqual(payload["summary"], "بنیان‌گذار امن‌تری بساز")
        self.assertEqual(payload["rationale"], "از بنیان‌گذاران محافظت کن")
        self.assertEqual(payload["target_path"], "organisms/prompt.md")

    def test_translate_missing_uses_cache_and_provider(self):
        with TemporaryDirectory() as temporary:
            cache = TranslationCache(Path(temporary) / "i18n-cache-fa.json")
            cache.put_many({"cached text here": "متن ذخیره‌شده"})
            provider = MagicMock()
            provider.generate_json.return_value = ModelReply(
                text=json.dumps(
                    {"translations": ["متن تازه"]},
                    ensure_ascii=False,
                ),
                input_tokens=10,
                output_tokens=10,
                model="mock",
            )
            resolved = translate_missing(
                ["cached text here", "fresh latin sentence"],
                cache=cache,
                provider=provider,
            )
            self.assertEqual(resolved["cached text here"], "متن ذخیره‌شده")
            self.assertEqual(resolved["fresh latin sentence"], "متن تازه")
            provider.generate_json.assert_called_once()
            self.assertEqual(cache.get("fresh latin sentence"), "متن تازه")

    def test_translate_missing_rejects_mismatched_batch(self):
        with TemporaryDirectory() as temporary:
            cache = TranslationCache(Path(temporary) / "cache.json")
            provider = MagicMock()
            provider.generate_json.return_value = ModelReply(
                text='{"translations":["only-one"]}',
                input_tokens=1,
                output_tokens=1,
                model="mock",
            )
            with self.assertRaises(TranslationError):
                translate_missing(
                    ["one sentence here", "second sentence here"],
                    cache=cache,
                    provider=provider,
                )


if __name__ == "__main__":
    unittest.main()
