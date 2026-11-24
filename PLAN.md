---
this_file: PLAN.md
---

# Remaining work

1. **First PyPI release.** Configure the publisher for `vexyart/vexy-pdfsvgpy`, workflow `release.yml`, environment `pypi`. The workflow exists at tag `v0.0.6`. Check its Actions run and verify the wheel and sdist on PyPI before closing the release.
2. **Directory inputs (101).** Exercise flat, recursive and glob selection with mixed-case JPG/JPEG filenames. Compare the actual output set with the expected files.
3. **Composition (101).** Wire multi-input `convert()` through the PDF reshape helpers. Reopen `pdf_m` and `pdf_l` results to check page order, count and layer names.
4. **CLI shortcuts (105).** Compare each supported format spelling with its explicit conversion command, including bare and content-only forms.
5. **Text treatment (106).** Inspect text objects, outlines and font resources for `text`, `paths` and default `fonts` on samples with and without embeddable fonts.
6. **Optional backends (107).** Install the extras and exercise the Cairo and Ghostscript hints on real inputs, including PDF outlining. Resolve the requested optional Poppler PDF path. Measure coverage and add extras-gated tests or document exclusions from the default coverage target.
7. **Windows CI.** Confirm wheels install on Windows for the supported CI Python versions, then add Windows to the test matrix.
8. **Coverage floor.** Once the optional-backend coverage decision is made, check whether an 80% CI floor is sustainable.
