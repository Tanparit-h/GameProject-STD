import tempfile
import unittest
from pathlib import Path

from tools.creator_asset_validator import validate_creator_exports


class CreatorAssetValidatorTests(unittest.TestCase):
    def test_validate_creator_exports_passes_with_glb_and_clean_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "exports"
            export_dir.mkdir()
            (export_dir / "asset.glb").write_bytes(b"glb")
            log = Path(temp_dir) / "blender.log"
            log.write_text("Exit code: 0", encoding="utf-8")

            result = validate_creator_exports(export_dir, log)

        self.assertIs(result["passed"], True)

    def test_validate_creator_exports_fails_on_error_marker(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "exports"
            export_dir.mkdir()
            (export_dir / "asset.glb").write_bytes(b"glb")
            log = Path(temp_dir) / "blender.log"
            log.write_text("Traceback", encoding="utf-8")

            result = validate_creator_exports(export_dir, log)

        self.assertIs(result["passed"], False)
        self.assertIn("Traceback", result["error_markers"])


if __name__ == "__main__":
    unittest.main()
