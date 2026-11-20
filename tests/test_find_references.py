import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(
  0,
  str(Path(__file__).resolve().parents[1] / "scripts")
)

from find_references import find_references


class TestFindReferences(unittest.TestCase):

  def test_ignora_comentarios_e_strings(self):
      source = '''// import axios from "axios";

const texto = 'require("lodash")';

/*
import express from "express";
*/

import express from "express";
const axios = require("axios");
const lodash = await import("lodash");
'''

      with tempfile.TemporaryDirectory() as directory:
          service = Path(directory) / "service-a"
          service.mkdir()

          (service / "index.js").write_text(
              source,
              encoding="utf-8"
          )

          dependencies = {
              "axios", "express", "lodash"
          }

          results = find_references(
              service,
              dependencies
          )

          found = {
              (item["component"], item["line"])
              for item in results
          }

          expected = {
              ("express", 9),
              ("axios", 10),
              ("lodash", 11)
          }

          self.assertEqual(found, expected)


if __name__ == "__main__":
  unittest.main()